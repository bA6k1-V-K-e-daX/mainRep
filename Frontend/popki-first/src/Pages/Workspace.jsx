import { useCallback, useState, useRef, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import {
  Plus,
  Paperclip,
  ArrowUp,
  Folder,
  User,
  MonitorPlay,
  Download,
  X,
  Sun,
  Moon,
} from "lucide-react";
import { useMedia } from "../context/MediaContext";
import { useTheme } from "../context/ThemeContext";
import LightboxModal from "../Components/LightboxModal";

export default function Workspace() {
  const {
    chats,
    activeChatId,
    setActiveChatId,
    createNewChat,
    media,
    uploadMedia,
    removeMedia,
    messages,
    submitPrompt,
    downloadArchive,
    isAnalyzing,
    filesCount,
    error,
  } = useMedia();
  const { theme, toggleTheme } = useTheme();
  const [prompt, setPrompt] = useState("");
  const [lightbox, setLightbox] = useState({ isOpen: false, images: [], currentIndex: 0 });
  const messagesEndRef = useRef(null);

  const openLightbox = (images, startIndex = 0) => {
    setLightbox({ isOpen: true, images, currentIndex: startIndex });
  };

  const closeLightbox = () => {
    setLightbox({ isOpen: false, images: [], currentIndex: 0 });
  };

  const navigateLightbox = (delta) => {
    setLightbox((prev) => {
      const newIndex = (prev.currentIndex + delta + prev.images.length) % prev.images.length;
      return { ...prev, currentIndex: newIndex };
    });
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const onDrop = useCallback(
    (acceptedFiles) => {
      uploadMedia(acceptedFiles);
    },
    [uploadMedia],
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { "video/*": [], "image/*": [] },
    noClick: true,
    multiple: true,
    disabled: isAnalyzing,
  });

  const onSubmit = () => {
    submitPrompt(prompt);
    setPrompt("");
  };

  const renderMessage = (message) => {
    if (message.type === "user") {
      return (
        <div key={message.id} className="flex gap-3 justify-end">
          <div className="max-w-[70%] rounded-2xl bg-[var(--bg-brand)] px-4 py-3">
            {message.prompt && (
              <p className="mb-2 text-sm">{message.prompt}</p>
            )}
            {message.media && message.media.length > 0 && (
              <div className="grid grid-cols-3 gap-2">
                {message.media.map((file) => (
                  <img
                    key={file.id}
                    src={file.url}
                    alt={file.name}
                    className="h-20 w-full cursor-pointer rounded-lg object-cover"
                    onClick={() => openLightbox(message.media.map((f) => f.url))}
                  />
                ))}
              </div>
            )}
          </div>
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-[10px] text-black">
            U
          </div>
        </div>
      );
    }

    return (
      <div key={message.id} className="flex gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--bg-brand)] text-[10px]">
          P
        </div>
        <div className="max-w-[70%] rounded-2xl bg-[var(--bg-surface)] px-4 py-3">
          {message.prompt && (
            <p className="mb-2 text-sm text-[var(--text-light)]">{message.prompt}</p>
          )}
          {message.results && message.results.length > 0 && (
            <div>
              <div className="grid grid-cols-2 gap-2">
                {message.results.map((result) => (
                  <div key={result.id}>
                    {result.img ? (
                      <img
                        src={result.img}
                        alt={`${result.folder} ${result.type}`}
                        className="h-24 w-full cursor-pointer rounded-lg object-cover"
                        onClick={() => openLightbox(message.results.filter(r => r.img).map(r => r.img))}
                        onError={(e) => {
                          e.target.style.display = "none";
                        }}
                      />
                    ) : (
                      <div className="flex h-24 items-center justify-center rounded-lg bg-[var(--bg-secondary)]">
                        <span className="text-xs text-[var(--text-muted)]">
                          {result.folder}
                        </span>
                      </div>
                    )}
                    <div className="mt-1 flex items-center justify-between text-[10px]">
                      <span className="text-[var(--text-muted)] truncate">
                        {result.folder}
                      </span>
                      <span className="rounded bg-[var(--bg-brand)]/20 px-1.5 py-0.5 text-[var(--text-light)]">
                        {result.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => downloadArchive(message.results, message.queryId)}
                className="mt-2 flex h-7 items-center gap-1.5 rounded-md bg-[var(--bg-brand)]/20 px-3 text-xs text-[var(--text-light)] transition hover:bg-[var(--bg-brand)]/30 disabled:opacity-50"
              >
                <Download className="h-3.5 w-3.5" />
                Скачать архив
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <section className="flex h-screen w-full flex-col bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <div className="flex h-full min-h-0">
        <aside className="hidden w-60 min-w-0 flex-col border-r border-[var(--border-primary)] bg-[var(--bg-secondary)] p-3 lg:flex">
          <div className="mb-4 flex items-center gap-2">
            <img
              src="/peeky-mini-logo.png"
              alt="Peeky logo"
              className="h-4 w-4"
            />
            <span className="text-lg font-light text-[var(--text-light)]">Peeky</span>
          </div>

          <button
            onClick={createNewChat}
            className="mb-4 flex h-8 items-center justify-between rounded-md bg-[var(--bg-brand)] px-3 text-xs transition hover:bg-[var(--bg-brand-hover)]"
          >
            <span>Новый чат</span>
            <Plus className="h-3.5 w-3.5" />
          </button>

          <p className="mb-2 text-[11px] text-[var(--text-label)]">Ваши чаты</p>
          <div className="flex-1 overflow-y-auto">
            {chats.map((chat) => (
              <button
                key={chat.id}
                onClick={async () => {
                  await setActiveChatId(chat.id);
                }}
                className={`w-full truncate rounded-md px-2 py-1.5 text-left text-sm transition ${
                  activeChatId === chat.id
                    ? "bg-[var(--bg-surface)] text-white"
                    : "text-[var(--text-muted)] hover:bg-[var(--bg-secondary)]"
                }`}
              >
                {chat.title}
              </button>
            ))}
          </div>

          <div className="mt-auto flex items-center justify-between gap-2 border-t border-[var(--border-primary)] pt-3">
            <div className="flex items-center gap-2">
              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-white/80 text-[10px] text-black">
                U
              </div>
              <span className="text-xs text-[var(--text-muted)]">User11</span>
            </div>
            <button
              onClick={toggleTheme}
              className="flex h-7 w-7 items-center justify-center rounded-full bg-white/10 transition hover:bg-white/20"
              aria-label="Переключить тему"
            >
              {theme === "light" ? (
                <Moon className="h-3.5 w-3.5 text-white" />
              ) : (
                <Sun className="h-3.5 w-3.5 text-white" />
              )}
            </button>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          <div
            {...getRootProps()}
            className="flex-1 overflow-y-auto px-4 py-4 lg:px-8"
          >
            <input {...getInputProps()} />

            {messages.length === 0 && !isAnalyzing ? (
              <div className="flex h-full flex-col items-center justify-center">
                <MonitorPlay className="mb-4 h-20 w-20 text-[var(--text-muted)]" />
                <p className="mb-6 whitespace-pre-line text-center text-[var(--text-muted)]">
                  {isDragActive
                    ? "Отпустите файлы здесь..."
                    : "Выберите файлы\nили перетащите их сюда"}
                </p>
                <button
                  onClick={open}
                  className="h-8 rounded-md bg-[var(--bg-brand)] px-12 text-sm transition hover:bg-[var(--bg-brand-hover)]"
                >
                  Выбрать файлы
                </button>
              </div>
            ) : (
              <div className="space-y-4 pb-4">
                {messages.map(renderMessage)}
                {isAnalyzing && (
                  <div className="flex gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--bg-brand)] text-[10px]">
                      P
                    </div>
                    <div className="rounded-2xl bg-[var(--bg-surface)] px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--text-muted)]"></span>
                          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--text-muted)]" style={{ animationDelay: "0.1s" }}></span>
                          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--text-muted)]" style={{ animationDelay: "0.2s" }}></span>
                        </div>
                        <p className="text-sm text-[var(--text-muted)]">
                          Обработка {filesCount} файлов...
                        </p>
                      </div>
                      <p className="mt-1 text-[10px] text-[var(--text-muted)]/60">
                        Это может занять несколько минут
                      </p>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="border-t border-[var(--border-primary)] bg-[var(--bg-tertiary)] p-3">
            {media.length > 0 && (
              <div className="mb-2 flex gap-2 overflow-x-auto pb-2">
                {media.map((file) => (
                  <div key={file.id} className="relative h-14 w-14 flex-shrink-0">
                    <img
                      src={file.url}
                      alt={file.name}
                      className="h-full w-full rounded-lg object-cover"
                    />
                    <button
                      onClick={() => removeMedia(file.id)}
                      className="absolute -right-1.5 -top-1.5 z-10 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-white shadow-md transition hover:bg-red-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-center gap-2">
              <button
                onClick={open}
                disabled={isAnalyzing}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--bg-surface)] transition hover:bg-[var(--bg-surface-hover)] disabled:opacity-50"
              >
                <Paperclip className="h-4 w-4" />
              </button>

              <input
                type="text"
                placeholder="Спросите у Peeky..."
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && onSubmit()}
                disabled={media.length === 0 || isAnalyzing}
                className="min-w-0 flex-1 rounded-full bg-[var(--bg-surface)] px-4 py-2 text-sm text-white outline-none placeholder:text-[var(--text-placeholder)] disabled:opacity-50"
              />

              <button
                onClick={onSubmit}
                disabled={media.length === 0 || !prompt.trim() || isAnalyzing}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--bg-brand)] transition hover:bg-[var(--bg-brand-hover)] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            </div>

            {error && (
              <p className="mt-2 text-xs text-[var(--text-error)]">{error}</p>
            )}
          </div>
        </main>
      </div>

      {lightbox.isOpen && (
        <LightboxModal
          images={lightbox.images}
          currentIndex={lightbox.currentIndex}
          onClose={closeLightbox}
          onNavigate={navigateLightbox}
        />
      )}
    </section>
  );
}