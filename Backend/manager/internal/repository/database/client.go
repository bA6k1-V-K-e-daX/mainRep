package dbclientt

import (
	"context"
	"encoding/json"
	"fmt"
	database1 "manager/contract/database"
	"manager/internal/models"
	"strconv"
	"strings"

	"google.golang.org/grpc"
)

type Client struct {
	api database1.DatabaseClient
}

func NewClient(cc grpc.ClientConnInterface) *Client {
	return &Client{api: database1.NewDatabaseClient(cc)}
}

func (c *Client) CreateUser(ctx context.Context, user models.User) error {
	data, err := json.Marshal(user)
	if err != nil {
		return err
	}
	_, err = c.api.CreateUser(ctx, &database1.CreateUserRequest{
		Data: data,
	})
	return err
}

func (c *Client) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	reqData, err := json.Marshal(map[string]string{"login": login})
	if err != nil {
		return models.User{}, err
	}
	resp, err := c.api.CheckUser(ctx, &database1.CheckUserRequest{Data: reqData})
	if err != nil {
		return models.User{}, err
	}

	var user models.User
	if err := json.Unmarshal(resp.Data, &user); err != nil {
		return models.User{}, err
	}
	return user, nil
}

func (c *Client) CreateChat(ctx context.Context, userID string, title string) (models.Chat, error) {
	reqData, err := json.Marshal(map[string]string{
		"operation": "create_chat",
		"user_id":   userID,
		"title":     title,
	})
	if err != nil {
		return models.Chat{}, err
	}

	resp, err := c.api.AddNewData(ctx, &database1.AddNewAnswerRequest{Data: reqData})
	if err != nil {
		return models.Chat{}, err
	}

	return models.Chat{
		ID:    resp.Message,
		Title: title,
	}, nil
}

func (c *Client) GetChats(ctx context.Context, userID string) ([]models.Chat, error) {
	resp, err := c.api.RequestOldDatas(ctx, &database1.RequestOldAnswersRequest{
		Quantity: 0,
		UserID:   userID,
		Flag:     "chats",
	})
	if err != nil {
		return nil, err
	}
	if resp.Message != "Success" {
		return nil, fmt.Errorf("failed to get chats: %s", resp.Message)
	}

	var chats []models.Chat
	if err := json.Unmarshal(resp.Data, &chats); err != nil {
		return nil, err
	}
	return chats, nil
}

func (c *Client) CreateQuery(ctx context.Context, userID string, chatID string, prompt string) (int64, error) {
	reqData, err := json.Marshal(map[string]string{
		"operation": "create_query",
		"user_id":   userID,
		"chat_id":   chatID,
		"prompt":    prompt,
	})
	if err != nil {
		return 0, err
	}

	resp, err := c.api.AddNewData(ctx, &database1.AddNewAnswerRequest{Data: reqData})
	if err != nil {
		return 0, err
	}

	queryID, err := strconv.ParseInt(resp.Message, 10, 64)
	if err != nil {
		return 0, err
	}
	return queryID, nil
}

func (c *Client) GetHistoryAnswers(ctx context.Context, quantity int64, userID, chatID, flag string) ([]int32, error) {
	requestFlag := strings.TrimSpace(flag)
	if strings.TrimSpace(chatID) != "" {
		requestFlag = "chat:" + strings.TrimSpace(chatID)
	}
	if requestFlag == "" {
		requestFlag = "all"
	}

	reqData, err := c.api.RequestOldDatas(ctx, &database1.RequestOldAnswersRequest{
		Quantity: quantity,
		UserID:   userID,
		Flag:     requestFlag,
	})
	if err != nil {
		return nil, err
	}
	if reqData.Message != "Success" {
		return nil, fmt.Errorf("failed to get history answers: %s", reqData.Message)
	}
	var answers []int32
	if err := json.Unmarshal(reqData.Data, &answers); err != nil {
		return nil, err
	}
	return answers, nil
}

func (c *Client) QueryBelongsToUser(ctx context.Context, userID string, queryID int64) (bool, error) {
	resp, err := c.api.RequestOldDatas(ctx, &database1.RequestOldAnswersRequest{
		Quantity: queryID,
		UserID:   userID,
		Flag:     "query_owner",
	})
	if err != nil {
		return false, err
	}
	if resp.Message != "Success" {
		return false, fmt.Errorf("failed to check query owner: %s", resp.Message)
	}

	var payload struct {
		Belongs bool `json:"belongs"`
	}
	if err := json.Unmarshal(resp.Data, &payload); err != nil {
		return false, err
	}
	return payload.Belongs, nil
}
