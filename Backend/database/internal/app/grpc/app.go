package grpcapp

// Error code 2500
import (
	"context"
	grpchandler "database/internal/handlers/grpc"
	"fmt"
	"net"
	"time"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type App struct {
	grpcServer *grpc.Server
	port       int
}

func New(serverAPI grpchandler.DatabaseService, port int) *App {
	opts := []grpc.ServerOption{grpc.UnaryInterceptor(loggingInterceptor())}
	gRPCServer := grpc.NewServer(opts...)
	grpchandler.Register(gRPCServer, serverAPI)
	return &App{grpcServer: gRPCServer, port: port}
}

func (a *App) MustRun() {
	if err := a.Run(); err != nil {
		logger.Fatal("Failed to run gRPC server", err, 2500, nil)
	}
}

func (a *App) Run() error {
	logger.Info("Starting gRPC server", map[string]any{"port": a.port})
	l, err := net.Listen("tcp", fmt.Sprintf(":%d", a.port))
	if err != nil {
		logger.Error("Error starting listener for gRPC server", err, 2502, map[string]any{"port": a.port})
		return err
	}
	logger.Debug("gRPC server is starting", 2503, map[string]any{"address": l.Addr().String()})
	if err := a.grpcServer.Serve(l); err != nil {
		logger.Error("Error starting gRPC server", err, 2504, nil)
		return err
	}
	logger.Info("gRPC server is runned", map[string]any{"address": l.Addr().String()})
	return nil
}

func (a *App) Stop() error {
	logger.Info("Stopping the gRPC server", nil)
	logger.Debug("gRPC server is stopping", 2505, nil)
	a.grpcServer.GracefulStop()
	logger.Debug("gRPC server is stopped", 2506, nil)
	return nil
}

func loggingInterceptor() grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		start := time.Now()
		resp, err := handler(ctx, req)
		duration := time.Since(start)
		if req == nil {
			logger.Warn("gRPC request without data", 2506, map[string]any{"method": info.FullMethod})
		}
		fields := map[string]any{
			"method":   info.FullMethod,
			"duration": duration.String(),
			"req":      req,
		}
		if err != nil {
			st, ok := status.FromError(err)
			if ok {
				fields["grpc_code"] = st.Code().String()
			} else {
				fields["grpc_code"] = codes.Unknown.String()
			}
			logger.Error("gRPC request failed", err, 2506, fields)
		} else {
			fields["grpc_code"] = codes.OK.String()
			logger.Info("gRPC request success", fields)
		}
		return resp, err
	}
}
