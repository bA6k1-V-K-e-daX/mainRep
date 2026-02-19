package grpchandler

import (
	database1 "database/contract"

	"google.golang.org/grpc"
)

type DatabaseService interface{}

type serverAPI struct {
	database1.UnimplementedDatabaseServer
	database DatabaseService
}

func Register(srv *grpc.Server, database DatabaseService) {
	database1.RegisterDatabaseServer(srv, &serverAPI{database: database})
}
