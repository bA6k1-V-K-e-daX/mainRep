// src/context/MediaProvider.jsx
import { useState } from "react";
import { MediaContext } from "./MediaContext"; // Импортируем сам контекст из соседнего файла

// Этот файл экспортирует ТОЛЬКО React-компонент, Vite будет доволен
export const MediaProvider = ({ children }) => {
  const [media, setMedia] = useState(null); // { file, url, name }
  const [results, setResults] = useState([]); // Массив результатов с бэкенда
  const [isLoading, setIsLoading] = useState(false);

  // Имитация отправки промпта на бэкенд
  const handlePromptSubmit = async (prompt) => {
    if (!prompt || !media) return;
    setIsLoading(true);

    setTimeout(() => {
      const mockBackendResponse = [
        {
          id: 1,
          type: "детекция",
          folder: "Коты",
          img: "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=300&q=80",
        },
        {
          id: 2,
          type: "сегментация",
          folder: "Коты",
          img: "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=300&q=80",
        },
        {
          id: 3,
          type: "кадры",
          folder: "Коты",
          img: "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=300&q=80",
        },
      ];
      setResults(mockBackendResponse);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <MediaContext.Provider
      value={{ media, setMedia, results, handlePromptSubmit, isLoading }}
    >
      {children}
    </MediaContext.Provider>
  );
};
