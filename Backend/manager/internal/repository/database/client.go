package dbclientt

import (
	"context"
	"encoding/json"
	database1 "manager/contract/database"
	"manager/internal/models"
	"strconv"

	"google.golang.org/grpc"
)

type Client struct {
	api database1.DatabaseClient
}

func NewClient(cc grpc.ClientConnInterface) *Client {
	return &Client{api: database1.NewDatabaseClient(cc)}
}

func (c *Client) CreateUser(ctx context.Context, user models.User) error {
	data, _ := json.Marshal(user)
	_, err := c.api.CreateUser(ctx, &database1.CreateUserRequest{
		Data: data,
	})
	return err
}

func (c *Client) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	reqData, _ := json.Marshal(map[string]string{"login": login})
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

func (c *Client) CreateQuery(ctx context.Context, userID string) (int64, error) {
	reqData, _ := json.Marshal(map[string]string{"user_id": userID})
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
