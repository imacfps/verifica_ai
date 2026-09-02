// Service worker (Manifest V3): menu de contexto em <img> -> POST /v1/analyze -> notificação.

const DEFAULT_API_URL = "http://localhost:8000";
const CONTEXT_MENU_ID = "verifica-ai-analyze";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: CONTEXT_MENU_ID,
    title: "Verificar com Verifica.AI",
    contexts: ["image"],
  });
});

chrome.action.onClicked.addListener(() => {
  chrome.runtime.openOptionsPage();
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === CONTEXT_MENU_ID && info.srcUrl) {
    analyzeImage(info.srcUrl);
  }
});

async function getApiUrl() {
  const { apiUrl } = await chrome.storage.sync.get("apiUrl");
  return (apiUrl || DEFAULT_API_URL).replace(/\/+$/, "");
}

async function analyzeImage(srcUrl) {
  try {
    const imageResponse = await fetch(srcUrl);
    if (!imageResponse.ok) {
      throw new Error(`Não foi possível baixar a imagem (HTTP ${imageResponse.status}).`);
    }
    const imageBlob = await imageResponse.blob();

    const apiUrl = await getApiUrl();
    const formData = new FormData();
    formData.append("file", imageBlob, "image");

    const response = await fetch(`${apiUrl}/v1/analyze`, {
      method: "POST",
      body: formData,
    });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(payload?.detail || `Erro HTTP ${response.status} ao consultar a API.`);
    }

    notifyResult(payload);
  } catch (error) {
    notifyError(error);
  }
}

function notifyResult(result) {
  const isAi = result.label === "ai-generated";
  const confidence = Math.round((isAi ? result.prob_ai : result.prob_real) * 100);
  const title = isAi ? "Provavelmente gerada por IA" : "Provavelmente real";

  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title: `Verifica.AI — ${title}`,
    message: `${confidence}% de confiança (modelo: ${result.model})`,
  });
}

function notifyError(error) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title: "Verifica.AI — falha na análise",
    message: error.message || "Erro desconhecido ao analisar a imagem.",
  });
}
