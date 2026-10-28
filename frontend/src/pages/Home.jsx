import { useEffect, useState } from "react";
import api from "../api/client";
import { formatError } from "../api/errors";
import RouteCard from "../components/RouteCard";

export default function Home() {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/routes/")
      .then((res) => setRoutes(res.data))
      .catch((err) => setError(formatError(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Зареждане...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div>
      <h1>Маршрути</h1>
      {routes.length === 0 ? (
        <p>Още няма публикувани маршрути.</p>
      ) : (
        routes.map((route) => <RouteCard key={route.id} route={route} />)
      )}
    </div>
  );
}