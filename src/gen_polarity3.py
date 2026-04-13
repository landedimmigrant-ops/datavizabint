"""
gen_polarity3.py
Generate AbInt_Phase2_Dashboard.html from polarity_data3.json
4 views: Polarity Landscape | Coverage Map | Emergent Voice | Signal Cards
"""
import json, re

DATA_FILE = '/sessions/sweet-sharp-clarke/mnt/Data viz for program report/src/polarity_data3.json'
OUT_FILE  = '/sessions/sweet-sharp-clarke/mnt/Data viz for program report/AbInt_Phase2_Dashboard.html'

with open(DATA_FILE) as f:
    raw = json.load(f)

# Embed JSON safely
data_js = json.dumps(raw, ensure_ascii=True, separators=(',', ':'))

# All 5 research areas (include Multi-Agent Systems even if not in data)
ALL_AREAS = [
    {'id': 'language',     'title': 'Language',               'color': '#34d399'},
    {'id': 'storytelling', 'title': 'Storytelling',           'color': '#a78bfa'},
    {'id': 'env',          'title': 'Env. Stewardship',       'color': '#4ade80'},
    {'id': 'socio_neuro',  'title': 'Socio-Neuro AI',         'color': '#f97316'},
    {'id': 'multi_agent',  'title': 'Multi-Agent Systems',    'color': '#60a5fa'},
]
all_areas_js = json.dumps(ALL_AREAS, ensure_ascii=True, separators=(',', ':'))

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AbInt Phase 2 · Research Intelligence Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
:root {
  --bg:      #0c0e17;
  --surface: #141826;
  --surface2:#1c2235;
  --border:  #2a3050;
  --text:    #e2e8f0;
  --muted:   #64748b;
  --pos:     #4ade80;
  --neg:     #f87171;
  --warn:    #fbbf24;
  --accent:  #818cf8;
  --lang:    #34d399;
  --story:   #a78bfa;
  --env:     #4ade80;
  --socio:   #f97316;
  --multi:   #60a5fa;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; font-family: 'Inter', system-ui, sans-serif;
             background: var(--bg); color: var(--text); font-size: 14px; }
/* ── Header ── */
.app-header {
  padding: 14px 24px 10px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: baseline; gap: 12px;
}
.app-header h1 { font-size: 18px; font-weight: 700; letter-spacing: -.3px; }
.app-header .sub { font-size: 12px; color: var(--muted); }
/* ── Nav tabs ── */
.nav-tabs {
  display: flex; gap: 4px; padding: 10px 24px 0;
  border-bottom: 1px solid var(--border);
}
.nav-tab {
  padding: 8px 18px; border: none; background: transparent;
  color: var(--muted); cursor: pointer; border-bottom: 3px solid transparent;
  font-size: 13px; font-weight: 500; transition: all .15s;
}
.nav-tab:hover { color: var(--text); }
.nav-tab.active { color: var(--text); border-bottom-color: var(--accent); }
/* ── View containers ── */
.view { display: none; padding: 20px 24px; }
.view.active { display: block; }
/* ── Shared util ── */
.chip {
  display: inline-block; padding: 2px 8px; border-radius: 99px;
  font-size: 11px; font-weight: 600; letter-spacing: .3px;
}
.chip-pos  { background: rgba(74,222,128,.15); color: var(--pos); }
.chip-neg  { background: rgba(248,113,113,.15); color: var(--neg); }
.chip-warn { background: rgba(251,191,36,.15);  color: var(--warn); }
.chip-blue { background: rgba(129,140,248,.15); color: var(--accent); }
.chip-muted{ background: rgba(100,116,139,.15); color: var(--muted); }

/* ── Legend ── */
.legend { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 12px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.legend-dot  { width: 11px; height: 11px; border-radius: 50%; }

/* ── Tooltip ── */
#tooltip {
  position: fixed; pointer-events: none; z-index: 999;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 14px; max-width: 320px;
  font-size: 12px; line-height: 1.5; display: none;
  box-shadow: 0 8px 32px rgba(0,0,0,.5);
}
#tooltip h4 { font-size: 13px; font-weight: 700; margin-bottom: 6px; }
#tooltip .tt-row { display: flex; gap: 6px; align-items: baseline; margin: 2px 0; }
#tooltip .tt-label { color: var(--muted); min-width: 70px; }
#tooltip .phrases { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 8px; }
#tooltip .ph-chip {
  font-size: 10px; padding: 2px 7px; border-radius: 99px;
  background: rgba(129,140,248,.2); color: var(--accent);
}

/* ── Landscape View ── */
#landscape-svg { width: 100%; }
.quadrant-label { font-size: 11px; fill: #3a4460; font-weight: 600; pointer-events: none; }
.axis-label     { font-size: 11px; fill: var(--muted); }
.node-label     { font-size: 10px; fill: var(--text); pointer-events: none; }
.bubble         { cursor: pointer; transition: opacity .15s; }
.bubble:hover   { opacity: .85; }

/* ── Coverage Map ── */
#coverage-wrap { overflow-x: auto; }
.coverage-table { border-collapse: separate; border-spacing: 0; min-width: 900px; }
.coverage-table th, .coverage-table td {
  padding: 0; text-align: center;
}
.ct-row-header {
  text-align: right; padding-right: 14px; font-size: 12px; font-weight: 600;
  white-space: nowrap; padding-left: 8px;
  border-right: 1px solid var(--border);
}
.ct-col-header {
  font-size: 10px; color: var(--muted);
  white-space: nowrap; vertical-align: bottom;
  cursor: pointer;
}
.ct-col-header:hover { background: rgba(129,140,248,.06); }
.ct-cell {
  width: 68px; height: 56px;
  border: 1px solid rgba(42,48,80,.4);
  position: relative; cursor: default;
  transition: background .1s;
}
.ct-cell:hover { background: rgba(129,140,248,.06); }
.ct-cell svg { display: block; margin: auto; }
.ct-no-data {
  background: repeating-linear-gradient(
    135deg, rgba(255,255,255,.01), rgba(255,255,255,.01) 4px,
    transparent 4px, transparent 10px
  );
}
.ct-gap-row .ct-row-header { color: var(--neg); }
.ct-score-bar { height: 4px; border-radius: 2px; margin: 2px auto 0; }
.coverage-legend { display: flex; gap: 20px; margin: 12px 0 16px; font-size: 12px; align-items: center; }
.coverage-legend-item { display: flex; align-items: center; gap: 6px; }

/* ── Emergent Voice ── */
#voice-wrap { display: flex; gap: 24px; }
#voice-svg-wrap { flex: 1; min-height: 480px; }
#voice-detail {
  width: 280px; flex-shrink: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 16px;
}
#voice-detail h3 { font-size: 13px; font-weight: 700; margin-bottom: 10px; color: var(--accent); }
#voice-detail .vd-phrase { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
#voice-detail .vd-projects { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
#voice-detail .vd-proj {
  background: var(--surface2); border-radius: 8px; padding: 8px 10px;
  font-size: 11px;
}
#voice-detail .vd-proj strong { font-size: 12px; display: block; margin-bottom: 2px; }
.voice-bubble { cursor: pointer; }
.voice-bubble text { pointer-events: none; font-weight: 600; }

