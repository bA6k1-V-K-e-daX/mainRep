FROM golang:1.24-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o /database ./cmd/main.go

FROM alpine:latest

WORKDIR /app

COPY --from=builder /database .
COPY config/ config/
COPY internal/migrations/ migrations/

EXPOSE 2021

CMD ["./database", "--config=config/config.yaml"]
