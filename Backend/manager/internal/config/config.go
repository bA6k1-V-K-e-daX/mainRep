package config

import (
	"flag"
	"os"
	"time"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	Env            string       `yaml:"env" env-default:"local"`               // debug, local, test, production
	FormatTime     string       `yaml:"format_time" env-default:"RFC3339"`     // time format
	LogFilePath    string       `yaml:"log_file_path" env-default:"app.log"`   // log file path
	TempObjectPath string       `yaml:"temp_object_path" env-default:"volume"` // temp object path
	JWTSecret      string       `yaml:"jwt_secret" env-default:"secret"`
	HttpServer     HttpConfig   `yaml:"httpserver"` // http server config
	Client         ClientConfig `yaml:"client"`     // client config
	Processing     Processing   `yaml:"processing"` // processing config
}

type ClientConfig struct {
	Database HttpConfig `yaml:"database"` // database client config
	ML       HttpConfig `yaml:"ml"`       // ml client config
}

type HttpConfig struct {
	Port                  int    `yaml:"port" env-required:"true"`                   // HTTP port
	Host                  string `yaml:"host" env-required:"true"`                   // HTTP host
	ReadTimeoutSeconds    int    `yaml:"read_timeout_seconds" env-default:"30"`      // HTTP read timeout
	WriteTimeoutSeconds   int    `yaml:"write_timeout_seconds" env-default:"3600"`   // HTTP write timeout
	IdleTimeoutSeconds    int    `yaml:"idle_timeout_seconds" env-default:"120"`     // HTTP idle timeout
	MaxMultipartMemoryMiB int64  `yaml:"max_multipart_memory_mib" env-default:"512"` // multipart memory limit
}

type Processing struct {
	MaxFilesPerRequest int         `yaml:"max_files_per_request" env-default:"256"` // max uploaded files in one request
	MLTimeoutSeconds   int         `yaml:"ml_timeout_seconds" env-default:"3600"`   // ml request timeout
	Video              VideoConfig `yaml:"video"`                                   // video preprocessing config
}

type VideoConfig struct {
	FFmpegPath  string   `yaml:"ffmpeg_path" env-default:"ffmpeg"` // ffmpeg executable
	FrameRate   string   `yaml:"frame_rate" env-default:"1"`       // extracted frames per second
	MaxFrames   int      `yaml:"max_frames" env-default:"900"`     // max extracted frames per video
	MaxParallel int      `yaml:"max_parallel" env-default:"2"`     // parallel video preprocessing jobs
	Extensions  []string `yaml:"extensions"`                       // supported video extensions
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
	cfg.normalize()
	return &cfg, relevel(cfg.Env)
}

func (c *Config) normalize() {
	if c.HttpServer.ReadTimeoutSeconds <= 0 {
		c.HttpServer.ReadTimeoutSeconds = 30
	}
	if c.HttpServer.WriteTimeoutSeconds <= 0 {
		c.HttpServer.WriteTimeoutSeconds = 3600
	}
	if c.HttpServer.IdleTimeoutSeconds <= 0 {
		c.HttpServer.IdleTimeoutSeconds = 120
	}
	if c.HttpServer.MaxMultipartMemoryMiB <= 0 {
		c.HttpServer.MaxMultipartMemoryMiB = 512
	}
	if c.Processing.MaxFilesPerRequest <= 0 {
		c.Processing.MaxFilesPerRequest = 256
	}
	if c.Processing.MLTimeoutSeconds <= 0 {
		c.Processing.MLTimeoutSeconds = 3600
	}
	if c.Processing.Video.FFmpegPath == "" {
		c.Processing.Video.FFmpegPath = "ffmpeg"
	}
	if c.Processing.Video.FrameRate == "" {
		c.Processing.Video.FrameRate = "1"
	}
	if c.Processing.Video.MaxFrames <= 0 {
		c.Processing.Video.MaxFrames = 900
	}
	if c.Processing.Video.MaxParallel <= 0 {
		c.Processing.Video.MaxParallel = 2
	}
	if len(c.Processing.Video.Extensions) == 0 {
		c.Processing.Video.Extensions = []string{
			".mp4",
			".mov",
			".avi",
			".mkv",
			".webm",
			".mpeg",
			".mpg",
			".m4v",
		}
	}
}

func fechPathConfig() string {
	var res string
	//--config="path/to/config.yaml"
	flag.StringVar(&res, "config", "", "path to config file")
	flag.Parse()
	return res
}