/* ── Signal Cards ── */
#cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
.signal-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px 16px; cursor: default;
  transition: border-color .15s;
}
.signal-card:hover { border-color: var(--accent); }
.sc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.sc-name { font-size: 13px; font-weight: 700; }
.sc-code { font-size: 11px; color: var(--muted); }
.sc-title { font-size: 11px; color: var(--muted); margin-bottom: 8px; line-height: 1.4; }
.sc-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.sc-scores { display: flex; gap: 12px; margin-bottom: 10px; }
.sc-score-block { text-align: center; }
.sc-score-num { font-size: 20px; font-weight: 800; line-height: 1; }
.sc-score-label { font-size: 10px; color: var(--muted); }
.sc-phrases { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 10px; }
.sc-phrase {
  font-size: 10px; padding: 2px 7px; border-radius: 99px;
  background: rgba(129,140,248,.15); color: var(--accent);
}
.sc-signal { margin-bottom: 6px; padding: 7px 9px; border-radius: 7px; font-size: 11px; line-height: 1.4; }
.sc-signal.pos { background: rgba(74,222,128,.07); border-left: 3px solid var(--pos); }
.sc-signal.neg { background: rgba(248,113,113,.07); border-left: 3px solid var(--neg); }
.sc-signal .src-tag { font-size: 10px; color: var(--muted); margin-bottom: 3px; }

/* ── Area summaries in Coverage tab ── */
.area-summary-bar {
  display: flex; gap: 12px; flex-wrap: wrap; margin-top: 20px;
}
.area-summary-card {
  flex: 1; min-width: 150px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 10px; padding: 12px;
}
.asc-name { font-size: 12px; font-weight: 700; margin-bottom: 4px; }
.asc-meta { font-size: 11px; color: var(--muted); margin-bottom: 6px; }
.asc-align { font-size: 22px; font-weight: 800; }
.asc-phrases { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 8px; }
.asc-gap { opacity: .5; border-style: dashed; }
.asc-gap .asc-align { color: var(--neg); }

/* ── Reviewer Intelligence ── */
#intel-layout { display: flex; gap: 20px; align-items: flex-start; }
#intel-phrases-panel {
  width: 220px; flex-shrink: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px;
  position: sticky; top: 0;
}
#intel-phrases-panel h4 { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 10px; }
.intel-phrase-tag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11px; padding: 4px 9px; border-radius: 99px;
  margin: 3px 2px; cursor: default;
  background: rgba(129,140,248,.12); color: var(--accent);
  border: 1px solid rgba(129,140,248,.2);
}
.intel-phrase-tag .itag-count {
  background: rgba(129,140,248,.25); border-radius: 99px;
  padding: 1px 5px; font-size: 10px; font-weight: 700;
}
#intel-main { flex: 1; min-width: 0; }
.intel-bucket { margin-bottom: 28px; }
.intel-bucket-header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 12px; padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.intel-bucket-icon { font-size: 18px; }
.intel-bucket-title { font-size: 14px; font-weight: 700; }
.intel-bucket-count { font-size: 11px; color: var(--muted); margin-left: auto; }
.intel-cards { display: flex; flex-direction: column; gap: 8px; }
.intel-card {
  border-radius: 10px; padding: 12px 14px;
  border-left: 4px solid transparent;
  font-size: 12px; line-height: 1.6;
  position: relative;
}
/* Colour per type */
.intel-card.recommendation {
  background: rgba(245,158,11,.08);
  border-left-color: #f59e0b;
}
.intel-card.question {
  background: rgba(34,211,238,.07);
  border-left-color: #22d3ee;
}
.intel-card.action {
  background: rgba(74,222,128,.07);
  border-left-color: #4ade80;
}
.intel-card.observation {
  background: rgba(167,139,250,.07);
  border-left-color: #a78bfa;
}
.intel-card-text { margin-bottom: 6px; color: var(--text); }
.intel-card-meta {
  display: flex; align-items: center; gap: 6px;
  font-size: 10px; color: var(--muted); flex-wrap: wrap;
}
.intel-area-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.intel-code {
  font-weight: 700; font-size: 10px;
  padding: 1px 6px; border-radius: 4px;
  background: var(--border);
}
.intel-filter-bar {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px;
}
.intel-filter-btn {
  font-size: 11px; padding: 5px 12px; border-radius: 99px;
  border: 1px solid var(--border); background: transparent;
  color: var(--muted); cursor: pointer; transition: all .15s;
}
.intel-filter-btn:hover { border-color: var(--accent); color: var(--text); }
.intel-filter-btn.active { color: var(--bg); }
.intel-filter-btn.f-all.active    { background: var(--accent); border-color: var(--accent); }
.intel-filter-btn.f-rec.active    { background: #f59e0b; border-color: #f59e0b; }
.intel-filter-btn.f-qst.active    { background: #22d3ee; border-color: #22d3ee; }
.intel-filter-btn.f-act.active    { background: #4ade80; border-color: #4ade80; }
.intel-filter-btn.f-obs.active    { background: #a78bfa; border-color: #a78bfa; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
</head>
<body>
<div id="tooltip"></div>

<div class="app-header">
  <h1>AbInt Phase 2 &mdash; Research Intelligence</h1>
  <span class="sub">10 projects &middot; 2 reviewers &middot; Imaginaries Axis</span>
</div>

<nav class="nav-tabs">
  <button class="nav-tab active" data-view="landscape">Polarity Landscape</button>
  <button class="nav-tab" data-view="coverage">Coverage Map</button>
  <button class="nav-tab" data-view="voice">Emergent Voice</button>
  <button class="nav-tab" data-view="cards">Signal Cards</button>
  <button class="nav-tab" data-view="intel">Reviewer Intelligence</button>
</nav>

<div id="view-landscape" class="view active"></div>
<div id="view-coverage"  class="view"></div>
<div id="view-voice"     class="view"></div>
<div id="view-cards"     class="view"></div>
<div id="view-intel"     class="view"></div>

<script>
// ── Data ──────────────────────────────────────────────────────────────────
const DATA = ''' + data_js + r''';
const ALL_AREAS = ''' + all_areas_js + r''';

const AREA_COLOR = {};
ALL_AREAS.forEach(function(a) { AREA_COLOR[a.id] = a.color; });
const AREA_NAME_TO_ID = {
  'Language': 'language', 'Storytelling': 'storytelling',
  'Env Stewardship': 'env', 'Environmental Stewardship': 'env',
  'Socio-Neuro AI': 'socio_neuro', 'Multi-Agent Systems': 'multi_agent',
  'Other': 'other', 'None': 'other'
};
function areaColor(name) {
  var id = AREA_NAME_TO_ID[name] || 'other';
  return AREA_COLOR[id] || '#64748b';
}
function areaId(name) { return AREA_NAME_TO_ID[name] || 'other'; }

// ── Display name: last name for people, short title for projects ──────────
function displayName(p) {
  var s = (p.short || '').trim();
  // "Title: subtitle..." → first 1-2 words before colon
  if (s.indexOf(':') > -1) {
    return s.split(':')[0].trim().split(' ').slice(0, 2).join(' ');
  }
  // "Project Name - Person Name" (space-dash-space = separator) → first 2 words
  if (s.indexOf(' - ') > -1) {
    return s.split(' - ')[0].trim().split(' ').slice(0, 2).join(' ');
  }
  // "Name, Institution" → last name from name segment
  if (s.indexOf(',') > -1) {
    var np = s.split(',')[0].trim().split(' ');
    return np[np.length - 1];
  }
  // "Name1 and Name2" → last names joined
  if (s.toLowerCase().indexOf(' and ') > -1) {
    return s.split(/\s+and\s+/i).map(function(n) {
      var parts = n.trim().split(' ');
      return parts[parts.length - 1];
    }).join(' & ');
  }
  // Simple person name → last word (handles hyphenated: Bellemare-Pepin)
  var parts = s.split(' ');
  return parts[parts.length - 1];
}

// ── Tooltip helpers ───────────────────────────────────────────────────────
var ttEl = document.getElementById('tooltip');
function showTT(html, x, y) {
  if (html !== null) ttEl.innerHTML = html;
  ttEl.style.display = 'block';
  var bw = document.documentElement.clientWidth;
  var bh = document.documentElement.clientHeight;
  var tw = ttEl.offsetWidth  || 300;
  var th = ttEl.offsetHeight || 180;
  var lx = x + 14;
  var ly = y - 10;
  if (lx + tw > bw - 10) lx = x - tw - 14;
  if (ly + th > bh - 10) ly = bh - th - 10;
  ttEl.style.left = lx + 'px';
  ttEl.style.top  = ly + 'px';
}
function hideTT() { ttEl.style.display = 'none'; }

// ── Tab switching ─────────────────────────────────────────────────────────
var rendered = {};
document.querySelectorAll('.nav-tab').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.nav-tab').forEach(function(b) { b.classList.remove('active'); });
    document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
    btn.classList.add('active');
    var v = btn.dataset.view;
    document.getElementById('view-' + v).classList.add('active');
    if (!rendered[v]) { rendered[v] = true; VIEWS[v](); }
  });
});

