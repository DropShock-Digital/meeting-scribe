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

const esc = value => String(value).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
const time = value => new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
const recordLinks = meeting => `<div class="record-links"><a href="/api/meetings/${encodeURIComponent(meeting.id)}/export.md">Open notes</a><a href="/api/meetings/${encodeURIComponent(meeting.id)}/export.json">Open full record</a></div>`;

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

function renderPreferences(rooms) {
  roomSelector.replaceChildren();
  if (!rooms.length) roomSelector.append(option('', 'No approved rooms are available.'));
  for (const room of rooms) roomSelector.append(option(room.key, room.label));
  roomSelector.disabled = rooms.length === 0;
  const savedRoom = stored(ROOM_PREFERENCE);
  const selectedRoom = rooms.find(room => room.key === savedRoom) || rooms[0];
  if (selectedRoom) roomSelector.value = selectedRoom.key;

  providerSelector.replaceChildren();
  providerSelector.append(option('', 'No helper available.'));
  providerSelector.disabled = true;

  const roomCopy = selectedRoom ? `Next room: ${selectedRoom.label}.` : 'No approved rooms are available.';
  preferenceStatus.textContent = `${roomCopy} No meeting helper is available. Saved only in this browser. Nothing has started.`;
}

function meetingCard(meeting) {
  const privateReview = meeting.mode === 'offline-review';
  const detail = privateReview
    ? 'Private review only. It does not join a call or record sound.'
    : 'This record does not join a call or record sound.';
  const closeLabel = privateReview ? 'Finish review' : 'Finish record';
  return `<article class="meeting-card"><div class="meeting-card-top"><p class="status ${esc(meeting.status)}">${privateReview ? 'PRIVATE REVIEW' : 'MEETING RECORD'}</p><time datetime="${esc(meeting.created_at)}">${esc(time(meeting.created_at))}</time></div><h3>${esc(meeting.title)}</h3><p>${esc(detail)}</p><div class="card-actions">${recordLinks(meeting)}${meeting.status !== 'finalized' ? `<button class="finish" data-finalize="${esc(meeting.id)}">${closeLabel}</button>` : ''}</div></article>`;
}

function emptyActive() {
  return `<article class="empty-state"><span class="empty-mark" aria-hidden="true">◌</span><div><h3>No record is open.</h3><p>Private reviews and meeting records appear here.</p></div></article>`;
}

function archiveRow(meeting) {
  return `<article class="archive-row"><div><p class="status finalized">SAVED</p><h3>${esc(meeting.title)}</h3><p>${esc(time(meeting.finalized_at || meeting.created_at))}</p></div>${recordLinks(meeting)}</article>`;
}

function render(snapshot) {
  const { system, rooms = [], disclosure, active, archive: archived } = snapshot;
  const openReview = active.some(meeting => meeting.mode === 'offline-review');
  const openRecord = active.length > 0;
  stateTitle.innerHTML = openReview
    ? 'Private review,<br><em>open.</em>'
    : openRecord
      ? 'Meeting record,<br><em>open.</em>'
      : 'Private reviews,<br><em>not recordings.</em>';
  stateSubtitle.textContent = openRecord
    ? 'This record cannot join a call or record sound.'
    : 'This version cannot join calls or record sound.';
  systemBadge.textContent = 'RECORDING OFF';
  systemBadge.className = 'status-badge hold';
  systemSummary.textContent = 'Private reviews are available.';
  signals.innerHTML = [
    signal('Approved rooms', system.configured_room_count ? `${system.configured_room_count} available` : 'None available', system.configured_room_count ? 'ready' : 'neutral'),
    signal('Calls', 'Not available', 'neutral'),
    signal('Participant notice', 'Required before any future recording', 'neutral'),
    signal('Recording', 'Not available', 'hold'),
  ].join('');
  captureLabel.textContent = 'RECORDING OFF';
  captureLabel.className = 'pause-label hold';
  captureReason.textContent = 'Recording is not available.';
  disclosureText.textContent = disclosure;
  renderPreferences(rooms);
  activeCount.textContent = active.length ? `${active.length} record${active.length === 1 ? '' : 's'} open` : 'NO RECORDS OPEN';
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
  preferenceStatus.textContent = `Next room: ${roomSelector.selectedOptions[0]?.textContent || 'approved room'}. No meeting helper is available. Saved only in this browser. Nothing has started.`;
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
