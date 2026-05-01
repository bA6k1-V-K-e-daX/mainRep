const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

/**
 * Анализ файлов с отправкой промпта на реальный бекенд.
 * Отправляет multipart/form-data с payload (JSON) и массивом файлов.
 */
export const analyzeMediaRequest = async ({ media, files, prompt }) => {
  const formData = new FormData();
  formData.append("payload", JSON.stringify({ prompt }));
  files.forEach((file) => {
    formData.append("files", file.file);
  });

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

  const results = (data.entries || []).map((entry, index) => {
    const resultUrl = entry.overlay_url
      ? `${API_BASE_URL}${entry.overlay_url}`
      : entry.boxes_url
      ? `${API_BASE_URL}${entry.boxes_url}`
      : files[0]?.url;

    return {
      id: `result-${index}`,
      type: entry.detections?.length ? getDetectionType(entry.detections) : "без результатов",
      folder: entry.filename,
      img: resultUrl,
    };
  });

  return { results, timelineFrames: [] };
};

const getDetectionType = (detections) => {
  const hasSegmentation = detections.some((d) => d.class.includes("seg") || d.class.includes("mask"));
  return hasSegmentation ? "сегментация" : "детекция";
};

/**
 * Скачивание результатов - создаёт zip со всеми файлами.
 */
export const downloadResultsRequest = async ({ results }) => {
  const link = document.createElement("a");
  link.href = results[0]?.img;
  link.download = "detection-results.zip";
  link.click();
};
