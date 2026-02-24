package models

type User struct {
	ID           string `json:"id"`
	Login        string `json:"login"`
	PasswordHash string `json:"password_hash"`
}

type Query struct {
	ID     int64  `json:"id"`
	UserID string `json:"user_id"`
}
