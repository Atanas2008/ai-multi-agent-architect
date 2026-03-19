/* =========================================================================
   Simple Markdown → HTML renderer (no external deps)
   ========================================================================= */

const MarkdownRenderer = {
  render(md) {
    let html = md
      // Escape HTML first
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')

      // Tables
      .replace(/^\|(.+)\|$/gm, (_, row) => `<tr>${row.split('|').map(c => `<td>${c.trim()}</td>`).join('')}</tr>`)
      .replace(/^\|[-| :]+\|$/gm, '')
      .replace(/(<tr>.*<\/tr>\n?)+/gs, (block) => {
        const rows = block.trim().split('\n');
        if (!rows.length) return block;
        const header = rows[0].replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>');
        const body = rows.slice(1).join('\n');
        return `<table><thead>${header}</thead><tbody>${body}</tbody></table>`;
      })

      // Headings
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')

      // Blockquotes
      .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')

      // HR
      .replace(/^---+$/gm, '<hr>')

      // Bold / italic
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')

      // Inline code
      .replace(/`([^`]+)`/g, '<code>$1</code>')

      // Lists
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
      .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>\n?)+/gs, block => `<ul>${block}</ul>`)

      // Paragraphs
      .split('\n\n')
      .map(para => {
        para = para.trim();
        if (!para) return '';
        if (para.match(/^<(h[1-6]|ul|ol|hr|table|blockquote)/)) return para;
        return `<p>${para.replace(/\n/g, '<br>')}</p>`;
      })
      .join('\n');

    return html;
  }
};

/* =========================================================================
   Main Application Logic
   ========================================================================= */

const API_BASE = '';  // same origin; backend serves frontend

const state = {
  isLoading: false,
  result: null,
};

// ── DOM refs ────────────────────────────────────────────────────────────── //

const $ = (sel) => document.querySelector(sel);

const els = {
  textarea:     $('#query-textarea'),
  charCount:    $('#char-count'),
  submitBtn:    $('#submit-btn'),
  tryBtns:      document.querySelectorAll('[data-sample]'),
  steps:        document.querySelectorAll('.step-card'),
  contextPanel: $('#context-panel'),
  contextTags:  $('#context-tags'),
  resultPanel:  $('#result-panel'),
  resultScore:  $('#result-score'),
  resultMode:   $('#result-mode'),
  resultContent:$('#result-content'),
  copyBtn:      $('#copy-btn'),
  resetBtn:     $('#reset-btn'),
  demoBtn:      $('#demo-cta-btn'),
};

// ── Char counter ────────────────────────────────────────────────────────── //

els.textarea.addEventListener('input', () => {
  const n = els.textarea.value.length;
  els.charCount.textContent = `${n}/2000`;
  els.charCount.classList.toggle('warn', n > 1800);
});

// ── Sample queries ──────────────────────────────────────────────────────── //

els.tryBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    els.textarea.value = btn.dataset.sample;
    els.textarea.dispatchEvent(new Event('input'));
    els.textarea.focus();
    document.getElementById('pipeline').scrollIntoView({ behavior: 'smooth' });
  });
});

if (els.demoBtn) {
  els.demoBtn.addEventListener('click', () => {
    document.getElementById('pipeline').scrollIntoView({ behavior: 'smooth' });
  });
}

// ── Submit ──────────────────────────────────────────────────────────────── //

els.submitBtn.addEventListener('click', runPipeline);
els.textarea.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) runPipeline();
});

async function runPipeline() {
  const query = els.textarea.value.trim();
  if (!query) { shakeTextarea(); return; }
  if (state.isLoading) return;

  state.isLoading = true;
  els.submitBtn.disabled = true;
  els.submitBtn.textContent = 'Processing…';

  resetPipelineUI();

  try {
    // ── Step 1: Agent 1 ────────────────────────────────────────────── //
    setStepState(0, 'active', 'Classifying input…');
    const t0 = performance.now();
    const data = await postQuery(query);
    const totalMs = performance.now() - t0;

    // Agent 1 done
    setStepState(0, 'done', `Done · ${data.timings.agent1}s`);

    // ── Step 2: Agent 2 ────────────────────────────────────────────── //
    setStepState(1, 'done', `Done · ${data.timings.agent2}s`);

    // ── Step 3: Agent 3 ────────────────────────────────────────────── //
    setStepState(2, 'done', `Done · ${data.timings.agent3}s`);

    // ── Show context ───────────────────────────────────────────────── //
    renderContext(data.context);

    // ── Show result ────────────────────────────────────────────────── //
    renderResult(data);

    state.result = data;

  } catch (err) {
    setStepState(0, 'error', 'Error');
    setStepState(1, 'error', 'Skipped');
    setStepState(2, 'error', 'Skipped');
    showError(err.message);
  } finally {
    state.isLoading = false;
    els.submitBtn.disabled = false;
    els.submitBtn.textContent = 'Run Pipeline';
  }
}

// ── API call ─────────────────────────────────────────────────────────────── //

async function postQuery(query) {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || `HTTP ${res.status}`);
  return json;
}

// ── UI helpers ───────────────────────────────────────────────────────────── //

function resetPipelineUI() {
  els.steps.forEach(el => {
    el.classList.remove('active', 'done', 'error');
    el.querySelector('.step-info__status').textContent = 'Waiting…';
    const timing = el.querySelector('.step-timing');
    if (timing) timing.textContent = '';
  });
  els.contextPanel.classList.remove('visible');
  els.resultPanel.classList.remove('visible');
}

function setStepState(index, state, statusText, icon = null) {
  const card = els.steps[index];
  card.classList.remove('active', 'done', 'error');
  card.classList.add(state);
  card.querySelector('.step-info__status').textContent = statusText;
  if (icon) {
    const iconEl = card.querySelector('.step-icon');
    if (iconEl) iconEl.textContent = icon;
  }
}

function renderContext(ctx) {
  const tags = [
    ['Domain', ctx.domain],
    ['Intent', ctx.intent],
    ['Urgency', ctx.urgency],
    ['Complexity', ctx.complexity],
  ];
  els.contextTags.innerHTML = tags
    .map(([k, v]) => `<div class="context-tag"><span class="context-tag__key">${k}:</span><span class="context-tag__val">${v}</span></div>`)
    .join('');

  const summary = document.getElementById('context-summary');
  if (summary) summary.textContent = ctx.summary || '';

  els.contextPanel.classList.add('visible');
}

function renderResult(data) {
  els.resultScore.textContent = `Quality Score: ${data.quality_score}/10`;
  els.resultMode.textContent = data.mode === 'live' ? 'Live AI' : 'Demo Mode';
  els.resultMode.className = `result-mode result-mode--${data.mode === 'live' ? 'live' : 'demo'}`;
  els.resultContent.innerHTML = MarkdownRenderer.render(data.final_output);
  els.resultPanel.classList.add('visible');
  els.resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(msg) {
  els.resultPanel.classList.add('visible');
  els.resultContent.innerHTML = `<p style="color:#ef4444"><strong>Error:</strong> ${msg}</p>
    <p style="color:var(--text-muted)">Please check the backend server is running and try again.</p>`;
}

function shakeTextarea() {
  els.textarea.style.animation = 'none';
  els.textarea.offsetHeight; // Force reflow so the browser registers the animation reset before restarting it
  els.textarea.style.animation = 'shake 0.4s ease';
  setTimeout(() => { els.textarea.style.animation = ''; }, 400);
  els.textarea.focus();
}

// ── Copy ─────────────────────────────────────────────────────────────────── //

els.copyBtn.addEventListener('click', () => {
  if (!state.result) return;
  navigator.clipboard.writeText(state.result.final_output).then(() => {
    const orig = els.copyBtn.textContent;
    els.copyBtn.textContent = 'Copied';
    setTimeout(() => { els.copyBtn.textContent = orig; }, 2000);
  });
});

// ── Reset ─────────────────────────────────────────────────────────────────── //

els.resetBtn.addEventListener('click', () => {
  els.textarea.value = '';
  els.textarea.dispatchEvent(new Event('input'));
  state.result = null;
  resetPipelineUI();
  els.textarea.focus();
  document.getElementById('pipeline').scrollIntoView({ behavior: 'smooth' });
});

// ── Add shake keyframe ─────────────────────────────────────────────────── //
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%,100% { transform: translateX(0); }
    20%      { transform: translateX(-8px); }
    40%      { transform: translateX(8px); }
    60%      { transform: translateX(-6px); }
    80%      { transform: translateX(6px); }
  }
`;
document.head.appendChild(shakeStyle);
