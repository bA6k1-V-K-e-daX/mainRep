package models

type User struct {
	ID           string `json:"id"`
	Login        string `json:"login"`
	PasswordHash string `json:"password_hash"`
}

type Chat struct {
	ID        string `json:"id"`
	UserID    string `json:"user_id"`
	Title     string `json:"title"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

type Query struct {
	ID        int64  `json:"id"`
	UserID    string `json:"user_id"`
	ChatID    string `json:"chat_id"`
	Prompt    string `json:"prompt"`
	CreatedAt string `json:"created_at"`
}