var VIEWS = {
  landscape: renderLandscape,
  coverage:  renderCoverage,
  voice:     renderVoice,
  cards:     renderCards,
  intel:     renderIntelligence
};

// ── VIEW 1: Polarity Landscape ────────────────────────────────────────────
function renderLandscape() {
  var el = document.getElementById('view-landscape');
  var projects = DATA.projects;

  // Compute adaptive midpoints
  var alignVals = projects.map(function(p) { return p.alignment_avg; });
  var riskVals  = projects.map(function(p) { return p.risk_score; });
  var midAlign  = (Math.min.apply(null,alignVals) + Math.max.apply(null,alignVals)) / 2;
  var midRisk   = (Math.min.apply(null,riskVals)  + Math.max.apply(null,riskVals))  / 2;

  var W = el.clientWidth || 860;
  var H = 500;
  var margin = { top: 40, right: 180, bottom: 60, left: 55 };
  var iw = W - margin.left - margin.right;
  var ih = H - margin.top  - margin.bottom;

  var xScale = d3.scaleLinear().domain([0, Math.max.apply(null,riskVals) * 1.15 + 0.02]).range([0, iw]);
  var yScale = d3.scaleLinear().domain([Math.min.apply(null,alignVals) - 0.5, 10.5]).range([ih, 0]);

  var svg = d3.select(el).append('svg')
    .attr('id', 'landscape-svg')
    .attr('viewBox', [0, 0, W, H].join(' '))
    .attr('preserveAspectRatio', 'xMidYMid meet');

  var g = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  // Quadrant backgrounds
  var cx = xScale(midRisk);
  var cy = yScale(midAlign);
  var quads = [
    {x:0,    y:0,    w:cx,    h:cy,    label:'Ready to Build On',       color:'rgba(74,222,128,.04)'},
    {x:cx,   y:0,    w:iw-cx, h:cy,    label:'High Potential\u2014Address Concerns',color:'rgba(251,191,36,.04)'},
    {x:0,    y:cy,   w:cx,    h:ih-cy, label:'Monitor Closely',         color:'rgba(129,140,248,.03)'},
    {x:cx,   y:cy,   w:iw-cx, h:ih-cy, label:'Significant Concerns',    color:'rgba(248,113,113,.04)'},
  ];
  quads.forEach(function(q) {
    g.append('rect').attr('x',q.x).attr('y',q.y).attr('width',q.w).attr('height',q.h)
      .attr('fill',q.color);
    g.append('text').attr('class','quadrant-label')
      .attr('x', q.x + q.w/2).attr('y', q.y + q.h/2)
      .attr('text-anchor','middle').attr('dominant-baseline','middle')
      .text(q.label);
  });

  // Divider lines
  g.append('line').attr('x1',cx).attr('x2',cx).attr('y1',0).attr('y2',ih)
    .attr('stroke','rgba(255,255,255,.08)').attr('stroke-dasharray','4,4');
  g.append('line').attr('x1',0).attr('x2',iw).attr('y1',cy).attr('y2',cy)
    .attr('stroke','rgba(255,255,255,.08)').attr('stroke-dasharray','4,4');

  // Axes
  g.append('g').attr('transform','translate(0,' + ih + ')')
    .call(d3.axisBottom(xScale).ticks(5).tickFormat(d3.format('.2f')))
    .call(function(a) {
      a.selectAll('path,line').attr('stroke','#2a3050');
      a.selectAll('text').attr('fill','#64748b').attr('font-size','11');
    });
  g.append('g')
    .call(d3.axisLeft(yScale).ticks(5))
    .call(function(a) {
      a.selectAll('path,line').attr('stroke','#2a3050');
      a.selectAll('text').attr('fill','#64748b').attr('font-size','11');
    });

  // Axis labels
  g.append('text').attr('class','axis-label')
    .attr('x', iw/2).attr('y', ih + 46).attr('text-anchor','middle')
    .text('Risk Signal \u2192 (from Risk column language)');
  g.append('text').attr('class','axis-label')
    .attr('transform','rotate(-90)').attr('x',-ih/2).attr('y',-42)
    .attr('text-anchor','middle').text('Alignment Score (1\u201310)');

  // AI depth radius scale
  var rScale = d3.scaleOrdinal()
    .domain(['None','Low','Mid','High'])
    .range([9, 12, 16, 20]);

  // Build node objects with target positions for force de-overlap
  var nodeData = projects.map(function(d) {
    return Object.assign({}, d, {
      tx: xScale(d.risk_score),
      ty: yScale(d.alignment_avg),
      x:  xScale(d.risk_score),
      y:  yScale(d.alignment_avg),
      r:  rScale(d.ai_depth),
    });
  });

  // Run force simulation synchronously to resolve overlaps
  var sim = d3.forceSimulation(nodeData)
    .force('x', d3.forceX(function(d) { return d.tx; }).strength(0.85))
    .force('y', d3.forceY(function(d) { return d.ty; }).strength(0.85))
    .force('collision', d3.forceCollide(function(d) { return d.r + 6; }).strength(1.0))
    .stop();
  for (var i = 0; i < 400; i++) sim.tick();

  var nodes = g.selectAll('.bubble')
    .data(nodeData).enter().append('g').attr('class','bubble')
    .attr('transform', function(d) {
      return 'translate(' + d.x + ',' + d.y + ')';
    });

  nodes.append('circle')
    .attr('r', function(d) { return d.r; })
    .attr('fill', function(d) { return areaColor(d.primary_area); })
    .attr('fill-opacity', .75)
    .attr('stroke', function(d) { return areaColor(d.primary_area); })
    .attr('stroke-width', 1.5);

  nodes.append('text').attr('class','node-label')
    .attr('y', function(d) { return -(d.r + 4); })
    .attr('text-anchor','middle')
    .text(function(d) { return displayName(d); });

  nodes.on('mousemove', function(event, d) {
    var phrases = (d.top_phrases || []).slice(0,5)
      .map(function(p) { return '<span class="ph-chip">' + p + '</span>'; }).join('');
    var pos0 = d.positives && d.positives[0]
      ? '<div style="margin-top:6px;font-size:11px;color:#4ade80">\u2713 ' + d.positives[0].text.slice(0,90) + '\u2026</div>'
      : '';
    var neg0 = d.concerns && d.concerns[0]
      ? '<div style="font-size:11px;color:#f87171">\u25B3 ' + d.concerns[0].text.slice(0,90) + '\u2026</div>'
      : '';
    var html = '<h4>' + d.short + (d.code ? ' <span style="color:#64748b;font-weight:400;font-size:11px">' + d.code + '</span>' : '') + '</h4>'
      + '<div style="font-size:11px;color:#a78bfa;margin-bottom:4px">' + d.title.slice(0,80) + '</div>'
      + '<div class="tt-row"><span class="tt-label">Area</span> <span>' + d.primary_area + '</span></div>'
      + '<div class="tt-row"><span class="tt-label">Status</span> <span>' + d.status + '</span></div>'
      + '<div class="tt-row"><span class="tt-label">AI Depth</span> <span>' + d.ai_depth + '</span></div>'
      + '<div class="tt-row"><span class="tt-label">Alignment</span> <strong style="color:#4ade80">' + d.alignment_avg + '/10</strong></div>'
      + '<div class="tt-row"><span class="tt-label">Risk</span> <strong style="color:#fbbf24">' + d.risk_score + '</strong></div>'
      + (phrases ? '<div class="phrases">' + phrases + '</div>' : '')
      + pos0 + neg0;
    showTT(html, event.clientX, event.clientY);
  }).on('mouseleave', hideTT);

  // Legend
  var legG = svg.append('g').attr('transform','translate(' + (W - margin.right + 14) + ',' + margin.top + ')');
  legG.append('text').attr('y',-4).attr('fill','#64748b').attr('font-size','11').text('Research Area');

  var legData = DATA.research_areas.concat(
    ALL_AREAS.filter(function(a) {
      return !DATA.research_areas.find(function(ra) { return ra.id === a.id; });
    }).map(function(a) { return {id: a.id, title: a.title, color: a.color, _gap: true}; })
  );
  legData.forEach(function(a, i) {
    var ly = 12 + i * 22;
    legG.append('circle').attr('cx', 7).attr('cy', ly).attr('r', 7)
      .attr('fill', a.color).attr('fill-opacity', a._gap ? 0.2 : 0.75);
    legG.append('text').attr('x', 18).attr('y', ly + 4)
      .attr('fill', a._gap ? '#f87171' : '#e2e8f0').attr('font-size', '11')
      .text(a.title + (a._gap ? ' (not reviewed)' : ''));
  });

  var ly2 = 12 + legData.length * 22 + 14;
  legG.append('text').attr('y', ly2 - 4).attr('fill','#64748b').attr('font-size','11').text('AI Depth');
  [['None',9],['Low',12],['Mid',16],['High',20]].forEach(function(pair, i) {
    var lly = ly2 + 12 + i * 22;
    legG.append('circle').attr('cx', pair[1]).attr('cy', lly).attr('r', pair[1])
      .attr('fill','#64748b').attr('fill-opacity', .4);
    legG.append('text').attr('x', 26).attr('y', lly + 4)
      .attr('fill','#64748b').attr('font-size','11').text(pair[0]);
  });
}

