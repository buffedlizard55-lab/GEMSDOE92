/* GitHub commit freshness only. This never inspects or authorizes submissions. */
(() => {
  "use strict";
  const allowed = new Set(["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
    "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]);
  const shaPattern = /^[0-9a-f]{40}$/;
  const labels = Array.from(document.querySelectorAll("[data-focus-repo][data-pinned-sha]"));
  const when = document.querySelector("[data-freshness-time]");
  async function update(label) {
    const site = label.dataset.focusRepo;
    const pinned = label.dataset.pinnedSha;
    if (!allowed.has(site) || !shaPattern.test(pinned || "")) {
      label.textContent = "GitHub check unavailable — historical snapshot only";
      label.dataset.freshness = "unknown";
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(`https://api.github.com/repos/buffedlizard55-lab/${site}/commits/main`, {
        headers: { Accept: "application/vnd.github+json" }, cache: "no-store", signal: controller.signal
      });
      if (!response.ok) throw new Error("GitHub request failed");
      const data = await response.json();
      if (typeof data.sha !== "string" || !shaPattern.test(data.sha)) throw new Error("Invalid commit");
      label.textContent = data.sha === pinned
        ? "Same main ref as pinned audit; artifacts not re-audited"
        : "Main ref changed since pinned audit; artifacts not re-audited";
      label.dataset.freshness = data.sha === pinned ? "unchanged" : "changed";
    } catch (_error) {
      label.textContent = "GitHub check unavailable — historical snapshot only";
      label.dataset.freshness = "unknown";
    } finally {
      clearTimeout(timer);
    }
  }
  if (labels.length) {
    Promise.all(labels.map(update)).then(() => {
      if (when) when.textContent = `Browser GitHub ref check completed ${new Date().toISOString()}.`;
    });
  }
})();
