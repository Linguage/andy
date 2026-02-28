(() => {
  const form = document.querySelector("#pub-filter-form");
  if (!form) return;
  const searchCore = window.PublicationSearchCore;
  if (!searchCore) {
    console.error("PublicationSearchCore is not loaded.");
    return;
  }

  const qInput = form.querySelector("#filter-q");
  const yearSelect = form.querySelector("#filter-year");
  const typeSelect = form.querySelector("#filter-type");
  const cards = [...document.querySelectorAll(".pub-card")];
  const counter = document.querySelector("#filter-count");
  const emptyState = document.querySelector("#filter-empty");
  const copyButtons = [...document.querySelectorAll(".copy-citation-btn")];

  const allowedTypes = new Set([...typeSelect.options].map((opt) => opt.value).filter(Boolean));
  const allowedYears = new Set([...yearSelect.options].map((opt) => opt.value).filter(Boolean));
  const params = new URLSearchParams(window.location.search);

  const state = {
    q: searchCore.normalizeQuery(params.get("q") || ""),
    year: params.get("year") || "",
    type: params.get("type") || ""
  };

  if (!allowedYears.has(state.year)) state.year = "";
  if (!allowedTypes.has(state.type)) state.type = "";

  qInput.value = state.q;
  yearSelect.value = state.year;
  typeSelect.value = state.type;

  const pushURLState = () => {
    const next = new URLSearchParams();
    if (state.q) next.set("q", state.q);
    if (state.year) next.set("year", state.year);
    if (state.type) next.set("type", state.type);
    const query = next.toString();
    const nextURL = query ? `${window.location.pathname}?${query}` : window.location.pathname;
    window.history.replaceState({}, "", nextURL);
  };

  const applyFilters = () => {
    let visible = 0;
    const queryTokens = searchCore.tokenizeQuery(state.q);

    cards.forEach((card) => {
      const text = card.dataset.search || "";
      const matchQ = !queryTokens.length || searchCore.matchesAllTokens(text, queryTokens);
      const matchYear = !state.year || card.dataset.year === state.year;
      const matchType = !state.type || card.dataset.type === state.type;
      const show = matchQ && matchYear && matchType;
      card.classList.toggle("hidden", !show);
      if (show) visible += 1;
    });

    counter.textContent = String(visible);
    emptyState.hidden = visible !== 0;
    pushURLState();
  };

  let timer;
  qInput.addEventListener("input", (event) => {
    clearTimeout(timer);
    timer = window.setTimeout(() => {
      state.q = searchCore.normalizeQuery(event.target.value);
      applyFilters();
    }, 100);
  });

  yearSelect.addEventListener("change", (event) => {
    state.year = event.target.value;
    applyFilters();
  });

  typeSelect.addEventListener("change", (event) => {
    state.type = event.target.value;
    applyFilters();
  });

  const copyCitation = async (button) => {
    const text = button.dataset.citation || "";
    if (!text) return;

    const originalLabel = button.dataset.originalLabel || button.textContent;
    if (!button.dataset.originalLabel) button.dataset.originalLabel = originalLabel;

    try {
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied";
    } catch (_error) {
      const area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "absolute";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      document.body.removeChild(area);
      button.textContent = "Copied";
    }

    window.setTimeout(() => {
      button.textContent = button.dataset.originalLabel || "Copy citation";
    }, 1200);
  };

  copyButtons.forEach((button) => {
    button.addEventListener("click", () => {
      copyCitation(button);
    });
  });

  applyFilters();
})();
