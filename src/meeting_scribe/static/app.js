const status = document.querySelector('#form-status');
const list = document.querySelector('#meetings');
const esc = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function loadMeetings() {
  const response = await fetch('/api/meetings');
  const meetings = await response.json();
  list.innerHTML = meetings.length ? meetings.map(m => `<article class="meeting"><div><p class="status ${esc(m.status)}">${esc(m.status)}</p><h3>${esc(m.title)}</h3><p>${esc(m.created_at)} · ${esc(m.channel_id)}</p></div><div class="actions"><a href="/api/meetings/${encodeURIComponent(m.id)}/export.md">Markdown</a><a href="/api/meetings/${encodeURIComponent(m.id)}/export.json">JSON</a>${m.status !== 'finalized' ? `<button data-disclose="${esc(m.id)}">Confirm disclosure</button><button data-finalize="${esc(m.id)}" class="secondary">Finalize</button>` : ''}</div></article>`).join('') : '<p class="empty">No meetings yet. Start a disclosed local demo meeting above.</p>';
}
async function action(id, suffix, body) {
  const response = await fetch(`/api/meetings/${encodeURIComponent(id)}/${suffix}`, {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(body)});
  if (!response.ok) throw new Error((await response.json()).detail || 'Request failed');
  await loadMeetings();
}
document.querySelector('#start-form').addEventListener('submit', async event => { event.preventDefault(); const fd=new FormData(event.currentTarget); status.textContent='Creating…'; const payload={title:fd.get('title'),channel_id:fd.get('channel_id'),operator_id:fd.get('operator_id'),disclosure:fd.get('disclosure'),operator_confirmed_disclosure:fd.get('confirmed') === 'on'}; const response=await fetch('/api/meetings',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)}); const data=await response.json(); status.textContent=response.ok ? `Created ${data.title}. Confirm disclosure before transcript capture.` : data.detail; if(response.ok) await loadMeetings(); });
list.addEventListener('click', async event => { const target=event.target; try { if(target.dataset.disclose) await action(target.dataset.disclose,'disclosure-delivered',{delivery:'operator-console'}); if(target.dataset.finalize) await action(target.dataset.finalize,'finalize',{reason:'operator-console'}); } catch(error) { status.textContent=error.message; } });
document.querySelector('#refresh').addEventListener('click', loadMeetings); loadMeetings();
