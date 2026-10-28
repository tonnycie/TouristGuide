import { Link } from "react-router-dom";
import Stars from "./Stars";

export default function RouteCard({ route }) {
  return (
    <div className="route-card">
      <h3>
        <Link to={`/routes/${route.id}`}>{route.title}</Link>
      </h3>
      <p className="muted">
        Дестинация: {route.destination} · автор:{" "}
        <Link to={`/users/${route.author}`}>{route.author}</Link>
      </p>
      <p>
        <Stars value={route.average_rating} />{" "}
        <span className="muted">({route.reviews_count} отзива)</span>
      </p>
      <p className="muted">
        {route.waypoints.length} точки ·{" "}
        {new Date(route.created_at).toLocaleDateString("bg-BG")}
      </p>
    </div>
  );
}