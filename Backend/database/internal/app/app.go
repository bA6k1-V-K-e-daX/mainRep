package app

// Error code 2000
import (
	grpcapp "database/internal/app/grpc"
	"database/internal/config"
	dbrepo "database/internal/repository"
	servicesdb "database/internal/services"
)

type App struct {
	GRPCServer *grpcapp.App
}

func New(cfg config.DatabaseConfig, port int) *App {
	dbr := dbrepo.New(cfg)
	dbservice := servicesdb.New(dbr)
	grpcapp := grpcapp.New(dbservice, port)
	return &App{GRPCServer: grpcapp}
}
