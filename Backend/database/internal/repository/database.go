package dbrepo

import (
	"context"
	"database/internal/config"
	"database/internal/migrator"
	"database/internal/models"
	"database/sql"
	"fmt"
	"strings"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
)

type DatabaseRepo struct {
	db *sql.DB
}

func New(cfg config.DatabaseConfig) *DatabaseRepo {
	logger.Info("Initializing database", nil)
	logger.Debug("Connecting to the database", 6000, map[string]any{
		"host":            cfg.Host,
		"port":            cfg.Port,
		"user":            cfg.User,
		"database":        cfg.Database,
		"migrations_path": cfg.MigrationsPath,
	})
	connstr := fmt.Sprintf(
		"host=%s port=%d dbname=%s user=%s password=%s sslmode=disable",
		cfg.Host,
		cfg.Port,
		cfg.Database,
		cfg.User,
		cfg.Password,
	)
	db, err := sql.Open("postgres", connstr)
	if err != nil {
		logger.Fatal("Failed to connect to the database", err, 6001, map[string]any{"connstr": connstr})
	}
	if err := db.Ping(); err != nil {
		logger.Fatal("Failed to ping database", err, 6002, map[string]any{"connstr": connstr})
	}
	logger.Info("Connected to the database successfully", nil)
	logger.Debug("Running migrations", 6003, map[string]any{"migrations_path": cfg.MigrationsPath})
	err = migrator.Run(db, cfg.MigrationsPath)
	if err != nil {
		logger.Fatal("Failed to migrate the database", err, 6004, map[string]any{"migrations_path": cfg.MigrationsPath})
	}
	logger.Info("Database migration completed", nil)
	return &DatabaseRepo{db: db}
}

func (r *DatabaseRepo) CreateUser(ctx context.Context, user models.User) error {
	query := `INSERT INTO users (login, password_hash) VALUES ($1, $2)`
	_, err := r.db.ExecContext(ctx, query, user.Login, user.PasswordHash)
	return err
}

func (r *DatabaseRepo) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	query := `SELECT id, login, password_hash FROM users WHERE login = $1`
	var user models.User
	err := r.db.QueryRowContext(ctx, query, login).Scan(&user.ID, &user.Login, &user.PasswordHash)
	return user, err
}

func (r *DatabaseRepo) CreateChat(ctx context.Context, userID string, title string) (string, error) {
	query := `
		INSERT INTO chats (user_id, title)
		VALUES ($1, COALESCE(NULLIF($2, ''), 'New chat'))
		RETURNING id::text
	`
	var chatID string
	err := r.db.QueryRowContext(ctx, query, userID, strings.TrimSpace(title)).Scan(&chatID)
	return chatID, err
}

func (r *DatabaseRepo) GetChats(ctx context.Context, userID string) ([]models.Chat, error) {
	query := `
		SELECT id::text, user_id::text, title, created_at::text, updated_at::text
		FROM chats
		WHERE user_id = $1
		ORDER BY updated_at DESC, created_at DESC
	`

	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var chats []models.Chat
	for rows.Next() {
		var chat models.Chat
		if err := rows.Scan(&chat.ID, &chat.UserID, &chat.Title, &chat.CreatedAt, &chat.UpdatedAt); err != nil {
			return nil, err
		}
		chats = append(chats, chat)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return chats, nil
}

func (r *DatabaseRepo) CreateQuery(ctx context.Context, userID string, chatID string, prompt string) (int64, error) {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return 0, err
	}
	defer tx.Rollback()

	var queryID int64
	if strings.TrimSpace(chatID) == "" {
		query := `INSERT INTO queries (user_id, prompt) VALUES ($1, $2) RETURNING id`
		if err := tx.QueryRowContext(ctx, query, userID, prompt).Scan(&queryID); err != nil {
			return 0, err
		}
	} else {
		query := `
			INSERT INTO queries (user_id, chat_id, prompt)
			SELECT $1, id, $3
			FROM chats
			WHERE id = $2 AND user_id = $1
			RETURNING id
		`
		if err := tx.QueryRowContext(ctx, query, userID, chatID, prompt).Scan(&queryID); err != nil {
			return 0, err
		}

		updateQuery := `UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = $1 AND user_id = $2`
		if _, err := tx.ExecContext(ctx, updateQuery, chatID, userID); err != nil {
			return 0, err
		}
	}

	if err := tx.Commit(); err != nil {
		return 0, err
	}
	return queryID, nil
}

func (r *DatabaseRepo) GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error) {
	var (
		query string
		rows  *sql.Rows
		err   error
	)

	chatID := strings.TrimPrefix(flag, "chat:")
	if strings.HasPrefix(flag, "chat:") && chatID != "" {
		query = `SELECT id FROM queries WHERE user_id = $1 AND chat_id = $2 ORDER BY id DESC LIMIT $3`
		rows, err = r.db.QueryContext(ctx, query, userID, chatID, quantity)
	} else {
		query = `SELECT id FROM queries WHERE user_id = $1 ORDER BY id DESC LIMIT $2`
		rows, err = r.db.QueryContext(ctx, query, userID, quantity)
	}

	var ids []int32
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var id int32
		err := rows.Scan(&id)
		if err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return ids, nil
}

func (r *DatabaseRepo) QueryBelongsToUser(ctx context.Context, userID string, queryID int64) (bool, error) {
	query := `SELECT EXISTS(SELECT 1 FROM queries WHERE id = $1 AND user_id = $2)`
	var belongs bool
	err := r.db.QueryRowContext(ctx, query, queryID, userID).Scan(&belongs)
	return belongs, err
}
