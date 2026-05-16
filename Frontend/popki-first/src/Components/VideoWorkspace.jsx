import { useMemo, useRef, useState } from "react";
import ReactPlayer from "react-player";
import { Play, Pause, RotateCcw, RotateCw } from "lucide-react";
import { useMedia } from "../context/MediaContext";

export default function VideoWorkspace() {
  const { media, timelineFrames } = useMedia();
  const playerRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [playedSeconds, setPlayedSeconds] = useState(0);
  const [duration, setDuration] = useState(0);
  const isVideo = media?.kind === "video";

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60)
      .toString()
      .padStart(2, "0");
    const s = Math.floor(seconds % 60)
      .toString()
      .padStart(2, "0");
    return `${m}:${s}`;
  };

  const skip = (amount) => {
    if (playerRef.current && isVideo) {
      const currentTime = playerRef.current.getCurrentTime();
      playerRef.current.seekTo(currentTime + amount, "seconds");
    }
  };

  const frames = useMemo(() => {
    if (!isVideo) return [];
    if (timelineFrames.length) {
      return timelineFrames;
    }
    return media ? [{ id: "preview", url: media.url }] : [];
  }, [isVideo, media, timelineFrames]);

  return (
    <div className='flex h-full flex-1 flex-col'>
      <div className='flex min-h-0 flex-1 items-center justify-center overflow-hidden rounded-2xl bg-[var(--bg-primary)] p-4 shadow-[0_0_24px_rgba(0,0,0,0.45)]'>
        {isVideo ? (
          <ReactPlayer
            ref={playerRef}
            url={media.url}
            playing={isPlaying}
            width='100%'
            height='100%'
            onProgress={(state) => {
              setProgress(state.played);
              setPlayedSeconds(state.playedSeconds);
            }}
            onDuration={setDuration}
            style={{ objectFit: "contain" }}
          />
        ) : (
          <img
            src={media.url}
            alt={media.name}
            className='max-h-full w-auto max-w-full rounded-lg object-contain'
          />
        )}
      </div>

      {isVideo ? (
        <div
          className='relative mt-4 flex h-16 overflow-hidden rounded-xl border border-[var(--border-primary)] bg-[var(--bg-tertiary)]'
          onClick={(e) => {
            if (!playerRef.current) return;
            const rect = e.currentTarget.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            playerRef.current.seekTo(percent, "fraction");
          }}
        >
          <div
            className='absolute bottom-0 top-0 z-10 w-[2px] bg-[var(--bg-brand)] shadow-[0_0_8px_var(--bg-brand)]'
            style={{ left: `${progress * 100}%` }}
          />
          {frames.map((frame) => (
            <div
              key={frame.id}
              className='min-w-0 flex-1 border-r border-[var(--border-primary)] last:border-r-0'
            >
              <img
                src={frame.url}
                alt='Превью кадра'
                className='h-full w-full object-cover opacity-80'
              />
            </div>
          ))}
        </div>
      ) : null}

      {isVideo ? (
        <div className='mt-4 flex items-center justify-between rounded-xl border border-[var(--border-primary)] bg-[var(--bg-tertiary)] px-4 py-3'>
          <div className='flex min-w-0 items-center gap-4'>
            <span className='shrink-0 font-mono text-xs text-[var(--text-muted)] md:text-sm'>
              {`${formatTime(playedSeconds)} / ${formatTime(duration)}`}
            </span>
            <div className='min-w-0 truncate text-xs text-[var(--text-primary)]/80 md:text-sm'>
              {media.name}
            </div>
          </div>

          <div className='flex items-center gap-3'>
            <button
              onClick={() => skip(-15)}
              className='p-1 text-[var(--text-muted)] transition hover:text-white'
            >
              <RotateCcw className='h-5 w-5' />
            </button>
            <button
              onClick={() => skip(15)}
              className='p-1 text-[var(--text-muted)] transition hover:text-white'
            >
              <RotateCw className='h-5 w-5' />
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className='p-1 text-white transition hover:text-[var(--bg-brand-hover)]'
            >
              {isPlaying ? (
                <Pause className='h-6 w-6 fill-current' />
              ) : (
                <Play className='h-6 w-6 fill-current' />
              )}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}