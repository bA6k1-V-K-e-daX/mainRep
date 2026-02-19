package app

// Error code 2000
import (
	grpcapp "database/internal/app/grpc"
	"database/internal/config"
	workhandler "database/internal/handlers/worker"
	dbrepo "database/internal/repository"
	servicesdb "database/internal/services"
)

type App struct {
	GRPCServer *grpcapp.App
	Worker     *workhandler.ServerAPI
}

func New(cfg config.DatabaseConfig, port int) *App {
	dbr := dbrepo.New(cfg)
	dbservice, dbworker := servicesdb.New(dbr)
	grpcapp := grpcapp.New(dbservice, port)
	workapp := workhandler.SetWorker(dbworker)
	return &App{GRPCServer: grpcapp, Worker: workapp}
}
