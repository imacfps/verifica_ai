import Footer from "./components/Footer.jsx";
import Header from "./components/Header.jsx";
import UploadPanel from "./components/UploadPanel.jsx";
import VerdictPanel from "./components/VerdictPanel.jsx";
import { useImageAnalysis } from "./hooks/useImageAnalysis.js";

export default function App() {
  const { file, preview, status, result, error, loadFile, analyze, reset } = useImageAnalysis();

  return (
    <div className="shell">
      <Header />

      <main className="grid">
        <UploadPanel
          file={file}
          preview={preview}
          status={status}
          onFileSelected={loadFile}
          onAnalyze={analyze}
          onReset={reset}
        />
        <VerdictPanel status={status} result={result} error={error} />
      </main>

      <Footer />
    </div>
  );
}
