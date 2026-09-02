import { useRef, useState } from "react";

export default function UploadPanel({ file, preview, status, onFileSelected, onAnalyze, onReset }) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  return (
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
            onFileSelected(e.dataTransfer.files[0]);
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
        onChange={(e) => onFileSelected(e.target.files[0])}
      />

      <div className="actions">
        <button
          className="btn btn--primary"
          onClick={onAnalyze}
          disabled={!file || status === "analyzing"}
        >
          {status === "analyzing" ? "Analisando…" : "Analisar imagem"}
        </button>
        {file && (
          <button className="btn btn--ghost" onClick={onReset}>
            Limpar
          </button>
        )}
      </div>
    </section>
  );
}
