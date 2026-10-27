import { useState } from "react";
import api from "./api/client";

export default function App() {
  const [msg, setMsg] = useState("Още не е тествано");

  const test = async () => {
    try {
      await api.post("/auth/login/", { username: "nikoi", password: "greshna" });
      setMsg("Неочакван успех");
    } catch (err) {
      if (err.response) setMsg(`Връзката работи, сървърът отговори: ${err.response.status}`);
      else setMsg("Няма връзка (проверете сървъра и CORS)");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Туристически пътеводител</h1>
      <button onClick={test}>Тествай връзката с API</button>
      <p>{msg}</p>
    </div>
  );
}