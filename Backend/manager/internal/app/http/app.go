package httpapp

// Error code: 2500

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"time"

	"manager/internal/config"

	"github.com/PrototypeSirius/ruglogger/middleware"
	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type HTTPApp struct {
	ginServer *gin.Engine
	server    *http.Server
	address   string
}

func New(cfg config.HttpConfig) *HTTPApp {
	gin.ForceConsoleColor()
	r := gin.New()
	r.MaxMultipartMemory = cfg.MaxMultipartMemoryMiB * 1024 * 1024
	r.Use(gin.Logger())
	r.Use(gin.Recovery())
	r.Use(middleware.StructuredLogHandler())
	r.Use(middleware.ErrorHandler())
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"}, // Modified for universal local access
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length", "Authorization"},
		AllowCredentials: true,
	}))
	address := fmt.Sprintf(":%d", cfg.Port)
	return &HTTPApp{
		ginServer: r,
		server: &http.Server{
			Addr:              address,
			Handler:           r,
			ReadHeaderTimeout: 10 * time.Second,
			ReadTimeout:       time.Duration(cfg.ReadTimeoutSeconds) * time.Second,
			WriteTimeout:      time.Duration(cfg.WriteTimeoutSeconds) * time.Second,
			IdleTimeout:       time.Duration(cfg.IdleTimeoutSeconds) * time.Second,
		},
		address: address,
	}
}

func (a *HTTPApp) GetEngine() *gin.Engine {
	return a.ginServer
}

func (a *HTTPApp) MustRun() {
	if err := a.Run(); err != nil {
		logger.Fatal("Failed to run http server", err, 2501, nil)
	}
}

func (a *HTTPApp) Run() error {
	logger.Info("HTTP server is running", map[string]any{"address": a.address})
	if err := a.server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}

func (a *HTTPApp) Shutdown(ctx context.Context) error {
	if a.server == nil {
		return nil
	}
	return a.server.Shutdown(ctx)
}
