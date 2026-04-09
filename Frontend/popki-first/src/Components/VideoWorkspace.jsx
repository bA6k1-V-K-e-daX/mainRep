import React, { useRef, useState } from "react";
import ReactPlayer from "react-player";
import { Play, Pause, RotateCcw, RotateCw, ChevronDown } from "lucide-react";
import { useMedia } from "../context/MediaContext";

export default function VideoWorkspace() {
  const { media } = useMedia();
  const playerRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0); // от 0 до 1
  const [playedSeconds, setPlayedSeconds] = useState(0);
  const [duration, setDuration] = useState(0);

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
    if (playerRef.current) {
      const currentTime = playerRef.current.getCurrentTime();
      playerRef.current.seekTo(currentTime + amount, "seconds");
    }
  };

  return (
    <div className='flex-1 flex flex-col relative h-full'>
      {/* Плеер */}
      <div className='flex-1 rounded-2xl bg-black overflow-hidden flex items-center justify-center relative shadow-lg'>
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
      </div>

      {/* Таймлайн с ползунком, который двигается синхронно с видео */}
      <div
        className='h-20 mt-4 bg-[#0a0710] rounded-xl flex overflow-hidden relative border border-white/5 cursor-pointer'
        onClick={(e) => {
          // Простая перемотка по клику на таймлайн
          const rect = e.currentTarget.getBoundingClientRect();
          const percent = (e.clientX - rect.left) / rect.width;
          playerRef.current.seekTo(percent, "fraction");
        }}
      >
        {/* Индикатор прогресса */}
        <div
          className='absolute top-0 bottom-0 w-0.5 bg-[#4C1DFF] z-10 shadow-[0_0_8px_#4C1DFF]'
          style={{ left: `${progress * 100}%` }}
        />
        {/* Имитация кадров (в реальном проекте генерируются бэкендом или ffmpeg.wasm) */}
        {[...Array(12)].map((_, i) => (
          <div
            key={i}
            className='flex-1 border-r border-black/50 bg-gray-800/20'
          />
        ))}
      </div>

      {/* Контролы плеера */}
      <div className='flex items-center justify-between mt-4 bg-[#0a0710] rounded-full px-6 py-3 border border-white/5'>
        <div className='flex items-center gap-6'>
          <span className='text-sm text-gray-400 font-mono'>
            {formatTime(playedSeconds)} / {formatTime(duration)}
          </span>
          <div className='flex items-center gap-2 px-3 py-1 text-sm text-gray-300 truncate max-w-50'>
            {media.name}
          </div>
        </div>
        <div className='flex items-center gap-4'>
          <button
            onClick={() => skip(-15)}
            className='text-gray-400 hover:text-white transition'
          >
            <RotateCcw className='w-5 h-5' />
          </button>
          <button
            onClick={() => skip(15)}
            className='text-gray-400 hover:text-white transition'
          >
            <RotateCw className='w-5 h-5' />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className='text-white hover:text-[#4C1DFF] transition ml-2'
          >
            {isPlaying ? (
              <Pause className='w-6 h-6 fill-current' />
            ) : (
              <Play className='w-6 h-6 fill-current' />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
