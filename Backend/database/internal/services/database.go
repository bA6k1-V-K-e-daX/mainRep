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
}

func New(db *dbrepo.DatabaseRepo) *Database {
	return &Database{
		usercreate:  db,
		userget:     db,
		querycreate: db,
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

func (s *Database) CreateUser(ctx context.Context, user models.User) error {
	return s.usercreate.CreateUser(ctx, user)
}

func (s *Database) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	return s.userget.GetUserByLogin(ctx, login)
}

func (s *Database) CreateQuery(ctx context.Context, userID string) (int64, error) {
	return s.querycreate.CreateQuery(ctx, userID)
}
