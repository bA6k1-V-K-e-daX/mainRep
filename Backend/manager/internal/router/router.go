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
			protected.POST("/detect", svc.Detect)
		}
	}

	// Mount the static files server to safely expose user results
	// Frontend usage: GET /results/{query_id}/result/i.jpg
	r.StaticFS("/results", gin.Dir(volumePath, false))
}
