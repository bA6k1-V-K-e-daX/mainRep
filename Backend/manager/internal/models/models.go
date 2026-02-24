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
