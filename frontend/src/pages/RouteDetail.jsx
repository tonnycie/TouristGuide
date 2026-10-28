import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../api/client";
import { formatError } from "../api/errors";
import { useAuth } from "../context/AuthContext";
import Stars from "../components/Stars";
import WaypointMap from "../components/WaypointMap";

export default function RouteDetail() {
  const { id } = useParams();
  const { username } = useAuth();
  const navigate = useNavigate();
  const [route, setRoute] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState("");
  const [text, setText] = useState("");
  const [rating, setRating] = useState(5);
  const [formError, setFormError] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const load = async () => {
    try {
      const [routeRes, reviewsRes] = await Promise.all([
        api.get(`/routes/${id}/`),
        api.get(`/routes/${id}/reviews/`),
      ]);
      setRoute(routeRes.data);
      setReviews(reviewsRes.data);
    } catch (err) {
      setError(formatError(err));
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, [id]);

  const submitReview = async (e) => {
    e.preventDefault();
    setFormError("");
    try {
      await api.post(`/routes/${id}/reviews/`, { text, rating: Number(rating) });
      setText("");
      setRating(5);
      await load();
    } catch (err) {
      setFormError(formatError(err));
    }
  };

  const deleteRoute = async () => {
    if (!window.confirm("Сигурни ли сте, че искате да изтриете маршрута? Това не може да се отмени.")) {
      return;
    }
    try {
      await api.delete(`/routes/${id}/`);
      navigate("/");
    } catch (err) {
      setDeleteError(formatError(err));
    }
  };

  if (error) return <p className="error">{error}</p>;
  if (!route) return <p>Зареждане...</p>;

  const isAuthor = username === route.author;
  const alreadyReviewed = reviews.some((r) => r.author === username);
  const photos = route.photos ?? [];

  return (
    <div>
      <Link to="/">← Всички маршрути</Link>
      <h1>{route.title}</h1>
      <p className="muted">
        Дестинация: {route.destination} · автор:{" "}
        <Link to={`/users/${route.author}`}>{route.author}</Link>
      </p>
      <p>
        <Stars value={route.average_rating} />{" "}
        <span className="muted">({route.reviews_count} отзива)</span>
      </p>

      {isAuthor && (
        <div className="actions">
          <Link to={`/routes/${route.id}/edit`} className="button-link">Редактирай</Link>{" "}
          <button type="button" className="danger" onClick={deleteRoute}>Изтрий маршрута</button>
          {deleteError && <p className="error">{deleteError}</p>}
        </div>
      )}

      <h3>Лични впечатления</h3>
      <p className="pre">{route.description || "Няма описание."}</p>

      <h3>Съвети за пътуване</h3>
      <p className="pre">{route.tips || "Няма съвети."}</p>

      <h3>Маршрут на картата</h3>
      <WaypointMap waypoints={route.waypoints} autoFit />

      {photos.length > 0 && (
        <>
          <h3>Снимки</h3>
          <div className="gallery">
            {photos.map((p) => (
              <a key={p.id} href={p.image} target="_blank" rel="noreferrer">
                <img src={p.image} alt={`Снимка към ${route.title}`} />
              </a>
            ))}
          </div>
        </>
      )}

      <h3>Междинни точки</h3>
      <ol>
        {route.waypoints.map((w) => (
          <li key={w.id}>
            {w.name}{" "}
            <span className="muted">
              ({w.latitude}, {w.longitude})
            </span>
          </li>
        ))}
      </ol>

      <h3>Отзиви</h3>
      {reviews.length === 0 && <p>Още няма отзиви.</p>}
      {reviews.map((r) => (
        <div key={r.id} className="review">
          <strong>{r.author}</strong> · <Stars value={r.rating} />
          <p className="pre">{r.text}</p>
          <span className="muted">
            {new Date(r.created_at).toLocaleDateString("bg-BG")}
          </span>
        </div>
      ))}

      {!username && (
        <p>
          <Link to="/login">Влезте</Link>, за да оставите отзив.
        </p>
      )}
      {isAuthor && (
        <p className="muted">Това е вашият маршрут, не можете да го оценявате.</p>
      )}
      {username && !isAuthor && alreadyReviewed && (
        <p className="muted">Вече сте оставили отзив за този маршрут.</p>
      )}
      {username && !isAuthor && !alreadyReviewed && (
        <form onSubmit={submitReview} className="review-form">
          <h4>Вашият отзив</h4>
          <label>
            Оценка
            <select value={rating} onChange={(e) => setRating(e.target.value)}>
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <label>
            Текст
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              required
            />
          </label>
          {formError && <p className="error">{formError}</p>}
          <button type="submit">Изпрати</button>
        </form>
      )}
    </div>
  );
}