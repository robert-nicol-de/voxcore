export default function RiskIndicator({ level }) {
  const colors = {
    low: "green",
    medium: "orange",
    high: "red",
  };

  return (
    <span className={`risk ${colors[level]}`}>
      {level.toUpperCase()}
    </span>
  );
}
