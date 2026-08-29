import { useCallback, useRef, useState } from "react";

const API_URL = "/api/analyze"; // proxy do Vite -> http://localhost:8000/analyze

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | analyzing | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const loadFile = useCallback((f) => {
    if (!f || !f.type.startsWith("image/")) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
    setStatus("idle");
  }, []);

  const analyze = async () => {
    if (!file) return;
    setStatus("analyzing");
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(API_URL, { method: "POST", body: form });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Erro ${res.status} na API`);
      }
      const data = await res.json();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setStatus("idle");
  };

  const probAI = result ? result.prob_ai : null;
  const isAI = probAI !== null && probAI >= 0.5;

  return (
    <div className="shell">
      <header className="header">
        <p className="eyebrow">TCC · Engenharia da Computação</p>
        <h1 className="title">Verifica.AI</h1>
        <p className="subtitle">
          Análise probabilística de imagens: real ou gerada por IA
        </p>
      </header>

      <main className="grid">
        {/* ── Painel de entrada ─────────────────────────── */}
        <section className="panel">
          <p className="panel-label">Entrada</p>

          {!preview ? (
            <div
              className={`dropzone ${dragOver ? "dropzone--over" : ""}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                loadFile(e.dataTransfer.files[0]);
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
            >
              <span className="dropzone-icon">⊹</span>
              <p>Arraste uma imagem ou clique para selecionar</p>
              <p className="dropzone-hint">JPEG · PNG · WebP · até 10 MB</p>
            </div>
          ) : (
            <div className="preview-wrap">
              <div className={`preview ${status === "analyzing" ? "preview--scanning" : ""}`}>
                <img src={preview} alt="Imagem selecionada para análise" />
                {status === "analyzing" && <div className="scanline" />}
              </div>
              <p className="filename">{file?.name}</p>
            </div>
          )}

          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            hidden
            onChange={(e) => loadFile(e.target.files[0])}
          />

          <div className="actions">
            <button
              className="btn btn--primary"
              onClick={analyze}
              disabled={!file || status === "analyzing"}
            >
              {status === "analyzing" ? "Analisando…" : "Analisar imagem"}
            </button>
            {file && (
              <button className="btn btn--ghost" onClick={reset}>
                Limpar
              </button>
            )}
          </div>
        </section>

        {/* ── Painel de veredito ────────────────────────── */}
        <section className="panel">
          <p className="panel-label">Veredito</p>

          {status === "done" && result ? (
            <div className="verdict">
              <p className={`verdict-tag ${isAI ? "tag--ai" : "tag--real"}`}>
                {isAI ? "Provável geração por IA" : "Provável imagem real"}
              </p>

              <p className="verdict-number">
                {(probAI * 100).toFixed(1)}
                <span className="verdict-unit">% IA</span>
              </p>

              {/* Espectro REAL ←→ IA com agulha de medição */}
              <div className="gauge" aria-label={`Probabilidade de IA: ${(probAI * 100).toFixed(1)}%`}>
                <div className="gauge-track">
                  <div className="gauge-needle" style={{ left: `${probAI * 100}%` }} />
                </div>
                <div className="gauge-labels">
                  <span>real</span>
                  <span>ia</span>
                </div>
              </div>

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
          ) : status === "error" ? (
            <div className="empty">
              <p className="error-msg">{error}</p>
              <p className="empty-hint">
                Verifique se a API está rodando em localhost:8000 e tente novamente.
              </p>
            </div>
          ) : (
            <div className="empty">
              <p>Nenhuma análise ainda.</p>
              <p className="empty-hint">
                Envie uma imagem e clique em “Analisar imagem” para ver a
                probabilidade estimada.
              </p>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>
          Resultado probabilístico — não constitui prova de autenticidade.
          Protótipo acadêmico.
        </p>
      </footer>
    </div>
  );
}
