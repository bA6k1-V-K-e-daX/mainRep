package config

import (
	"flag"
	"os"
	"time"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	Env        string         `yaml:"env" env-default:"local"`           // debug, local, test, production
	FormatTime string         `yaml:"format_time" env-default:"RFC3339"` // time format
	FilePath   string         `yaml:"file_path" env-default:"app.log"`   // log file path
	GRPC       GRPCConfig     `yaml:"grpc"`                              // gRPC config
	Database   DatabaseConfig `yaml:"postgres" env-required:"true"`      // database config
}

type GRPCConfig struct {
	Port    int `yaml:"port"`    // gRPC port
	Timeout int `yaml:"timeout"` // gRPC timeout
}

type DatabaseConfig struct {
	Host           string `yaml:"host" env-required:"true"`            // database host
	Port           int    `yaml:"port" env-required:"true"`            // database port
	User           string `yaml:"user" env-required:"true"`            // database user
	Password       string `yaml:"password" env-required:"true"`        // database password
	Database       string `yaml:"database" env-required:"true"`        // database name
	MigrationsPath string `yaml:"migrations_path" env-required:"true"` // migrations path
}

var level logger.Level

var timeLayouts = map[string]string{
	"Layout":      time.Layout,
	"ANSIC":       time.ANSIC,
	"UnixDate":    time.UnixDate,
	"RubyDate":    time.RubyDate,
	"RFC822":      time.RFC822,
	"RFC822Z":     time.RFC822Z,
	"RFC850":      time.RFC850,
	"RFC1123":     time.RFC1123,
	"RFC1123Z":    time.RFC1123Z,
	"RFC3339":     time.RFC3339,
	"RFC3339Nano": time.RFC3339Nano,
	"Kitchen":     time.Kitchen,
	"Stamp":       time.Stamp,
	"StampMilli":  time.StampMilli,
	"StampMicro":  time.StampMicro,
	"StampNano":   time.StampNano,
	"DataTime":    time.DateTime,
	"DataOnly":    time.DateOnly,
	"TimeOnly":    time.TimeOnly,
}

func getTimeLayout(configValue string) string {
	if layout, ok := timeLayouts[configValue]; ok {
		return layout
	}
	return time.RFC3339
}

func relevel(l string) logger.Level {
	if l == "" {
		l = "local"
	}
	switch l {
	case "debug":
		level = logger.LevelDebug
	case "local":
		level = logger.LevelInfo
	case "test":
		level = logger.LevelWarn
	case "production":
		level = logger.LevelError
	}
	return level
}

func MustLoad() (*Config, logger.Level) {
	path := fechPathConfig()
	if path == "" {
		panic("config path is empty")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		panic("config file not found: " + path)
	}
	var cfg Config
	if err := cleanenv.ReadConfig(path, &cfg); err != nil {
		panic("failed to load config: " + err.Error())
	}
	cfg.FormatTime = getTimeLayout(cfg.FormatTime)
	return &cfg, relevel(cfg.Env)
}

func fechPathConfig() string {
	var res string
	//--config="path/to/config.yaml"
	flag.StringVar(&res, "config", "", "path to config file")
	flag.Parse()
	return res
}