// ── Pod & infra constants ─────────────────────────────────────────────────
var POD_COLORS = {
  'Niitsitapi Pod':           '#fbbf24',
  "Ka Hawai'i Pae '\u0100ina Pod": '#38bdf8',
  "T'karonto Pod":            '#34d399',
  "Wih\u00e1\u014bble S\u2019a Pod": '#c084fc',
  'Hiringa Te Mara':          '#fb7185',
  'Haudenosaunee Pod':        '#a78bfa',
  'Podless':                  '#475569',
};
function podColor(pod) { return POD_COLORS[pod] || '#475569'; }

var INFRA_COLORS = {
  'Public':       '#4ade80',
  'AbInt Network':'#818cf8',
  'Pod':          '#fbbf24',
  'None':         '#1e293b',
};
var INFRA_DESC = {
  'Public':       'Shareable publicly',
  'AbInt Network':'Shareable across AbInt Network',
  'Pod':          'Shareable within pod',
  'None':         'Not yet designated',
};
function infraColor(v) { return INFRA_COLORS[v] || '#1e293b'; }

// ── VIEW 2: Coverage Map ──────────────────────────────────────────────────
function renderCoverage() {
  var el = document.getElementById('view-coverage');
  var projects = DATA.projects.slice().sort(function(a,b) { return b.alignment_avg - a.alignment_avg; });

  var areaDataMap = {};
  DATA.research_areas.forEach(function(a) { areaDataMap[a.id] = a; });

  function projectAreaType(proj, areaId) {
    if (areaId === AREA_NAME_TO_ID[proj.primary_area])   return 'primary';
    if (areaId === AREA_NAME_TO_ID[proj.secondary_area]) return 'secondary';
    return 'none';
  }

  // ── Legend row 1: Coverage symbols ────────────────────────────
  var legendHTML = '<div style="display:flex;flex-wrap:wrap;gap:24px;margin-bottom:14px;align-items:flex-start">';

  // Coverage circles
  legendHTML += '<div><div style="font-size:11px;font-weight:700;color:#64748b;margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">Circle type</div>'
    + '<div style="display:flex;flex-direction:column;gap:6px">'
    + '<span style="display:flex;align-items:center;gap:7px;font-size:12px">'
    + '<svg width="22" height="22"><circle cx="11" cy="11" r="9" fill="#a78bfa" fill-opacity=".7"/><text x="11" y="15" text-anchor="middle" fill="#fff" font-size="9" font-weight="700">9</text></svg>'
    + 'Primary research area (score inside)</span>'
    + '<span style="display:flex;align-items:center;gap:7px;font-size:12px">'
    + '<svg width="22" height="22"><circle cx="11" cy="11" r="8" fill="none" stroke="#a78bfa" stroke-width="2" stroke-opacity=".7"/><text x="11" y="15" text-anchor="middle" fill="#a78bfa" font-size="9">9</text></svg>'
    + 'Secondary area</span>'
    + '<span style="display:flex;align-items:center;gap:7px;font-size:12px">'
    + '<svg width="22" height="22"><circle cx="11" cy="11" r="4" fill="#2a3050"/></svg>'
    + 'Not in area</span>'
    + '</div></div>';

  // Pod legend
  var usedPods = [];
  var seenPods = {};
  projects.forEach(function(p) { if (p.pod && !seenPods[p.pod]) { seenPods[p.pod] = true; usedPods.push(p.pod); } });
  usedPods.push('Podless');

  legendHTML += '<div><div style="font-size:11px;font-weight:700;color:#64748b;margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">Pod (column top strip)</div>'
    + '<div style="display:flex;flex-direction:column;gap:5px">';
  usedPods.forEach(function(pod) {
    var count = projects.filter(function(p) { return p.pod === pod; }).length;
    if (!count) return;
    legendHTML += '<span style="display:flex;align-items:center;gap:7px;font-size:12px">'
      + '<span style="display:inline-block;width:28px;height:6px;background:' + podColor(pod) + ';border-radius:3px"></span>'
      + pod + ' <span style="color:#64748b">(' + count + ')</span></span>';
  });
  legendHTML += '</div></div>';

  // Infra sharability legend
  legendHTML += '<div><div style="font-size:11px;font-weight:700;color:#64748b;margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">Infrastructure sharability (coloured dot)</div>'
    + '<div style="display:flex;flex-direction:column;gap:5px">';
  ['Public','AbInt Network','Pod','None'].forEach(function(v) {
    var border = v === 'None' ? 'border:1.5px solid #334155;' : '';
    legendHTML += '<span style="display:flex;align-items:center;gap:7px;font-size:12px">'
      + '<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:' + infraColor(v) + ';' + border + '"></span>'
      + '<strong>' + v + '</strong> \u2014 ' + INFRA_DESC[v] + '</span>';
  });
  legendHTML += '</div></div>';

  legendHTML += '</div>';

  // ── Column headers: pod strip + infra dot + code + name ───────
  var tableHTML = '<div id="coverage-wrap" style="overflow-x:auto"><table class="coverage-table"><thead><tr>'
    + '<th class="ct-row-header" style="border:none;min-width:160px"></th>';

  projects.forEach(function(p) {
    var pc = podColor(p.pod);
    var ic = infraColor(p.infra_share || 'None');
    var infraBorder = (p.infra_share === 'None') ? 'border:1.5px solid #334155;' : '';
    tableHTML += '<th class="ct-col-header" data-pid="' + p.id.replace(/"/g, '') + '" style="cursor:pointer;vertical-align:bottom;padding:0 2px 6px;width:72px">'
      // Pod strip — full width coloured bar
      + '<div style="height:6px;background:' + pc + ';border-radius:3px 3px 0 0;margin-bottom:5px;opacity:.9"></div>'
      // Infra dot
      + '<div style="display:flex;justify-content:center;margin-bottom:4px">'
      + '<span title="' + (p.infra_share || 'None') + '" style="display:inline-block;width:11px;height:11px;border-radius:50%;background:' + ic + ';' + infraBorder + '"></span>'
      + '</div>'
      // Code + first name (not rotated — compact)
      + '<div style="font-size:10px;font-weight:700;text-align:center;color:#e2e8f0;line-height:1.2">' + displayName(p) + '</div>'
      + '</th>';
  });

  tableHTML += '<th style="width:36px;font-size:11px;color:#64748b;padding:4px 6px;text-align:left;vertical-align:bottom">n</th>'
    + '<th style="width:76px;font-size:11px;color:#64748b;padding:4px 6px;text-align:left;vertical-align:bottom">Avg&nbsp;Align</th>'
    + '</tr></thead><tbody>';

  // ── Area rows ──────────────────────────────────────────────────
  ALL_AREAS.forEach(function(area) {
    var hasData = !!areaDataMap[area.id];
    var rowClass = hasData ? '' : ' ct-gap-row';
    tableHTML += '<tr class="' + rowClass + '">';
    tableHTML += '<td class="ct-row-header" style="color:' + area.color + '">' + area.title + '</td>';

    projects.forEach(function(proj) {
      var type = projectAreaType(proj, area.id);
      var alignOpacity = (proj.alignment_avg - 4) / 6;
      var cellBg = type !== 'none'
        ? 'background:rgba(' + hexToRgb(area.color) + ',' + (alignOpacity * 0.18).toFixed(2) + ')'
        : '';

      tableHTML += '<td class="ct-cell' + (type === 'none' ? ' ct-no-data' : '') + '" style="' + cellBg + '">';
      if (type === 'primary') {
        tableHTML += '<svg width="46" height="50">'
          + '<circle cx="23" cy="26" r="17" fill="' + area.color + '" fill-opacity=".7"/>'
          + '<text x="23" y="30" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">'
          + proj.alignment_avg + '</text>'
          + '</svg>';
      } else if (type === 'secondary') {
        tableHTML += '<svg width="46" height="50">'
          + '<circle cx="23" cy="26" r="13" fill="none" stroke="' + area.color + '" stroke-width="2" stroke-opacity=".7"/>'
          + '<text x="23" y="30" text-anchor="middle" fill="' + area.color + '" font-size="10" fill-opacity=".8">'
          + proj.alignment_avg + '</text>'
          + '</svg>';
      } else {
        tableHTML += '<svg width="46" height="50">'
          + '<circle cx="23" cy="26" r="4" fill="#2a3050"/>'
          + '</svg>';
      }
      tableHTML += '</td>';
    });

    var aData = areaDataMap[area.id];
    if (aData) {
      var barW = Math.round((aData.alignment_avg / 10) * 60);
      tableHTML += '<td style="padding:4px 6px;font-size:12px;color:#64748b">' + aData.n_projects + '</td>'
        + '<td style="padding:4px 6px"><div style="font-size:13px;font-weight:700;color:' + area.color + '">'
        + aData.alignment_avg + '</div>'
        + '<div style="width:' + barW + 'px;height:3px;background:' + area.color + ';border-radius:2px;opacity:.5;margin-top:3px"></div>'
        + '</td>';
    } else {
      tableHTML += '<td colspan="2" style="padding:4px 8px;font-size:11px;color:#f87171">Not yet reviewed</td>';
    }
    tableHTML += '</tr>';
  });

  // Alignment score footer row
  tableHTML += '<tr><td class="ct-row-header" style="color:#64748b;font-size:11px">Alignment</td>';
  projects.forEach(function(p) {
    var sc = p.alignment_avg >= 8.5 ? '#4ade80' : (p.alignment_avg >= 7 ? '#fbbf24' : '#f87171');
    tableHTML += '<td style="text-align:center;padding:5px 0">'
      + '<span style="font-size:13px;font-weight:800;color:' + sc + '">' + p.alignment_avg + '</span>'
      + '</td>';
  });
  tableHTML += '<td></td><td></td></tr>';
  tableHTML += '</tbody></table></div>';

  // ── TS Dimensions table ────────────────────────────────────────
  var dimHTML = '<div style="margin-top:28px"><h3 style="font-size:13px;font-weight:700;margin-bottom:10px;color:#818cf8">'
    + 'Transformation Statement Coverage</h3>'
    + '<p style="font-size:11px;color:#64748b;margin-bottom:12px">Bar width = how strongly reviewer language maps onto each TS dimension.</p>'
    + '<div style="overflow-x:auto"><table class="coverage-table"><thead><tr>'
    + '<th class="ct-row-header" style="border:none;min-width:160px"></th>';

  projects.forEach(function(p) {
    dimHTML += '<th style="font-size:10px;color:#64748b;padding:4px 2px;text-align:center;width:72px">' + displayName(p) + '</th>';
  });
  dimHTML += '</tr></thead><tbody>';

  DATA.ts_dimensions.forEach(function(dim) {
    dimHTML += '<tr><td class="ct-row-header" style="font-size:11px;color:#94a3b8">' + dim.label + '</td>';
    projects.forEach(function(p) {
      var score = (DATA.ts_project_scores[p.id] || {})[dim.id] || 0;
      var opacity = Math.max(0.07, score * 2);
      var barW = Math.round(score * 52);
      dimHTML += '<td style="padding:6px 2px;text-align:center">';
      if (score > 0.05) {
        dimHTML += '<div style="background:#818cf8;opacity:' + opacity.toFixed(2)
          + ';height:7px;border-radius:4px;width:' + barW + 'px;margin:0 auto"></div>';
      } else {
        dimHTML += '<div style="background:#1c2235;height:7px;border-radius:4px;width:22px;margin:0 auto"></div>';
      }
      dimHTML += '</td>';
    });
    dimHTML += '</tr>';
  });
  dimHTML += '</tbody></table></div></div>';

  // ── Area summary cards ─────────────────────────────────────────
  var cardHTML = '<div class="area-summary-bar" style="margin-top:24px">';
  ALL_AREAS.forEach(function(area) {
    var aData = areaDataMap[area.id];
    var phrases = aData ? (aData.top_phrases || []).slice(0,3) : [];
    var isGap = !aData;
    cardHTML += '<div class="area-summary-card' + (isGap ? ' asc-gap' : '') + '" style="border-color:' + area.color + '40">'
      + '<div class="asc-name" style="color:' + area.color + '">' + area.title + '</div>'
      + '<div class="asc-meta">' + (aData ? aData.n_projects + ' reviewed project' + (aData.n_projects > 1 ? 's' : '') : '&#9650; Not reviewed') + '</div>'
      + '<div class="asc-align" style="color:' + area.color + '">' + (aData ? aData.alignment_avg + '<small style="font-size:12px;color:#64748b">/10</small>' : '&mdash;') + '</div>'
      + '<div class="asc-phrases">'
      + phrases.map(function(ph) {
          return '<span style="font-size:10px;padding:2px 7px;border-radius:99px;background:rgba(' + hexToRgb(area.color) + ',.15);color:' + area.color + '">' + ph + '</span>';
        }).join('')
      + '</div>'
      + '</div>';
  });
  cardHTML += '</div>';

  el.innerHTML = legendHTML + tableHTML + dimHTML + cardHTML;

  // ── Attach hover tooltips to column headers (after innerHTML set) ──
  el.querySelectorAll('[data-pid]').forEach(function(th) {
    var pid = th.dataset.pid;
    // Match pid loosely (the id has special chars that may be partially trimmed)
    var proj = DATA.projects.find(function(p) {
      return p.id.replace(/"/g,'') === pid || p.code === pid;
    });
    if (!proj) return;

    th.addEventListener('mouseenter', function(event) {
      var pc = podColor(proj.pod);
      var ic = infraColor(proj.infra_share || 'None');
      var infraBorder = (proj.infra_share === 'None') ? 'border:1.5px solid #334155;' : '';
      var phraseChips = (proj.top_phrases || []).slice(0,4)
        .map(function(ph) { return '<span class="ph-chip">' + ph + '</span>'; }).join('');

      var html = '<h4 style="line-height:1.35">' + proj.title + '</h4>'
        + '<div style="font-size:11px;color:#64748b;margin-bottom:8px">' + proj.short + ' &middot; ' + proj.code + '</div>'
        + '<div class="tt-row"><span class="tt-label">Pod</span>'
        + '<span style="display:inline-flex;align-items:center;gap:5px">'
        + '<span style="width:10px;height:10px;border-radius:50%;background:' + pc + ';display:inline-block"></span>'
        + proj.pod + '</span></div>'
        + '<div class="tt-row"><span class="tt-label">Type</span><span>' + (proj.type || 'CfP') + '</span></div>'
        + '<div class="tt-row"><span class="tt-label">Status</span><span>' + proj.status + '</span></div>'
        + '<div class="tt-row"><span class="tt-label">AI Depth</span><span>' + proj.ai_depth + '</span></div>'
        + '<div class="tt-row"><span class="tt-label">Infra share</span>'
        + '<span style="display:inline-flex;align-items:center;gap:5px">'
        + '<span style="width:10px;height:10px;border-radius:50%;background:' + ic + ';' + infraBorder + ';display:inline-block"></span>'
        + (proj.infra_share || 'None') + '</span></div>';
      if (proj.sharable_method && proj.sharable_method !== 'None') {
        html += '<div class="tt-row"><span class="tt-label">Meth. share</span><span>' + proj.sharable_method + '</span></div>';
      }
      html += '<div class="tt-row"><span class="tt-label">Alignment</span>'
        + '<strong style="color:#4ade80">' + proj.alignment_avg + '/10</strong></div>';
      if (phraseChips) html += '<div class="phrases" style="margin-top:7px">' + phraseChips + '</div>';

      showTT(html, event.clientX, event.clientY);
    });
    th.addEventListener('mousemove', function(event) {
      showTT(null, event.clientX, event.clientY);
    });
    th.addEventListener('mouseleave', hideTT);
  });

  // Update showTT to support position-only calls
  var _origShowTT = showTT;
  showTT = function(html, x, y) {
    if (html !== null) ttEl.innerHTML = html;
    ttEl.style.display = 'block';
    var bw = document.documentElement.clientWidth;
    var bh = document.documentElement.clientHeight;
    var tw = ttEl.offsetWidth  || 300;
    var th2 = ttEl.offsetHeight || 180;
    var lx = x + 14;
    var ly = y - 10;
    if (lx + tw > bw - 10) lx = x - tw - 14;
    if (ly + th2 > bh - 10) ly = bh - th2 - 10;
    ttEl.style.left = lx + 'px';
    ttEl.style.top  = ly + 'px';
  };
}

// ── VIEW 3: Emergent Voice ────────────────────────────────────────────────
function renderVoice() {
  var el = document.getElementById('view-voice');
  var themes = DATA.research_themes || [];

  el.innerHTML =
    '<div style="margin-bottom:10px">'
    + '<h3 style="font-size:13px;font-weight:700;color:#64748b;margin-bottom:3px">'
    + 'Research themes interpreted from reviewer language &mdash; not predefined categories.'
    + '</h3>'
    + '<p style="font-size:11px;color:#475569;line-height:1.5">'
    + 'Bubble size = number of <strong>unique reviewers</strong> who touched this theme. '
    + 'Dashed border = pattern surfaced automatically, not yet named. Click any bubble to explore.'
    + '</p></div>'
    + '<div id="voice-wrap">'
    + '<div id="voice-svg-wrap"></div>'
    + '<div id="voice-detail">'
    + '<div style="font-size:12px;color:#64748b;line-height:1.7;padding-top:8px">'
    + 'Select a theme to see which reviewers touched it, the phrases they used, and key sentences.'
    + '</div></div></div>';

  var svgWrap = document.getElementById('voice-svg-wrap');
  var W = svgWrap.clientWidth || 560;
  var H = 460;

  // Scale: bubble size = unique reviewer count (relational — all sizes matter)
  var maxRev = d3.max(themes, function(t) { return t.n_reviewers; }) || 1;
  var minRev = d3.min(themes, function(t) { return t.n_reviewers; }) || 1;
  // Use sqrt scale so smallest is still visible, largest doesn't overwhelm
  var rScale = d3.scaleSqrt()
    .domain([minRev, maxRev])
    .range([32, 72]);

  var nodes = themes.map(function(t, i) {
    var angle = (i / themes.length) * 2 * Math.PI;
    var spread = 120;
    return {
      id:          t.id,
      label:       t.label,
      color:       t.color,
      desc:        t.desc,
      n_reviewers: t.n_reviewers,
      reviewers:   t.reviewers || [],
      n_projects:  t.n_projects,
      projects:    t.projects || [],
      phrases:     t.phrases || [],
      sentences:   t.sentences || [],
      emerging:    t.emerging || false,
      r:           rScale(t.n_reviewers),
      x:           W/2 + Math.cos(angle) * spread,
      y:           H/2 + Math.sin(angle) * spread,
    };
  });

  var svg = d3.select(svgWrap).append('svg')
    .attr('width', W).attr('height', H);

  var sim = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(6))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide(function(d) { return d.r + 8; }).strength(0.92))
    .force('x', d3.forceX(W/2).strength(0.03))
    .force('y', d3.forceY(H/2).strength(0.04));

  var bubb = svg.selectAll('.voice-bubble')
    .data(nodes).enter().append('g').attr('class','voice-bubble')
    .style('cursor','pointer');

  // Circle — dashed stroke for emerging themes
  bubb.append('circle')
    .attr('r', function(d) { return d.r; })
    .attr('fill', function(d) { return d.color; })
    .attr('fill-opacity', .15)
    .attr('stroke', function(d) { return d.color; })
    .attr('stroke-width', function(d) { return d.emerging ? 1.5 : 2; })
    .attr('stroke-dasharray', function(d) { return d.emerging ? '5,3' : 'none'; })
    .attr('stroke-opacity', .8);

  // Theme label — wrap long labels onto two lines
  bubb.each(function(d) {
    var g = d3.select(this);
    var words = d.label.split(' ');
    var mid = Math.ceil(words.length / 2);
    var line1 = words.slice(0, mid).join(' ');
    var line2 = words.slice(mid).join(' ');
    var fs = Math.max(8, Math.min(12, d.r * 0.28));
    if (line2) {
      g.append('text').attr('text-anchor','middle').attr('dominant-baseline','middle')
        .attr('y', -fs * 0.7).attr('fill', d.color).attr('font-size', fs)
        .attr('font-weight','700').attr('pointer-events','none').text(line1);
      g.append('text').attr('text-anchor','middle').attr('dominant-baseline','middle')
        .attr('y', fs * 0.7).attr('fill', d.color).attr('font-size', fs)
        .attr('font-weight','700').attr('pointer-events','none').text(line2);
    } else {
      g.append('text').attr('text-anchor','middle').attr('dominant-baseline','middle')
        .attr('fill', d.color).attr('font-size', fs)
        .attr('font-weight','700').attr('pointer-events','none').text(line1);
    }
    // Reviewer count badge
    g.append('text').attr('text-anchor','middle').attr('dominant-baseline','middle')
      .attr('y', d.r - 13).attr('fill', d.color).attr('font-size', 9)
      .attr('opacity', .75).attr('pointer-events','none')
      .text(d.n_reviewers + (d.n_reviewers === 1 ? ' reviewer' : ' reviewers'));
  });

  sim.on('tick', function() {
    bubb.attr('transform', function(d) {
      d.x = Math.max(d.r + 6, Math.min(W - d.r - 6, d.x));
      d.y = Math.max(d.r + 6, Math.min(H - d.r - 6, d.y));
      return 'translate(' + d.x + ',' + d.y + ')';
    });
  });

  bubb.on('click', function(event, d) {
    bubb.selectAll('circle').attr('fill-opacity', .07).attr('stroke-opacity', .3);
    d3.select(this).select('circle').attr('fill-opacity', .28).attr('stroke-opacity', 1);

    var detail = document.getElementById('voice-detail');

    // Phrases as tags
    var phraseTags = (d.phrases || []).map(function(ph) {
      return '<span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:99px;'
        + 'background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);'
        + 'margin:2px;color:#94a3b8">' + ph + '</span>';
    }).join('');

    // Reviewer list
    var revList = (d.reviewers || []).map(function(rv) {
      return '<span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:99px;'
        + 'background:' + d.color + '22;color:' + d.color + ';margin:2px">' + rv + '</span>';
    }).join('');

    // Key sentences (up to 3)
    var sentHTML = (d.sentences || []).slice(0, 3).map(function(s) {
      var polColor = s.polarity === 'positive' ? '#4ade80' : s.polarity === 'concern' ? '#f87171' : '#94a3b8';
      var polIcon  = s.polarity === 'positive' ? '\u25B2' : s.polarity === 'concern' ? '\u25BC' : '\u25CF';
      return '<div style="padding:8px 10px;border-radius:8px;background:rgba(255,255,255,.04);'
        + 'border-left:3px solid ' + d.color + ';margin-bottom:6px;font-size:11px;line-height:1.5;">'
        + '<div style="color:var(--text)">' + s.text + '</div>'
        + '<div style="font-size:10px;color:#64748b;margin-top:4px">'
        + '<span style="color:' + polColor + '">' + polIcon + '</span> '
        + s.reviewer + ' &middot; <strong style="color:#94a3b8">' + s.code + '</strong>'
        + '</div></div>';
    }).join('');

    var emBadge = d.emerging
      ? '<span style="font-size:10px;padding:2px 8px;border-radius:99px;border:1px dashed #94a3b8;color:#94a3b8;margin-left:6px">auto-detected</span>'
      : '';

    detail.innerHTML =
      '<div style="border-left:3px solid ' + d.color + ';padding-left:10px;margin-bottom:10px">'
      + '<div style="font-size:15px;font-weight:700;color:' + d.color + '">' + d.label + emBadge + '</div>'
      + '<div style="font-size:11px;color:#64748b;margin-top:3px">' + d.desc + '</div>'
      + '</div>'
      + '<div style="font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Reviewers</div>'
      + '<div style="margin-bottom:10px">' + revList + '</div>'
      + (phraseTags ? '<div style="font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Phrases</div>'
          + '<div style="margin-bottom:10px">' + phraseTags + '</div>' : '')
      + (sentHTML ? '<div style="font-size:10px;color:#64748b;margin-bottom:6px;text-transform:uppercase;letter-spacing:.05em">Reviewer Sentences</div>'
          + sentHTML : '');
  });
}

