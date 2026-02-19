package dbrepo

import (
	"database/internal/config"
	"database/internal/migrator"
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
