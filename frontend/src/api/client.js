import axios from "axios";

const api = axios.create({ baseURL: "http://127.0.0.1:8000/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ако токенът е изтекъл: изчистваме входа и пращаме към страницата за вход
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const expired = error.response?.data?.code === "token_not_valid";
    if (expired && localStorage.getItem("access")) {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("username");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;