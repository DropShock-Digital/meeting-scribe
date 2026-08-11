const stateTitle = document.querySelector('#state-title');
const stateSubtitle = document.querySelector('#state-subtitle');
const systemBadge = document.querySelector('#system-badge');
const systemSummary = document.querySelector('#system-summary');
const signals = document.querySelector('#signals');
const captureReason = document.querySelector('#capture-reason');
const captureLabel = document.querySelector('#capture-label');
const activeMeetings = document.querySelector('#active-meetings');
const activeCount = document.querySelector('#active-count');
const archive = document.querySelector('#archive');
const actionStatus = document.querySelector('#action-status');
const disclosureDialog = document.querySelector('#disclosure-dialog');
const disclosureText = document.querySelector('#disclosure-text');
const roomSelector = document.querySelector('#room-selector');
const providerSelector = document.querySelector('#provider-selector');
const preferenceStatus = document.querySelector('#preference-status');

const ROOM_PREFERENCE = 'meeting-scribe.room-preference';
const PROVIDER_PREFERENCE = 'meeting-scribe.provider-preference';

const esc = value => String(value).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
const time = value => new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
const recordLinks = meeting => `<div class="record-links"><a href="/api/meetings/${encodeURIComponent(meeting.id)}/export.md">Open Markdown</a><a href="/api/meetings/${encodeURIComponent(meeting.id)}/export.json">Open JSON</a></div>`;

function signal(label, value, tone = 'neutral') {
  return `<div class="signal"><dt><span class="signal-dot ${tone}" aria-hidden="true"></span>${esc(label)}</dt><dd>${esc(value)}</dd></div>`;
}

function stored(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}

function remember(key, value) {
  try { localStorage.setItem(key, value); } catch { /* Browser preference is optional. */ }
}

function option(value, label, disabled = false) {
  const node = document.createElement('option');
  node.value = value;
  node.textContent = label;
  node.disabled = disabled;
  return node;
}

function renderPreferences(rooms, providers) {
  roomSelector.replaceChildren();
  if (!rooms.length) roomSelector.append(option('', 'No named room catalog configured'));
  for (const room of rooms) roomSelector.append(option(room.key, room.label));
  roomSelector.disabled = rooms.length === 0;
  const savedRoom = stored(ROOM_PREFERENCE);
  const selectedRoom = rooms.find(room => room.key === savedRoom) || rooms[0];
  if (selectedRoom) roomSelector.value = selectedRoom.key;

  providerSelector.replaceChildren();
  const configuredProviders = providers.filter(provider => provider.configured);
  if (!configuredProviders.length) {
    providerSelector.append(option('', 'No provider configured yet'));
  }
  for (const provider of providers) {
    providerSelector.append(option(
      provider.key,
      `${provider.label} · ${provider.configured ? 'configured' : 'not configured'}`,
      !provider.configured,
    ));
  }
  providerSelector.disabled = configuredProviders.length === 0;
  const savedProvider = stored(PROVIDER_PREFERENCE);
  const selectedProvider = configuredProviders.find(provider => provider.key === savedProvider)
    || configuredProviders[0];
  if (selectedProvider) providerSelector.value = selectedProvider.key;

  const roomCopy = selectedRoom ? `Next room: ${selectedRoom.label}.` : 'No approved voice rooms are configured.';
  const providerCopy = selectedProvider
    ? `AI preference: ${selectedProvider.label} configured. ${selectedProvider.detail}`
    : 'AI preference: none configured. Configure a protected provider connection outside this browser.';
  preferenceStatus.textContent = `${roomCopy} ${providerCopy} No Discord join, audio capture, or AI request occurs from this screen.`;
}

function meetingCard(meeting) {
  const offlineReview = meeting.mode === 'offline-review';
  const waiting = meeting.status === 'disclosing';
  const detail = offlineReview
    ? 'Offline review record. It cannot begin capture.'
    : waiting ? 'Waiting for the verified Discord gateway.' : `Status: ${meeting.status}.`;
  const closeLabel = offlineReview ? 'Close review' : 'Close record';
  return `<article class="meeting-card"><div class="meeting-card-top"><p class="status ${esc(meeting.status)}">${offlineReview ? 'OFFLINE REVIEW' : waiting ? 'WAITING FOR GATEWAY' : esc(meeting.status)}</p><time datetime="${esc(meeting.created_at)}">${esc(time(meeting.created_at))}</time></div><h3>${esc(meeting.title)}</h3><p>${esc(detail)}</p><div class="card-actions">${recordLinks(meeting)}${meeting.status !== 'finalized' ? `<button class="finish" data-finalize="${esc(meeting.id)}">${closeLabel}</button>` : ''}</div></article>`;
}

function emptyActive() {
  return `<article class="empty-state"><span class="empty-mark" aria-hidden="true">◌</span><div><h3>No active meeting yet</h3><p>A configured Discord room will open here automatically when the verified gateway is available.</p></div></article>`;
}

