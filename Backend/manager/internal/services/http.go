package httpservices

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"manager/internal/config"
	"manager/internal/media"
	"manager/internal/models"
	dbclientt "manager/internal/repository/database"
	mlclient "manager/internal/repository/ml"
	"net/http"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

type HTTPService struct {
	dbClient           *dbclientt.Client
	mlClient           *mlclient.Client
	jwtSecret          []byte
	volumePath         string
	maxFilesPerRequest int
	mlTimeout          time.Duration
	videoProcessor     *media.VideoProcessor
}

func New(
	db *dbclientt.Client,
	ml *mlclient.Client,
	secret string,
	volumePath string,
	processing config.Processing,
) *HTTPService {
	return &HTTPService{
		dbClient:           db,
		mlClient:           ml,
		jwtSecret:          []byte(secret),
		volumePath:         volumePath,
		maxFilesPerRequest: processing.MaxFilesPerRequest,
		mlTimeout:          time.Duration(processing.MLTimeoutSeconds) * time.Second,
		videoProcessor: media.NewVideoProcessor(media.VideoProcessorConfig{
			FFmpegPath:  processing.Video.FFmpegPath,
			FrameRate:   processing.Video.FrameRate,
			MaxFrames:   processing.Video.MaxFrames,
			MaxParallel: processing.Video.MaxParallel,
			Extensions:  processing.Video.Extensions,
		}),
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

func (s *HTTPService) CreateChat(c *gin.Context) {
	userID := c.GetString("user_id")

	var req models.ChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	chat, err := s.dbClient.CreateChat(c.Request.Context(), userID, normalizeChatTitle(req.Title))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create chat", "details": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"chat": chat})
}

func (s *HTTPService) Chats(c *gin.Context) {
	userID := c.GetString("user_id")

	chats, err := s.dbClient.GetChats(c.Request.Context(), userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get chats", "details": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"chats": chats})
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

	chatID := strings.TrimSpace(payload.ChatID)
	if chatID == "" {
		chat, err := s.dbClient.CreateChat(c.Request.Context(), userID, buildChatTitle(payload))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create chat", "details": err.Error()})
			return
		}
		chatID = chat.ID
	}

	queryID, err := s.dbClient.CreateQuery(c.Request.Context(), userID, chatID, payload.Prompt)
	if err != nil {
		c.JSON(http.StatusForbidden, gin.H{"error": "Failed to register query task for this chat", "details": err.Error()})
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
	if len(files) > s.maxFilesPerRequest {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":          "Too many files provided",
			"max_files":      s.maxFilesPerRequest,
			"provided_files": len(files),
		})
		return
	}

	uploadedNames := make(map[string]struct{}, len(files))
	savedFiles := make([]string, 0, len(files))

	for _, file := range files {
		if _, exists := uploadedNames[file.Filename]; exists {
			c.JSON(http.StatusBadRequest, gin.H{
				"error":    "Duplicate filenames are not allowed in one request",
				"filename": file.Filename,
			})
			return
		}
		uploadedNames[file.Filename] = struct{}{}

		destination := filepath.Join(sourceDir, file.Filename)
		if err := c.SaveUploadedFile(file, destination); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Failed to save file: %s", file.Filename)})
			return
		}
		savedFiles = append(savedFiles, destination)
	}

	mediaSummary := s.videoProcessor.SummarizeFiles(savedFiles)
	if mediaSummary.ImageFiles == 0 && mediaSummary.VideoFiles == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "No supported image or video files provided",
		})
		return
	}

	generatedFrames, err := s.videoProcessor.ExpandVideos(c.Request.Context(), savedFiles)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Video preprocessing failed",
			"details": err.Error(),
		})
		return
	}

	mlCtx, cancel := context.WithTimeout(c.Request.Context(), s.mlTimeout)
	defer cancel()

	resp, err := s.mlClient.Detect(mlCtx, queryID, s.volumePath, payload.Prompt)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "ML Service failure", "details": err.Error()})
		return
	}

	if !resp.Success {
		c.JSON(http.StatusUnprocessableEntity, gin.H{"error": "Detection failed", "message": resp.ErrorMessage})
		return
	}

	entries, err := s.loadQueryEntries(queryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare result entries", "details": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"query_id":          resp.QueryId,
		"chat_id":           chatID,
		"status":            "Success",
		"instance_info":     resp.InstanceInfo,
		"total":             resp.TotalObjects,
		"result_dir":        fmt.Sprintf("/results/%s/result/", queryStrID),
		"entries":           entries,
		"uploaded_images":   mediaSummary.ImageFiles,
		"uploaded_videos":   mediaSummary.VideoFiles,
		"unsupported_files": mediaSummary.UnsupportedFiles,
		"generated_frames":  generatedFrames,
	})
}

