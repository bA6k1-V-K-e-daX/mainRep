import { useCallback, useEffect, useMemo, useState } from "react";
import { MediaContext } from "./MediaContext";
import {
  analyzeMediaRequest,
  downloadResultsRequest,
  downloadArchiveRequest,
} from "../api/workspaceApi";

const STORAGE_KEY = "peeky-chats-data";

const getInitialData = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch {}
  return {
    chats: [
      { id: "chat-1", title: "Горы" },
      { id: "chat-2", title: "Коты и собаки" },
      { id: "chat-3", title: "Котопсы и человеки" },
    ],
    activeChatId: "chat-1",
    messagesByChat: {
      "chat-1": [],
      "chat-2": [],
      "chat-3": [],
    },
  };
};

const buildMediaPayload = (file) => ({
  id: crypto.randomUUID(),
  file,
  name: file.name,
  size: file.size,
  mimeType: file.type,
  url: URL.createObjectURL(file),
  kind: file.type.startsWith("video/") ? "video" : "image",
});

const fileToBase64 = (file) =>
  new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.readAsDataURL(file);
  });

const serializeMediaForStorage = async (mediaFiles) => {
  const serialized = [];
  for (const m of mediaFiles) {
    const url = m.url;
    const isBlobUrl = url.startsWith("blob:");
    serialized.push({
      id: m.id,
      name: m.name,
      size: m.size,
      mimeType: m.mimeType,
      kind: m.kind,
      url: isBlobUrl ? await fileToBase64(m.file) : url,
    });
  }
  return serialized;
};

// Clean blob URLs from loaded messages (they become invalid after reload)
const cleanMessageMedia = (messages) => {
  if (!Array.isArray(messages)) return messages;
  return messages.map((msg) => {
    if (msg.media) {
      msg.media = msg.media.map((m) => ({ ...m, url: m.url?.startsWith("blob:") ? null : m.url }));
    }
    return msg;
  });
};

export const MediaProvider = ({ children }) => {
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messagesByChat, setMessagesByChat] = useState({});
  const [media, setMedia] = useState([]);
  const [results, setResults] = useState([]);
  const [queryId, setQueryId] = useState(null);
  const [timelineFrames, setTimelineFrames] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [filesCount, setFilesCount] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState("");

  // Load data from localStorage on mount
  useEffect(() => {
    const initial = getInitialData();
    setChats(initial.chats);
    setActiveChatId(initial.activeChatId);
    const cleanedMessages = {};
    for (const [id, msgs] of Object.entries(initial.messagesByChat)) {
      cleanedMessages[id] = cleanMessageMedia(msgs);
    }
    setMessagesByChat(cleanedMessages);
  }, []);

  // Save to localStorage whenever chats or messages change
  useEffect(() => {
    if (chats.length === 0) return;
    const data = {
      chats,
      activeChatId,
      messagesByChat,
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {}
  }, [chats, activeChatId, messagesByChat]);

  // Get current chat messages
  const messages = messagesByChat[activeChatId] || [];

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
    setError("");
  }, []);

  const createNewChat = useCallback(() => {
    const nextIndex = chats.length + 1;
    const newChat = {
      id: `chat-${Date.now()}`,
      title: `Новый чат ${nextIndex}`,
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    setMessagesByChat((prev) => ({
      ...prev,
      [newChat.id]: [],
    }));
    resetWorkspace();
  }, [chats.length, resetWorkspace]);

  // Switch chat - load messages for selected chat
  const handleSetActiveChatId = useCallback(
    (id) => {
      setActiveChatId(id);
      resetWorkspace();
    },
    [resetWorkspace],
  );

  const submitPrompt = useCallback(
    async (prompt) => {
      if (!prompt?.trim() || media.length === 0 || isAnalyzing) return;

      const filesToSend = [...media];
      setFilesCount(filesToSend.length);

      setIsAnalyzing(true);
      setError("");

      const userMessage = {
        id: crypto.randomUUID(),
        type: "user",
        prompt,
        media: await serializeMediaForStorage(filesToSend),
        timestamp: Date.now(),
      };

      setMessagesByChat((prev) => ({
        ...prev,
        [activeChatId]: [...(prev[activeChatId] || []), userMessage],
      }));

      // Очищаем media после отправки
      setMedia([]);

      try {
        const response = await analyzeMediaRequest({
          media: filesToSend[0],
          prompt,
          files: filesToSend,
        });

        const botMessage = {
          id: crypto.randomUUID(),
          type: "bot",
          results: response.results ?? [],
          prompt,
          timestamp: Date.now(),
        };

        setMessagesByChat((prev) => ({
          ...prev,
          [activeChatId]: [...(prev[activeChatId] || []), botMessage],
        }));

        setResults(response.results ?? []);
        setTimelineFrames(response.timelineFrames ?? []);
        setQueryId(response.queryId ?? null);
      } catch {
        setError(
          "Не удалось получить результат. Проверьте соединение и повторите.",
        );
      } finally {
        setIsAnalyzing(false);
        setFilesCount(0);
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

  const downloadArchive = useCallback(async () => {
    if (!results.length || isDownloading) return;

    setIsDownloading(true);
    setError("");
    try {
      await downloadArchiveRequest({ queryId, results });
    } catch (err) {
      console.error("Archive download error:", err);
      setError(`Ошибка скачивания: ${err.message || "Попробуйте ещё раз"}`);
    } finally {
      setIsDownloading(false);
    }
  }, [isDownloading, queryId, results]);

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
      setActiveChatId: handleSetActiveChatId,
      createNewChat,
      media,
      uploadMedia,
      removeMedia,
      resetWorkspace,
      results,
      queryId,
      timelineFrames,
      messages,
      submitPrompt,
      downloadResults,
      downloadArchive,
      isAnalyzing,
      filesCount,
      isDownloading,
      error,
    }),
    [
      chats,
      activeChatId,
      handleSetActiveChatId,
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
      filesCount,
      isDownloading,
      error,
    ],
  );

  return (
    <MediaContext.Provider value={value}>{children}</MediaContext.Provider>
  );
};