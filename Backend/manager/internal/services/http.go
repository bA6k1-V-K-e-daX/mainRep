package httpservices

import (
	"bufio"
	"encoding/json"
	"fmt"
	"manager/internal/models"
	dbclientt "manager/internal/repository/database"
	mlclient "manager/internal/repository/ml"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
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

	form, err := c.MultipartForm()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Failed to parse multipart data",
			"details": err.Error(),
		})
		return
	}

	payloadValues := form.Value["payload"]
	if len(payloadValues) == 0 || payloadValues[0] == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'payload' field in form data"})
		return
	}

	payloadStr := payloadValues[0]

	var payload models.DetectPayload
	if err := json.Unmarshal([]byte(payloadStr), &payload); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid JSON in 'payload' field",
			"details": err.Error(),
		})
		return
	}

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

	files := form.File["files"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No files provided"})
		return
	}

	for _, file := range files {
		destination := filepath.Join(sourceDir, file.Filename)
		if err := c.SaveUploadedFile(file, destination); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Failed to save file: %s", file.Filename)})
			return
		}
	}

	resp, err := s.mlClient.Detect(c.Request.Context(), queryID, s.volumePath, payload.Targets)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "ML Service failure", "details": err.Error()})
		return
	}

	if !resp.Success {
		c.JSON(http.StatusUnprocessableEntity, gin.H{"error": "Detection failed", "message": resp.ErrorMessage})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"query_id":      resp.QueryId,
		"status":        "Success",
		"instance_info": resp.InstanceInfo,
		"total":         resp.TotalObjects,
		"result_dir":    fmt.Sprintf("/results/%s/result/", queryStrID),
	})
}

func (s *HTTPService) History(c *gin.Context) {
	userID := c.GetString("user_id")

	var req models.HistoryAnswer
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	queries, err := s.dbClient.GetHistoryAnswers(c.Request.Context(), req.Quantity, userID, req.Flag)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user queries"})
		return
	}
	var response []models.HistoryResponse
	for _, queryID := range queries {
		reportPath := filepath.Join(s.volumePath, strconv.FormatInt(int64(queryID), 10), "result", "report.txt")
		if _, err := os.Stat(reportPath); os.IsNotExist(err) {
			reportPath = filepath.Join(s.volumePath, strconv.FormatInt(int64(queryID), 10), "result", "detection_summary.txt")
		}

		entries, err := ParseReport(reportPath)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Report not found or invalid format", "details": err.Error()})
			return
		}
		response = append(response, models.HistoryResponse{
			QueryId: queryID,
			Entries: entries,
		})
	}
	c.JSON(http.StatusOK, gin.H{
		"queries": response,
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

func ParseReport(filePath string) ([]models.ReportEntry, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open report file: %w", err)
	}
	defer file.Close()

	var entries []models.ReportEntry
	scanner := bufio.NewScanner(file)

	var currentFilename string
	step := 0

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if line == "---" {
			step = 0
			continue
		}

		if step == 0 {
			currentFilename = line
			step = 1
		} else if step == 1 {
			var detections []models.Detection
			if err := json.Unmarshal([]byte(line), &detections); err != nil {
				return nil, fmt.Errorf("failed to parse JSON for file %s: %w", currentFilename, err)
			}

			entries = append(entries, models.ReportEntry{
				Filename:   currentFilename,
				Detections: detections,
			})

			step = 2
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("error reading report file: %w", err)
	}

	return entries, nil
}
