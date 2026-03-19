"""
process_polarity3.py
--------------------
Merges data from:
  1. AbInt Project Evaluation Form (reviewer feedback)
  2. Research Dashboard (project metadata: area, AI depth, status, pod)

Produces polarity_data3.json with:
  - 10 enriched project objects
  - Research Area summaries
  - Emergent phrases: bigrams/hyphenated ONLY, appearing across 2+ projects
  - Typed sentences: recommendation | question | action | observation
  - Network signals: cross-project typed sentences for Reviewer Intelligence view
"""

import json, math, re, openpyxl
from collections import Counter, defaultdict

EVAL_XLSX = '/sessions/gifted-exciting-ramanujan/mnt/Data viz for program report/AbInt Phase 2 Evaluation Form.xlsx).xlsx'
DASH_XLSX = '/sessions/gifted-exciting-ramanujan/mnt/uploads/1. Research Dashboard.xlsx'
OUT       = '/sessions/gifted-exciting-ramanujan/polarity_data3.json'

# ── Load Evaluation Form ──────────────────────────────────────────────────
wb_eval = openpyxl.load_workbook(EVAL_XLSX)
ws_eval = wb_eval.active

COL = {h: i for i, h in enumerate([c.value for c in ws_eval[1]])}

def colval(row, key):
    v = row[COL[key]]
    return str(v).strip() if v else ''

eval_rows = []
for row in ws_eval.iter_rows(min_row=2, values_only=True):
    name = colval(row, 'Your Name')
    proj = colval(row, 'Project')
    if not name or not proj or 'test' in proj.lower() or len(proj) < 4:
        continue
    align_key = [k for k in COL if 'ALIGNMENT SCORE' in str(k)]
    qual_key  = [k for k in COL if 'QUALITY SCORE' in str(k)]
    eval_rows.append({
        'reviewer': name,
        'project':  proj,
        'transform': colval(row, "Transformation: How does this contribute to AbInt's Transformation Statement?"),
        'risk':      colval(row, 'Risks: What risks may be associated with this project, and how may these be addressed or mitigated? What are the risks with not pursuing this project?'),
        'collab':    colval(row, 'Collaboration potential : Where do you see potential for this project to connect/collaborate with other project(s) in the AbInt Network?'),
        'advance':   colval(row, 'Potential for Advancement: How do you see this research advancing in the Imaginaries and Intelligences Phases? What would need to pivot, deepen, or be added to support these phases?'),
        'align':     row[COL[align_key[0]]] if align_key else None,
        'quality':   row[COL[qual_key[0]]]  if qual_key  else None,
        'notes':     colval(row, 'Notes & Final thoughts:'),
    })

print(f"Loaded {len(eval_rows)} evaluation rows from {len(set(r['project'] for r in eval_rows))} projects")

# ── Load Research Dashboard ───────────────────────────────────────────────
wb_dash = openpyxl.load_workbook(DASH_XLSX)
ws_dash = wb_dash['Research Dashboard - Ready for ']

def norm_name(s):
    if not s: return ''
    s = str(s).lower().strip()
    s = re.split(r'[,\(]', s)[0].strip()
    return s

dashboard = {}
for row_idx in range(3, 102):
    b = ws_dash.cell(row_idx, 2).value
    c = ws_dash.cell(row_idx, 3).value
    e = ws_dash.cell(row_idx, 5).value
    f = ws_dash.cell(row_idx, 6).value
    g = ws_dash.cell(row_idx, 7).value
    i = ws_dash.cell(row_idx, 9).value
    j = ws_dash.cell(row_idx, 10).value
    k = ws_dash.cell(row_idx, 11).value
    m = ws_dash.cell(row_idx, 13).value
    n = ws_dash.cell(row_idx, 14).value
    o = ws_dash.cell(row_idx, 15).value
    if not b or not str(b).strip(): continue
    key = norm_name(b)
    title_clean = re.sub(r'\s+', ' ', str(c)).strip() if c else ''
    type_val = str(e).strip() if e and not str(e).startswith('=') else 'CfP'
    record = {
        'title':            title_clean,
        'type':             type_val,
        'pod':              str(f).strip() if f else '',
        'status':           str(g).strip() if g else '',
        'primary_area':     str(i).strip() if i else 'Other',
        'secondary_area':   str(j).strip() if j else '',
        'ai_depth':         str(k).strip() if k else 'None',
        'ik_methods':       str(m).strip() if m else 'None',
        'infra_share':      str(n).strip() if n else 'None',
        'sharable_method':  str(o).strip() if o else 'None',
    }
    if key not in dashboard:
        dashboard[key] = record

