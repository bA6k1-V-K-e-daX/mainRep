package app

import (
	"context"
	httpapp "manager/internal/app/http"
	"manager/internal/config"
	dbclient "manager/internal/repository/database"
	mlclient "manager/internal/repository/ml"
	"manager/internal/router"
	httpservices "manager/internal/services"
	"strconv"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type App struct {
	HTTPApp *httpapp.HTTPApp
	dbConn  *grpc.ClientConn
	mlConn  *grpc.ClientConn
}

func New(cfg *config.Config) *App {
	// Initialize gRPC Connections
	dbTarget := cfg.Client.Database.Host + ":" + strconv.Itoa(cfg.Client.Database.Port)
	dbConn, err := grpc.NewClient(dbTarget, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		panic("failed to connect to DB service: " + err.Error())
	}
	dbCli := dbclient.NewClient(dbConn)

	mlTarget := cfg.Client.ML.Host + ":" + strconv.Itoa(cfg.Client.ML.Port)
	mlConn, err := grpc.NewClient(mlTarget, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		panic("failed to connect to ML service: " + err.Error())
	}
	mlCli := mlclient.NewClient(mlConn)

	// Build Business Layer
	httpService := httpservices.New(dbCli, mlCli, cfg.JWTSecret, cfg.TempObjectPath, cfg.Processing)

	// Configure HTTP Core Server
	http := httpapp.New(cfg.HttpServer)

	// Delegate routing registration
	router.RouterRegister(http.GetEngine(), httpService, cfg.TempObjectPath)

	return &App{
		HTTPApp: http,
		dbConn:  dbConn,
		mlConn:  mlConn,
	}
}

// Close ensures the graceful termination of associated dialers.
func (a *App) Close() {
	if a.HTTPApp != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		_ = a.HTTPApp.Shutdown(ctx)
	}
	if a.dbConn != nil {
		a.dbConn.Close()
	}
	if a.mlConn != nil {
		a.mlConn.Close()
	}
}
