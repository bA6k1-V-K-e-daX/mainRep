const API_BASE_URL = "/api";

/**
 * Выполняет HTTP-запрос и возвращает JSON.
 * @param {string} path
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
const request = async (path, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json();
};

/**
 * Получает тестовое сообщение с бэкенда.
 * @returns {Promise<{message: string}>}
 */
export const getHelloMessage = () => request("/hello");

export const register = (data) =>
  request("/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const login = async (data) => {
  const response = await fetch(`${API_BASE_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json();
};

