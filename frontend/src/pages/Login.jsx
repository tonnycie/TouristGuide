import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatError } from "../api/errors";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(formatError(err));
    }
  };

  return (
    <div className="card">
      <h2>Вход</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Потребителско име
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Парола
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Вход</button>
      </form>
    </div>
  );
}
