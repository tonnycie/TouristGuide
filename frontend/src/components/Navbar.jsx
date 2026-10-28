import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { username, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="brand">Туристически пътеводител</Link>
      <div>
        {username ? (
          <>
            <Link to="/publish">Публикувай маршрут</Link>
            <span>Здравей, {username}</span>
            <button onClick={handleLogout}>Изход</button>
          </>
        ) : (
          <>
            <Link to="/login">Вход</Link>
            <Link to="/register">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  );
}