print(f"Dashboard: {len(dashboard)} project leads loaded")

# ── Match eval form to dashboard ─────────────────────────────────────────
def extract_lead(proj_str):
    lead = re.split(r'\s*-\s*CfP', proj_str)[0].strip()
    lead = lead.replace('&', 'and')
    return lead

def get_dash_info(proj_str):
    lead = extract_lead(proj_str)
    key  = norm_name(lead)
    if key in dashboard:
        return dashboard[key]
    last = key.split()[-1] if key.split() else ''
    for dk, dv in dashboard.items():
        if last and last in dk:
            return dv
    return {
        'title': lead, 'type': 'CfP', 'pod': '', 'status': '',
        'primary_area': 'Other', 'secondary_area': '',
        'ai_depth': 'None', 'ik_methods': 'None',
        'infra_share': 'None', 'sharable_method': 'None',
    }

print("\nProject matching:")
for pid in sorted(set(r['project'] for r in eval_rows)):
    info = get_dash_info(pid)
    print(f"  {pid[:40]:40s} → {info['primary_area']:20s} AI={info['ai_depth']:4s} {info['status']}")

# ── Language scoring ──────────────────────────────────────────────────────
CONV_W = ['strongly','clearly','well positioned','demonstrates','actively',
          'robust','grounded','deeply','effectively','leading','excellent',
          'exceptional','outstanding','notably','directly','firmly','concrete',
          'significant potential','valuable','critical','essential']
HEDGE_W = ['not entirely certain','unclear','it is not clear','hard to assess',
           'difficult to assess','somewhat','might','perhaps','possibly',
           'not sure','limited','unclear how','seems like','may or may not']
CONC_W  = ['concern','challenge','challenging','difficult','experimental',
           'relies on','dependent on','capacity','funding','sustainability',
           'unclear','uncertain','not clear','question','problematic',
           'late getting started','highly experimental','does not']

def lang_scores(texts):
    c = ' '.join(texts).lower()
    t = max(len(c.split()), 1)
    def cnt(b): return sum(c.count(p) for p in b)
    nc, nh, nr = cnt(CONV_W), cnt(HEDGE_W), cnt(CONC_W)
    norm = t / 100
    net  = (nc/norm) - (nh/norm)*1.5
    conv = round(min(.95, max(.15, .2 + .65/(1+math.exp(-net*.35)))), 3)
    conc = round(min(.90, (nr/norm)*.16), 3)
    return conv, conc

# ── Risk score ───────────────────────────────────────────────────────────
RISK_NEG = ['one risk is','a risk is','risk is that','concern is','challenge is',
            'challenging','highly experimental','relies on','not clear how',
            'it is not clear','limited scope','solely focused','dependent on',
            'sustainability','primarily focused','not tied to','i do not see',
            'late getting started','hard to assess','does not address',
            'narrow','underdeveloped','unclear','no clear']
RISK_POS = ['risk appears relatively low','risk appears low','relatively low risk',
            'no significant risk','well mitigated','not high-risk','low risk',
            'risk of not pursuing','risk is low','fairly straightforward',
            'manageable','minimal risk']

def risk_col_score(risk_text):
    if not risk_text: return 0.15
    t = risk_text.lower()
    words = t.split()
    norm = max(len(words), 1) / 100
    neg = sum(t.count(p) for p in RISK_NEG)
    pos = sum(t.count(p) for p in RISK_POS)
    net = (neg / max(norm, 0.1)) - (pos / max(norm, 0.1)) * 2.0
    score = min(0.90, max(0.05, 0.15 + net * 0.10))
    return round(score, 3)

