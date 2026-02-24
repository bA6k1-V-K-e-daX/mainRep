package httpservices

import (
	"fmt"
	"manager/internal/models"
	dbclientt "manager/internal/repository/database"
	mlclient "manager/internal/repository/ml"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

type HTTPService struct {
	dbClient   *dbclientt.Client
	mlClient   *mlclient.Client
	jwtSecret  []byte
	volumePath string
}

func New(db *dbclientt.Client, ml *mlclient.Client, secret string, volumePath string) *HTTPService {
	return &HTTPService{
		dbClient:   db,
		mlClient:   ml,
		jwtSecret:  []byte(secret),
		volumePath: volumePath,
	}
}

func (s *HTTPService) Register(c *gin.Context) {
	var req models.AuthRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	user := models.User{
		Login:        req.Login,
		PasswordHash: string(hash),
	}

	if err := s.dbClient.CreateUser(c.Request.Context(), user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register user (likely exists)"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "User registered successfully"})
}

func (s *HTTPService) Login(c *gin.Context) {
	var req models.AuthRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	user, err := s.dbClient.GetUserByLogin(c.Request.Context(), req.Login)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": user.ID,
		"exp":     time.Now().Add(72 * time.Hour).Unix(),
	})

	tokenString, err := token.SignedString(s.jwtSecret)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, models.AuthResponse{Token: tokenString})
}

func (s *HTTPService) Detect(c *gin.Context) {
	userID := c.GetString("user_id")

	queryID, err := s.dbClient.CreateQuery(c.Request.Context(), userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register query task"})
		return
	}

	queryStrID := strconv.FormatInt(queryID, 10)
	queryBasePath := filepath.Join(s.volumePath, queryStrID)
	sourceDir := filepath.Join(queryBasePath, "source")
	resultDir := filepath.Join(queryBasePath, "result")

	if err := os.MkdirAll(sourceDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create source directory"})
		return
	}
	if err := os.MkdirAll(resultDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create result directory"})
		return
	}

	form, err := c.MultipartForm()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to parse multipart data"})
		return
	}

	files := form.File["files"]
	for _, file := range files {
		destination := filepath.Join(sourceDir, file.Filename)
		if err := c.SaveUploadedFile(file, destination); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Failed to save file: %s", file.Filename)})
			return
		}
	}

	targets := c.PostFormArray("targets")

	resp, err := s.mlClient.Detect(c.Request.Context(), queryID, queryBasePath, targets)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "ML Service failure", "details": err.Error()})
		return
	}

	if !resp.Success {
		c.JSON(http.StatusUnprocessableEntity, gin.H{"error": "Detection failed", "message": resp.ErrorMessage})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"query_id":     resp.QueryId,
		"status":       "Success",
		"class_counts": resp.ClassCounts,
		"total":        resp.TotalObjects,
		"result_dir":   fmt.Sprintf("/results/%s/result/", queryStrID),
	})
}

func (s *HTTPService) AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tokenString := c.GetHeader("Authorization")
		if tokenString == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		if len(tokenString) > 7 && tokenString[:7] == "Bearer " {
			tokenString = tokenString[7:]
		}

		token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method")
			}
			return s.jwtSecret, nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid claims map"})
			c.Abort()
			return
		}

		c.Set("user_id", claims["user_id"])
		c.Next()
	}
}
