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
    if (hasBoxes) {
      results.push({
        id: `result-${entryIndex}-detection`,
        type: entry.detections?.length ? "детекция" : "без результатов",
        folder: entry.filename,
        img: cleanInvalidBlobUrls(entry.boxes_url),
      });
    }

    if (hasOverlay) {
      results.push({
        id: `result-${entryIndex}-segmentation`,
        type: entry.detections?.length ? "сегментация" : "без результатов",
        folder: entry.filename,
        img: cleanInvalidBlobUrls(entry.overlay_url),
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
  const token = localStorage.getItem("auth_token");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  // Добавляем изображения в архив
  const validResults = results.filter((r) => r.img && !r.img.startsWith("blob:"));
  for (let i = 0; i < validResults.length; i++) {
    const result = validResults[i];
    try {
      const response = await fetch(result.img, { headers, credentials: "include" });
      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.status} ${result.img}`);
      }
      const blob = await response.blob();
      const fileName = result.img.split("/").pop() || `image-${i}.png`;
      zip.file(fileName, blob);
    } catch (err) {
      console.error("Error fetching image:", result.img, err);
      throw new Error(`Ошибка загрузки изображения: ${err.message}`);
    }
  }

  // Добавляем report.txt
  if (queryId) {
    const reportUrl = `/results/${queryId}/result/report.txt`;
    try {
      const reportResponse = await fetch(reportUrl, { headers, credentials: "include" });
      if (reportResponse.ok) {
        const reportText = await reportResponse.text();
        zip.file("report.txt", reportText);
      }
    } catch (e) {
      // report.txt may not exist
      console.log("Report not found:", reportUrl);
    }
  }

  const content = await zip.generateAsync({ type: "blob" });
  saveAs(content, `results-${queryId || Date.now()}.zip`);
};
