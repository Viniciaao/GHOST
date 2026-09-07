/* GHOST: interface offline. Sem fetch, analytics ou abertura automática de links. */
'use strict';
(function () {
  const STORAGE_KEY = 'ghost-bdo-selection-v1';
  function normalize(value) {
    return String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }
  function matches(mod, filters, selected = new Set()) {
    if (filters.category && mod.category !== filters.category) return false;
    if (filters.scope && mod.scope !== filters.scope) return false;
    if (filters.verification && mod.source.verification !== filters.verification) return false;
    if (filters.onlySelected && !selected.has(mod.id)) return false;
    if (filters.body === 'unknown' && mod.body.length) return false;
    if (filters.body && filters.body !== 'unknown' && !mod.body.some(b => normalize(b.split(/[\s(]/)[0]) === normalize(filters.body))) return false;
    const haystack = normalize([mod.id, mod.name, mod.summary, mod.family, ...mod.authors, ...mod.body, ...mod.requirements, ...mod.notes].join(' '));
    return normalize(filters.query || '').trim().split(/\s+/).every(word => haystack.includes(word));
  }
  function restoreSelection(raw, mods) {
    const allowed = new Set(mods.map(m => m.id));
    try {
      const values = JSON.parse(raw);
      return new Set(Array.isArray(values) ? values.filter(id => typeof id === 'string' && allowed.has(id)) : []);
    } catch (_) { return new Set(); }
  }
  function exportPlan(catalog, selected) {
    return {
      type: 'research_plan_not_downloaded_mods',
      catalog_version: catalog.catalog_version,
      checked_on: catalog.checked_on,
      notice: 'Seleção de referências para pesquisa e download manual na fonte. Nenhum arquivo de mod é fornecido ou foi baixado por esta interface.',
      entries: catalog.mods.filter(m => selected.has(m.id)).map(m => ({
        id: m.id, name: m.name, scope: m.scope, source: m.source.url,
        verification: m.source.verification, availability: m.availability,
        redistribution: m.redistribution.status,
        requirements: [...m.requirements], requirements_complete: m.requirements_complete,
        notes: [...m.notes], downloaded: false
      }))
    };
  }
  function planText(plan) {
    return ['GHOST · Plano de pesquisa Black Desert → Skyrim SE/AE',
      `Catálogo ${plan.catalog_version} · Pesquisa ${plan.checked_on}`, plan.notice, '',
      ...plan.entries.map((m, i) => `${i + 1}. ${m.name}\n   ID: ${m.id}\n   Escopo: ${m.scope}\n   Fonte: ${m.source}\n   Evidência: ${m.verification}\n   Disponibilidade: ${m.availability}\n   Redistribuição: ${m.redistribution}\n   Requisitos anotados: ${m.requirements.join('; ') || 'não conferidos'}\n   Arquivo baixado por esta interface: NÃO\n`)
    ].join('\n');
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { normalize, matches, restoreSelection, exportPlan, planText };
  }
  if (typeof document === 'undefined') return;

  const { catalog, stats, labels } = JSON.parse(document.getElementById('catalog-data').textContent);
  const get = id => document.getElementById(id);
  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const external = (url, label, className) => {
    const a = el('a', label, className);
    a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer';
    return a;
  };
  const setStatus = value => { get('status').textContent = value; };
  let selected = new Set();
  let storageAvailable = true;
  try { selected = restoreSelection(localStorage.getItem(STORAGE_KEY), catalog.mods); }
  catch (_) { storageAvailable = false; }
  function persist() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify([...selected].sort())); }
    catch (_) { storageAvailable = false; }
    if (!storageAvailable) setStatus('O navegador não permite salvar a seleção local. Exporte TXT/JSON antes de fechar esta página.');
  }
  function selectionUI() {
    get('selection-count').textContent = `${selected.size} selecionado${selected.size === 1 ? '' : 's'}`;
    for (const id of ['export-txt', 'export-json', 'clear-selection']) get(id).disabled = selected.size === 0;
  }
  function makeCard(mod) {
    const card = el('article', undefined, 'card');
    card.id = 'mod-' + mod.id;
    const head = el('div', undefined, 'card-head');
    const top = el('div', undefined, 'card-top');
    top.append(el('span', labels.categories[mod.category], 'category'), el('span', labels.scopes[mod.scope], 'badge'));
    head.append(top, el('h3', mod.name), el('p', mod.summary, 'description'));
    head.append(el('p', `${mod.authors.join(' · ') || 'Autor não confirmado'} · ${mod.body.join(' / ') || 'Corpo não confirmado'}`, 'meta'));
    head.append(el('p', labels.methods[mod.source.verification] + ' · ' + mod.source.checked_on, 'meta'));
    head.append(el('p', labels.availability[mod.availability], 'meta'));
    head.append(el('p', labels.permissions[mod.redistribution.status], 'permission'));
    const actions = el('div', undefined, 'card-actions');
    const selectLabel = el('label', undefined, 'checklabel');
    const check = el('input'); check.type = 'checkbox'; check.checked = selected.has(mod.id);
    check.setAttribute('aria-label', 'Selecionar para pesquisa: ' + mod.name);
    check.addEventListener('change', () => {
      if (check.checked) selected.add(mod.id); else selected.delete(mod.id);
      persist(); selectionUI();
      if (get('only-selected').checked) render();
    });
    selectLabel.append(check, el('span', 'Selecionar para pesquisa'));
    actions.append(selectLabel, external(mod.source.url, mod.scope === 'historico' ? 'Ver referência ↗' : 'Consultar fonte ↗', 'button'));
    const details = el('details');
    const summary = el('summary', 'Requisitos, observações e evidências');
    const content = el('div', undefined, 'details-content');
    content.append(el('p', 'ID: ' + mod.id + ' · Família: ' + mod.family));
    content.append(el('p', 'Versão observada: ' + (mod.version_observed || 'não fixada / não conferida')));
    content.append(el('h4', 'Compatibilidade'), el('p', mod.runtime_note));
    content.append(el('h4', mod.requirements_complete ? 'Requisitos publicados consultados — conferir também os transitivos' : 'Requisitos parciais / não auditados'));
    const requirements = el('ul');
    for (const requirement of mod.requirements.length ? mod.requirements : ['Não conferidos integralmente. Lista vazia não significa ausência de dependências.']) requirements.append(el('li', requirement));
    content.append(requirements, el('h4', 'Observações'));
    const notes = el('ul');
    for (const note of mod.notes) notes.append(el('li', note));
    content.append(notes, el('h4', 'Permissão de redistribuição'), el('p', mod.redistribution.note));
    if (mod.redistribution.evidence_url) content.append(external(mod.redistribution.evidence_url, 'Consultar a evidência de permissão ↗'));
    if (mod.related_ids.length) {
      content.append(el('h4', 'Veja também — não é ordem de instalação'));
      for (const id of mod.related_ids) {
        const other = catalog.mods.find(m => m.id === id);
        const link = el('a', other.name);
        link.href = '#mod-' + id;
        link.addEventListener('click', event => {
          event.preventDefault(); resetFilters(false); get('scope').value = ''; get('query').value = id; render();
          const target = get('mod-' + id);
          if (target) { target.setAttribute('tabindex', '-1'); target.focus(); }
        });
        const relatedParagraph = el('p');
        relatedParagraph.append(link);
        content.append(relatedParagraph);
      }
    }
    content.append(el('h4', 'Fontes'));
    content.append(external(mod.source.url, `[${mod.source.search_result_id || 1}] ${mod.source.url}`));
    for (const evidence of mod.evidence) {
      const p = el('p', evidence.note + ' ');
      p.append(external(evidence.url, `[${evidence.search_result_id || 1}] ${evidence.url}`));
      content.append(p);
    }
    content.append(el('p', 'Arquivo de mod na release: não. Hash e tamanho do mod: desconhecidos.'));
    if (mod.external_site_may_show_adult_content) content.append(el('p', 'Aviso: o site externo pode exibir conteúdo adulto.', 'warning'));
    details.append(summary, content); card.append(head, actions, details);
    return card;
  }
  function render() {
    const filters = { query: get('query').value, category: get('category').value,
      scope: get('scope').value, body: get('body').value,
      verification: get('verification').value, onlySelected: get('only-selected').checked };
    const visible = catalog.mods.filter(mod => matches(mod, filters, selected));
    const fragment = document.createDocumentFragment();
    for (const mod of visible) fragment.append(makeCard(mod));
    get('cards').replaceChildren(fragment);
    get('results').textContent = `${visible.length} referência${visible.length === 1 ? '' : 's'} nesta visualização`;
    get('empty').hidden = visible.length > 0;
    selectionUI();
  }
  function resetFilters(redraw = true) {
    for (const id of ['query', 'category', 'body', 'verification']) get(id).value = '';
    get('scope').value = 'principal'; get('only-selected').checked = false;
    if (redraw) render();
  }
  function downloadPlan(format) {
    const plan = exportPlan(catalog, selected);
    const content = format === 'json' ? JSON.stringify(plan, null, 2) + '\n' : planText(plan);
    const url = URL.createObjectURL(new Blob([content], { type: format === 'json' ? 'application/json;charset=utf-8' : 'text/plain;charset=utf-8' }));
    const a = el('a'); a.href = url; a.download = 'ghost-minha-selecao.' + format;
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    setStatus(`Plano com ${plan.entries.length} referências exportado. Nenhum arquivo de mod foi baixado.`);
  }
  for (const [key, name] of Object.entries(labels.categories)) {
    const option = el('option', name); option.value = key; get('category').append(option);
  }
  for (const id of ['category', 'scope', 'body', 'verification', 'only-selected']) get(id).addEventListener('change', render);
  get('query').addEventListener('input', render);
  get('reset-filters').addEventListener('click', () => resetFilters());
  get('clear-selection').addEventListener('click', () => { selected.clear(); persist(); render(); });
  for (const format of ['txt', 'json']) get('export-' + format).addEventListener('click', () => {
    try { downloadPlan(format); }
    catch (_) { setStatus('Não foi possível exportar neste navegador. Use catalog/mods.csv ou tente outro navegador.'); }
  });
  get('total-records').textContent = stats.total;
  get('coverage').textContent = `${stats.scopes.principal || 0} principais · ${stats.scopes.pendente || 0} a aprofundar · ${stats.scopes.historico || 0} históricos`;
  get('version').textContent = `GHOST / Catálogo ${catalog.catalog_version} · Pesquisa ${catalog.checked_on} · Funciona offline`;
  if (!storageAvailable) setStatus('Seleção temporária: armazenamento local indisponível. Exporte sua seleção antes de fechar.');
  render();
})();
