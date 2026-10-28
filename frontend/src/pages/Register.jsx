import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatError } from "../api/errors";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Паролите не съвпадат.");
      return;
    }
    try {
      await register(username, email, password);
      navigate("/");
    } catch (err) {
      setError(formatError(err));
    }
  };

  return (
    <div className="card">
      <h2>Регистрация</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Потребителско име
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Имейл
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
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
        <label>
          Повторете паролата
          <input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Регистрация</button>
      </form>
    </div>
  );
}