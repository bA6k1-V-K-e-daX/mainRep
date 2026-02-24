package main

import (
	"fmt"
	"manager/internal/app"
	"manager/internal/config"
	"os"
	"os/signal"
	"syscall"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
)

func main() {
	cfg, level := config.MustLoad()
	err := logger.Init(level, cfg.Env, cfg.LogFilePath)
	if err != nil {
		fmt.Printf("Failed to init logger: %v\n", err)
		return
	}
	defer func() {
		if err := logger.Close(); err != nil {
			fmt.Printf("Failed to close logger: %v\n", err)
		}
	}()
	logger.Info("Config has been successfully loaded", nil)
	logger.Debug("Config data", 1000, map[string]any{
		"env":                  cfg.Env,
		"format_time":          cfg.FormatTime,
		"file_path":            cfg.LogFilePath,
		"httpserver_port":      cfg.HttpServer.Port,
		"httpserver_host":      cfg.HttpServer.Host,
		"client_database_host": cfg.Client.Database.Host,
		"client_database_port": cfg.Client.Database.Port,
		"client_ml_host":       cfg.Client.ML.Host,
		"client_ml_port":       cfg.Client.ML.Port,
	})
	application := app.New(cfg)
	defer application.Close()
	logger.Info("Application has been successfully initialized", nil)
	go func() {
		application.HTTPApp.MustRun()
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop
	logger.Info("Gracefully stopped", nil)
}