# ── Sentence classifiers ──────────────────────────────────────────────────
POS_PATTERNS = [
    'well positioned','strong potential','contributes strongly',
    'demonstrates how','fits naturally','risk appears relatively low',
    'risk appears low','very strong potential','strong alignment',
    'grounds','relational','community-led','actively reworking',
    'grounded in','deep engagement','capacity building',
    'directly advances','clearly demonstrates','rich potential',
    'valuable contribution','important contribution',
]
NEG_PATTERNS = [
    'not entirely certain','hard to assess','i do not see',
    'it is not clear','fairly contained','late getting started',
    'highly experimental','relies on highly','one risk is',
    'a risk is','moderate risk','in this case','solely focused',
    'not tied to','does not','challenging','challenge is',
    'primarily focused on','limited scope','limited collaboration',
    'narrow in scope','underdeveloped','no clear plan',
]

# Sentence TYPE patterns (independent of positive/concern polarity)
RECOMMENDATION_PATTERNS = [
    'should ', 'would benefit', 'recommend', 'suggest', 'could consider',
    'needs to', 'need to', 'ought to', 'it would be worth', 'would be helpful',
    'would be valuable', 'would be important', 'could be strengthened',
    'could be deepened', 'could be expanded', 'might consider', 'might benefit',
    'could explore', 'should consider', 'should explore', 'would encourage',
    'important to', 'critical to ensure', 'essential to',
    # Patterns from actual reviewer language
    'could deepen', 'could expand', 'could develop', 'could strengthen',
    'could add', 'could include', 'could benefit', 'could be added',
    'would need', 'would require', 'may be needed', 'may need to',
    'might be worth', 'might want to', 'might be helpful',
    'more attention', 'clearer', 'more explicit', 'more concrete',
    'pivot', 'deepen', 'be added to support',
]
QUESTION_PATTERNS = [
    '?', 'unclear', 'it is not clear', 'hard to assess', 'difficult to assess',
    'not sure', 'i wonder', 'uncertain', 'question is', 'not entirely clear',
    'remains to be seen', 'how will', 'what will', 'whether ', 'not yet clear',
    'curious', 'unsure', 'hard to know', 'difficult to know',
]
ACTION_PATTERNS = [
    'will ', 'is developing', 'has developed', 'has been', 'is building',
    'is working', 'is creating', 'plans to', 'intends to', 'next step',
    'moving forward', 'committed to', 'currently working', 'is already',
    'has already', 'is actively', 'has established', 'is engaged',
    'is partnering', 'is collaborating', 'has partnered',
]

def split_sentences(text):
    text = re.sub(r'\s+', ' ', text.strip())
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if len(s.split()) >= 6]

def classify_polarity(sent):
    """Returns positive/concern/neutral + strength."""
    s = sent.lower()
    pos = sum(1 for p in POS_PATTERNS if p in s)
    neg = sum(1 for p in NEG_PATTERNS if p in s)
    if pos > neg and pos > 0:  return 'positive', pos
    if neg >= pos and neg > 0: return 'concern',  neg
    return 'neutral', 0

def classify_type(sent):
    """
    Returns one of: recommendation | question | action | observation
    Priority order: recommendation > question > action > observation
    """
    s = sent.lower()
    # Recommendation takes priority — it's the most actionable
    if any(p in s for p in RECOMMENDATION_PATTERNS):
        return 'recommendation'
    # Questions / uncertainty
    if any(p in s for p in QUESTION_PATTERNS):
        return 'question'
    # Action signals — what's in motion
    if any(p in s for p in ACTION_PATTERNS):
        return 'action'
    # Everything else is an observation
    return 'observation'

def extract_sentences(row):
    """Extract polarity-classified sentences (positive/concern) per row."""
    positives, concerns = [], []
    fields = [('transform', row['transform']), ('advance', row['advance']),
              ('risk', row['risk']), ('collab', row['collab'])]
    for col_name, text in fields:
        if not text: continue
        for sent in split_sentences(text):
            label, strength = classify_polarity(sent)
            if label == 'positive':
                positives.append({'text': sent, 'reviewer': row['reviewer'],
                                   'project': row['project'], 'source': col_name,
                                   'strength': strength})
            elif label == 'concern':
                concerns.append({'text': sent, 'reviewer': row['reviewer'],
                                  'project': row['project'], 'source': col_name,
                                  'strength': strength})
    return positives, concerns

