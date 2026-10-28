import { useEffect, useState } from "react";
import api from "../api/client";
import { formatError } from "../api/errors";
import RouteCard from "../components/RouteCard";

const EMPTY = { search: "", min_rating: "", ordering: "" };

export default function Home() {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState(EMPTY);
  const [applied, setApplied] = useState(EMPTY);

  useEffect(() => {
    setLoading(true);
    setError("");
    const params = Object.fromEntries(
      Object.entries(applied).filter(([, value]) => value !== "")
    );
    api
      .get("/routes/", { params })
      .then((res) => setRoutes(res.data))
      .catch((err) => setError(formatError(err)))
      .finally(() => setLoading(false));
  }, [applied]);

  const change = (field) => (e) => setFilters({ ...filters, [field]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    setApplied({ ...filters, search: filters.search.trim() });
  };

  const handleReset = () => {
    setFilters(EMPTY);
    setApplied(EMPTY);
  };

  const hasFilters = Object.values(applied).some((value) => value !== "");

  return (
    <div>
      <h1>Маршрути</h1>

      <form onSubmit={handleSubmit} className="filters">
        <input
          type="text"
          placeholder="Търсене по заглавие, дестинация или описание"
          value={filters.search}
          onChange={change("search")}
        />
        <select value={filters.min_rating} onChange={change("min_rating")}>
          <option value="">Всички оценки</option>
          <option value="4">4 и нагоре</option>
          <option value="3">3 и нагоре</option>
          <option value="2">2 и нагоре</option>
        </select>
        <select value={filters.ordering} onChange={change("ordering")}>
          <option value="">Най-нови</option>
          <option value="rating">Най-високо оценени</option>
        </select>
        <button type="submit">Търси</button>
        <button type="button" onClick={handleReset}>Изчисти</button>
      </form>

      {loading && <p>Зареждане...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && routes.length === 0 && (
        <p>{hasFilters ? "Няма резултати." : "Още няма публикувани маршрути."}</p>
      )}
      {!loading && routes.map((route) => <RouteCard key={route.id} route={route} />)}
    </div>
  );
}