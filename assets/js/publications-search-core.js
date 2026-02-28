(() => {
  const tokenizeQuery = (raw) => {
    const seen = new Set();
    return (raw || "")
      .toLowerCase()
      .split(/[\s,]+/)
      .map((token) => token.trim())
      .filter((token) => {
        if (!token || seen.has(token)) return false;
        seen.add(token);
        return true;
      });
  };

  const normalizeQuery = (raw) => tokenizeQuery(raw).join(" ");

  const matchesAllTokens = (text, tokens) => tokens.every((token) => text.includes(token));

  const countMatches = (texts, tokens) => {
    if (!tokens.length) return texts.length;
    return texts.reduce((acc, text) => (matchesAllTokens(text, tokens) ? acc + 1 : acc), 0);
  };

  window.PublicationSearchCore = {
    tokenizeQuery,
    normalizeQuery,
    matchesAllTokens,
    countMatches
  };
})();
