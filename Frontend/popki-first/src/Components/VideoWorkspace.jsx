import { useRef, useState } from "react";
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
    <div className='flex-1 flex flex-col relative h-full w-full'>
      {/* Плеер */}
      <div className='flex-1 rounded-xl md:rounded-2xl lg:rounded-2xl bg-black overflow-hidden flex items-center justify-center relative shadow-lg min-h-0'>
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
        className='h-10 sm:h-12 md:h-14 lg:h-16 mt-2 sm:mt-3 md:mt-4 lg:mt-4 bg-[#0a0710] rounded-lg md:rounded-xl lg:rounded-xl flex overflow-hidden relative border border-white/5 cursor-pointer flex-shrink-0'
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
      <div className='flex flex-col sm:flex-row md:flex-row items-start sm:items-center md:items-center justify-between gap-2 sm:gap-3 md:gap-4 lg:gap-6 mt-2 sm:mt-3 md:mt-4 lg:mt-4 bg-[#0a0710] rounded-lg md:rounded-full px-3 sm:px-4 md:px-6 py-2 md:py-3 lg:py-3 border border-white/5 flex-shrink-0'>
        <div className='flex items-center gap-2 md:gap-3 lg:gap-6 w-full sm:w-auto md:w-auto min-w-0'>
          <span className='text-xs sm:text-sm md:text-sm lg:text-sm text-gray-400 font-mono shrink-0'>
            {formatTime(playedSeconds)} / {formatTime(duration)}
          </span>
          <div className='flex items-center gap-1 md:gap-2 lg:gap-2 px-2 py-1 text-xs sm:text-sm md:text-sm lg:text-sm text-gray-300 truncate min-w-0 bg-white/5 sm:bg-white/5 md:bg-transparent rounded md:bg-transparent md:px-0'>
            {media.name}
          </div>
        </div>
        <div className='flex items-center gap-1 sm:gap-2 md:gap-3 md:gap-4 lg:gap-4 shrink-0 w-full sm:w-auto md:w-auto justify-between sm:justify-end'>
          <button
            onClick={() => skip(-15)}
            className='text-gray-400 hover:text-white transition p-1'
          >
            <RotateCcw className='w-4 sm:w-4 md:w-5 lg:w-5 h-4 sm:h-4 md:h-5 lg:h-5' />
          </button>
          <button
            onClick={() => skip(15)}
            className='text-gray-400 hover:text-white transition p-1'
          >
            <RotateCw className='w-4 sm:w-4 md:w-5 lg:w-5 h-4 sm:h-4 md:h-5 lg:h-5' />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className='text-white hover:text-[#4C1DFF] transition p-1'
          >
            {isPlaying ? (
              <Pause className='w-5 sm:w-5 md:w-6 lg:w-6 h-5 sm:h-5 md:h-6 lg:h-6 fill-current' />
            ) : (
              <Play className='w-5 sm:w-5 md:w-6 lg:w-6 h-5 sm:h-5 md:h-6 lg:h-6 fill-current' />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