func (s *HTTPService) History(c *gin.Context) {
	userID := c.GetString("user_id")

	var req models.HistoryAnswer
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	queries, err := s.dbClient.GetHistoryAnswers(c.Request.Context(), req.Quantity, userID, req.ChatID, req.Flag)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user queries"})
		return
	}
	var response []models.HistoryResponse
	for _, queryID := range queries {
		entries, err := s.loadQueryEntries(int64(queryID))
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

func (s *HTTPService) ResultFile(c *gin.Context) {
	userID := c.GetString("user_id")
	rawPath := c.Param("filepath")

	queryID, safePath, err := s.resolveProtectedResultPath(rawPath)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Result file not found"})
		return
	}

	belongs, err := s.dbClient.QueryBelongsToUser(c.Request.Context(), userID, queryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to verify result owner"})
		return
	}
	if !belongs {
		c.JSON(http.StatusForbidden, gin.H{"error": "Access denied"})
		return
	}

	info, err := os.Stat(safePath)
	if err != nil || info.IsDir() {
		c.JSON(http.StatusNotFound, gin.H{"error": "Result file not found"})
		return
	}

	c.File(safePath)
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

func normalizeChatTitle(title string) string {
	normalized := strings.TrimSpace(title)
	if normalized == "" {
		return "New chat"
	}
	runes := []rune(normalized)
	if len(runes) > 255 {
		return string(runes[:255])
	}
	return normalized
}

func buildChatTitle(payload models.DetectPayload) string {
	if strings.TrimSpace(payload.ChatTitle) != "" {
		return normalizeChatTitle(payload.ChatTitle)
	}
	if strings.TrimSpace(payload.Prompt) != "" {
		return normalizeChatTitle(payload.Prompt)
	}
	return "New chat"
}

func (s *HTTPService) resolveProtectedResultPath(rawPath string) (int64, string, error) {
	cleanPath := path.Clean("/" + strings.TrimPrefix(rawPath, "/"))
	if cleanPath == "." || cleanPath == "/" {
		return 0, "", fmt.Errorf("empty result path")
	}

	parts := strings.Split(strings.TrimPrefix(cleanPath, "/"), "/")
	if len(parts) < 2 {
		return 0, "", fmt.Errorf("invalid result path")
	}

	queryID, err := strconv.ParseInt(parts[0], 10, 64)
	if err != nil || queryID <= 0 {
		return 0, "", fmt.Errorf("invalid query id")
	}

	queryRoot := filepath.Join(s.volumePath, parts[0])
	relativePath := filepath.FromSlash(strings.Join(parts[1:], "/"))
	filePath := filepath.Join(queryRoot, relativePath)

	absRoot, err := filepath.Abs(queryRoot)
	if err != nil {
		return 0, "", err
	}
	absFile, err := filepath.Abs(filePath)
	if err != nil {
		return 0, "", err
	}

	if absFile != absRoot && !strings.HasPrefix(absFile, absRoot+string(os.PathSeparator)) {
		return 0, "", fmt.Errorf("result path escapes query root")
	}

	return queryID, absFile, nil
}
func ParseReport(filePath string) ([]models.ReportEntry, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open report file: %w", err)
	}
	defer file.Close()

	var entries []models.ReportEntry
	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 1024), 10*1024*1024)

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

