package app

import (
	httpapp "manager/internal/app/http"
	"manager/internal/config"
)

type App struct {
	HTTPApp *httpapp.HTTPApp
}

func New(cfg *config.Config) *App {
	//TODO: implement database connection

	return &App{}
}