function archiveRow(meeting) {
  return `<article class="archive-row"><div><p class="status finalized">CLOSED</p><h3>${esc(meeting.title)}</h3><p>${esc(time(meeting.finalized_at || meeting.created_at))}</p></div>${recordLinks(meeting)}</article>`;
}

function render(snapshot) {
  const { system, rooms = [], providers = [], capture, disclosure, active, archive: archived } = snapshot;
  const liveActive = active.some(meeting => meeting.mode !== 'offline-review');
  const offlineReviewOpen = active.some(meeting => meeting.mode === 'offline-review');
  const capturePaused = !capture.available;
  const gatewayConfigured = system.discord_enabled;
  stateTitle.innerHTML = liveActive
    ? 'A meeting is<br><em>in progress.</em>'
    : offlineReviewOpen
      ? 'Offline review,<br><em>open.</em>'
      : gatewayConfigured
        ? 'Waiting for<br><em>a configured room.</em>'
        : 'Control room,<br><em>standing by.</em>';
  stateSubtitle.textContent = liveActive
    ? 'The verified gateway is managing the current meeting state.'
    : offlineReviewOpen
      ? 'This is a local walkthrough record. It cannot join Discord or capture audio.'
      : gatewayConfigured
        ? capturePaused
          ? 'The automatic meeting loop is ready. Voice capture stays safely paused until its encrypted Discord receive path has passed verification.'
          : 'A verified gateway controls disclosure and capture automatically.'
        : 'Connect the verified Discord gateway to enable automatic meeting flow. Voice capture remains safely paused until its encrypted receive path has passed verification.';
  systemBadge.textContent = gatewayConfigured && !capturePaused ? 'READY' : 'SAFE HOLD';
  systemBadge.className = `status-badge ${gatewayConfigured && !capturePaused ? 'ready' : 'hold'}`;
  systemSummary.textContent = gatewayConfigured
    ? capturePaused ? 'Gateway configuration is loaded. Voice capture is paused.' : 'The automatic loop is ready.'
    : 'The control room is ready. Gateway connection and voice capture are not live.';
  signals.innerHTML = [
    signal('Configured rooms', `${system.configured_room_count} loaded`, 'ready'),
    signal('Gateway', system.discord_enabled ? 'Configuration loaded' : 'Not connected', system.discord_enabled ? 'ready' : 'neutral'),
    signal('Disclosure', 'Generated automatically', 'ready'),
    signal('Voice capture', capturePaused ? 'Safely paused' : 'Ready', capturePaused ? 'hold' : 'ready'),
  ].join('');
  captureLabel.textContent = capture.label.toUpperCase();
  captureLabel.className = `pause-label ${capturePaused ? 'hold' : 'ready'}`;
  captureReason.textContent = capture.reason;
  disclosureText.textContent = disclosure;
  renderPreferences(rooms, providers);
  activeCount.textContent = active.length ? `${active.length} open` : 'NO OPEN SESSIONS';
  activeMeetings.innerHTML = active.length ? active.map(meetingCard).join('') : emptyActive();
  archive.innerHTML = archived.length ? archived.map(archiveRow).join('') : '<p class="archive-empty">Closed meetings and their exports will appear here.</p>';
}

async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'The request could not be completed.');
  return data;
}

async function load() {
  try {
    render(await request('/api/console'));
  } catch (error) {
    actionStatus.textContent = error.message;
  }
}

document.querySelector('#create-review').addEventListener('click', async () => {
  actionStatus.textContent = 'Creating offline review record…';
  try {
    await request('/api/meetings/offline-review', { method: 'POST' });
    actionStatus.textContent = 'Offline review record created. It is not capturing audio.';
    await load();
  } catch (error) {
    actionStatus.textContent = error.message;
  }
});

document.querySelector('#refresh').addEventListener('click', () => void load());
document.querySelector('#view-disclosure').addEventListener('click', () => disclosureDialog.showModal());
roomSelector.addEventListener('change', () => {
  remember(ROOM_PREFERENCE, roomSelector.value);
  preferenceStatus.textContent = `Next room preference saved: ${roomSelector.selectedOptions[0]?.textContent || 'approved room'}. No Discord join occurs yet.`;
});
providerSelector.addEventListener('change', () => {
  remember(PROVIDER_PREFERENCE, providerSelector.value);
  preferenceStatus.textContent = `AI preference saved: ${providerSelector.selectedOptions[0]?.textContent || 'configured provider'}. This remains unverified; no meeting content is sent yet.`;
});
activeMeetings.addEventListener('click', async event => {
  const button = event.target.closest('[data-finalize]');
  if (!button) return;
  actionStatus.textContent = 'Closing record…';
  try {
    await request(`/api/meetings/${encodeURIComponent(button.dataset.finalize)}/finalize`, {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ reason: 'offline-review-complete' }),
    });
    actionStatus.textContent = 'Record closed. Its exports are available below.';
    await load();
  } catch (error) {
    actionStatus.textContent = error.message;
  }
});

load();
