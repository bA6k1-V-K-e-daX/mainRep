package dbrepo

import (
	"context"
	"database/internal/config"
	"database/internal/migrator"
	"database/internal/models"
	"database/sql"
	"fmt"

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

func (r *DatabaseRepo) CreateQuery(ctx context.Context, userID string) (int64, error) {
	query := `INSERT INTO queries (user_id) VALUES ($1) RETURNING id`
	var queryID int64
	err := r.db.QueryRowContext(ctx, query, userID).Scan(&queryID)
	return queryID, err
}
