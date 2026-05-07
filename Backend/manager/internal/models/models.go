package models

type AuthRequest struct {
	Login    string `json:"login" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type User struct {
	ID           string `json:"id"`
	Login        string `json:"login"`
	PasswordHash string `json:"password_hash"`
}

type AuthResponse struct {
	Token string `json:"token"`
}

type DetectPayload struct {
	Prompt    string `json:"prompt"`
	ChatID    string `json:"chat_id"`
	ChatTitle string `json:"chat_title"`
}

type HistoryAnswer struct {
	Quantity int64  `json:"quantity"`
	Flag     string `json:"flag"`
	ChatID   string `json:"chat_id"`
}

type ChatRequest struct {
	Title string `json:"title"`
}

type Chat struct {
	ID        string `json:"id"`
	UserID    string `json:"user_id,omitempty"`
	Title     string `json:"title"`
	CreatedAt string `json:"created_at,omitempty"`
	UpdatedAt string `json:"updated_at,omitempty"`
}

type HistoryResponse struct {
	QueryId int32         `json:"query_id"`
	Entries []ReportEntry `json:"entries"`
}

type Detection struct {
	Class      string    `json:"class"`
	Confidence float64   `json:"confidence"`
	BBox       []float64 `json:"bbox"`
}

type ReportEntry struct {
	Filename     string      `json:"filename"`
	Detections   []Detection `json:"detections"`
	ResultFolder string      `json:"result_folder,omitempty"`
	BoxesURL     string      `json:"boxes_url,omitempty"`
	OverlayURL   string      `json:"overlay_url,omitempty"`
}
