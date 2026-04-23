// src/context/MediaContext.jsx
import { createContext, useContext } from "react";

// Экспортируем сам контекст (нужен для Провайдера)
export const MediaContext = createContext();

// Экспортируем хук (нужен для компонентов, чтобы получать данные)
export const useMedia = () => {
  const context = useContext(MediaContext);
  if (!context) {
    throw new Error("useMedia must be used within a MediaProvider");
  }
  return context;
};
