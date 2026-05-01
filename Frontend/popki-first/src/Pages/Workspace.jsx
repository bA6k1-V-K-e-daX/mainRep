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
} from "lucide-react";
import { useMedia } from "../context/MediaContext";

export default function Workspace() {
  const {
    chats,
    activeChatId,
    setActiveChatId,
    createNewChat,
    media,
    uploadMedia,
    removeMedia,
    resetWorkspace,
    results,
    messages,
    submitPrompt,
    isAnalyzing,
    error,
  } = useMedia();
  const [prompt, setPrompt] = useState("");
  const messagesEndRef = useRef(null);

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

  const handleDownload = async () => {
    if (!results.length) return;

    results.forEach((result, i) => {
      const link = document.createElement("a");
      link.href = result.img;
      link.download = `${result.type}-${i + 1}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  };

  const renderMessage = (message) => {
    if (message.type === "user") {
      return (
        <div key={message.id} className="flex gap-3 justify-end">
          <div className="max-w-[70%] rounded-2xl bg-[#4C1DFF] px-4 py-3">
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
                    className="h-20 w-full rounded-lg object-cover"
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
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#4C1DFF] text-[10px]">
          P
        </div>
        <div className="max-w-[70%] rounded-2xl bg-[#1D1241] px-4 py-3">
          {message.prompt && (
            <p className="mb-2 text-sm text-[#D8D4F3]">{message.prompt}</p>
          )}
          {message.results && message.results.length > 0 && (
            <div className="grid grid-cols-2 gap-2">
              {message.results.map((result) => (
                <div key={result.id}>
                  {result.img ? (
                    <img
                      src={result.img}
                      alt={`${result.folder} ${result.type}`}
                      className="h-24 w-full rounded-lg object-cover"
                      onError={(e) => {
                        e.target.style.display = "none";
                      }}
                    />
                  ) : (
                    <div className="flex h-24 items-center justify-center rounded-lg bg-[#12092A]">
                      <span className="text-xs text-[#8F88B7]">
                        {result.folder}
                      </span>
                    </div>
                  )}
                  <div className="mt-1 flex items-center justify-between text-[10px]">
                    <span className="text-[#8F88B7] truncate">
                      {result.folder}
                    </span>
                    <span className="rounded bg-[#4C1DFF]/20 px-1.5 py-0.5 text-[#B8B2D8]">
                      {result.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <section className="flex h-screen w-full flex-col bg-[#080312] text-white">
      <div className="flex h-full min-h-0">
        <aside className="hidden w-60 min-w-0 flex-col border-r border-[#1B1236] bg-[#06010E] p-3 lg:flex">
          <div className="mb-4 flex items-center gap-2">
            <img
              src="/peeky-mini-logo.png"
              alt="Peeky logo"
              className="h-4 w-4"
            />
            <span className="text-lg font-light text-[#D8D4F3]">Peeky</span>
          </div>

          <button
            onClick={createNewChat}
            className="mb-4 flex h-8 items-center justify-between rounded-md bg-[#4C1DFF] px-3 text-xs transition hover:bg-[#5D33FF]"
          >
            <span>Новый чат</span>
            <Plus className="h-3.5 w-3.5" />
          </button>

          <p className="mb-2 text-[11px] text-[#7C739F]">Ваши чаты</p>
          <div className="flex-1 overflow-y-auto">
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

          <div className="mt-auto flex items-center gap-2 border-t border-[#1B1236] pt-3">
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-white/80 text-[10px] text-black">
              U
            </div>
            <span className="text-xs text-[#B0AACC]">User11</span>
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
                <MonitorPlay className="mb-4 h-20 w-20 text-[#A8A1CC]" />
                <p className="mb-6 whitespace-pre-line text-center text-[#A8A1CC]">
                  {isDragActive
                    ? "Отпустите файлы здесь..."
                    : "Выберите файлы\nили перетащите их сюда"}
                </p>
                <button
                  onClick={open}
                  className="h-8 rounded-md bg-[#4C1DFF] px-12 text-sm transition hover:bg-[#5D33FF]"
                >
                  Выбрать файлы
                </button>
              </div>
            ) : (
              <div className="space-y-4 pb-4">
                {messages.map(renderMessage)}
                {isAnalyzing && (
                  <div className="flex gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#4C1DFF] text-[10px]">
                      P
                    </div>
                    <div className="rounded-2xl bg-[#1D1241] px-4 py-3">
                      <p className="text-sm text-[#8F88B7]">
                        Идёт обработка файлов...
                      </p>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="border-t border-[#1B1236] bg-[#0B051A] p-3">
            {media.length > 0 && (
              <div className="mb-2 grid grid-cols-6 gap-2 overflow-x-auto pb-2">
                {media.map((file) => (
                  <div key={file.id} className="relative flex-shrink-0">
                    <img
                      src={file.url}
                      alt={file.name}
                      className="h-14 w-14 rounded-lg object-cover"
                    />
                    <button
                      onClick={() => removeMedia(file.id)}
                      className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-white"
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
                className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1D1241] transition hover:bg-[#251257] disabled:opacity-50"
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
                className="min-w-0 flex-1 rounded-full bg-[#1D1241] px-4 py-2 text-sm text-white outline-none placeholder:text-[#7C739F] disabled:opacity-50"
              />

              <button
                onClick={onSubmit}
                disabled={media.length === 0 || !prompt.trim() || isAnalyzing}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-[#4C1DFF] transition hover:bg-[#5D33FF] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            </div>

            {error && (
              <p className="mt-2 text-xs text-red-300">{error}</p>
            )}
          </div>
        </main>
      </div>
    </section>
  );
}