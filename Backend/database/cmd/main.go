package main

import (
	"database/internal/app"
	"database/internal/config"
	"fmt"
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
		"env":                      config.Env,
		"format_time":              config.FormatTime,
		"file_path":                config.FilePath,
		"grpc_port":                config.GRPC.Port,
		"grpc_timeout":             config.GRPC.Timeout,
		"database_port":            config.Database.Port,
		"database_host":            config.Database.Host,
		"database_user":            config.Database.User,
		"database_database":        config.Database.Database,
		"database_migrations_path": config.Database.MigrationsPath,
	})
	application := app.New(config.Database, config.GRPC.Port)
	logger.Info("Application has been successfully initialized", nil)
	go func() {
		application.GRPCServer.MustRun()
		application.Worker.SetWorker()
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop
	application.GRPCServer.Stop()
	logger.Info("Gracefully stopped", nil)
}
