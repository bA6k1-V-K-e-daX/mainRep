package grpchandler

import (
	"context"
	database1 "database/contract"
	"database/internal/models"
	"encoding/json"
	"fmt"

	"google.golang.org/grpc"
)

type DatabaseService interface {
	CreateUser(ctx context.Context, user models.User) error
	GetUserByLogin(ctx context.Context, login string) (models.User, error)
	CreateQuery(ctx context.Context, userID string) (int64, error)
	GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error)
}

type serverAPI struct {
	database1.UnimplementedDatabaseServer
	database DatabaseService
}

func Register(srv *grpc.Server, database DatabaseService) {
	database1.RegisterDatabaseServer(srv, &serverAPI{database: database})
}

func (s *serverAPI) CreateUser(ctx context.Context, req *database1.CreateUserRequest) (*database1.CreateUserResponse, error) {
	var user models.User
	if err := json.Unmarshal(req.Data, &user); err != nil {
		return nil, fmt.Errorf("failed to decode user data: %w", err)
	}

	if err := s.database.CreateUser(ctx, user); err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	return &database1.CreateUserResponse{Message: "Success"}, nil
}

func (s *serverAPI) CheckUser(ctx context.Context, req *database1.CheckUserRequest) (*database1.CheckUserResponse, error) {
	var requestData map[string]string
	if err := json.Unmarshal(req.Data, &requestData); err != nil {
		return nil, fmt.Errorf("failed to decode login data: %w", err)
	}

	user, err := s.database.GetUserByLogin(ctx, requestData["login"])
	if err != nil {
		return nil, fmt.Errorf("user not found or db error: %w", err)
	}

	responseData, _ := json.Marshal(user)
	return &database1.CheckUserResponse{
		Message: "Success",
		Data:    responseData,
	}, nil
}

func (s *serverAPI) AddNewData(ctx context.Context, req *database1.AddNewAnswerRequest) (*database1.AddNewAnswerResponse, error) {
	var requestData map[string]string
	if err := json.Unmarshal(req.Data, &requestData); err != nil {
		return nil, fmt.Errorf("failed to decode user id: %w", err)
	}

	queryID, err := s.database.CreateQuery(ctx, requestData["user_id"])
	if err != nil {
		return nil, fmt.Errorf("failed to register query: %w", err)
	}

	return &database1.AddNewAnswerResponse{
		Message: fmt.Sprintf("%d", queryID),
	}, nil
}

func (s *serverAPI) RequestOldDatas(ctx context.Context, req *database1.RequestOldAnswersRequest) (*database1.RequestOldAnswersResponse, error) {
	var (
		quantity int64  = req.GetQuantity()
		userID   string = req.GetUserID()
		flag     string = req.GetFlag()
	)
	if quantity == 0 || userID == "" || flag == "" {
		return nil, fmt.Errorf("invalid request parameters")
	}

	answers, err := s.database.GetHistoryAnswers(ctx, quantity, userID, flag)
	if err != nil {
		return nil, fmt.Errorf("failed to get history answers: %w", err)
	}

	responseData, err := json.Marshal(answers)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal answers: %w", err)
	}
	return &database1.RequestOldAnswersResponse{
		Message: "Success",
		Data:    responseData,
	}, nil
}
