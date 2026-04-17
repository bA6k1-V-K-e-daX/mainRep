import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  Plus,
  Paperclip,
  ArrowUp,
  Folder,
  User,
  MonitorPlay,
} from "lucide-react";
import { useMedia } from "../context/MediaContext";
import VideoWorkspace from "../Components/VideoWorkspace";

export default function Workspace() {
  const { media, setMedia, results, handlePromptSubmit, isLoading } =
    useMedia();
  const [prompt, setPrompt] = useState("");

  const onDrop = useCallback(
    (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (file) {
        setMedia({
          file,
          url: URL.createObjectURL(file),
          name: file.name,
        });
      }
    },
    [setMedia],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/*": [], "image/*": [] },
  });

  const onSubmit = () => {
    handlePromptSubmit(prompt);
    setPrompt("");
  };

  const bgDarkest = "bg-[#0B0814]";
  const bgMain = "bg-[#110D1E]";
  const primaryColor = "bg-[#4C1DFF]";

  return (
    <div
      className={`flex flex-col lg:flex-row h-screen w-full text-white font-sans ${bgDarkest} overflow-hidden`}
    >
      {/* ЛЕВАЯ ПАНЕЛЬ - скрыта на мобилке, видна на lg; fixed width на desktop */}
      <aside className='hidden lg:flex lg:w-64 xl:w-72 2xl:w-80 flex-col p-4 md:p-5 lg:p-6 border-b lg:border-b-0 lg:border-r border-white/5 shrink-0 overflow-y-auto'>
        <div className='flex items-center gap-2 mb-8'>
          <div className='w-6 h-6 rounded-full bg-white flex items-center justify-center shrink-0'>
            <span className='text-black text-xs font-bold'>P</span>
          </div>
          <span className='text-sm md:text-base lg:text-lg font-medium tracking-wide truncate'>
            Peeky
          </span>
        </div>

        <button
          onClick={() => setMedia(null)}
          className={`w-full ${primaryColor} hover:bg-[#5a2df5] transition-colors rounded-lg py-2 px-3 md:py-2.5 md:px-4 lg:py-2 lg:px-4 flex items-center justify-between mb-4 md:mb-6 lg:mb-6 text-xs sm:text-sm`}
        >
          <span className='text-xs md:text-sm'>Новый чат</span>
          <Plus className='w-3 h-3 md:w-4 md:h-4' />
        </button>

        <div className='flex-1 overflow-y-auto'>
          <span className='text-xs text-gray-500 mb-2 md:mb-3 px-2'>
            Ваши чаты
          </span>
          <div className='space-y-1'>
            <div className='px-2 md:px-3 py-2 rounded-lg text-xs sm:text-sm text-gray-400 hover:bg-white/5 cursor-pointer truncate'>
              Горы
            </div>
            <div className='px-2 md:px-3 py-2 rounded-lg text-xs sm:text-sm text-white bg-white/10 cursor-pointer truncate'>
              Коты и собаки
            </div>
            <div className='px-2 md:px-3 py-1 md:py-2 rounded-lg text-xs md:text-sm text-gray-400 hover:bg-white/5 cursor-pointer truncate'>
              Котопсы и человеки
            </div>
          </div>
        </div>

        <div className='mt-auto pt-4 border-t border-white/5 cursor-pointer flex items-center gap-2 md:gap-3 px-2 hover:bg-white/5 rounded-lg py-2'>
          <div className='w-6 md:w-8 lg:w-8 h-6 md:h-8 lg:h-8 rounded-full bg-gray-700 flex items-center justify-center shrink-0'>
            <User className='w-3 md:w-4 h-3 md:h-4 text-gray-300' />
          </div>
          <span className='text-xs md:text-sm lg:text-sm text-gray-300 truncate'>
            Мой аккаунт
          </span>
        </div>
      </aside>

      {/* ЦЕНТРАЛЬНАЯ ОБЛАСТЬ - фиксированный контейнер с max-width для desktop */}
      <main
        className={`flex-1 flex flex-col ${bgMain} m-1 sm:m-2 md:m-3 lg:m-4 rounded-xl md:rounded-2xl lg:rounded-2xl relative shadow-2xl p-3 sm:p-4 md:p-5 lg:p-6 max-w-full`}
      >
        {!media ? (
          <div
            {...getRootProps()}
            className={`flex-1 border-2 border-dashed rounded-xl md:rounded-2xl lg:rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-colors
              ${isDragActive ? "border-white bg-[#4C1DFF]/10" : "border-[#4C1DFF] bg-[#0d0a17] hover:bg-[#151125]"}`}
          >
            <input {...getInputProps()} />
            <MonitorPlay className='w-12 sm:w-16 md:w-20 lg:w-24 h-12 sm:h-16 md:h-20 lg:h-24 text-gray-400 mb-3 sm:mb-4 md:mb-4 lg:mb-6 opacity-50' />
            <p className='text-gray-400 text-center mb-4 sm:mb-5 md:mb-6 lg:mb-6 text-xs sm:text-sm md:text-base lg:text-base'>
              {isDragActive
                ? "Отпустите файл здесь..."
                : "Выберите файл\nили перетащите его сюда"}
            </p>
            <button
              className={`${primaryColor} py-2 px-4 sm:px-6 md:px-8 lg:px-8 rounded-lg text-xs sm:text-sm md:text-sm lg:text-sm pointer-events-none`}
            >
              Выбрать файл
            </button>
          </div>
        ) : (
          <VideoWorkspace />
        )}

        <div
          className={`mt-3 sm:mt-4 md:mt-4 lg:mt-4 bg-[#0a0710] rounded-full flex items-center px-3 sm:px-4 md:px-4 lg:px-4 py-2 md:py-3 lg:py-3 border border-white/5 ${!media && "opacity-50 pointer-events-none"}`}
        >
          <Paperclip className='w-4 sm:w-5 md:w-5 lg:w-5 h-4 sm:h-5 md:h-5 lg:h-5 text-gray-400 mr-2 md:mr-3 lg:mr-3 cursor-pointer hover:text-white shrink-0' />
          <input
            type='text'
            placeholder='Спросите у Peeky...'
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSubmit()}
            className='flex-1 bg-transparent text-xs sm:text-sm md:text-sm lg:text-sm text-white focus:outline-none min-w-0'
          />
          <button
            onClick={onSubmit}
            className={`w-6 sm:w-7 md:w-8 lg:w-8 h-6 sm:h-7 md:h-8 lg:h-8 rounded-full ${primaryColor} flex items-center justify-center hover:bg-[#5a2df5] transition shrink-0 ml-2`}
          >
            <ArrowUp className='w-3 md:w-5 lg:w-5 h-3 md:h-5 lg:h-5 text-white' />
          </button>
        </div>
      </main>

      {/* ПРАВАЯ ПАНЕЛЬ - скрыта на мобилке, видна на lg; fixed width на desktop */}
      <aside className='hidden lg:flex lg:w-80 xl:w-96 2xl:w-md flex-col p-4 md:p-5 lg:p-6 border-t lg:border-t-0 lg:border-l border-white/5 shrink-0 overflow-y-auto'>
        <h2 className='text-xs text-gray-500 mb-1 md:mb-2'>Ваши файлы</h2>
        <h1 className='text-lg md:text-xl lg:text-xl font-light mb-4 md:mb-6 lg:mb-8 text-gray-200'>
          Результат работы
        </h1>

        {isLoading ? (
          <div className='flex justify-center mt-10'>
            <span className='text-gray-400 text-xs sm:text-sm'>
              Поиск объектов...
            </span>
          </div>
        ) : results.length === 0 ? (
          <p className='text-xs sm:text-sm text-gray-500'>
            Пока здесь ничего нет...
          </p>
        ) : (
          <div className='flex-1 flex flex-col gap-3 sm:gap-4 md:gap-4 lg:gap-4 overflow-y-auto pr-2'>
            {results.map((res) => (
              <div
                key={res.id}
                className='bg-[#1f1740] rounded-lg md:rounded-xl lg:rounded-xl p-3 sm:p-3 md:p-3 lg:p-3 border border-[#4C1DFF]/30'
              >
                <div className='flex justify-between items-center mb-2 md:mb-2 lg:mb-2 gap-2'>
                  <div className='flex items-center gap-1 md:gap-2 lg:gap-2 text-xs sm:text-sm md:text-sm lg:text-sm text-white min-w-0'>
                    <Folder className='w-3 md:w-4 lg:w-4 h-3 md:h-4 lg:h-4 text-gray-400 shrink-0' />
                    <span className='truncate'>{res.folder}</span>
                  </div>
                  <span className='text-xs sm:text-xs md:text-xs lg:text-xs text-gray-400 shrink-0'>
                    {res.type}
                  </span>
                </div>

                <div className='w-full h-16 sm:h-20 md:h-20 lg:h-24 rounded-lg overflow-hidden relative'>
                  <img
                    src={res.img}
                    alt={res.type}
                    className='w-full h-full object-cover'
                  />
                  {res.type === "сегментация" && (
                    <div className='absolute inset-0 bg-red-500/40 mix-blend-color'></div>
                  )}
                </div>
              </div>
            ))}

            <div className='mt-3 sm:mt-4 md:mt-4 lg:mt-4 flex justify-center'>
              <button
                className={`${primaryColor} hover:bg-[#5a2df5] transition-colors py-2 md:py-2 lg:py-2 px-4 sm:px-6 md:px-6 lg:px-6 rounded-full text-xs sm:text-sm md:text-sm lg:text-sm flex items-center gap-1 md:gap-2 lg:gap-2 w-full justify-center`}
              >
                Скачать файлы{" "}
                <ArrowUp className='w-3 md:w-4 lg:w-4 h-3 md:h-4 lg:h-4' />
              </button>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
