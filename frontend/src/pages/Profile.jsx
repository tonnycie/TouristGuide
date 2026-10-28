import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import { formatError } from "../api/errors";
import RouteCard from "../components/RouteCard";

export default function Profile() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    setProfile(null);
    setError("");
    Promise.all([
      api.get(`/users/${encodeURIComponent(username)}/`),
      api.get("/routes/", { params: { author: username } }),
    ])
      .then(([profileRes, routesRes]) => {
        setProfile(profileRes.data);
        setRoutes(routesRes.data);
      })
      .catch((err) =>
        setError(
          err.response?.status === 404
            ? "Потребителят не съществува."
            : formatError(err)
        )
      );
  }, [username]);

  if (error) return <p className="error">{error}</p>;
  if (!profile) return <p>Зареждане...</p>;

  return (
    <div>
      <h1>{profile.username}</h1>
      <p className="muted">
        Регистриран на {new Date(profile.date_joined).toLocaleDateString("bg-BG")} ·{" "}
        {profile.routes_count} маршрута · {profile.reviews_count} отзива
      </p>

      <h2>Маршрути</h2>
      {routes.length === 0 ? (
        <p>Този потребител още не е публикувал маршрути.</p>
      ) : (
        routes.map((route) => <RouteCard key={route.id} route={route} />)
      )}
    </div>
  );
}