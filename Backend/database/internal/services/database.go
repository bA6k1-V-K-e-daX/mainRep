package servicesdb

import (
	"context"
	"database/internal/models"
	dbrepo "database/internal/repository"
)

type Database struct {
	usercreate  UserCreator
	userget     UserGetter
	chatcreate  ChatCreator
	chatget     ChatGetter
	querycreate QueryCreator
	historyget  HistoryGetter
	queryowner  QueryOwnerChecker
}

func New(db *dbrepo.DatabaseRepo) *Database {
	return &Database{
		usercreate:  db,
		userget:     db,
		chatcreate:  db,
		chatget:     db,
		querycreate: db,
		historyget:  db,
		queryowner:  db,
	}
}

type UserCreator interface {
	CreateUser(ctx context.Context, user models.User) error
}

type UserGetter interface {
	GetUserByLogin(ctx context.Context, login string) (models.User, error)
}

type ChatCreator interface {
	CreateChat(ctx context.Context, userID string, title string) (string, error)
}

type ChatGetter interface {
	GetChats(ctx context.Context, userID string) ([]models.Chat, error)
}

type QueryCreator interface {
	CreateQuery(ctx context.Context, userID string, chatID string, prompt string) (int64, error)
}

type HistoryGetter interface {
	GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error)
}

type QueryOwnerChecker interface {
	QueryBelongsToUser(ctx context.Context, userID string, queryID int64) (bool, error)
}

func (s *Database) CreateUser(ctx context.Context, user models.User) error {
	return s.usercreate.CreateUser(ctx, user)
}

func (s *Database) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	return s.userget.GetUserByLogin(ctx, login)
}

func (s *Database) CreateChat(ctx context.Context, userID string, title string) (string, error) {
	return s.chatcreate.CreateChat(ctx, userID, title)
}

func (s *Database) GetChats(ctx context.Context, userID string) ([]models.Chat, error) {
	return s.chatget.GetChats(ctx, userID)
}

func (s *Database) CreateQuery(ctx context.Context, userID string, chatID string, prompt string) (int64, error) {
	return s.querycreate.CreateQuery(ctx, userID, chatID, prompt)
}

func (s *Database) GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error) {
	return s.historyget.GetHistoryAnswers(ctx, quantity, userID, flag)
}

func (s *Database) QueryBelongsToUser(ctx context.Context, userID string, queryID int64) (bool, error) {
	return s.queryowner.QueryBelongsToUser(ctx, userID, queryID)
}
