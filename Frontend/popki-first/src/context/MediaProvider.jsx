import { useCallback, useEffect, useMemo, useState } from "react";
import { MediaContext } from "./MediaContext";
import {
  analyzeMediaRequest,
  downloadResultsRequest,
} from "../api/workspaceApi";

const INITIAL_CHATS = [
  { id: "chat-1", title: "Горы" },
  { id: "chat-2", title: "Коты и собаки" },
  { id: "chat-3", title: "Котопсы и человеки" },
];

const buildMediaPayload = (file) => ({
  id: crypto.randomUUID(),
  file,
  name: file.name,
  size: file.size,
  mimeType: file.type,
  url: URL.createObjectURL(file),
  kind: file.type.startsWith("video/") ? "video" : "image",
});

export const MediaProvider = ({ children }) => {
  const [chats, setChats] = useState(INITIAL_CHATS);
  const [activeChatId, setActiveChatId] = useState(
    INITIAL_CHATS[0]?.id ?? null,
  );
  const [media, setMedia] = useState(null);
  const [results, setResults] = useState([]);
  const [timelineFrames, setTimelineFrames] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState("");

  const uploadMedia = useCallback((file) => {
    if (!file) return;

    setMedia((prevMedia) => {
      if (prevMedia?.url) {
        URL.revokeObjectURL(prevMedia.url);
      }
      return buildMediaPayload(file);
    });

    setResults([]);
    setTimelineFrames([]);
    setError("");
  }, []);

  const resetWorkspace = useCallback(() => {
    setMedia((prevMedia) => {
      if (prevMedia?.url) {
        URL.revokeObjectURL(prevMedia.url);
      }
      return null;
    });
    setResults([]);
    setTimelineFrames([]);
    setError("");
    setIsAnalyzing(false);
  }, []);

  const createNewChat = useCallback(() => {
    const nextIndex = chats.length + 1;
    const newChat = {
      id: `chat-${Date.now()}`,
      title: `Новый чат ${nextIndex}`,
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    resetWorkspace();
  }, [chats.length, resetWorkspace]);

  const submitPrompt = useCallback(
    async (prompt) => {
      if (!prompt?.trim() || !media || isAnalyzing) return;

      setIsAnalyzing(true);
      setError("");

      try {
        const response = await analyzeMediaRequest({
          chatId: activeChatId,
          media,
          prompt,
        });
        setResults(response.results ?? []);
        setTimelineFrames(response.timelineFrames ?? []);
      } catch {
        setError(
          "Не удалось получить результат. Проверьте соединение и повторите.",
        );
      } finally {
        setIsAnalyzing(false);
      }
    },
    [activeChatId, isAnalyzing, media],
  );

  const downloadResults = useCallback(async () => {
    if (!results.length || isDownloading) return;

    setIsDownloading(true);
    try {
      await downloadResultsRequest({
        chatId: activeChatId,
        results,
      });
    } catch {
      setError("Скачать файлы пока не удалось. Попробуйте ещё раз.");
    } finally {
      setIsDownloading(false);
    }
  }, [activeChatId, isDownloading, results]);

  useEffect(
    () => () => {
      if (media?.url) {
        URL.revokeObjectURL(media.url);
      }
    },
    [media],
  );

  const value = useMemo(
    () => ({
      chats,
      activeChatId,
      setActiveChatId,
      createNewChat,
      media,
      uploadMedia,
      resetWorkspace,
      results,
      timelineFrames,
      submitPrompt,
      downloadResults,
      isAnalyzing,
      isDownloading,
      error,
    }),
    [
      chats,
      activeChatId,
      createNewChat,
      media,
      uploadMedia,
      resetWorkspace,
      results,
      timelineFrames,
      submitPrompt,
      downloadResults,
      isAnalyzing,
      isDownloading,
      error,
    ],
  );

  return (
    <MediaContext.Provider value={value}>{children}</MediaContext.Provider>
  );
};
