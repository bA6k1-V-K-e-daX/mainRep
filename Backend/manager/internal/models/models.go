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
	Prompt string `json:"prompt"`
}

type HistoryAnswer struct {
	Quantity int64  `json:"quantity"`
	Flag     string `json:"flag"`
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