def extract_typed_sentences(row, project_area):
    """
    Extract ALL sentences with type classification.
    Returns list of {text, type, polarity, reviewer, project, source, area}
    Filters out very short or uninformative sentences.
    """
    results = []
    fields = [
        ('transform', row['transform']),
        ('advance',   row['advance']),
        ('collab',    row['collab']),
        ('risk',      row['risk']),
    ]
    for col_name, text in fields:
        if not text: continue
        for sent in split_sentences(text):
            # Skip sentences that are just too generic to be useful
            if len(sent.split()) < 8:
                continue
            sent_type    = classify_type(sent)
            polarity, _  = classify_polarity(sent)
            # For observations, only include positive or concern — skip neutral noise
            if sent_type == 'observation' and polarity == 'neutral':
                continue
            results.append({
                'text':     sent,
                'type':     sent_type,
                'polarity': polarity,
                'reviewer': row['reviewer'],
                'project':  row['project'],
                'source':   col_name,
                'area':     project_area,
            })
    return results

# ── Stopwords ─────────────────────────────────────────────────────────────
STOPWORDS = set([
    'project','projects','abint','network','phase','development','approach',
    'work','working','provide','provides','include','includes','focus',
    'activity','activities','process','processes','number','level','levels',
    'important','particular','overall','general','specific','certain','various',
    'different','similar','potential','risk','risks','largely','primarily',
    'relatively','particularly','especially','significant','key','currently',
    'become','area','areas','contribution','contributes','contribute','support',
    'supports','strong','strongly','well','clearly','directly','fully','highly',
    'aspect','aspects','way','ways','part','parts','help','helps','review',
    'transformation','statement','advance','advancing','imaginaries',
    'intelligences','research','researcher','researchers','community','communities',
    'indigenous','centred','centered','based','grounded','through','their','this',
    'that','with','from','for','and','the','are','has','have','been','its',
    'would','could','should','other','also','within','across','they','which',
    'into','about','each','both','some','all','how','your','use','than','then',
    'up','if','so','do','over','between','after','here','those','was','did',
    'had','me','us','them','my','own','one','two','well','get','got','new',
    'see','many','make','made','too','even','still','since','while','before',
    'where','who','whom','whose','being','having','doing','rather','further',
    'already','often','given','whether','however','although','therefore','thus',
    'a','an','is','by','on','as','at','be','or','can','may','not','but','will',
    'more','to','in','of','it','i','we','he','she','our','very','such','also',
    'need','needs','needed','using','used','make','makes','making','take',
    'takes','taking','think','thinking','allow','allows','allowing',
    'abundant','dish','spoon','described','description','materials','material',
    'internal','environment','environments','storytelling',
    'collaboration','collaborative','goal','transforming','transformations',
    'context','contexts','connection','connections','example','examples',
    'approach','approaches','structure','structures','element','elements',
    # Keep 'language' out of stopwords so bigram "language revitalization" can form
])

