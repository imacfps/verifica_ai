import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import UploadPanel from "./UploadPanel.jsx";

describe("UploadPanel", () => {
  it("mostra a dropzone quando não há imagem selecionada", () => {
    render(
      <UploadPanel
        file={null}
        preview={null}
        status="idle"
        onFileSelected={vi.fn()}
        onAnalyze={vi.fn()}
        onReset={vi.fn()}
      />
    );
    expect(screen.getByText(/arraste uma imagem/i)).toBeInTheDocument();
  });

  it("desabilita o botão de análise sem arquivo selecionado", () => {
    render(
      <UploadPanel
        file={null}
        preview={null}
        status="idle"
        onFileSelected={vi.fn()}
        onAnalyze={vi.fn()}
        onReset={vi.fn()}
      />
    );
    expect(screen.getByRole("button", { name: /analisar imagem/i })).toBeDisabled();
  });
});
