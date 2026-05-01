import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import {
  Plus,
  Paperclip,
  ArrowUp,
  Folder,
  User,
  MonitorPlay,
  Download,
} from "lucide-react";
import { useMedia } from "../context/MediaContext";
import VideoWorkspace from "../Components/VideoWorkspace";

export default function Workspace() {
  const {
    chats,
    activeChatId,
    setActiveChatId,
    createNewChat,
    media,
    uploadMedia,
    resetWorkspace,
    results,
    submitPrompt,
    downloadResults,
    isAnalyzing,
    isDownloading,
    error,
  } = useMedia();
  const [prompt, setPrompt] = useState("");

  const onDrop = useCallback(
    (acceptedFiles) => {
      uploadMedia(acceptedFiles[0]);
    },
    [uploadMedia],
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { "video/*": [], "image/*": [] },
    noClick: true,
  });

  const onSubmit = () => {
    submitPrompt(prompt);
    setPrompt("");
  };

  return (
    <section className='h-screen w-full bg-[#080312] text-white'>
      <div className='grid h-full min-h-0 grid-cols-1 lg:grid-cols-[220px_1fr_240px]'>
        <aside className='hidden min-h-0 border-r border-[#1B1236] bg-[#06010E] p-3 lg:flex lg:flex-col'>
          <div className='mb-4 flex items-center gap-2'>
            <img
              src='/peeky-mini-logo.png'
              alt='Peeky logo'
              className='h-4 w-4'
            />
            <span className='text-lg font-light text-[#D8D4F3]'>Peeky</span>
          </div>

          <button
            onClick={createNewChat}
            className='mb-4 flex h-8 items-center justify-between rounded-md bg-[#4C1DFF] px-3 text-xs transition hover:bg-[#5D33FF]'
          >
            <span>Новый чат</span>
            <Plus className='h-3.5 w-3.5' />
          </button>

          <p className='mb-2 text-[11px] text-[#7C739F]'>Ваши чаты</p>
          <div className='space-y-1'>
            {chats.map((chat) => (
              <button
                key={chat.id}
                onClick={() => {
                  setActiveChatId(chat.id);
                  resetWorkspace();
                }}
                className={`w-full truncate rounded-md px-2 py-1.5 text-left text-sm transition ${
                  activeChatId === chat.id
                    ? "bg-[#1D1241] text-white"
                    : "text-[#9C94C4] hover:bg-[#12092A]"
                }`}
              >
                {chat.title}
              </button>
            ))}
          </div>

          <div className='mt-auto flex items-center gap-2 border-t border-[#1B1236] pt-3'>
            <div className='flex h-5 w-5 items-center justify-center rounded-full bg-white/80 text-[10px] text-black'>
              U
            </div>
            <span className='text-xs text-[#B0AACC]'>User11</span>
          </div>
        </aside>

        <main className='flex min-h-0 min-w-0 flex-col bg-[#090215] px-4 py-5 lg:px-8'>
          {!media ? (
            <div
              {...getRootProps()}
              className={`flex min-h-0 flex-1 flex-col items-center justify-center rounded-[28px] border-2 border-dashed bg-[#0C041B] transition ${
                isDragActive
                  ? "border-[#6A4DFF] shadow-[0_0_20px_rgba(95,74,255,0.35)]"
                  : "border-[#3E2D8A] hover:border-[#6A4DFF]"
              }`}
            >
              <input {...getInputProps()} />
              <MonitorPlay className='mb-4 h-20 w-20 text-[#A8A1CC]' />
              <p className='mb-6 whitespace-pre-line text-center text-[#A8A1CC]'>
                {isDragActive
                  ? "Отпустите файл здесь..."
                  : "Выберите файл\nили перетащите его сюда"}
              </p>
              <button
                onClick={open}
                className='h-8 rounded-md bg-[#4C1DFF] px-12 text-sm transition hover:bg-[#5D33FF]'
              >
                Выбрать файл
              </button>
            </div>
          ) : (
            <VideoWorkspace />
          )}

          <div className='mt-4 rounded-xl border border-[#26194E] bg-[#0B051A] px-3 py-2'>
            <div className='mb-2 flex items-center gap-2 text-xs text-[#8E86B9]'>
              <Paperclip className='h-4 w-4' />
              <button onClick={open} className='transition hover:text-white'>
                Прикрепить файл
              </button>
              {media ? (
                <span className='truncate text-[#B8B2D8]'>{media.name}</span>
              ) : null}
            </div>

            <div className='flex items-center gap-3'>
              <input
                type='text'
                placeholder='Спросите у Peeky...'
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && onSubmit()}
                disabled={!media || isAnalyzing}
                className='min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-[#7C739F] disabled:opacity-50'
              />
              <button
                onClick={onSubmit}
                disabled={!media || !prompt.trim() || isAnalyzing}
                className='flex h-7 w-7 items-center justify-center rounded-full bg-[#4C1DFF] transition hover:bg-[#5D33FF] disabled:cursor-not-allowed disabled:opacity-50'
              >
                <ArrowUp className='h-4 w-4' />
              </button>
            </div>

            {error ? (
              <p className='mt-2 text-xs text-red-300'>{error}</p>
            ) : null}
          </div>
        </main>

        <aside className='hidden min-h-0 border-l border-[#1B1236] bg-[#06010E] p-3 lg:flex lg:flex-col'>
          <p className='text-xs text-[#7C739F]'>Ваши файлы</p>
          <h2 className='mb-4 text-2xl font-light text-[#D9D6EE]'>
            Результат работы
          </h2>

          {isAnalyzing ? (
            <p className='text-sm text-[#8F88B7]'>Идёт обработка файла...</p>
          ) : null}

          {!isAnalyzing && !results.length ? (
            <p className='text-sm text-[#8F88B7]'>Пока здесь ничего нет...</p>
          ) : null}

          <div className='flex flex-1 flex-col gap-2 overflow-y-auto'>
            {results.map((result) => (
              <article
                key={result.id}
                className='rounded-lg border border-[#3B2A79] bg-[#251257] p-2'
              >
                <div className='mb-2 flex items-center justify-between gap-2 text-xs'>
                  <div className='flex items-center gap-1 text-[#E5E1FF]'>
                    <Folder className='h-3.5 w-3.5' />
                    <span>{result.folder}</span>
                  </div>
                  <span className='text-[#B8B2D8]'>{result.type}</span>
                </div>
                <img
                  src={result.img}
                  alt={`${result.folder} ${result.type}`}
                  className='h-16 w-full rounded object-cover'
                />
              </article>
            ))}
          </div>

          <button
            onClick={downloadResults}
            disabled={!results.length || isDownloading}
            className='mt-3 flex h-8 items-center justify-center gap-2 rounded-full bg-[#4C1DFF] text-xs transition hover:bg-[#5D33FF] disabled:cursor-not-allowed disabled:opacity-50'
          >
            <span>{isDownloading ? "Скачивание..." : "Скачать файлы"}</span>
            <Download className='h-3.5 w-3.5' />
          </button>
        </aside>
      </div>

      <div className='pointer-events-none absolute bottom-4 left-3 hidden items-center gap-2 text-xs text-[#B0AACC] lg:flex'>
        <User className='h-3.5 w-3.5' />
        <span>User11</span>
      </div>
    </section>
  );
}