def tokenize(text):
    words = re.findall(r'\b[a-z][a-z\-]{2,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 3]

def get_bigrams(tokens):
    return [tokens[i]+' '+tokens[i+1] for i in range(len(tokens)-1)
            if tokens[i] not in STOPWORDS and tokens[i+1] not in STOPWORDS]

def get_hyphenated(text):
    """Extract hyphenated compound terms like indigenous-centred, community-led."""
    return re.findall(r'\b[a-z]{3,}-[a-z]{3,}\b', text.lower())

# ── Build project-level data ──────────────────────────────────────────────
project_data = {}
for r in eval_rows:
    pid = r['project']
    if pid not in project_data:
        dash = get_dash_info(pid)
        lead = extract_lead(pid)
        code_match = re.search(r'CfP[\w\-]+', pid)
        code = code_match.group(0) if code_match else ''
        project_data[pid] = {
            'id': pid,
            'short': lead,
            'code': code,
            'title': dash['title'],
            'type': dash['type'],
            'primary_area': dash['primary_area'],
            'secondary_area': dash['secondary_area'],
            'ai_depth': dash['ai_depth'],
            'status': dash['status'],
            'pod': dash['pod'],
            'ik_methods': dash['ik_methods'],
            'infra_share': dash['infra_share'],
            'sharable_method': dash['sharable_method'],
            'texts': [],
            'transform_texts': [],
            'risk_texts': [],
            'reviewers': [],
            'alignment': [],
            'quality': [],
            'positives': [],
            'concerns': [],
            'typed_sentences': [],
        }
    pd = project_data[pid]
    all_texts = [r['transform'], r['risk'], r['collab'], r['advance']]
    pd['texts'].extend([t for t in all_texts if t])
    if r['transform']: pd['transform_texts'].append(r['transform'])
    if r['risk']:      pd['risk_texts'].append(r['risk'])
    pd['reviewers'].append(r['reviewer'])
    if r['align']:   pd['alignment'].append(float(r['align']))
    if r['quality']: pd['quality'].append(float(r['quality']))
    pos_sents, neg_sents = extract_sentences(r)
    pd['positives'].extend(pos_sents)
    pd['concerns'].extend(neg_sents)
    # Typed sentences for Reviewer Intelligence view
    area = get_dash_info(pid)['primary_area']
    pd['typed_sentences'].extend(extract_typed_sentences(r, area))

# Compute scores per project
AI_DEPTH_NUM = {'High': 3, 'Mid': 2, 'Low': 1, 'None': 0}

for pid, pd in project_data.items():
    conv, conc = lang_scores(pd['texts'])
    raw_align  = sum(pd['alignment']) / len(pd['alignment']) if pd['alignment'] else 5.0
    raw_qual   = sum(pd['quality'])   / len(pd['quality'])   if pd['quality']   else 5.0
    risk_sc    = risk_col_score(' '.join(pd['risk_texts']))
    pd['alignment_avg']  = round(raw_align, 2)
    pd['quality_avg']    = round(raw_qual, 2)
    pd['risk_score']     = risk_sc
    pd['conviction']     = conv
    pd['concern_lang']   = conc
    pd['ai_depth_num']   = AI_DEPTH_NUM.get(pd['ai_depth'], 0)

# ── TF-IDF: bigrams + hyphenated only, must appear in 2+ projects ─────────
all_phrases_per_doc = {}
for pid, pd in project_data.items():
    text = ' '.join(pd['texts']).lower()
    toks = tokenize(text)
    bigs = get_bigrams(toks)
    hyph = get_hyphenated(text)
    # Only bigrams and hyphenated — no single words
    all_phrases_per_doc[pid] = Counter(bigs + hyph)

N = len(all_phrases_per_doc)
phrase_doc_freq = Counter()
for pid, counts in all_phrases_per_doc.items():
    for phrase in counts:
        phrase_doc_freq[phrase] += 1

def tfidf(pid, phrase):
    tf = all_phrases_per_doc[pid].get(phrase, 0)
    if tf == 0: return 0
    idf = math.log(N / phrase_doc_freq[phrase])
    return tf * idf

# Global phrase scores — CROSS-PROJECT ONLY (doc_freq >= 2)
phrase_scores = {}
for pid in all_phrases_per_doc:
    for phrase in all_phrases_per_doc[pid]:
        if phrase_doc_freq[phrase] < 2:
            continue  # Skip phrases that only appear in one project
        if phrase not in phrase_scores:
            phrase_scores[phrase] = 0
        phrase_scores[phrase] += tfidf(pid, phrase)

# Determine polarity of each phrase from sentence context
phrase_polarity = Counter()
for r in eval_rows:
    for field_name, text in [('transform', r['transform']), ('advance', r['advance']),
                               ('collab', r['collab']), ('risk', r['risk'])]:
        if not text: continue
        for sent in split_sentences(text):
            label, _ = classify_polarity(sent)
            if label in ('positive', 'concern'):
                toks = tokenize(sent)
                bigs = get_bigrams(toks)
                hyph = get_hyphenated(sent)
                for ph in bigs + hyph:
                    if label == 'positive': phrase_polarity[ph] += 1
                    else:                   phrase_polarity[ph] -= 1

top_global = sorted(
    [(ph, sc) for ph, sc in phrase_scores.items() if len(ph) > 4],
    key=lambda x: -x[1]
)[:50]

print("\n=== TOP 30 EMERGENT PHRASES (cross-project, multi-word only) ===")
for ph, sc in top_global[:30]:
    pol   = phrase_polarity.get(ph, 0)
    n_doc = phrase_doc_freq[ph]
    pids  = [pid[:20] for pid, cnts in all_phrases_per_doc.items() if cnts.get(ph, 0) > 0]
    pol_label = 'POS' if pol > 0 else ('NEG' if pol < 0 else 'MIX')
    print(f"  {ph:35s} {sc:.2f}  {pol_label:3s}  n={n_doc}  [{', '.join(pids[:3])}]")

emergent_phrases = []
for ph, sc in top_global[:40]:
    pol = phrase_polarity.get(ph, 0)
    projects_using = [pid for pid, cnts in all_phrases_per_doc.items()
                      if cnts.get(ph, 0) > 0]
    emergent_phrases.append({
        'phrase':     ph,
        'score':      round(sc, 3),
        'polarity':   1 if pol > 0 else (-1 if pol < 0 else 0),
        'n_projects': len(projects_using),
        'projects':   projects_using,
        'doc_freq':   phrase_doc_freq[ph],
    })

# Per-project top phrases (cross-project bigrams/hyphenated only)
for pid, pd in project_data.items():
    top_p = sorted(
        [(ph, sc) for ph, sc in all_phrases_per_doc.get(pid, {}).items()
         if phrase_doc_freq[ph] >= 2],
        key=lambda x: -tfidf(pid, x[0])
    )[:6]
    pd['top_phrases'] = [p for p, _ in top_p]

# ── Network Signals: typed sentences across all projects ─────────────────
# Build four buckets for Reviewer Intelligence view
network_signals = {
    'recommendations': [],
    'questions':       [],
    'actions':         [],
    'observations':    [],
}

seen_sigs = set()
for pid, pd in project_data.items():
    for s in pd['typed_sentences']:
        key = s['text'][:80]
        if key in seen_sigs:
            continue
        seen_sigs.add(key)
        entry = {
            'text':       s['text'],
            'type':       s['type'],
            'polarity':   s['polarity'],
            'reviewer':   s['reviewer'],
            'project':    pd['short'],
            'project_id': pid,
            'code':       pd['code'],
            'area':       pd['primary_area'],
        }
        type_map = {
            'recommendation': 'recommendations',
            'question':       'questions',
            'action':         'actions',
            'observation':    'observations',
        }
        bucket = type_map.get(s['type'], 'observations')
        network_signals[bucket].append(entry)

# Sort each bucket: positive first, then by text length (longer = more substantive)
for bucket in network_signals:
    network_signals[bucket].sort(
        key=lambda x: (0 if x['polarity'] == 'positive' else 1, -len(x['text']))
    )

print(f"\n=== REVIEWER INTELLIGENCE SIGNALS ===")
for bname, items in network_signals.items():
    print(f"  {bname:20s}: {len(items)} sentences")
    for item in items[:2]:
        print(f"    [{item['code']}] {item['text'][:100]}...")

# ── Research Area summaries ───────────────────────────────────────────────
RESEARCH_AREAS = [
    {'id': 'language',     'title': 'Language',              'color': '#34d399',
     'desc': 'Expanding NLP capabilities to handle Indigenous linguistic structures and language densities.'},
    {'id': 'storytelling', 'title': 'Storytelling',          'color': '#a78bfa',
     'desc': 'Drawing on Indigenous storytelling and oral traditions to develop richer machine understandings.'},
    {'id': 'env',          'title': 'Environmental Stewardship','color': '#4ade80',
     'desc': 'Traditional land management and stewardship practices informing AI-driven restoration systems.'},
    {'id': 'socio_neuro',  'title': 'Socio-Neuro AI',        'color': '#f97316',
     'desc': 'Using IK diversity to model how humans draw on socio-cultural context to learn and decide.'},
    {'id': 'multi_agent',  'title': 'Multi-Agent Systems',   'color': '#60a5fa',
     'desc': 'Robust approaches to diverse agents interacting with socio-cultural context, human and non-human.'},
]

AREA_KEYS = {
    'Language':               'language',
    'Storytelling':           'storytelling',
    'Env Stewardship':        'env',
    'Environmental Stewardship': 'env',
    'Socio-Neuro AI':         'socio_neuro',
    'Multi-Agent Systems':    'multi_agent',
}

area_projects = defaultdict(list)
for pid, pd in project_data.items():
    ak1 = AREA_KEYS.get(pd['primary_area'])
    ak2 = AREA_KEYS.get(pd['secondary_area'])
    if ak1: area_projects[ak1].append((pid, 1.0))
    if ak2 and ak2 != ak1: area_projects[ak2].append((pid, 0.5))

def wavg(vals, weights):
    if not vals: return 0
    wt = list(zip(vals, weights))
    return sum(v*w for v,w in wt) / sum(w for _,w in wt)

output_areas = []
for area in RESEARCH_AREAS:
    aid = area['id']
    plist = area_projects.get(aid, [])
    if not plist: continue

    valid   = [(pid, w) for pid, w in plist if pid in project_data]
    pids    = [x[0] for x in valid]
    weights = [x[1] for x in valid]

    align_vals = [project_data[p]['alignment_avg'] for p in pids]
    risk_vals  = [project_data[p]['risk_score']    for p in pids]
    align_avg  = round(wavg(align_vals, weights), 2)
    risk_avg   = round(wavg(risk_vals,  weights), 3)

    all_pos, all_neg = [], []
    seen_pos, seen_neg = set(), set()
    for pid, w in valid:
        for s in project_data[pid]['positives']:
            key = s['text'][:60]
            if key not in seen_pos:
                seen_pos.add(key)
                all_pos.append({
                    'text': s['text'], 'reviewer': s['reviewer'],
                    'project': project_data[pid]['short'],
                    'project_code': project_data[pid]['code'],
                    'source': s['source'], 'weight': w,
                })
        for s in project_data[pid]['concerns']:
            key = s['text'][:60]
            if key not in seen_neg:
                seen_neg.add(key)
                all_neg.append({
                    'text': s['text'], 'reviewer': s['reviewer'],
                    'project': project_data[pid]['short'],
                    'project_code': project_data[pid]['code'],
                    'source': s['source'], 'weight': w,
                })
    all_pos.sort(key=lambda x: -x['weight'])
    all_neg.sort(key=lambda x: -x['weight'])

    area_phrases = []
    seen_ph = set()
    for pid in pids:
        for ph in project_data[pid].get('top_phrases', []):
            if ph not in seen_ph:
                seen_ph.add(ph)
                area_phrases.append(ph)

    output_areas.append({
        'id':            aid,
        'title':         area['title'],
        'color':         area['color'],
        'desc':          area['desc'],
        'n_projects':    len(pids),
        'projects':      [{'id': pid, 'short': project_data[pid]['short'],
                           'code': project_data[pid]['code'],
                           'is_primary': w == 1.0}
                          for pid, w in valid],
        'alignment_avg': align_avg,
        'risk_score':    risk_avg,
        'top_phrases':   area_phrases[:8],
        'positive_sentences': all_pos[:5],
        'concern_sentences':  all_neg[:5],
    })

# ── Reviewer profiles ─────────────────────────────────────────────────────
rev_names = sorted(set(r['reviewer'] for r in eval_rows))

def reviewer_words(rrows):
    all_text = ' '.join(
        r['transform']+' '+r['advance']+' '+r['collab']+' '+r['risk']
        for r in rrows
    )
    words   = [w for w in tokenize(all_text) if w not in STOPWORDS and len(w) > 3]
    bigrams = [words[i]+' '+words[i+1] for i in range(len(words)-1)]
    return {
        'words':   Counter(words).most_common(60),
        'bigrams': Counter(bigrams).most_common(20),
    }

output_reviewers = []
for name in rev_names:
    rrows    = [r for r in eval_rows if r['reviewer'] == name]
    all_text = []
    for r in rrows:
        all_text.extend([r['transform'], r['risk'], r['collab'], r['advance']])
    conv, conc = lang_scores([t for t in all_text if t])
    output_reviewers.append({
        'name':        name,
        'n_projects':  len(rrows),
        'projects':    list(set(r['project'] for r in rrows)),
        'conviction':  conv,
        'concern':     conc,
        'themes':      reviewer_words(rrows),
    })

# ── Projects list ─────────────────────────────────────────────────────────
output_projects = []
for pid, pd in project_data.items():
    output_projects.append({
        'id':             pid,
        'short':          pd['short'],
        'code':           pd['code'],
        'title':          pd['title'],
        'primary_area':   pd['primary_area'],
        'secondary_area': pd['secondary_area'],
        'type':           pd['type'],
        'ai_depth':       pd['ai_depth'],
        'ai_depth_num':   pd['ai_depth_num'],
        'status':         pd['status'],
        'pod':            pd['pod'],
        'ik_methods':     pd['ik_methods'],
        'infra_share':    pd['infra_share'],
        'sharable_method':pd['sharable_method'],
        'alignment_avg':  pd['alignment_avg'],
        'quality_avg':    pd['quality_avg'],
        'risk_score':     pd['risk_score'],
        'conviction':     pd['conviction'],
        'concern_lang':   pd['concern_lang'],
        'reviewers':      list(set(pd['reviewers'])),
        'top_phrases':    pd.get('top_phrases', []),
        'positives':      pd['positives'][:4],
        'concerns':       pd['concerns'][:4],
    })

# ── TS dimensions ─────────────────────────────────────────────────────────
TS_DIMENSIONS = [
    {'id': 'ts_ik',       'label': 'Indigenous Knowledge Integration',
     'desc': 'IK holders, knowledge systems, and ways of knowing brought into AI'},
    {'id': 'ts_relational','label': 'Relational Practice',
     'desc': 'Relational approaches to knowledge creation and collaboration'},
    {'id': 'ts_community', 'label': 'Community-Centred',
     'desc': 'Community representation, community-defined priorities, community benefit'},
    {'id': 'ts_technical', 'label': 'Technical AI Transformation',
     'desc': 'Actively reworking AI systems, architectures, data pipelines'},
    {'id': 'ts_governance','label': 'Data Sovereignty & Governance',
     'desc': 'Data sovereignty, governance frameworks, community-controlled AI'},
    {'id': 'ts_network',   'label': 'Network & Cross-Project',
     'desc': 'Building the network, bridging projects, cross-community collaboration'},
    {'id': 'ts_imaginaries','label': 'Imaginaries & Speculative',
     'desc': 'Future imaginaries, speculative design, visioning for Phase 2+'},
]

TS_KEYWORDS = {
    'ts_ik':        ['indigenous knowledge','knowledge system','ways of knowing',
                     'knowledge holder','traditional knowledge','land-based'],
    'ts_relational':['relational','relationship','reciprocal','reciprocity',
                     'place-based','grounded','community-led'],
    'ts_community': ['community','community-defined','community-led','community-centred',
                     'community-centered','community-based','local'],
    'ts_technical': ['actively reworking','technical','model','data pipeline',
                     'architecture','training data','machine learning','neural',
                     'algorithm','system'],
    'ts_governance':['data sovereignty','governance','protocol','ethical framework',
                     'community control','data rights','ownership'],
    'ts_network':   ['collaboration','collaborate','network','bridge','connect',
                     'other project','cross-project','partnership'],
    'ts_imaginaries':['imaginar','speculative','future','vision','phase 2',
                      'imaginaries','phase two','next phase'],
}

ts_project_scores = {}
for pid, pd in project_data.items():
    full_text = ' '.join(pd['texts']).lower()
    scores = {}
    for dim_id, keywords in TS_KEYWORDS.items():
        hits = sum(full_text.count(kw) for kw in keywords)
        word_count = max(len(full_text.split()), 1)
        scores[dim_id] = round(min(1.0, hits / (word_count / 100) * 0.5), 3)
    ts_project_scores[pid] = scores

# ── Final JSON output ─────────────────────────────────────────────────────
out_data = {
    'research_areas':      output_areas,
    'projects':            output_projects,
    'reviewers':           output_reviewers,
    'emergent_phrases':    emergent_phrases,
    'network_signals':     network_signals,
    'ts_dimensions':       TS_DIMENSIONS,
    'ts_project_scores':   ts_project_scores,
    'top_global_phrases':  [p['phrase'] for p in emergent_phrases[:30]],
}

with open(OUT, 'w') as f:
    json.dump(out_data, f, ensure_ascii=True, indent=2)

print(f"\n=== OUTPUT SUMMARY ===")
print(f"Saved to {OUT}")
print(f"Research Areas: {len(output_areas)}")
for a in output_areas:
    print(f"  {a['title']:25s} n={a['n_projects']} align={a['alignment_avg']} risk={a['risk_score']}")
print(f"Projects: {len(output_projects)}")
for p in sorted(output_projects, key=lambda x: -x['alignment_avg']):
    print(f"  {p['short'][:25]:25s} {p['code']:8s} align={p['alignment_avg']} risk={p['risk_score']} area={p['primary_area']}")
print(f"Emergent phrases (cross-project): {len(emergent_phrases)}")
print(f"Top 10 phrases: {[p['phrase'] for p in emergent_phrases[:10]]}")
print(f"\nNetwork Signals:")
for bname, items in network_signals.items():
    print(f"  {bname:20s}: {len(items)} sentences")
