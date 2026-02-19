package migrator

// Error code 4000
import (
	"database/sql"
	"errors"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	_ "github.com/lib/pq"
)

var migrationsPathDefault string = "./migrations"

func Run(db *sql.DB, migrationsPath string) error {
	logger.Info("Running migrations for the database", nil)
	logger.Debug("Checking if db is nil", 4000, nil)
	if db == nil {
		err := errors.New("db is nil")
		logger.Error("Could not run migrations", err, 4001, nil)
		return err
	}
	logger.Debug("Checking if migrations path is empty", 4002, nil)
	if migrationsPath == "" {
		logger.Warn("Migrations path is empty, using default path", 4003, nil)
		migrationsPath = migrationsPathDefault
	}
	logger.Debug("Creating database driver", 4004, nil)
	driver, err := postgres.WithInstance(db, &postgres.Config{})
	if err != nil {
		logger.Error("Could not create database driver", err, 4005, nil)
		return err
	}
	logger.Debug("Creating migrate instance", 4006, map[string]any{"migrations_path": migrationsPath})
	m, err := migrate.NewWithDatabaseInstance(
		migrationsPath,
		"postgres",
		driver,
	)
	if err != nil {
		logger.Error("Could not create migrate instance", err, 4007, map[string]any{"migrations_path": migrationsPath})
		return err
	}
	logger.Debug("Running migrations", 4008, nil)
	err = m.Up()
	if err == nil || errors.Is(err, migrate.ErrNoChange) {
		logger.Info("Migrations completed", nil)
		return nil
	}
	logger.Error("Migrations failed", err, 4009, nil)
	logger.Warn("Trying to force rollback to previous version", 4009, nil)
	logger.Debug("Getting migrate version", 4009, nil)
	version, dirty, verErr := m.Version()
	if verErr != nil {
		logger.Error("Could not get migrate version", verErr, 4010, nil)
		return verErr
	}
	logger.Debug("Migrate version", 4011, map[string]any{"version": version, "dirty": dirty})
	if dirty {
		logger.Warn("Dirty migration detected", 4012, map[string]any{"version": version})
		prevVersion := int(version) - 1
		logger.Debug("Forcing rollback to previous version", 4013, map[string]any{"version": prevVersion})
		if prevVersion < 0 {
			logger.Warn("Previous version is less than 0, setting it to 0", 4014, nil)
			prevVersion = 0
		}
		logger.Debug("Forcing rollback to previous version", 4015, map[string]any{"version": prevVersion})
		if forceErr := m.Force(prevVersion); forceErr != nil {
			logger.Error("Could not force rollback to previous version", forceErr, 4016, map[string]any{"version": prevVersion})
			return forceErr
		}
		logger.Warn("Forced rollback to previous version successfully", 4017, map[string]any{"version": prevVersion})
		return err
	}
	logger.Error("Could not force rollback to previous version", err, 4018, map[string]any{"version": version})
	return err
}
