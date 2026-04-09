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
      className={`flex h-screen w-full text-white font-sans ${bgDarkest} overflow-hidden`}
    >
      {/* ЛЕВАЯ ПАНЕЛЬ */}
      <aside className='w-64 flex flex-col p-4 border-r border-white/5'>
        <div className='flex items-center gap-2 mb-8'>
          <div className='w-6 h-6 rounded-full bg-white flex items-center justify-center'>
            <span className='text-black text-xs font-bold'>P</span>
          </div>
          <span className='text-xl font-medium tracking-wide'>Peeky</span>
        </div>

        <button
          onClick={() => setMedia(null)}
          className={`w-full ${primaryColor} hover:bg-[#5a2df5] transition-colors rounded-lg py-2 px-4 flex items-center justify-between mb-6`}
        >
          <span className='text-sm'>Новый чат</span>
          <Plus className='w-4 h-4' />
        </button>

        <div className='flex-1 overflow-y-auto'>
          <p className='text-xs text-gray-500 mb-3 px-2'>Ваши чаты</p>
          <div className='space-y-1'>
            <div className='px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5 cursor-pointer'>
              Горы
            </div>
            <div className='px-3 py-2 rounded-lg text-sm text-white bg-white/10 cursor-pointer'>
              Коты и собаки
            </div>
            <div className='px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5 cursor-pointer'>
              Котопсы и человеки
            </div>
          </div>
        </div>

        <div className='mt-auto pt-4 border-t border-white/5 cursor-pointer flex items-center gap-3 px-2 hover:bg-white/5 rounded-lg py-2'>
          <div className='w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center'>
            <User className='w-4 h-4 text-gray-300' />
          </div>
          <span className='text-sm text-gray-300'>Мой аккаунт</span>
        </div>
      </aside>

      {/* ЦЕНТРАЛЬНАЯ ОБЛАСТЬ */}
      <main
        className={`flex-1 flex flex-col ${bgMain} m-2 rounded-2xl relative shadow-2xl p-6`}
      >
        {!media ? (
          <div
            {...getRootProps()}
            className={`flex-1 border-2 border-dashed rounded-3xl flex flex-col items-center justify-center cursor-pointer transition-colors
              ${isDragActive ? "border-white bg-[#4C1DFF]/10" : "border-[#4C1DFF] bg-[#0d0a17] hover:bg-[#151125]"}`}
          >
            <input {...getInputProps()} />
            <MonitorPlay className='w-24 h-24 text-gray-400 mb-4 opacity-50' />
            <p className='text-gray-400 text-center mb-6 text-sm'>
              {isDragActive
                ? "Отпустите файл здесь..."
                : "Выберите файл\nили перетащите его сюда"}
            </p>
            <button
              className={`${primaryColor} py-2 px-8 rounded-lg text-sm pointer-events-none`}
            >
              Выбрать файл
            </button>
          </div>
        ) : (
          <VideoWorkspace />
        )}

        <div
          className={`mt-4 bg-[#0a0710] rounded-full flex items-center px-4 py-3 border border-white/5 ${!media && "opacity-50 pointer-events-none"}`}
        >
          <Paperclip className='w-5 h-5 text-gray-400 mr-3 cursor-pointer hover:text-white' />
          <input
            type='text'
            placeholder='Спросите у Peeky...'
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSubmit()}
            className='flex-1 bg-transparent text-sm text-white focus:outline-none'
          />
          <button
            onClick={onSubmit}
            className={`w-8 h-8 rounded-full ${primaryColor} flex items-center justify-center hover:bg-[#5a2df5] transition`}
          >
            <ArrowUp className='w-5 h-5 text-white' />
          </button>
        </div>
      </main>

      {/* ПРАВАЯ ПАНЕЛЬ */}
      <aside className='w-80 flex flex-col p-6 border-l border-white/5'>
        <h2 className='text-xs text-gray-500 mb-1'>Ваши файлы</h2>
        <h1 className='text-xl font-light mb-8 text-gray-200'>
          Результат работы
        </h1>

        {isLoading ? (
          <div className='flex justify-center mt-10'>
            <span className='text-gray-400 text-sm'>Поиск объектов...</span>
          </div>
        ) : results.length === 0 ? (
          <p className='text-sm text-gray-500'>Пока здесь ничего нет...</p>
        ) : (
          <div className='flex-1 flex flex-col gap-4 overflow-y-auto pr-2'>
            {results.map((res) => (
              <div
                key={res.id}
                className='bg-[#1f1740] rounded-xl p-3 border border-[#4C1DFF]/30'
              >
                <div className='flex justify-between items-center mb-2'>
                  <div className='flex items-center gap-2 text-sm text-white'>
                    <Folder className='w-4 h-4 text-gray-400' /> {res.folder}
                  </div>
                  <span className='text-xs text-gray-400'>{res.type}</span>
                </div>

                <div className='w-full h-24 rounded-lg overflow-hidden relative'>
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

            <div className='mt-4 flex justify-center'>
              <button
                className={`${primaryColor} hover:bg-[#5a2df5] transition-colors py-2 px-6 rounded-full text-sm flex items-center gap-2 w-full justify-center`}
              >
                Скачать файлы <ArrowUp className='w-4 h-4' />
              </button>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
