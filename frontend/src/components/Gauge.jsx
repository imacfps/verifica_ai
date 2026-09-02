export default function Gauge({ probAI }) {
  const percent = (probAI * 100).toFixed(1);

  return (
    <div className="gauge" aria-label={`Probabilidade de IA: ${percent}%`}>
      <div className="gauge-track">
        <div className="gauge-needle" style={{ left: `${probAI * 100}%` }} />
      </div>
      <div className="gauge-labels">
        <span>real</span>
        <span>ia</span>
      </div>
    </div>
  );
}
