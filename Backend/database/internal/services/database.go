package servicesdb

import (
	"context"
	"database/internal/models"
	dbrepo "database/internal/repository"
)

type Database struct {
	usercreate  UserCreator
	userget     UserGetter
	querycreate QueryCreator
	historyget  HistoryGetter
}

func New(db *dbrepo.DatabaseRepo) *Database {
	return &Database{
		usercreate:  db,
		userget:     db,
		querycreate: db,
		historyget:  db,
	}
}

type UserCreator interface {
	CreateUser(ctx context.Context, user models.User) error
}

type UserGetter interface {
	GetUserByLogin(ctx context.Context, login string) (models.User, error)
}

type QueryCreator interface {
	CreateQuery(ctx context.Context, userID string) (int64, error)
}

type HistoryGetter interface {
	GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error)
}

func (s *Database) CreateUser(ctx context.Context, user models.User) error {
	return s.usercreate.CreateUser(ctx, user)
}

func (s *Database) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	return s.userget.GetUserByLogin(ctx, login)
}

func (s *Database) CreateQuery(ctx context.Context, userID string) (int64, error) {
	return s.querycreate.CreateQuery(ctx, userID)
}

func (s *Database) GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error) {
	return s.historyget.GetHistoryAnswers(ctx, quantity, userID, flag)
}
