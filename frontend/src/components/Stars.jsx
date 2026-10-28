export default function Stars({ value }) {
  if (value == null) return <span className="muted">Още няма оценки</span>;
  const full = Math.round(value);
  return (
    <span title={`${value} от 5`}>
      <span className="stars">{"★".repeat(full)}{"☆".repeat(5 - full)}</span> {value}
    </span>
  );
}