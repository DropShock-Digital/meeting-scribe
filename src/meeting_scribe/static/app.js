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
const recordLinks = meeting => `<div class="record-links"><a href="/api/meetings/${encodeURIComponent(meeting.id)}/export.md">Open notes</a><a href="/api/meetings/${encodeURIComponent(meeting.id)}/export.json">Download record</a></div>`;

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
  if (!rooms.length) roomSelector.append(option('', 'No approved rooms are set up yet'));
  for (const room of rooms) roomSelector.append(option(room.key, room.label));
  roomSelector.disabled = rooms.length === 0;
  const savedRoom = stored(ROOM_PREFERENCE);
  const selectedRoom = rooms.find(room => room.key === savedRoom) || rooms[0];
  if (selectedRoom) roomSelector.value = selectedRoom.key;

  providerSelector.replaceChildren();
  const configuredProviders = providers.filter(provider => provider.configured);
  if (!configuredProviders.length) providerSelector.append(option('', 'No meeting helper is set up yet'));
  for (const provider of providers) {
    providerSelector.append(option(
      provider.key,
      `${provider.label} — ${provider.configured ? 'set up' : 'needs setup'}`,
      !provider.configured,
    ));
  }
  providerSelector.disabled = configuredProviders.length === 0;
  const savedProvider = stored(PROVIDER_PREFERENCE);
  const selectedProvider = configuredProviders.find(provider => provider.key === savedProvider)
    || configuredProviders[0];
  if (selectedProvider) providerSelector.value = selectedProvider.key;

  const roomCopy = selectedRoom ? `Next room: ${selectedRoom.label}.` : 'No approved rooms are set up yet.';
  const helperCopy = selectedProvider
    ? `Meeting helper: ${selectedProvider.label}.`
    : 'No meeting helper is set up yet.';
  preferenceStatus.textContent = `${roomCopy} ${helperCopy} Saved only in this browser. Nothing has started.`;
}

function meetingCard(meeting) {
  const privateReview = meeting.mode === 'offline-review';
  const waiting = meeting.status === 'disclosing';
  const detail = privateReview
    ? 'Private review only. It does not join a call or record sound.'
    : waiting ? 'Waiting for the meeting connection.' : 'Meeting status is being updated.';
  const closeLabel = privateReview ? 'Finish review' : 'Finish meeting';
  return `<article class="meeting-card"><div class="meeting-card-top"><p class="status ${esc(meeting.status)}">${privateReview ? 'PRIVATE REVIEW' : waiting ? 'WAITING' : esc(meeting.status)}</p><time datetime="${esc(meeting.created_at)}">${esc(time(meeting.created_at))}</time></div><h3>${esc(meeting.title)}</h3><p>${esc(detail)}</p><div class="card-actions">${recordLinks(meeting)}${meeting.status !== 'finalized' ? `<button class="finish" data-finalize="${esc(meeting.id)}">${closeLabel}</button>` : ''}</div></article>`;
}

function emptyActive() {
  return `<article class="empty-state"><span class="empty-mark" aria-hidden="true">◌</span><div><h3>No meeting is open.</h3><p>When a meeting is active, it will show up here.</p></div></article>`;
}

function archiveRow(meeting) {
  return `<article class="archive-row"><div><p class="status finalized">SAVED</p><h3>${esc(meeting.title)}</h3><p>${esc(time(meeting.finalized_at || meeting.created_at))}</p></div>${recordLinks(meeting)}</article>`;
}

