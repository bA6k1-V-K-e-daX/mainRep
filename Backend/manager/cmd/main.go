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
	config, level := config.MustLoad()
	err := logger.Init(level, config.Env, config.FilePath)
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
		"env":                  config.Env,
		"format_time":          config.FormatTime,
		"file_path":            config.FilePath,
		"httpserver_port":      config.HttpServer.Port,
		"httpserver_host":      config.HttpServer.Host,
		"client_database_host": config.Client.Database.Host,
		"client_database_port": config.Client.Database.Port,
		"client_ml_host":       config.Client.ML.Host,
		"client_ml_port":       config.Client.ML.Port,
	})
	application := app.New(config)
	logger.Info("Application has been successfully initialized", nil)
	go func() {
		// TODO: implement runner application
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop
	// TODO: implement graceful shutdown
	logger.Info("Gracefully stopped", nil)
}
