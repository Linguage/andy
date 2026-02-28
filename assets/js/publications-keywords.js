(() => {
  const app = document.querySelector("#pub-keyword-app");
  if (!app) return;
  const searchCore = window.PublicationSearchCore;
  if (!searchCore) {
    console.error("PublicationSearchCore is not loaded.");
    return;
  }

  const cloud = app.querySelector("#keyword-cloud");
  const selectionLabel = app.querySelector("#keyword-cloud-selection");
  const extraTermsLabel = app.querySelector("#keyword-cloud-extra");
  const matchLabel = app.querySelector("#keyword-cloud-match");
  const clearButton = app.querySelector("#keyword-clear-btn");
  const applyLink = app.querySelector("#keyword-apply-link");
  const sources = [...app.querySelectorAll(".pub-keyword-source")];
  const publicationsURL = app.dataset.publicationsUrl || "/publications/";
  const params = new URLSearchParams(window.location.search);

  const STOP_WORDS = new Set([
    "about", "after", "all", "also", "among", "and", "any", "are", "been", "between", "both",
    "can", "could", "did", "does", "each", "for", "from", "had", "has", "have", "into", "its",
    "more", "new", "not", "one", "our", "over", "paper", "results", "study", "such", "than",
    "that", "the", "their", "these", "this", "those", "through", "towards", "under", "using",
    "was", "were", "what", "when", "where", "which", "with",
    "och", "vid", "med", "hos", "som", "den", "det", "ett", "att", "av", "fran", "från", "till",
    "doi", "report", "reports", "journal", "conference", "manuscript", "submitted", "download"
  ]);
  const TOPIC_STOP_WORDS = new Set([
    "analysis", "analys", "assessment", "evaluation", "effect", "effects", "influence",
    "method", "methods", "model", "models", "design", "response", "responses",
    "engineering", "international", "structures", "structural", "system", "systems",
    "considering", "some", "data", "application", "applications", "chapter", "conf", "int",
    "september", "november", "july", "may",
    "athens", "greece", "italy", "netherlands", "stockholm",
    "eurodyn", "evaces",
    "gamla", "avseende", "kontroll", "några", "sammanställning", "översiktlig",
    "beräkning", "beräkningar", "beräknings", "bärförmåga", "bärighetsanalys",
    "citybanan", "årstabron", "graveforstunnlarna", "innertak", "svinesund",
    "bergblock", "broexciterare", "supported",
    "bro", "dynamisk", "dynamiska", "statisk", "analyser", "simulering",
    "inverkan", "respons", "järnvägsbro", "järnvägsbroar", "för", "över", "rail"
  ]);
  const MIN_TOKEN_LENGTH = 4;
  const MIN_FREQUENCY = 4;
  const MAX_WORDS = 140;
  const ASCII_ONLY_TOKENS = true;

  const tokenizeAuthorText = (raw) => {
    const tokens = (raw || "").toLowerCase().match(/[\p{L}]+(?:-[\p{L}]+)*/gu) || [];
    return tokens
      .filter((token) => token.length >= 3)
      .filter((token) => (ASCII_ONLY_TOKENS ? /^[a-z-]+$/.test(token) : true));
  };

  const authorTokens = new Set();
  sources.forEach((node) => {
    tokenizeAuthorText(node.dataset.authors || "").forEach((token) => authorTokens.add(token));
  });

  const tokenizeSourceText = (raw) => {
    const tokens = (raw || "").toLowerCase().match(/[\p{L}\p{N}]+(?:-[\p{L}\p{N}]+)*/gu) || [];
    return tokens
      .filter((token) => {
        if (token.length < MIN_TOKEN_LENGTH) return false;
        if (ASCII_ONLY_TOKENS && !/^[a-z-]+$/.test(token)) return false;
        if (authorTokens.has(token)) return false;
        if (STOP_WORDS.has(token)) return false;
        if (TOPIC_STOP_WORDS.has(token)) return false;
        if (/\d/.test(token)) return false;
        if (token.startsWith("doi")) return false;
        if (token.startsWith("trv")) return false;
        if (token.endsWith("pdf")) return false;
        return true;
      });
  };

  const publicationTokens = sources.map((node) => new Set(tokenizeSourceText(node.dataset.keywords || "")));
  const publicationSearchTexts = sources.map((node) => node.dataset.search || "");

  const frequencies = new Map();
  publicationTokens.forEach((tokenSet) => {
    tokenSet.forEach((token) => {
      frequencies.set(token, (frequencies.get(token) || 0) + 1);
    });
  });

  const words = [...frequencies.entries()]
    .filter((entry) => entry[1] >= MIN_FREQUENCY)
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, MAX_WORDS);
  const cloudWordSet = new Set(words.map(([word]) => word));

  const wordMatchCount = new Map();
  words.forEach(([word]) => {
    const count = searchCore.countMatches(publicationSearchTexts, [word]);
    wordMatchCount.set(word, count);
  });

  const selected = new Set(
    searchCore.tokenizeQuery(params.get("q") || "")
  );

  const wordCountValues = words.map((entry) => entry[1]);
  const minCount = wordCountValues.length ? Math.min(...wordCountValues) : 0;
  const maxCount = wordCountValues.length ? Math.max(...wordCountValues) : 0;

  const queryFromSelection = () => searchCore.normalizeQuery([...selected].join(" "));

  const countMatches = () => {
    return searchCore.countMatches(publicationSearchTexts, searchCore.tokenizeQuery(queryFromSelection()));
  };

  const sizeLevelForCount = (count) => {
    if (!maxCount || maxCount === minCount) return 3;
    const ratio = (count - minCount) / (maxCount - minCount);
    return Math.min(5, Math.max(1, Math.round(ratio * 4) + 1));
  };

  const updateURL = () => {
    const next = new URLSearchParams(window.location.search);
    const query = queryFromSelection();
    if (query) next.set("q", query);
    else next.delete("q");
    const queryString = next.toString();
    const nextURL = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
    window.history.replaceState({}, "", nextURL);
  };

  const updateActions = () => {
    const selectedTerms = searchCore.tokenizeQuery(queryFromSelection());
    const matchedCount = countMatches();
    const nonCloudTerms = selectedTerms.filter((term) => !cloudWordSet.has(term));

    if (!selectedTerms.length) {
      selectionLabel.textContent = "No keyword selected.";
      matchLabel.textContent = `${publicationSearchTexts.length} publications available.`;
    } else {
      selectionLabel.textContent = `Selected keywords (${selectedTerms.length}): ${selectedTerms.join(", ")}`;
      matchLabel.textContent = `${matchedCount} publications match current selection.`;
    }

    if (extraTermsLabel) {
      if (nonCloudTerms.length) {
        extraTermsLabel.hidden = false;
        extraTermsLabel.textContent = `Additional query terms not in cloud: ${nonCloudTerms.join(", ")}`;
      } else {
        extraTermsLabel.hidden = true;
        extraTermsLabel.textContent = "";
      }
    }

    const pubParams = new URLSearchParams();
    if (selectedTerms.length) pubParams.set("q", selectedTerms.join(" "));
    const pubQuery = pubParams.toString();
    applyLink.href = pubQuery ? `${publicationsURL}?${pubQuery}` : publicationsURL;
    applyLink.textContent = selectedTerms.length
      ? `View ${matchedCount} filtered publications`
      : "View all publications";

    clearButton.disabled = selectedTerms.length === 0;
  };

  const renderCloud = () => {
    cloud.innerHTML = "";

    if (!words.length) {
      const fallback = document.createElement("p");
      fallback.className = "meta";
      fallback.textContent = "No keyword data available.";
      cloud.appendChild(fallback);
      return;
    }

    words.forEach(([word, count]) => {
      const button = document.createElement("button");
      const active = selected.has(word);
      const matched = wordMatchCount.get(word) || 0;
      button.type = "button";
      button.className = `keyword-token keyword-level-${sizeLevelForCount(count)}`;
      if (active) button.classList.add("is-active");
      button.dataset.keyword = word;
      button.setAttribute("aria-pressed", active ? "true" : "false");
      button.title = `${matched} publications`;
      button.textContent = word;
      cloud.appendChild(button);
    });
  };

  cloud.addEventListener("click", (event) => {
    const button = event.target.closest("button.keyword-token");
    if (!button) return;
    const word = button.dataset.keyword || "";
    if (!word) return;

    if (selected.has(word)) selected.delete(word);
    else selected.add(word);

    renderCloud();
    updateActions();
    updateURL();
  });

  clearButton.addEventListener("click", () => {
    if (!selected.size) return;
    selected.clear();
    renderCloud();
    updateActions();
    updateURL();
  });

  renderCloud();
  updateActions();
  updateURL();
})();
