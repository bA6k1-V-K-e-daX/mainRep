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
  const [media, setMedia] = useState([]);
  const [results, setResults] = useState([]);
  const [timelineFrames, setTimelineFrames] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState("");

  const uploadMedia = useCallback((files) => {
    if (!files || files.length === 0) return;

    const newFiles = Array.from(files).map(buildMediaPayload);
    setMedia((prev) => [...prev, ...newFiles]);
    setResults([]);
    setTimelineFrames([]);
    setError("");
  }, []);

  const removeMedia = useCallback((id) => {
    setMedia((prev) => {
      const toRemove = prev.find((m) => m.id === id);
      if (toRemove?.url) URL.revokeObjectURL(toRemove.url);
      return prev.filter((m) => m.id !== id);
    });
  }, []);

  const resetWorkspace = useCallback(() => {
    setMedia((prev) => {
      prev.forEach((m) => {
        if (m.url) URL.revokeObjectURL(m.url);
      });
      return [];
    });
    setResults([]);
    setTimelineFrames([]);
    setMessages([]);
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
      if (!prompt?.trim() || media.length === 0 || isAnalyzing) return;

      setIsAnalyzing(true);
      setError("");

      const userMessage = {
        id: crypto.randomUUID(),
        type: "user",
        prompt,
        media: [...media],
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Очищаем media после отправки
      setMedia([]);

      try {
        const response = await analyzeMediaRequest({
          media: media[0],
          prompt,
          files: media,
        });

        const botMessage = {
          id: crypto.randomUUID(),
          type: "bot",
          results: response.results ?? [],
          prompt,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, botMessage]);

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
      media.forEach((m) => {
        if (m.url) URL.revokeObjectURL(m.url);
      });
    },
    [],
  );

  const value = useMemo(
    () => ({
      chats,
      activeChatId,
      setActiveChatId,
      createNewChat,
      media,
      uploadMedia,
      removeMedia,
      resetWorkspace,
      results,
      timelineFrames,
      messages,
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
      removeMedia,
      resetWorkspace,
      results,
      timelineFrames,
      messages,
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
