const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const USE_MOCK = (import.meta.env.VITE_USE_WORKSPACE_MOCK ?? "true") === "true";

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const buildMockResults = (mediaUrl) => [
  {
    id: "result-detection",
    type: "детекция",
    folder: "Коты",
    img: mediaUrl,
  },
  {
    id: "result-segmentation",
    type: "сегментация",
    folder: "Коты",
    img: mediaUrl,
  },
  {
    id: "result-frames",
    type: "кадры",
    folder: "Коты",
    img: mediaUrl,
  },
];

const buildMockFrames = (mediaUrl) =>
  Array.from({ length: 10 }, (_, index) => ({
    id: `frame-${index + 1}`,
    url: mediaUrl,
  }));

/**
 * Анализ файла с отправкой промпта.
 * Для интеграции с реальным бэкендом отключите мок:
 * VITE_USE_WORKSPACE_MOCK=false
 */
export const analyzeMediaRequest = async ({ chatId, media, prompt }) => {
  if (USE_MOCK) {
    await wait(1200);
    return {
      results: buildMockResults(media.url),
      timelineFrames: buildMockFrames(media.url),
    };
  }

  const formData = new FormData();
  formData.append("chatId", chatId ?? "");
  formData.append("prompt", prompt);
  formData.append("file", media.file);

  const response = await fetch(`${API_BASE_URL}/workspace/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Analyze request failed");
  }

  return response.json();
};

/**
 * Скачивание результатов (zip/file URL).
 * В mock-режиме просто имитируется успех.
 */
export const downloadResultsRequest = async ({ chatId, results }) => {
  if (USE_MOCK) {
    await wait(400);
    return;
  }

  const response = await fetch(`${API_BASE_URL}/workspace/download`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chatId,
      resultIds: results.map((item) => item.id),
    }),
  });

  if (!response.ok) {
    throw new Error("Download request failed");
  }
};
