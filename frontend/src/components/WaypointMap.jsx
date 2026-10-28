import { useEffect } from "react";
import L from "leaflet";
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// поправка: със Vite иконките на маркерите иначе не се зареждат
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

function ClickHandler({ onAddPoint }) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng.wrap(); // държи дължината между -180 и 180
      onAddPoint(lat, lng);
    },
  });
  return null;
}

function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 1) map.setView(points[0], 10);
    else if (points.length > 1) map.fitBounds(points, { padding: [30, 30] });
  }, [map, points.length]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

export default function WaypointMap({ waypoints, onAddPoint, autoFit = false }) {
  const points = waypoints.map((w) => [Number(w.latitude), Number(w.longitude)]);

  return (
    <MapContainer
      center={points[0] || [42.7, 25.3]}
      zoom={points.length ? 8 : 7}
      className="map"
      scrollWheelZoom
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {onAddPoint && <ClickHandler onAddPoint={onAddPoint} />}
      {autoFit && <FitBounds points={points} />}
      {points.length > 1 && <Polyline positions={points} />}
      {waypoints.map((w, i) => (
        <Marker key={i} position={points[i]}>
          <Popup>
            {i + 1}. {w.name}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}