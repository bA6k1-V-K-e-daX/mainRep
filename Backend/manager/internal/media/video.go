package media

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync"

	"golang.org/x/sync/errgroup"
)

var imageExtensions = map[string]struct{}{
	".jpg":  {},
	".jpeg": {},
	".png":  {},
	".bmp":  {},
	".webp": {},
	".tif":  {},
	".tiff": {},
}

type FileSummary struct {
	ImageFiles       int
	VideoFiles       int
	UnsupportedFiles int
}

type VideoProcessorConfig struct {
	FFmpegPath  string
	FrameRate   string
	MaxFrames   int
	MaxParallel int
	Extensions  []string
}

type VideoProcessor struct {
	ffmpegPath      string
	frameRate       string
	maxFrames       int
	maxParallel     int
	videoExtensions map[string]struct{}
}

func NewVideoProcessor(cfg VideoProcessorConfig) *VideoProcessor {
	videoExtensions := make(map[string]struct{}, len(cfg.Extensions))
	for _, extension := range cfg.Extensions {
		normalized := normalizeExtension(extension)
		if normalized == "" {
			continue
		}
		videoExtensions[normalized] = struct{}{}
	}

	return &VideoProcessor{
		ffmpegPath:      cfg.FFmpegPath,
		frameRate:       cfg.FrameRate,
		maxFrames:       cfg.MaxFrames,
		maxParallel:     cfg.MaxParallel,
		videoExtensions: videoExtensions,
	}
}

func (p *VideoProcessor) SummarizeFiles(filePaths []string) FileSummary {
	var summary FileSummary
	for _, filePath := range filePaths {
		switch {
		case p.IsVideoFile(filePath):
			summary.VideoFiles++
		case isImageFile(filePath):
			summary.ImageFiles++
		default:
			summary.UnsupportedFiles++
		}
	}
	return summary
}

func (p *VideoProcessor) IsVideoFile(filePath string) bool {
	_, exists := p.videoExtensions[normalizeExtension(filepath.Ext(filePath))]
	return exists
}

func (p *VideoProcessor) ExpandVideos(ctx context.Context, filePaths []string) (int, error) {
	videoPaths := make([]string, 0, len(filePaths))
	for _, filePath := range filePaths {
		if p.IsVideoFile(filePath) {
			videoPaths = append(videoPaths, filePath)
		}
	}

	if len(videoPaths) == 0 {
		return 0, nil
	}
	if _, err := exec.LookPath(p.ffmpegPath); err != nil {
		return 0, fmt.Errorf("ffmpeg executable %q is unavailable: %w", p.ffmpegPath, err)
	}

	group, groupCtx := errgroup.WithContext(ctx)
	group.SetLimit(p.maxParallel)

	var (
		mu              sync.Mutex
		generatedFrames int
	)

	for _, videoPath := range videoPaths {
		videoPath := videoPath
		group.Go(func() error {
			frames, err := p.extractFrames(groupCtx, videoPath)
			if err != nil {
				return err
			}

			mu.Lock()
			generatedFrames += frames
			mu.Unlock()
			return nil
		})
	}

	if err := group.Wait(); err != nil {
		return 0, err
	}
	return generatedFrames, nil
}

func (p *VideoProcessor) extractFrames(ctx context.Context, videoPath string) (int, error) {
	videoDir := filepath.Dir(videoPath)
	videoName := filepath.Base(videoPath)
	videoStem := strings.TrimSuffix(videoName, filepath.Ext(videoName))
	videoExt := strings.TrimPrefix(normalizeExtension(filepath.Ext(videoPath)), ".")
	framePrefix := fmt.Sprintf("%s__%s__frame_", videoStem, videoExt)
	outputPattern := filepath.Join(videoDir, framePrefix+"%06d.jpg")

	args := []string{
		"-hide_banner",
		"-loglevel", "error",
		"-y",
		"-i", videoPath,
		"-vf", fmt.Sprintf("fps=%s", p.frameRate),
	}
	if p.maxFrames > 0 {
		args = append(args, "-frames:v", strconv.Itoa(p.maxFrames))
	}
	args = append(args, outputPattern)

	cmd := exec.CommandContext(ctx, p.ffmpegPath, args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return 0, fmt.Errorf("ffmpeg failed for %s: %w: %s", videoName, err, strings.TrimSpace(string(output)))
	}

	entries, err := os.ReadDir(videoDir)
	if err != nil {
		return 0, fmt.Errorf("failed to inspect extracted frames for %s: %w", videoName, err)
	}

	framesCount := 0
	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}
		fileName := entry.Name()
		if strings.HasPrefix(fileName, framePrefix) && strings.HasSuffix(strings.ToLower(fileName), ".jpg") {
			framesCount++
		}
	}
	if framesCount == 0 {
		return 0, fmt.Errorf("ffmpeg produced no frames for %s", videoName)
	}
	return framesCount, nil
}

func isImageFile(filePath string) bool {
	_, exists := imageExtensions[normalizeExtension(filepath.Ext(filePath))]
	return exists
}

func normalizeExtension(extension string) string {
	if extension == "" {
		return ""
	}
	value := strings.ToLower(strings.TrimSpace(extension))
	if !strings.HasPrefix(value, ".") {
		value = "." + value
	}
	return value
}
