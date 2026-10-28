import { createContext, useContext, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [username, setUsername] = useState(() => localStorage.getItem("username"));

  const login = async (usernameInput, password) => {
    const { data } = await api.post("/auth/login/", {
      username: usernameInput,
      password,
    });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("username", usernameInput);
    setUsername(usernameInput);
  };

  const register = async (usernameInput, email, password) => {
    await api.post("/auth/register/", {
      username: usernameInput,
      email,
      password,
    });
    await login(usernameInput, password); // след регистрация влизаме автоматично
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    setUsername(null);
  };

  return (
    <AuthContext.Provider value={{ username, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);