// ── VIEW 4: Signal Cards ──────────────────────────────────────────────────
function renderCards() {
  var el = document.getElementById('view-cards');
  var projects = DATA.projects.slice().sort(function(a,b) { return b.alignment_avg - a.alignment_avg; });

  var html = '<div id="cards-grid">';
  projects.forEach(function(p) {
    var acolor = areaColor(p.primary_area);
    var alignColor = p.alignment_avg >= 8.5 ? '#4ade80' : (p.alignment_avg >= 7 ? '#fbbf24' : '#f87171');
    var riskColor  = p.risk_score < 0.1 ? '#4ade80' : (p.risk_score < 0.25 ? '#fbbf24' : '#f87171');

    var statusChip = '';
    if (p.status === 'Completed')  statusChip = '<span class="chip chip-pos">Completed</span>';
    else if (p.status === 'Mid-Point') statusChip = '<span class="chip chip-warn">Mid-Point</span>';
    else if (p.status === 'Beginning') statusChip = '<span class="chip chip-blue">Beginning</span>';

    var aiChip = p.ai_depth !== 'None'
      ? '<span class="chip chip-muted">AI: ' + p.ai_depth + '</span>' : '';
    var ikChip = p.ik_methods && p.ik_methods !== 'None'
      ? '<span class="chip chip-blue">IK: ' + p.ik_methods + '</span>' : '';
    var areaChip = '<span class="chip" style="background:rgba(' + hexToRgb(acolor) + ',.15);color:' + acolor + '">'
      + p.primary_area + '</span>';

    var phrases = (p.top_phrases || []).slice(0, 4).map(function(ph) {
      return '<span class="sc-phrase">' + ph + '</span>';
    }).join('');

    var pos0 = p.positives && p.positives[0]
      ? '<div class="sc-signal pos"><div class="src-tag">'
        + p.positives[0].reviewer + ' &middot; ' + p.positives[0].source + '</div>'
        + p.positives[0].text.slice(0, 100) + '\u2026</div>'
      : '';
    var neg0 = p.concerns && p.concerns[0]
      ? '<div class="sc-signal neg"><div class="src-tag">'
        + p.concerns[0].reviewer + ' &middot; ' + p.concerns[0].source + '</div>'
        + p.concerns[0].text.slice(0, 100) + '\u2026</div>'
      : '';

    var reviewers = (p.reviewers || []).join(', ');

    html += '<div class="signal-card" style="border-top:3px solid ' + acolor + '">'
      + '<div class="sc-header">'
      + '<div><div class="sc-name">' + p.short + '</div>'
      + '<div class="sc-code">' + p.code + '</div></div>'
      + '<div class="sc-scores">'
      + '<div class="sc-score-block"><div class="sc-score-num" style="color:' + alignColor + '">'
      + p.alignment_avg + '</div><div class="sc-score-label">Align</div></div>'
      + '<div class="sc-score-block"><div class="sc-score-num" style="color:' + riskColor + ';font-size:15px">'
      + p.risk_score.toFixed(2) + '</div><div class="sc-score-label">Risk</div></div>'
      + '</div></div>'
      + '<div class="sc-title" title="' + p.title + '">' + p.title.slice(0, 65) + (p.title.length > 65 ? '\u2026' : '') + '</div>'
      + '<div class="sc-meta">' + areaChip + statusChip + aiChip + ikChip + '</div>'
      + (phrases ? '<div class="sc-phrases">' + phrases + '</div>' : '')
      + '<div style="font-size:10px;color:#64748b;margin-bottom:6px">Reviewed by: ' + reviewers + '</div>'
      + pos0 + neg0
      + '</div>';
  });
  html += '</div>';
  el.innerHTML = html;
}