function render(snapshot) {
  const { system, rooms = [], providers = [], capture, disclosure, active, archive: archived } = snapshot;
  const liveActive = active.some(meeting => meeting.mode !== 'offline-review');
  const offlineReviewOpen = active.some(meeting => meeting.mode === 'offline-review');
  const capturePaused = !capture.available;
  const gatewayConfigured = system.discord_enabled;
  stateTitle.innerHTML = liveActive
    ? 'A meeting is<br><em>underway.</em>'
    : offlineReviewOpen
      ? 'Private review,<br><em>open.</em>'
      : gatewayConfigured
        ? 'Set up and<br><em>waiting.</em>'
        : 'Nothing to record,<br><em>yet.</em>';
  stateSubtitle.textContent = liveActive
    ? 'The current meeting is being managed here.'
    : offlineReviewOpen
      ? 'This private review cannot join a call or record sound.'
      : gatewayConfigured
        ? capturePaused
          ? 'Your room settings are saved. Recording stays off until this connection has been fully checked.'
          : 'This meeting can begin after people receive the participant notice.'
        : 'Pick a room when you are ready. Recording stays off until this connection has been fully checked.';
  systemBadge.textContent = capturePaused ? 'NOT RECORDING' : 'RECORDING AVAILABLE';
  systemBadge.className = `status-badge ${capturePaused ? 'hold' : 'ready'}`;
  systemSummary.textContent = capturePaused
    ? gatewayConfigured ? 'Your room settings are saved. Nothing is recording.' : 'Nothing is recording.'
    : 'Recording can begin after the participant notice.';
  signals.innerHTML = [
    signal('Approved rooms', system.configured_room_count ? `${system.configured_room_count} set up` : 'None yet', system.configured_room_count ? 'ready' : 'neutral'),
    signal('Meeting connection', system.discord_enabled ? 'Set up' : 'Not set up', system.discord_enabled ? 'ready' : 'neutral'),
    signal('Participant notice', 'Shown first', 'ready'),
    signal('Recording', capturePaused ? 'Off' : 'Available', capturePaused ? 'hold' : 'ready'),
  ].join('');
  captureLabel.textContent = capturePaused ? 'RECORDING OFF' : 'AVAILABLE';
  captureLabel.className = `pause-label ${capturePaused ? 'hold' : 'ready'}`;
  captureReason.textContent = capturePaused
    ? 'Recording is off until this connection has been fully checked.'
    : 'People see the participant notice before recording can begin.';
  disclosureText.textContent = disclosure;
  renderPreferences(rooms, providers);
  activeCount.textContent = active.length ? `${active.length} meeting${active.length === 1 ? '' : 's'} open` : 'NO MEETINGS OPEN';
  activeMeetings.innerHTML = active.length ? active.map(meetingCard).join('') : emptyActive();
  archive.innerHTML = archived.length ? archived.map(archiveRow).join('') : '<p class="archive-empty">Finished meetings will be saved here.</p>';
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
  } catch {
    actionStatus.textContent = 'We could not check this right now. Please try again.';
  }
}

document.querySelector('#create-review').addEventListener('click', async () => {
  actionStatus.textContent = 'Opening your private review…';
  try {
    await request('/api/meetings/offline-review', { method: 'POST' });
    actionStatus.textContent = 'Private review opened. It is not recording sound.';
    await load();
  } catch {
    actionStatus.textContent = 'We could not open the review. Please try again.';
  }
});

document.querySelector('#refresh').addEventListener('click', () => void load());
document.querySelector('#view-disclosure').addEventListener('click', () => disclosureDialog.showModal());
roomSelector.addEventListener('change', () => {
  remember(ROOM_PREFERENCE, roomSelector.value);
  preferenceStatus.textContent = `Next room: ${roomSelector.selectedOptions[0]?.textContent || 'approved room'}. Saved only in this browser. Nothing has started.`;
});
providerSelector.addEventListener('change', () => {
  remember(PROVIDER_PREFERENCE, providerSelector.value);
  preferenceStatus.textContent = `Meeting helper: ${providerSelector.selectedOptions[0]?.textContent || 'meeting helper'}. Saved only in this browser. Nothing has started.`;
});
activeMeetings.addEventListener('click', async event => {
  const button = event.target.closest('[data-finalize]');
  if (!button) return;
  actionStatus.textContent = 'Finishing this review…';
  try {
    await request(`/api/meetings/${encodeURIComponent(button.dataset.finalize)}/finalize`, {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ reason: 'offline-review-complete' }),
    });
    actionStatus.textContent = 'Saved. You can open the notes below.';
    await load();
  } catch {
    actionStatus.textContent = 'We could not finish this review. Please try again.';
  }
});

load();
