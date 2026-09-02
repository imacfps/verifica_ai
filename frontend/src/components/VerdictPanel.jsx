import Gauge from "./Gauge.jsx";

export default function VerdictPanel({ status, result, error }) {
  return (
    <section className="panel">
      <p className="panel-label">Veredito</p>

      {status === "done" && result ? (
        <VerdictReady result={result} />
      ) : status === "error" ? (
        <div className="empty">
          <p className="error-msg">{error}</p>
          <p className="empty-hint">
            Verifique se a API está rodando e tente novamente.
          </p>
        </div>
      ) : (
        <div className="empty">
          <p>Nenhuma análise ainda.</p>
          <p className="empty-hint">
            Envie uma imagem e clique em “Analisar imagem” para ver a probabilidade estimada.
          </p>
        </div>
      )}
    </section>
  );
}

function VerdictReady({ result }) {
  const probAI = result.prob_ai;
  const isAI = probAI >= 0.5;

  return (
    <div className="verdict">
      <p className={`verdict-tag ${isAI ? "tag--ai" : "tag--real"}`}>
        {isAI ? "Provável geração por IA" : "Provável imagem real"}
      </p>

      <p className="verdict-number">
        {(probAI * 100).toFixed(1)}
        <span className="verdict-unit">% IA</span>
      </p>

      <Gauge probAI={probAI} />

      <dl className="meta">
        <div>
          <dt>P(real)</dt>
          <dd>{(result.prob_real * 100).toFixed(1)}%</dd>
        </div>
        <div>
          <dt>P(IA)</dt>
          <dd>{(result.prob_ai * 100).toFixed(1)}%</dd>
        </div>
        <div>
          <dt>Modelo</dt>
          <dd>{result.model}</dd>
        </div>
      </dl>
    </div>
  );
}