// ── Util: hex color to RGB string ─────────────────────────────────────────
function hexToRgb(hex) {
  hex = hex.replace('#','');
  if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
  var r = parseInt(hex.substring(0,2),16);
  var g = parseInt(hex.substring(2,4),16);
  var b = parseInt(hex.substring(4,6),16);
  return r + ',' + g + ',' + b;
}

// ── VIEW 5: Reviewer Intelligence ─────────────────────────────────────────
function renderIntelligence() {
  var el = document.getElementById('view-intel');
  var sig = DATA.network_signals;
  var phrases = DATA.emergent_phrases.filter(function(p) {
    return (p.phrase.indexOf(' ') > -1 || p.phrase.indexOf('-') > -1) && p.n_projects >= 2;
  }).slice(0, 30);

  // Area colour lookup
  var AREA_COL = {
    'Language': '#34d399', 'Storytelling': '#a78bfa',
    'Environmental Stewardship': '#4ade80', 'Env Stewardship': '#4ade80',
    'Socio-Neuro AI': '#f97316', 'Multi-Agent Systems': '#60a5fa',
    'Other': '#64748b'
  };

  // ── Cross-project phrase tags panel ──
  var tagHTML = phrases.map(function(p) {
    var pol = p.polarity > 0 ? 'rgba(74,222,128,.15)' : p.polarity < 0 ? 'rgba(248,113,113,.15)' : 'rgba(129,140,248,.12)';
    var polBorder = p.polarity > 0 ? 'rgba(74,222,128,.3)' : p.polarity < 0 ? 'rgba(248,113,113,.3)' : 'rgba(129,140,248,.2)';
    var polText = p.polarity > 0 ? '#4ade80' : p.polarity < 0 ? '#f87171' : '#818cf8';
    return '<span class="intel-phrase-tag" style="background:' + pol + ';border-color:' + polBorder + ';color:' + polText + '" title="' + p.n_projects + ' projects">'
      + p.phrase
      + '<span class="itag-count" style="background:' + polBorder + '">' + p.n_projects + '</span>'
      + '</span>';
  }).join('');

  // ── Build a sentence card ──
  function makeCard(s) {
    var aColor = AREA_COL[s.area] || '#64748b';
    var polIcon = s.polarity === 'positive' ? '\u25B2' : s.polarity === 'concern' ? '\u25BC' : '\u25CF';
    var polColor = s.polarity === 'positive' ? '#4ade80' : s.polarity === 'concern' ? '#f87171' : '#64748b';
    return '<div class="intel-card ' + s.type + '">'
      + '<div class="intel-card-text">' + s.text + '</div>'
      + '<div class="intel-card-meta">'
      + '<span class="intel-area-dot" style="background:' + aColor + '"></span>'
      + '<span class="intel-code">' + s.code + '</span>'
      + '<span style="color:#94a3b8">' + s.reviewer + '</span>'
      + '<span style="color:' + polColor + ';margin-left:auto">' + polIcon + ' ' + s.polarity + '</span>'
      + '</div></div>';
  }

  // ── Bucket sections ──
  var buckets = [
    { key: 'recommendations', label: 'Recommendations', icon: '\uD83D\uDCA1', cls: 'f-rec',
      desc: 'What reviewers think should happen — suggestions, pivots, improvements' },
    { key: 'questions',       label: 'Open Questions',   icon: '\u2753',      cls: 'f-qst',
      desc: 'What remains unclear, hard to assess, or unresolved across the network' },
    { key: 'actions',         label: 'Action Signals',   icon: '\uD83D\uDD04', cls: 'f-act',
      desc: 'What is already in motion — active work, partnerships, commitments' },
    { key: 'observations',    label: 'Key Observations', icon: '\uD83D\uDCCC', cls: 'f-obs',
      desc: 'Substantive insights from reviewers — strong reads on projects' },
  ];

  // Filter bar
  var filterHTML = '<div class="intel-filter-bar">'
    + '<button class="intel-filter-btn f-all active" onclick="intelFilter(\'all\',this)">All</button>';
  buckets.forEach(function(b) {
    var n = (sig[b.key] || []).length;
    filterHTML += '<button class="intel-filter-btn ' + b.cls + '" onclick="intelFilter(\'' + b.key + '\',this)">'
      + b.icon + ' ' + b.label + ' <span style="opacity:.6">(' + n + ')</span></button>';
  });
  filterHTML += '</div>';

  // Bucket HTML
  var bucketsHTML = buckets.map(function(b) {
    var items = sig[b.key] || [];
    if (!items.length) return '';
    var cards = items.map(makeCard).join('');
    return '<div class="intel-bucket" data-bucket="' + b.key + '">'
      + '<div class="intel-bucket-header">'
      + '<span class="intel-bucket-icon">' + b.icon + '</span>'
      + '<div><div class="intel-bucket-title">' + b.label + '</div>'
      + '<div style="font-size:11px;color:#64748b;margin-top:2px">' + b.desc + '</div></div>'
      + '<span class="intel-bucket-count">' + items.length + ' signals</span>'
      + '</div>'
      + '<div class="intel-cards">' + cards + '</div>'
      + '</div>';
  }).join('');

  el.innerHTML =
    '<div style="margin-bottom:16px">'
    + '<h3 style="font-size:13px;font-weight:700;color:#64748b;margin-bottom:4px">'
    + 'Reviewer Intelligence &mdash; what the reviewers are actually saying, in their own words.'
    + '</h3>'
    + '<p style="font-size:11px;color:#475569;line-height:1.5">'
    + 'Full sentences from evaluation forms, classified by type. Phrases in the left panel appear across 2+ projects independently.'
    + '</p></div>'
    + filterHTML
    + '<div id="intel-layout">'
    + '<div id="intel-phrases-panel"><h4>Cross-Project Phrases</h4>' + tagHTML + '</div>'
    + '<div id="intel-main">' + bucketsHTML + '</div>'
    + '</div>';
}

function intelFilter(bucket, btn) {
  // Update button states
  document.querySelectorAll('.intel-filter-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
  // Show/hide buckets
  document.querySelectorAll('.intel-bucket').forEach(function(b) {
    if (bucket === 'all' || b.dataset.bucket === bucket) {
      b.style.display = '';
    } else {
      b.style.display = 'none';
    }
  });
}

// ── Init ──────────────────────────────────────────────────────────────────
rendered['landscape'] = true;
renderLandscape();
</script>
</body>
</html>
'''

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Written: {OUT_FILE}")
print(f"Size: {len(HTML):,} bytes")
