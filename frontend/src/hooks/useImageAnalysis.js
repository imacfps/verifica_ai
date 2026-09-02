import { useCallback, useEffect, useRef, useState } from "react";

import { ALLOWED_IMAGE_TYPES, MAX_UPLOAD_MB } from "../config.js";
import { analyzeImage } from "../services/api.js";

const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024;

export function useImageAnalysis() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | analyzing | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const previewUrlRef = useRef(null);

  // Evita vazamento de memória de object URLs entre trocas de imagem/unmount.
  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
      abortRef.current?.abort();
    };
  }, []);

  const loadFile = useCallback((candidate) => {
    if (!candidate) return;

    if (!ALLOWED_IMAGE_TYPES.includes(candidate.type)) {
      setError("Formato não suportado. Use JPEG, PNG ou WebP.");
      setStatus("error");
      return;
    }
    if (candidate.size > MAX_UPLOAD_BYTES) {
      setError(`Imagem excede ${MAX_UPLOAD_MB} MB.`);
      setStatus("error");
      return;
    }

    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    const url = URL.createObjectURL(candidate);
    previewUrlRef.current = url;

    setFile(candidate);
    setPreview(url);
    setResult(null);
    setError(null);
    setStatus("idle");
  }, []);

  const analyze = useCallback(async () => {
    if (!file) return;
    setStatus("analyzing");
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const data = await analyzeImage(file, { signal: controller.signal });
      setResult(data);
      setStatus("done");
    } catch (err) {
      if (err.name === "AbortError") return;
      setError(err.message);
      setStatus("error");
    }
  }, [file]);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    previewUrlRef.current = null;
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setStatus("idle");
  }, []);

  return { file, preview, status, result, error, loadFile, analyze, reset };
}
