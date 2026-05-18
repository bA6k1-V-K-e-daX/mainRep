const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

/**
 * Adds auth token to URL as query parameter for <img> tag support.
 */
export const addTokenToUrl = (url) => {
  const token = localStorage.getItem("auth_token");
  if (!token || !url) return url;
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}token=${encodeURIComponent(token)}`;
};

/**
 * Анализ файлов с отправкой промпта на реальный бекенд.
 * Отправляет multipart/form-data с payload (JSON) и массивом файлов.
 */
export const analyzeMediaRequest = async ({ media, files, prompt, chatId, chatTitle }) => {
  const formData = new FormData();
  formData.append("payload", JSON.stringify({ prompt, chat_id: chatId, chat_title: chatTitle }));
  files.forEach((file) => {
    formData.append("files", file.file);
  });

  const token = localStorage.getItem("auth_token");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/detect`, {
      method: "POST",
      headers,
      body: formData,
      signal: AbortSignal.timeout(300000), // 5 minutes timeout
    });
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }

  if (!response.ok) {
    let errorText;
    try {
      errorText = await response.text();
    } catch {
      errorText = "Unknown error";
    }
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  let data;
  try {
    data = await response.json();
  } catch (err) {
    throw new Error(`Failed to parse response: ${err.message}`);
  }

  const results = [];
  (data.entries || []).forEach((entry, entryIndex) => {
    const hasOverlay = entry.overlay_url;
    const hasBoxes = entry.boxes_url;

    // Backend already returns full /results/... URLs
    // Add token to URLs for <img> tag support
    if (hasBoxes) {
      results.push({
        id: `result-${entryIndex}-detection`,
        type: entry.detections?.length ? "детекция" : "без результатов",
        folder: entry.filename,
        img: addTokenToUrl(cleanInvalidBlobUrls(entry.boxes_url)),
      });
    }

    if (hasOverlay) {
      results.push({
        id: `result-${entryIndex}-segmentation`,
        type: entry.detections?.length ? "сегментация" : "без результатов",
        folder: entry.filename,
        img: addTokenToUrl(cleanInvalidBlobUrls(entry.overlay_url)),
      });
    }

    if (!hasBoxes && !hasOverlay) {
      results.push({
        id: `result-${entryIndex}`,
        type: entry.detections?.length ? getDetectionType(entry.detections) : "без результатов",
        folder: entry.filename,
        img: null,
      });
    }
  });

  return {
    queryId: data.query_id,
    results,
    timelineFrames: []
  };
};

const getDetectionType = (detections) => {
  const hasSegmentation = detections.some((d) => d.class.includes("seg") || d.class.includes("mask"));
  return hasSegmentation ? "сегментация" : "детекция";
};

// Clean invalid blob URLs from old localStorage data
const cleanInvalidBlobUrls = (url) => {
  if (!url) return null;
  if (url.startsWith("blob:")) return null;
  return url;
};

import JSZip from "jszip";
import { saveAs } from "file-saver";

/**
 * Скачивание результатов - скачивает каждое изображение отдельно.
 */
export const downloadResultsRequest = async ({ results }) => {
  const validResults = results.filter((r) => r.img && !r.img.startsWith("blob:"));
  for (const result of validResults) {
    const link = document.createElement("a");
    link.href = result.img;
    link.download = `${result.type}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

/**
 * Скачивание архива со всеми изображениями и report.txt.
 */
export const downloadArchiveRequest = async ({ queryId, results }) => {
  const zip = new JSZip();

  // Добавляем изображения в архив
  const validResults = results.filter((r) => r.img && !r.img.startsWith("blob:"));
  console.log("downloadArchiveRequest: validResults count:", validResults.length, validResults.map(r => r.img));

  for (let i = 0; i < validResults.length; i++) {
    const result = validResults[i];
    try {
      // URL уже содержит токен как query параметр, не отправляем Authorization header
      // Handle relative URLs by prepending API_BASE_URL
      const imgUrl = result.img.startsWith("http")
        ? result.img
        : `${API_BASE_URL}${result.img}`;
      const response = await fetch(imgUrl);
      if (!response.ok) {
        console.error(`Failed to fetch image: ${response.status} ${imgUrl}`);
        continue; // Skip failed images instead of throwing
      }
      const blob = await response.blob();
      const fileName = result.img.split("/").pop()?.split("?")[0] || `image-${i}.png`;
      zip.file(fileName, blob);
      console.log("Added to zip:", fileName);
    } catch (err) {
      console.error("Error fetching image:", result.img, err);
    }
  }

  // Добавляем report.txt
  if (queryId) {
    const token = localStorage.getItem("auth_token");
    const reportUrl = `${API_BASE_URL}/results/${queryId}/result/report.txt${token ? `?token=${encodeURIComponent(token)}` : ""}`;
    try {
      const reportResponse = await fetch(reportUrl);
      if (reportResponse.ok) {
        const reportText = await reportResponse.text();
        zip.file("report.txt", reportText);
      }
    } catch (e) {
      console.log("Report not found:", reportUrl);
    }
  }

  const content = await zip.generateAsync({ type: "blob" });
  saveAs(content, `results-${queryId || Date.now()}.zip`);
};

const getAuthHeaders = () => {
  const token = localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const createChatRequest = async ({ title }) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/chats`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create chat: ${response.status}`);
  }

  const data = await response.json();
  return data.chat;
};

export const getChatsRequest = async () => {
  const response = await fetch(`${API_BASE_URL}/api/v1/chats`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get chats: ${response.status}`);
  }

  const data = await response.json();
  return data.chats || [];
};

export const getHistoryRequest = async ({ chatId, quantity = 20 }) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/history`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ chat_id: chatId, quantity }),
  });

  if (!response.ok) {
    throw new Error(`Failed to get history: ${response.status}`);
  }

  const data = await response.json();
  return data.queries || [];
};
