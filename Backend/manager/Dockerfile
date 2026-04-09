FROM golang:1.24-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o /manager ./cmd/main.go

FROM alpine:latest

RUN apk add --no-cache ca-certificates ffmpeg \
    && adduser -D -u 10001 appuser

WORKDIR /app

COPY --from=builder /manager .
COPY config/ config/

RUN mkdir -p volume \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["./manager", "--config=config/config.yaml"]
