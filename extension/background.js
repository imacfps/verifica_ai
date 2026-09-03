// Service worker (Manifest V3): menu de contexto em <img> -> POST /v1/analyze -> notificação.

const DEFAULT_API_URL = "http://localhost:8000";
const CONTEXT_MENU_ID = "verifica-ai-analyze";

console.log("[Verifica.AI] service worker iniciado");

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: CONTEXT_MENU_ID,
    title: "Verificar com Verifica.AI",
    contexts: ["image"],
  }, () => {
    if (chrome.runtime.lastError) {
      console.error("[Verifica.AI] erro ao criar menu de contexto:", chrome.runtime.lastError.message);
    } else {
      console.log("[Verifica.AI] menu de contexto criado");
    }
  });
});

chrome.action.onClicked.addListener(() => {
  chrome.runtime.openOptionsPage();
});

chrome.contextMenus.onClicked.addListener((info) => {
  console.log("[Verifica.AI] item de menu clicado:", info);
  if (info.menuItemId === CONTEXT_MENU_ID && info.srcUrl) {
    analyzeImage(info.srcUrl);
  } else {
    console.warn("[Verifica.AI] clique ignorado — sem srcUrl ou menuItemId inesperado");
  }
});

async function getApiUrl() {
  const { apiUrl } = await chrome.storage.sync.get("apiUrl");
  return (apiUrl || DEFAULT_API_URL).replace(/\/+$/, "");
}

async function analyzeImage(srcUrl) {
  setBadge("...", "#8291ad");
  try {
    console.log("[Verifica.AI] baixando imagem:", srcUrl);
    const imageResponse = await fetch(srcUrl);
    if (!imageResponse.ok) {
      throw new Error(`Não foi possível baixar a imagem (HTTP ${imageResponse.status}).`);
    }
    const imageBlob = await imageResponse.blob();
    console.log("[Verifica.AI] imagem baixada:", imageBlob.size, "bytes,", imageBlob.type);

    const apiUrl = await getApiUrl();
    const formData = new FormData();
    formData.append("file", imageBlob, "image");

    console.log("[Verifica.AI] chamando API:", `${apiUrl}/v1/analyze`);
    const response = await fetch(`${apiUrl}/v1/analyze`, {
      method: "POST",
      body: formData,
    });
    const payload = await response.json().catch(() => null);
    console.log("[Verifica.AI] resposta da API:", response.status, payload);

    if (!response.ok) {
      throw new Error(payload?.detail || `Erro HTTP ${response.status} ao consultar a API.`);
    }

    notifyResult(payload);
  } catch (error) {
    console.error("[Verifica.AI] falha na análise:", error);
    notifyError(error);
  }
}

function setBadge(text, color) {
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color });
}

function notifyResult(result) {
  const isAi = result.label === "ai-generated";
  const confidence = Math.round((isAi ? result.prob_ai : result.prob_real) * 100);
  const title = isAi ? "Provavelmente gerada por IA" : "Provavelmente real";

  setBadge(`${confidence}%`, isAi ? "#ffb020" : "#43d9a3");
  chrome.action.setTitle({ title: `Verifica.AI — ${title} (${confidence}%)` });
  clearBadgeLater();

  chrome.notifications.create(
    {
      type: "basic",
      iconUrl: "icons/icon128.png",
      title: `Verifica.AI — ${title}`,
      message: `${confidence}% de confiança (modelo: ${result.model})`,
    },
    () => {
      if (chrome.runtime.lastError) {
        console.error("[Verifica.AI] notificação não exibida:", chrome.runtime.lastError.message);
      } else {
        console.log("[Verifica.AI] notificação exibida");
      }
    },
  );
}

function notifyError(error) {
  setBadge("!", "#ff5c5c");
  chrome.action.setTitle({ title: `Verifica.AI — erro: ${error.message || "falha desconhecida"}` });
  clearBadgeLater();

  chrome.notifications.create(
    {
      type: "basic",
      iconUrl: "icons/icon128.png",
      title: "Verifica.AI — falha na análise",
      message: error.message || "Erro desconhecido ao analisar a imagem.",
    },
    () => {
      if (chrome.runtime.lastError) {
        console.error("[Verifica.AI] notificação de erro não exibida:", chrome.runtime.lastError.message);
      }
    },
  );
}

function clearBadgeLater() {
  setTimeout(() => {
    chrome.action.setBadgeText({ text: "" });
    chrome.action.setTitle({ title: "Configurar Verifica.AI" });
  }, 8000);
}
