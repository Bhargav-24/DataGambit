const API_URL = "https://datagambit.onrender.com/recommend/";

const btn = document.getElementById("analyseBtn");
const statusBox = document.getElementById("status");
const resultsBox = document.getElementById("results");
const recommendedBox = document.getElementById("recommended");
const metaBox = document.getElementById("meta");

btn.addEventListener("click", analyse);

async function analyse() {
  btn.disabled = true;
  btn.textContent = "Analysing...";
  statusBox.textContent = "Fetching recommendations...";
  resultsBox.classList.add("hidden");

  try {
    console.log("[DataGambit] Sending request to:", API_URL);

    const payload = await getCurrentLichessGame();

    console.log("[DataGambit] Payload:", payload);

    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    console.log("[DataGambit] Status:", res.status);

    const rawText = await res.text();
    console.log("[DataGambit] Raw response:", rawText);

    let data;
    try {
      data = JSON.parse(rawText);
    } catch (e) {
      throw new Error("Server just woke up. Press Analyse again.");
    }

    if (!res.ok) {
      throw new Error(data.error || `Backend error ${res.status}`);
    }

    render(data);
    statusBox.textContent = "";
  } catch (err) {
    console.error("[DataGambit] Full error:", err);

    statusBox.textContent = err.message || "Could not connect to DataGambit backend.";
  }

  btn.disabled = false;
  btn.textContent = "Analyse";
}

function render(data) {
  recommendedBox.innerHTML = "";

  const uniqueOpenings = [];
  const seenNames = new Set();

  data.recommended.forEach(item => {
    const baseName = item.opening.trim();
    if (!seenNames.has(baseName)) {
      seenNames.add(baseName);
      uniqueOpenings.push(item);
    }
  });

  uniqueOpenings.slice(0, 3).forEach(item => {
    const li = document.createElement("li");

    li.innerHTML = `
      <span class="opening-name">${item.opening}</span>
      <span class="winrate">${(item.score * 100).toFixed(1)}% winrate</span>
    `;

    recommendedBox.appendChild(li);
  });

  metaBox.textContent = `Opponent: ${data.opponent_username}`;
  resultsBox.classList.remove("hidden");
}

async function getCurrentLichessGame() {
  const tabs = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

  const tab = tabs[0];

  if (!tab || !tab.url || !tab.url.includes("lichess.org")) {
    throw new Error("Open a Lichess game first.");
  }

  const injected = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const path = location.pathname;
      const match = path.match(/^\/([A-Za-z0-9]{8,})(?:\/(?:white|black))?\/?$/);
      const rawId = match ? match[1] : "";

      const canonicalLink = document.querySelector("link[rel='canonical']")?.href;
      const ogUrl = document.querySelector("meta[property='og:url']")?.content;
      const canonicalSource = canonicalLink || ogUrl || "";
      const canonicalMatch = canonicalSource.match(/https?:\/\/lichess\.org\/([A-Za-z0-9]{8})/);
      const gameId = canonicalMatch ? canonicalMatch[1] : rawId.slice(0, 8);

      const bottomUser =
        document.querySelector(".ruser-bottom a[href^='/@/']") ||
        document.querySelector(".ruser-bottom a.user-link") ||
        document.querySelector(".ruser-top a[href^='/@/']") ||
        document.querySelector(".ruser-top a.user-link");

      const forUsername = bottomUser ? bottomUser.textContent.trim() : "";

      let forColor = "white";
      if (document.querySelector(".cg-wrap.orientation-black")) {
        forColor = "black";
      }

      const board = document.querySelector(".cg-board") || document.querySelector(".round__app");
      if (!board || !gameId || gameId.length !== 8) {
        return {
          ok: false,
          error: "This page is not a supported Lichess game board. Open a live game page first."
        };
      }

      return {
        ok: true,
        data: {
          game_id: gameId,
          for_username: forUsername,
          for_color: forColor
        }
      };
    }
  });

  const result = injected[0].result;

  if (!result.ok) {
    throw new Error(result.error);
  }

  return result.data;
}
