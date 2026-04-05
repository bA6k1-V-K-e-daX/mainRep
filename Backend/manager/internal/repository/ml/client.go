package mlclient

import (
	"context"
	ml1 "manager/contract/ml"

	"google.golang.org/grpc"
)

type Client struct {
	api ml1.DetectorClient
}

func NewClient(cc grpc.ClientConnInterface) *Client {
	return &Client{api: ml1.NewDetectorClient(cc)}
}

func (c *Client) Detect(ctx context.Context, queryID int64, dirPath string, prompt string) (*ml1.DetectionResponse, error) {
	return c.api.ImageDetection(ctx, &ml1.DetectionRequest{
		QueryId: queryID,
		DirPath: dirPath,
		Prompt:  prompt,
	})
}
