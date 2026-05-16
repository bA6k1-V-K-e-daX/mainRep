import { useCallback, useEffect, useMemo, useState } from "react";
import { MediaContext } from "./MediaContext";
import {
  analyzeMediaRequest,
  downloadResultsRequest,
  downloadArchiveRequest,
  createChatRequest,
  getChatsRequest,
  getHistoryRequest,
  addTokenToUrl,
} from "../api/workspaceApi";

const STORAGE_KEY = "peeky-chats-data";
const PROCESSING_BY_CHAT_KEY = "peeky-processing-by-chat";

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
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState("");
  const [isLoadingChats, setIsLoadingChats] = useState(false);
  const [processingByChat, setProcessingByChat] = useState(() => {
    try {
      const stored = localStorage.getItem(PROCESSING_BY_CHAT_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        const now = Date.now();
        const filtered = {};
        for (const [chatId, status] of Object.entries(parsed)) {
          if (status.timestamp > now - 10 * 60 * 1000) {
            filtered[chatId] = status;
          }
        }
        return filtered;
      }
    } catch {}
    return {};
  });

  // Load chats from server on mount - restore from localStorage first
  useEffect(() => {
    const loadChats = async () => {
      setIsLoadingChats(true);
      try {
        // Try to restore from localStorage first
        const savedData = localStorage.getItem(STORAGE_KEY);
        let savedMessagesByChat = {};
        let savedActiveChatId = null;

        if (savedData) {
          try {
            const parsed = JSON.parse(savedData);
            savedMessagesByChat = parsed.messagesByChat || {};
            savedActiveChatId = parsed.activeChatId || null;
          } catch {}
        }

        const serverChats = await getChatsRequest();
        setChats(serverChats);

        if (serverChats.length > 0) {
          // Merge saved messages with server chats (only for chats that still exist)
          const chatIds = new Set(serverChats.map(c => c.id));
          const mergedMessages = {};
          for (const chat of serverChats) {
            mergedMessages[chat.id] = savedMessagesByChat[chat.id] || [];
          }
          setMessagesByChat(mergedMessages);

          // Use saved active chat if it still exists, otherwise first chat
          const activeId = savedActiveChatId && chatIds.has(savedActiveChatId)
            ? savedActiveChatId
            : serverChats[0].id;
          setActiveChatId(activeId);
        }
      } catch (err) {
        setError("Не удалось загрузить чаты");
      } finally {
        setIsLoadingChats(false);
      }
    };
    loadChats();
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

  // Save processingByChat to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(PROCESSING_BY_CHAT_KEY, JSON.stringify(processingByChat));
    } catch {}
  }, [processingByChat]);

  // Get current chat messages
  const messages = messagesByChat[activeChatId] || [];

  // Derive processing state from per-chat state
  const chatProcessingStatus = processingByChat[activeChatId];
  const isAnalyzingChat = !!chatProcessingStatus;
  const filesCountChat = chatProcessingStatus?.filesCount || 0;

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

  const createNewChat = useCallback(async () => {
    const nextIndex = chats.length + 1;
    const title = `Новый чат ${nextIndex}`;
    try {
      const newChat = await createChatRequest({ title });
      setChats((prev) => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      setMessagesByChat((prev) => ({
        ...prev,
        [newChat.id]: [],
      }));
      resetWorkspace();
    } catch (err) {
      setError("Не удалось создать чат");
    }
  }, [chats.length, resetWorkspace]);

  // Switch chat - load messages for selected chat
  const handleSetActiveChatId = useCallback(
    async (id) => {
      if (id === activeChatId) return;
      // Load history for the selected chat
      const existingMessages = messagesByChat[id];
      if (!existingMessages || existingMessages.length === 0) {
        try {
          const history = await getHistoryRequest({ chatId: id });
          const flattenedMessages = [];
          for (const query of history) {
            // Add user message
            flattenedMessages.push({
              id: `user-${query.query_id}`,
              type: "user",
              prompt: query.prompt || "",
              media: [],
              timestamp: query.query_id,
            });
            // Add bot messages for each entry - include both boxes and overlay results
            for (const entry of query.entries || []) {
              const results = [];

              if (entry.boxes_url || entry.boxesURL) {
                results.push({
                  id: `${crypto.randomUUID()}-detection`,
                  folder: entry.filename,
                  type: entry.detections?.length ? "детекция" : "без результатов",
                  img: addTokenToUrl(entry.boxes_url || entry.boxesURL),
                  detections: entry.detections || [],
                });
              }

              if (entry.overlay_url || entry.overlayURL) {
                results.push({
                  id: `${crypto.randomUUID()}-segmentation`,
                  folder: entry.filename,
                  type: entry.detections?.length ? "сегментация" : "без результатов",
                  img: addTokenToUrl(entry.overlay_url || entry.overlayURL),
                  detections: entry.detections || [],
                });
              }

              if (results.length > 0) {
                flattenedMessages.push({
                  id: `history-${query.query_id}-${entry.filename}`,
                  type: "bot",
                  results,
                  prompt: query.prompt || "",
                  timestamp: query.query_id,
                  filename: entry.filename,
                  queryId: query.query_id,
                });
              }
            }
          }
          setMessagesByChat((prev) => ({
            ...prev,
            [id]: flattenedMessages,
          }));
        } catch (err) {
          console.error("Failed to load history:", err);
        }
      }
      setActiveChatId(id);
      resetWorkspace();
    },
    [activeChatId, messagesByChat, resetWorkspace],
  );

  const submitPrompt = useCallback(
    async (prompt) => {
      if (!prompt?.trim() || media.length === 0 || isAnalyzingChat) return;

      const filesToSend = [...media];

      // Set processing state for this specific chat (useEffect will persist to localStorage)
      const processingEntry = { timestamp: Date.now(), filesCount: filesToSend.length };
      setProcessingByChat((prev) => ({
        ...prev,
        [activeChatId]: processingEntry,
      }));

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
        const activeChat = chats.find((c) => c.id === activeChatId);
        const response = await analyzeMediaRequest({
          media: filesToSend[0],
          prompt,
          files: filesToSend,
          chatId: activeChatId,
          chatTitle: activeChat?.title,
        });

        // Results already have img field from workspaceApi.js transformation
        const transformedResults = (response.results ?? []).map((r) => ({
          ...r,
        }));

        const botMessage = {
          id: crypto.randomUUID(),
          type: "bot",
          results: transformedResults,
          prompt,
          timestamp: Date.now(),
          queryId: response.queryId ?? null,
        };

        setMessagesByChat((prev) => ({
          ...prev,
          [activeChatId]: [...(prev[activeChatId] || []), botMessage],
        }));

        setResults(transformedResults);
        setTimelineFrames(response.timelineFrames ?? []);
        setQueryId(response.queryId ?? null);
      } catch {
        setError(
          "Не удалось получить результат. Проверьте соединение и повторите.",
        );
      } finally {
        // Clear processing state for this chat only (useEffect will persist to localStorage)
        setProcessingByChat((prev) => {
          const updated = { ...prev };
          delete updated[activeChatId];
          return updated;
        });
      }
    },
    [activeChatId, isAnalyzingChat, media, chats],
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

  const downloadArchive = useCallback(async (messageResults, messageQueryId) => {
    const r = messageResults || results;
    const qid = messageQueryId || queryId;
    if (!r.length || isDownloading) return;

    setIsDownloading(true);
    setError("");
    try {
      await downloadArchiveRequest({ queryId: qid, results: r });
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
      isAnalyzing: isAnalyzingChat,
      filesCount: filesCountChat,
      isDownloading,
      error,
      isLoadingChats,
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
      downloadArchive,
      isAnalyzingChat,
      filesCountChat,
      isDownloading,
      error,
      isLoadingChats,
    ],
  );

  return (
    <MediaContext.Provider value={value}>{children}</MediaContext.Provider>
  );
};