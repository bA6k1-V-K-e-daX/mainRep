package httpapp

// Error code: 2500

import (
	"fmt"

	"github.com/PrototypeSirius/ruglogger/middleware"
	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type HTTPApp struct {
	ginServer *gin.Engine
	port      int
}

func New(port int) *HTTPApp {
	gin.ForceConsoleColor()
	r := gin.New()
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
	return &HTTPApp{
		ginServer: r,
		port:      port,
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
	addr := fmt.Sprintf(":%d", a.port)
	logger.Info("HTTP server is running", map[string]any{"address": addr})
	if err := a.ginServer.Run(addr); err != nil {
		return err
	}
	return nil
}
