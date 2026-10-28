import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import api from "../api/client";
import { formatError } from "../api/errors";
import { useAuth } from "../context/AuthContext";
import WaypointMap from "../components/WaypointMap";

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const MAX_FILES = 10;

export default function PublishRoute() {
  const { id } = useParams(); // има стойност само при редакция
  const isEdit = Boolean(id);
  const { username } = useAuth();
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [destination, setDestination] = useState("");
  const [description, setDescription] = useState("");
  const [tips, setTips] = useState("");
  const [waypoints, setWaypoints] = useState([]);
  const [existingPhotos, setExistingPhotos] = useState([]);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [createdId, setCreatedId] = useState(null);
  const [loading, setLoading] = useState(isEdit);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    if (!isEdit || !username) return;
    api
      .get(`/routes/${id}/`)
      .then(({ data }) => {
        if (data.author !== username) {
          setLoadError("Можете да редактирате само собствените си маршрути.");
          return;
        }
        setTitle(data.title);
        setDestination(data.destination);
        setDescription(data.description);
        setTips(data.tips);
        setWaypoints(
          data.waypoints.map((w) => ({
            name: w.name,
            latitude: Number(w.latitude),
            longitude: Number(w.longitude),
          }))
        );
        setExistingPhotos(data.photos ?? []);
      })
      .catch((err) =>
        setLoadError(err.response?.status === 404 ? "Маршрутът не съществува." : formatError(err))
      )
      .finally(() => setLoading(false));
  }, [id, isEdit, username]);

  if (!username) return <Navigate to="/login" replace />;
  if (loading) return <p>Зареждане...</p>;
  if (loadError) return <p className="error">{loadError}</p>;

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

  const removePhoto = async (photoId) => {
    if (!window.confirm("Да изтрия ли снимката?")) return;
    try {
      await api.delete(`/routes/${id}/photos/${photoId}/`);
      setExistingPhotos((prev) => prev.filter((p) => p.id !== photoId));
    } catch (err) {
      setError(formatError(err));
    }
  };

  const handleFiles = (e) => {
    const selected = Array.from(e.target.files);
    const tooBig = selected.find((f) => f.size > MAX_FILE_SIZE);
    if (tooBig) {
      setError(`"${tooBig.name}" е над 5 MB.`);
      e.target.value = "";
      return;
    }
    if (existingPhotos.length + selected.length > MAX_FILES) {
      setError(`Максимум ${MAX_FILES} снимки на маршрут.`);
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
          latitude: w.latitude.toFixed(6),
          longitude: w.longitude.toFixed(6),
        })),
      };
      const { data: route } = isEdit
        ? await api.put(`/routes/${id}/`, payload)
        : await api.post("/routes/", payload);

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
        setError(`Маршрутът е записан, но не се качиха: ${failed.join(", ")}.`);
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
      <h2>{isEdit ? "Редакция на маршрут" : "Публикуване на маршрут"}</h2>

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
      <WaypointMap waypoints={waypoints} onAddPoint={addPoint} autoFit={isEdit} />

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

      {isEdit && existingPhotos.length > 0 && (
        <>
          <h3>Текущи снимки</h3>
          <div className="gallery">
            {existingPhotos.map((p) => (
              <div key={p.id} className="gallery-item">
                <img src={p.image} alt="" />
                <button type="button" onClick={() => removePhoto(p.id)}>Изтрий</button>
              </div>
            ))}
          </div>
        </>
      )}

      <label className="field">
        {isEdit ? "Добавяне на снимки" : "Снимки"} (по желание, всяка до 5 MB; JPEG, PNG или WebP)
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          onChange={handleFiles}
        />
      </label>

      {error && <p className="error">{error}</p>}
      {createdId && <Link to={`/routes/${createdId}`}>Към маршрута</Link>}
      <div>
        <button type="submit" disabled={saving || createdId !== null}>
          {saving ? "Запазване..." : isEdit ? "Запази промените" : "Публикувай"}
        </button>
      </div>
    </form>
  );
}