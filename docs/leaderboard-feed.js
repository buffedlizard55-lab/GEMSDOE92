/* Public leaderboard display only; this feed never changes submission status. */
(() => {
  const script = document.currentScript;
  if (!script) return;
  const nodes = document.querySelectorAll('[data-official-leaderboard]');
  if (!nodes.length) return;
  const unavailable = 'Official leaderboard refresh unavailable; consult the organizer page directly.';
  const show = text => nodes.forEach(node => { node.textContent = text; });
  const source = 'https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/';
  fetch(new URL('downloads/live_leaderboard.json', script.src), {cache: 'no-store'})
    .then(response => {
      if (!response.ok) throw new Error('feed unavailable');
      return response.json();
    })
    .then(feed => {
      if (feed.schema !== 'gemsdoe92-official-leaderboard-feed-v1' || feed.source !== source ||
          !['ok', 'snapshot'].includes(feed.status) || feed.rank !== 1 ||
          typeof feed.public_dw_tversky !== 'number' || !Number.isFinite(feed.public_dw_tversky) ||
          feed.public_dw_tversky < 0 || feed.public_dw_tversky > 1) throw new Error('invalid feed');
      const date = feed.status === 'ok' ? feed.checked_at_utc : feed.observed_on_utc;
      if (typeof date !== 'string' || !/^\d{4}-\d\d-\d\d/.test(date)) throw new Error('invalid date');
      show(`Official public #1: ${feed.public_dw_tversky.toFixed(4)}; ${feed.status === 'ok' ? 'checked' : 'observed'} ${date} UTC. Snapshot only; not a project receipt.`);
    })
    .catch(() => show(unavailable));
})();
