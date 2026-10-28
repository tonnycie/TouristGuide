import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import api from "../api/client";
import { formatError } from "../api/errors";
import { useAuth } from "../context/AuthContext";
import WaypointMap from "../components/WaypointMap";

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const MAX_FILES = 10;

export default function PublishRoute() {
  const { username } = useAuth();
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [destination, setDestination] = useState("");
  const [description, setDescription] = useState("");
  const [tips, setTips] = useState("");
  const [waypoints, setWaypoints] = useState([]);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [createdId, setCreatedId] = useState(null);

  if (!username) return <Navigate to="/login" replace />;

  const addPoint = (lat, lng) => {
    setWaypoints((prev) => [
      ...prev,
      { name: `Точка ${prev.length + 1}`, latitude: lat, longitude: lng },
    ]);
  };

  const renameWaypoint = (index, name) => {
    setWaypoints((prev) => prev.map((w, i) => (i === index ? { ...w, name } : w)));
  };

  const removeWaypoint = (index) => {
    setWaypoints((prev) => prev.filter((_, i) => i !== index));
  };

  const moveWaypoint = (index, delta) => {
    setWaypoints((prev) => {
      const target = index + delta;
      if (target < 0 || target >= prev.length) return prev;
      const next = [...prev];
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  };

  const handleFiles = (e) => {
    const selected = Array.from(e.target.files);
    const tooBig = selected.find((f) => f.size > MAX_FILE_SIZE);
    if (tooBig) {
      setError(`"${tooBig.name}" е над 5 MB.`);
      e.target.value = "";
      return;
    }
    if (selected.length > MAX_FILES) {
      setError(`Максимум ${MAX_FILES} снимки.`);
      e.target.value = "";
      return;
    }
    setError("");
    setFiles(selected);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (waypoints.length === 0) {
      setError("Добавете поне една точка, като кликнете върху картата.");
      return;
    }
    setSaving(true);
    try {
      const payload = {
        title,
        destination,
        description,
        tips,
        waypoints: waypoints.map((w) => ({
          name: w.name,
          latitude: w.latitude.toFixed(6), // бекендът пази 6 знака след запетаята
          longitude: w.longitude.toFixed(6),
        })),
      };
      const { data: route } = await api.post("/routes/", payload);

      const failed = [];
      for (const file of files) {
        const form = new FormData();
        form.append("image", file);
        try {
          await api.post(`/routes/${route.id}/photos/`, form);
        } catch {
          failed.push(file.name);
        }
      }

      if (failed.length > 0) {
        setError(`Маршрутът е публикуван, но не се качиха: ${failed.join(", ")}.`);
        setCreatedId(route.id);
      } else {
        navigate(`/routes/${route.id}`);
      }
    } catch (err) {
      setError(formatError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="publish-form">
      <h2>Публикуване на маршрут</h2>

      <label className="field">
        Заглавие
        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label className="field">
        Дестинация
        <input
          type="text"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          required
        />
      </label>
      <label className="field">
        Лични впечатления
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} />
      </label>
      <label className="field">
        Съвети за пътуване
        <textarea value={tips} onChange={(e) => setTips(e.target.value)} rows={3} />
      </label>

      <h3>Маршрут на картата</h3>
      <p className="muted">
        Кликнете върху картата, за да добавите точка. Редът на точките е редът на маршрута.
      </p>
      <WaypointMap waypoints={waypoints} onAddPoint={addPoint} />

      <ol className="waypoint-list">
        {waypoints.map((w, i) => (
          <li key={i}>
            <input
              type="text"
              value={w.name}
              onChange={(e) => renameWaypoint(i, e.target.value)}
              required
            />
            <span className="muted">
              {w.latitude.toFixed(4)}, {w.longitude.toFixed(4)}
            </span>{" "}
            <button type="button" onClick={() => moveWaypoint(i, -1)}>Горе</button>{" "}
            <button type="button" onClick={() => moveWaypoint(i, 1)}>Долу</button>{" "}
            <button type="button" onClick={() => removeWaypoint(i)}>Махни</button>
          </li>
        ))}
      </ol>

      <label className="field">
        Снимки (по желание, до 10, всяка до 5 MB; JPEG, PNG или WebP)
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          onChange={handleFiles}
        />
      </label>

      {error && <p className="error">{error}</p>}
      {createdId && <Link to={`/routes/${createdId}`}>Към публикувания маршрут</Link>}
      <div>
        <button type="submit" disabled={saving || createdId !== null}>
          {saving ? "Публикуване..." : "Публикувай"}
        </button>
      </div>
    </form>
  );
}
