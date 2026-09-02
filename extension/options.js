const DEFAULT_API_URL = "http://localhost:8000";

const input = document.getElementById("apiUrl");
const status = document.getElementById("status");

chrome.storage.sync.get("apiUrl", ({ apiUrl }) => {
  input.value = apiUrl || DEFAULT_API_URL;
});

document.getElementById("save").addEventListener("click", async () => {
  const value = input.value.trim().replace(/\/+$/, "") || DEFAULT_API_URL;
  await chrome.storage.sync.set({ apiUrl: value });
  input.value = value;
  status.textContent = "Salvo.";
  setTimeout(() => {
    status.textContent = "";
  }, 2000);
});