func (s *HTTPService) loadQueryEntries(queryID int64) ([]models.ReportEntry, error) {
	resultDir := filepath.Join(s.volumePath, strconv.FormatInt(queryID, 10), "result")
	reportPath := filepath.Join(resultDir, "report.txt")
	if _, err := os.Stat(reportPath); os.IsNotExist(err) {
		reportPath = filepath.Join(resultDir, "detection_summary.txt")
	}

	entries, err := ParseReport(reportPath)
	if err != nil {
		return nil, err
	}

	for index := range entries {
		resultFolder, boxesFileName, overlayFileName := resolveResultArtifacts(resultDir, entries[index].Filename)
		entries[index].ResultFolder = resultFolder
		if resultFolder != "" && boxesFileName != "" {
			entries[index].BoxesURL = buildResultAssetURL(queryID, resultFolder, boxesFileName)
		}
		if resultFolder != "" && overlayFileName != "" {
			entries[index].OverlayURL = buildResultAssetURL(queryID, resultFolder, overlayFileName)
		}
	}

	return entries, nil
}

func resolveResultArtifacts(resultDir string, filename string) (string, string, string) {
	fileStem := strings.TrimSuffix(filename, filepath.Ext(filename))
	fileExt := strings.TrimPrefix(strings.ToLower(filepath.Ext(filename)), ".")
	if fileStem == "" {
		return "", "", ""
	}

	boxesFileName := fileStem + "_boxes.png"
	overlayFileName := fileStem + "_overlay.png"
	candidateFolders := uniqueStrings([]string{
		fileStem,
		strings.TrimSuffix(filename, filepath.Ext(filename)),
		buildLegacyFolderName(fileStem, fileExt),
	})

	for _, folderName := range candidateFolders {
		if folderName == "" {
			continue
		}
		boxesPath := filepath.Join(resultDir, folderName, boxesFileName)
		overlayPath := filepath.Join(resultDir, folderName, overlayFileName)
		if fileExists(boxesPath) || fileExists(overlayPath) {
			return folderName, existingFileName(boxesPath), existingFileName(overlayPath)
		}
	}

	entries, err := os.ReadDir(resultDir)
	if err != nil {
		return "", "", ""
	}

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		folderName := entry.Name()
		boxesPath := filepath.Join(resultDir, folderName, boxesFileName)
		overlayPath := filepath.Join(resultDir, folderName, overlayFileName)
		if fileExists(boxesPath) || fileExists(overlayPath) {
			return folderName, existingFileName(boxesPath), existingFileName(overlayPath)
		}
	}

	return "", "", ""
}

func buildLegacyFolderName(fileStem, fileExt string) string {
	if fileStem == "" {
		return ""
	}
	if fileExt == "" {
		return fileStem
	}
	return fileStem + "_" + fileExt
}

func buildResultAssetURL(queryID int64, folderName, fileName string) string {
	return path.Join(
		"/results",
		strconv.FormatInt(queryID, 10),
		"result",
		url.PathEscape(folderName),
		url.PathEscape(fileName),
	)
}

func existingFileName(filePath string) string {
	if !fileExists(filePath) {
		return ""
	}
	return filepath.Base(filePath)
}

func fileExists(filePath string) bool {
	info, err := os.Stat(filePath)
	if err != nil {
		return false
	}
	return !info.IsDir()
}

func uniqueStrings(values []string) []string {
	unique := make([]string, 0, len(values))
	seen := make(map[string]struct{}, len(values))
	for _, value := range values {
		if value == "" {
			continue
		}
		if _, exists := seen[value]; exists {
			continue
		}
		seen[value] = struct{}{}
		unique = append(unique, value)
	}
	return unique
}
