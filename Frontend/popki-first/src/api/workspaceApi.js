const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

/**
 * Анализ файла с отправкой промпта на реальный бекенд.
 * Отправляет multipart/form-data с payload (JSON) и файлами.
 */
export const analyzeMediaRequest = async ({ media, prompt }) => {
  const formData = new FormData();
  formData.append("payload", JSON.stringify({ prompt }));
  formData.append("files", media.file);

  const token = localStorage.getItem("auth_token");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(`${API_BASE_URL}/api/v1/detect`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Analyze request failed");
  }

  const data = await response.json();

  const results = (data.entries || []).map((entry, index) => ({
    id: `result-${index}`,
    type: entry.detections?.length ? "детекция" : "без результатов",
    folder: entry.filename,
    img: entry.overlay_url
      ? `${API_BASE_URL}${entry.overlay_url}`
      : entry.boxes_url
      ? `${API_BASE_URL}${entry.boxes_url}`
      : media.url,
  }));

  return { results, timelineFrames: [] };
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
