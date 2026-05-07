package router

import (
	httpservices "manager/internal/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

func RouterRegister(r *gin.Engine, svc *httpservices.HTTPService, volumePath string) {
	r.GET("/health", func(c *gin.Context) { c.String(http.StatusOK, "OK") })

	v1 := r.Group("/api/v1")
	{
		auth := v1.Group("/auth")
		{
			auth.POST("/register", svc.Register)
			auth.POST("/login", svc.Login)
		}

		protected := v1.Group("/")
		protected.Use(svc.AuthMiddleware())
		{
			protected.GET("/chats", svc.Chats)
			protected.POST("/chats", svc.CreateChat)
			protected.POST("/detect", svc.Detect)
			protected.POST("/history", svc.History)
		}
	}

	results := r.Group("/results")
	results.Use(svc.AuthMiddleware())
	{
		results.GET("/*filepath", svc.ResultFile)
	}
}
