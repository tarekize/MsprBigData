#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""memoire.tex → memoire.pdf  (weasyprint)"""
import re, html as HM, sys
from pathlib import Path

BASE     = Path(r"c:\Users\tarek\Downloads\MsprBigData")
TEX_FILE = BASE / "memoire.tex"
PDF_FILE = BASE / "memoire.pdf"

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@page {
  size: A4; margin: 2.5cm 2.5cm 2.5cm 3cm;
  @top-left   { content: "Electio-Analytics — Mémoire MSPR Big Data";
                font-size:8pt; color:#666; font-style:italic; }
  @top-right  { content: counter(page); font-size:8pt; color:#555; }
  @bottom-center {
    content: "Certification Professionnelle RNCP35584 — Promotion I1 EISI 2025/2026";
    font-size:7pt; color:#999; font-style:italic; }
}
* { box-sizing:border-box; }
html { font-size:11pt; }
body { font-family:Georgia,"Times New Roman",serif; line-height:1.55;
       color:#111; text-align:justify; }

.titlepage { text-align:center; page-break-after:always; padding:18pt 0; }
.tp-school  { font-size:12.5pt; font-variant:small-caps; letter-spacing:.05em; }
.tp-cert    { font-size:10.5pt; margin:2pt 0; }
.tp-rule    { border:none; border-top:1.5px solid #333; margin:14pt 0 10pt; }
.tp-title   { font-size:21pt; font-weight:bold; color:#1a1a5e; margin:8pt 0 4pt; }
.tp-sub     { font-size:14pt; font-weight:bold; color:#1a1a5e; margin:3pt 0 12pt; }
.tp-desc    { font-size:12pt; font-style:italic; margin:10pt 0 3pt; }
.tp-client  { font-size:11pt; margin-bottom:20pt; }
table.team  { margin:16pt auto; border-collapse:collapse; }
table.team th{ padding:5pt 18pt; border-top:2px solid #333;
               border-bottom:1px solid #888; font-weight:bold; }
table.team td{ padding:4pt 18pt; }
table.team tr:last-child td{ border-bottom:2px solid #333; }
.tp-info    { margin-top:16pt; font-size:10.5pt; }
.tp-conf    { font-size:9pt; font-style:italic; color:#666; margin-top:22pt; }

h1           { font-size:18pt; text-align:center; color:#1a1a5e;
               page-break-before:always; margin:38pt 0 20pt; }
h1 .ch-label { display:block; font-size:10.5pt; color:#777;
               font-weight:normal; margin-bottom:5pt; }
h1.nopb      { page-break-before:avoid; }
h2  { font-size:13pt; color:#1a1a5e; border-bottom:1px solid #9ab;
      padding-bottom:2pt; margin-top:17pt; margin-bottom:5pt; }
h3  { font-size:11.5pt; color:#333; margin-top:13pt; margin-bottom:4pt; }
h4  { font-size:11pt; color:#555; font-style:italic;
      margin-top:9pt; margin-bottom:3pt; }

p   { margin:0 0 7pt; }
code{ font-family:"Courier New",Courier,monospace; font-size:8.8pt;
      background:#f2f2f8; padding:1px 3px; border-radius:2px;
      word-break:break-all; }
pre { font-family:"Courier New",Courier,monospace; font-size:7.4pt;
      background:#f2f2f8; border:1px solid #ccd; border-radius:3px;
      padding:7pt 10pt; margin:7pt 0 2pt; white-space:pre-wrap;
      word-break:break-all; line-height:1.33; }
.listing-cap{ font-size:9pt; color:#555; font-style:italic;
              text-align:center; margin:2pt 0 9pt; }

table    { border-collapse:collapse; width:100%; margin:7pt 0 2pt; font-size:10pt; }
table.nw { width:auto; margin:7pt auto 2pt; }
th  { background:#e5e8f0; font-weight:bold; padding:4pt 7pt;
      text-align:left; border-top:2px solid #444; border-bottom:1px solid #777; }
td  { padding:3pt 7pt; border-bottom:1px solid #dde; vertical-align:top; }
tr.mid td{ border-top:1px solid #999; border-bottom:none;
           padding:0; height:1px; font-size:0; }
tr.bot td{ border-bottom:2px solid #444; }
.mono { font-family:"Courier New",monospace; font-size:8.2pt;
        word-break:break-all; }
.col-r{ text-align:right; }
.col-c{ text-align:center; }
.tab-cap { font-size:9.5pt; font-style:italic; text-align:center;
           margin:2pt 0 5pt; color:#333; }
.tab-num { font-weight:bold; }

.infobox   { border:1.5px solid #2e5bcc; background:#eef2ff;
             padding:9pt 11pt; margin:9pt 0; border-radius:3px; }
.resultbox { border:1.5px solid #2d8050; background:#efffee;
             padding:9pt 11pt; margin:9pt 0; border-radius:3px; }
.warnbox   { border:1.5px solid #b85c00; background:#fff7ee;
             padding:9pt 11pt; margin:9pt 0; border-radius:3px; }
.box-title { font-weight:bold; margin-bottom:6pt; padding-bottom:4pt;
             border-bottom:1px solid rgba(0,0,0,.15); font-size:10.5pt; }
.infobox  .box-title{ color:#1a3faa; }
.resultbox .box-title{ color:#1a5e35; }
.warnbox  .box-title { color:#7a3800; }

ul,ol { margin:5pt 0 5pt 18pt; }
li    { margin-bottom:3pt; }
dl    { margin:5pt 0; }
dt    { font-weight:bold; margin-top:7pt; }
dd    { margin-left:18pt; margin-bottom:4pt; }

.equation { font-family:"Courier New",monospace; text-align:center;
            padding:6pt; margin:7pt 0; background:#fafafa;
            border:1px solid #eee; font-style:italic; font-size:10pt; }
figure    { margin:9pt 0; text-align:center; }
figure img{ max-width:95%; height:auto; }
figcaption{ font-size:9pt; font-style:italic; color:#555; margin-top:3pt; }
hr.sep    { border:none; border-top:1px solid #ccc; margin:12pt 0; }
sup,sub   { font-size:7.5pt; }
"""

# ── State ─────────────────────────────────────────────────────────────────────
class S:
    ch = sec = ssec = tab = fig = lst = 0
    appendix = False

# ── Helpers ───────────────────────────────────────────────────────────────────
def esc(s): return HM.escape(str(s), quote=False)

_TEXT = [
    (r'\\oe\{\}','œ'), (r'\\OE\{\}','Œ'), (r'\\ae\{\}','æ'),
    (r'(?<![\\-])---','—'), (r'(?<!\\)--','–'),
    (r'\\textendash\b','–'), (r'\\textemdash\b','—'),
    (r'\\ldots\b','…'), (r'\\dots\b','…'),
    (r'\\%','%'), (r'\\&(?!amp;)','&amp;'), (r'\\\$','$'),
    (r'\\_','_'), (r'\\#','#'),
    (r'\\textasciitilde(?:\{\})?','~'),
    (r'\\textasciicircum(?:\{\})?','^'),
    (r'\\checkmark\b','✓'), (r'\\times\b','×'),
    (r'\\,', ' '), (r'(?<!\\)~',' '),
    (r'\\noindent\b',''), (r'\\hfill\b',''), (r'\\vfill\b',''),
    (r'\\clearpage\b',''), (r'\\newpage\b',''),
    (r'\\bigskip\b',''), (r'\\medskip\b',''), (r'\\smallskip\b',''),
    (r'\\vspace\{[^}]*\}',''), (r'\\hspace\{[^}]*\}',' '),
    (r'\\setlength\{[^}]*\}\{[^}]*\}',''),
    (r'\\label\{[^}]*\}',''), (r'\\ref\{[^}]*\}',''),
    (r'\\pageref\{[^}]*\}',''), (r'\\eqref\{[^}]*\}',''),
    (r'\\centering\b',''), (r'\\raggedright\b',''), (r'\\raggedleft\b',''),
    (r'\\(?:small|normalsize|footnotesize|scriptsize|large|Large'
     r'|huge|Huge|normalfont|ttfamily|bfseries|itshape)\b',''),
    (r'\\addcontentsline\{[^}]*\}\{[^}]*\}\{[^}]*\}',''),
    (r'\\(?:tableofcontents|listoffigures|listoftables|printbibliography)\b',''),
    (r'\\rule\{[^}]*\}\{[^}]*\}','<hr class="sep">'),
    (r'\\(?:toprule|midrule|bottomrule|hline|endhead'
     r'|endfirsthead|endfoot|endlastfoot|arraybackslash)\b',''),
    (r'\\cline\{[^}]*\}',''),
]

def subst(s):
    for p, r in _TEXT:
        s = re.sub(p, r, s)
    return s

def math_txt(s):
    for p, r in [
        (r'\\mathbf\{([^}]*)\}', r'<strong>\1</strong>'),
        (r'\\text\{([^}]*)\}', r'\1'),
        (r'\\approx','≈'), (r'\\times','×'), (r'\\pm','±'),
        (r'\\lvert|\\rvert','|'),
        (r'\\varepsilon|\\epsilon','ε'), (r'\\delta','δ'),
        (r'\\Delta','Δ'), (r'\\sigma','σ'), (r'\\alpha','α'),
        (r'\\beta','β'), (r'\\pi\b','π'), (r'\\mu','μ'),
        (r'\\sqrt\{([^}]*)\}', r'√(\1)'),
        (r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)'),
        (r'\\\,',' '), (r'\\_','_'), (r'\\%','%'),
        (r'_\{([^}]*)\}', r'<sub>\1</sub>'),
        (r'\^\{([^}]*)\}', r'<sup>\1</sup>'),
        (r'_([a-zA-Z0-9])', r'<sub>\1</sub>'),
        (r'\^([a-zA-Z0-9])', r'<sup>\1</sup>'),
        (r'\\[a-zA-Z]+\{([^}]*)\}', r'\1'),
        (r'\\[a-zA-Z]+',''),
    ]:
        s = re.sub(p, r, s)
    return s

def inline(s):
    s = re.sub(r'\\pct\{([^}]*)\}', lambda m: m.group(1)+' %', s)
    s = re.sub(r'\\(?:code|texttt)\{([^{}]*)\}',
               lambda m: f'<code>{esc(m.group(1))}</code>', s)
    s = re.sub(r'\\textbf\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
               lambda m: f'<strong>{_inner(m.group(1))}</strong>', s)
    s = re.sub(r'\\(?:textit|emph|textsl)\{([^{}]*)\}', r'<em>\1</em>', s)
    s = re.sub(r'\\important\{([^{}]*)\}', r'<strong>\1</strong>', s)
    s = re.sub(r'\\textsuperscript\{([^{}]*)\}', r'<sup>\1</sup>', s)
    s = re.sub(r'\\textsubscript\{([^{}]*)\}', r'<sub>\1</sub>', s)
    s = re.sub(r'\\textsc\{([^{}]*)\}',
               r'<span style="font-variant:small-caps">\1</span>', s)
    s = re.sub(r'\\url\{([^{}]*)\}', r'<code>\1</code>', s)
    s = re.sub(r'\\href\{[^{}]*\}\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\textcolor\{[^{}]*\}\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\$([^$\n]{1,200})\$', lambda m: f'<i>{math_txt(m.group(1))}</i>', s)
    # fallback strips
    s = re.sub(r'\\[a-zA-Z]+\*?\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\*?\s*', '', s)
    return s

def _inner(s):  # simplified inline for nested bold
    s = re.sub(r'\\(?:code|texttt)\{([^{}]*)\}',
               lambda m: f'<code>{esc(m.group(1))}</code>', s)
    s = re.sub(r'\\pct\{([^}]*)\}', lambda m: m.group(1)+' %', s)
    s = re.sub(r'\\textsuperscript\{([^{}]*)\}', r'<sup>\1</sup>', s)
    s = re.sub(r'\\[a-zA-Z]+\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\s*', '', s)
    return s

def proc(s):
    return inline(subst(s))

def cell(s):
    s = subst(s)
    s = re.sub(r'\\textbf\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
               r'<strong>\1</strong>', s)
    s = re.sub(r'\\(?:code|texttt)\{([^{}]*)\}',
               lambda m: f'<code>{esc(m.group(1))}</code>', s)
    s = re.sub(r'\\(?:textit|emph)\{([^{}]*)\}', r'<em>\1</em>', s)
    s = re.sub(r'\\pct\{([^}]*)\}', lambda m: m.group(1)+' %', s)
    s = re.sub(r'\\textsuperscript\{([^{}]*)\}', r'<sup>\1</sup>', s)
    s = re.sub(r'\\checkmark\b', '✓', s)
    s = re.sub(r'\$\s*\\times\s*\$', '×', s)
    s = re.sub(r'\$([^$]{1,60})\$', lambda m: f'<i>{math_txt(m.group(1))}</i>', s)
    s = re.sub(r'\\multicolumn\{\d+\}\{[^}]*\}\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\*?\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\*?\s*', '', s)
    return s.strip()

# ── Environment finder ────────────────────────────────────────────────────────
def find_env(tex, env):
    """Find balanced \\begin{env}...\\end{env}.
    Returns (pre, args, content, post) or None."""
    bp = re.compile(r'\\begin\{' + re.escape(env) + r'\}')
    ep = re.compile(r'\\end\{' + re.escape(env) + r'\}')
    m  = bp.search(tex)
    if not m:
        return None
    pre = tex[:m.start()]
    pos = m.end()
    args = ''
    while pos < len(tex):
        am = re.match(r'\s*(\[[^\]]*\]|\{[^}]*\})', tex[pos:])
        if am:
            args += am.group(1); pos += am.end()
        else:
            break
    depth = 1; cs = pos
    while depth > 0 and pos < len(tex):
        nb = bp.search(tex, pos)
        ne = ep.search(tex, pos)
        if not ne: break
        if nb and nb.start() < ne.start():
            depth += 1; pos = nb.end()
        else:
            depth -= 1
            if depth == 0:
                return pre, args, tex[cs:ne.start()], tex[ne.end():]
            pos = ne.end()
    return None

# ── Table ─────────────────────────────────────────────────────────────────────
def _col_types(spec):
    cols, i, s = [], 0, spec.strip()
    while i < len(s):
        c = s[i]
        if c in 'lLrRcCXxmM':
            cols.append(c.lower()); i += 1
        elif c == 'p':
            j = s.find('}', i); cols.append('p')
            i = j+1 if j >= 0 else i+1
        elif c == '>':
            j = s.find('}', i)
            interior = s[i:j+1] if j >= 0 else ''
            mono = 'ttfamily' in interior or 'mono' in interior
            i = j+1 if j >= 0 else i+1
            if i < len(s):
                nc = s[i]
                if nc in 'lLrRcCpPXx':
                    if nc == 'p':
                        j2 = s.find('}', i)
                        i = j2+1 if j2 >= 0 else i+1
                    else:
                        i += 1
                    cols.append('mono' if mono else nc.lower())
                else:
                    i += 1
        elif c in '@|! ':
            i += 1
            if c in '@!':
                j = s.find('}', i)
                i = j+1 if j >= 0 else i+1
        else:
            i += 1
    return cols

def mk_table(raw, caption='', tnum=''):
    sm = re.match(r'\s*(?:\{[^}]*\}\s*)?\{([^}]*)\}(.*)', raw.strip(), re.DOTALL)
    if not sm:
        return f'<p>{proc(raw)}</p>'
    cols  = _col_types(sm.group(1))
    body  = sm.group(2)

    body = re.sub(r'\\toprule\b', 'XTOP', body)
    body = re.sub(r'\\midrule\b', 'XMID', body)
    body = re.sub(r'\\bottomrule\b', 'XBOT', body)
    body = re.sub(r'\\hline\b', 'XMID', body)
    body = re.sub(r'\\endhead\b|\\endfirsthead\b|\\endfoot\b|\\endlastfoot\b', '', body)
    body = re.sub(r'\\cline\{[^}]*\}', '', body)

    rows_html, is_hdr = [], True

    for rp in re.split(r'\\\\', body):
        rp_s = rp.strip()
        has_top = 'XTOP' in rp_s
        has_mid = 'XMID' in rp_s
        has_bot = 'XBOT' in rp_s
        clean = rp_s.replace('XTOP','').replace('XMID','').replace('XBOT','').strip()

        if has_mid and not clean:
            if not is_hdr:
                rows_html.append(
                    '<tr class="mid"><td colspan="20" style="padding:0;height:1px"></td></tr>')
            is_hdr = False
            continue
        if not clean:
            continue

        cells  = clean.split('&')
        tag    = 'th' if is_hdr else 'td'
        tr_cls = ' class="bot"' if has_bot else ''
        row    = f'<tr{tr_cls}>'
        for i, c in enumerate(cells):
            c = c.strip()
            mc = re.match(r'\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}$', c, re.DOTALL)
            if mc:
                row += f'<{tag} colspan="{mc.group(1)}">{cell(mc.group(2))}</{tag}>'
                continue
            ct = cols[i] if i < len(cols) else 'l'
            ex = (' class="col-r"' if ct=='r' else
                  ' class="col-c"' if ct=='c' else
                  ' class="mono"'  if ct=='mono' else '')
            row += f'<{tag}{ex}>{cell(c)}</{tag}>'
        row += '</tr>'
        rows_html.append(row)
        if is_hdr and (has_mid or has_top):
            is_hdr = False

    cap = ''
    if caption:
        num = f'<span class="tab-num">Tableau {tnum} — </span>' if tnum else ''
        cap = f'<div class="tab-cap">{num}{proc(caption)}</div>\n'
    return cap + '<table>' + ''.join(rows_html) + '</table>'

# ── Listing ───────────────────────────────────────────────────────────────────
def mk_listing(content, args):
    content = content.strip('\n')
    cap_m   = re.search(r'caption=\{([^}]*)\}', args)
    caption = cap_m.group(1) if cap_m else ''
    S.lst  += 1
    cap_html = ''
    if caption:
        cap_html = f'<div class="listing-cap">Listing {S.lst} — {esc(caption)}</div>'
    return f'<pre>{esc(content)}</pre>\n{cap_html}'

# ── Lists ─────────────────────────────────────────────────────────────────────
def mk_list(env, content):
    tag  = 'ul' if env == 'itemize' else 'ol'
    bits = re.split(r'\\item\b', content)
    items = []
    for raw in bits[1:]:
        lm = re.match(r'\s*\[([^\]]*)\]\s*', raw)
        lbl = ''
        if lm:
            lbl = f'<strong>{proc(lm.group(1))}</strong> '
            raw = raw[lm.end():]
        items.append(f'<li>{lbl}{convert(raw.strip())}</li>')
    return f'<{tag}>' + ''.join(items) + f'</{tag}>'

def mk_desc(content):
    bits  = re.split(r'\\item\b', content)
    items = []
    for raw in bits[1:]:
        lm = re.match(r'\s*\[([^\]]*)\]\s*', raw)
        term = ''
        if lm:
            term = f'<dt>{proc(lm.group(1))}</dt>'
            raw  = raw[lm.end():]
        items.append(f'{term}<dd>{convert(raw.strip())}</dd>')
    return '<dl>' + ''.join(items) + '</dl>'

# ── Colour boxes ──────────────────────────────────────────────────────────────
def mk_box(cls, args, content):
    tm = re.match(r'\[([^\]]*)\]', args)
    title = tm.group(1) if tm else ''
    th = f'<div class="box-title">{proc(title)}</div>\n' if title.strip() else ''
    return f'<div class="{cls}">{th}{convert(content)}</div>'

# ── Figure ────────────────────────────────────────────────────────────────────
def mk_figure(content):
    S.fig += 1
    ig = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}', content)
    img = ''
    if ig:
        rp = ig.group(1).replace('\\', '/')
        p  = BASE / rp
        if p.exists():
            img = f'<img src="{p.as_uri()}" alt="Figure {S.fig}">'
        else:
            img = f'<p style="color:#aaa;text-align:center">[Figure: {esc(rp)}]</p>'
    cap_m = re.search(r'\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', content)
    cap   = f'<figcaption>Figure {S.fig} — {proc(cap_m.group(1))}</figcaption>' if cap_m else ''
    return f'<figure>{img}{cap}</figure>'

# ── Equation ──────────────────────────────────────────────────────────────────
def mk_eq(content):
    return f'<div class="equation">{math_txt(content.strip())}</div>'

# ── Acronym ───────────────────────────────────────────────────────────────────
def mk_acronym(content):
    items = re.findall(r'\\acro\{([^}]*)\}\{([^}]*)\}', content)
    if not items:
        return ''
    rows = ''.join(f'<tr><td><strong>{esc(a)}</strong></td><td>{esc(d)}</td></tr>'
                   for a, d in items)
    return (f'<table class="nw"><tr><th>Acronyme</th><th>Signification</th></tr>'
            f'{rows}</table>')

# ── Table within a \begin{table} wrapper ─────────────────────────────────────
def mk_table_env(content):
    cap_m   = re.search(r'\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', content)
    caption = cap_m.group(1) if cap_m else ''
    S.tab  += 1
    tnum    = str(S.tab)
    for tenv in ('tabularx', 'tabular', 'longtable'):
        r = find_env(content, tenv)
        if r:
            _, tab_args, tab_body, _ = r
            return mk_table(tab_args + tab_body, caption, tnum)
    return mk_table(content, caption, tnum)

# ── titlepage ─────────────────────────────────────────────────────────────────
def mk_titlepage(content):
    return f'<div class="titlepage">{convert(content)}</div>'

# ── Paragraphs (structural text, no environments) ────────────────────────────
def mk_paragraphs(tex):
    if not tex.strip():
        return ''

    # appendix marker
    if '___APPENDIX___' in tex:
        parts = tex.split('___APPENDIX___', 1)
        return mk_paragraphs(parts[0]) + _do_appendix() + mk_paragraphs(parts[1])

    # Headings
    def do_ch(m):
        S.ch += 1; S.sec = 0; S.ssec = 0
        lbl = (f'Annexe {chr(64+S.ch)}' if S.appendix
               else f'Chapitre {S.ch}')
        return f'<h1><span class="ch-label">{lbl}</span>{proc(m.group(1))}</h1>\n'

    def do_ch_star(m):
        return f'<h1 class="nopb">{proc(m.group(1))}</h1>\n'

    def do_sec(m):
        S.sec += 1; S.ssec = 0
        num = f'{S.ch}.{S.sec} ' if S.ch else ''
        return f'<h2>{num}{proc(m.group(1))}</h2>\n'

    def do_sec_star(m):
        return f'<h2>{proc(m.group(1))}</h2>\n'

    def do_ssec(m):
        S.ssec += 1
        num = f'{S.ch}.{S.sec}.{S.ssec} ' if S.ch else ''
        return f'<h3>{num}{proc(m.group(1))}</h3>\n'

    def do_sssec(m):
        return f'<h4>{proc(m.group(1))}</h4>\n'

    tex = re.sub(r'\\chapter\*\{([^{}]*)\}',       do_ch_star,  tex)
    tex = re.sub(r'\\chapter\{([^{}]*)\}',          do_ch,       tex)
    tex = re.sub(r'\\section\*\{([^{}]*)\}',        do_sec_star, tex)
    tex = re.sub(r'\\section\{([^{}]*)\}',           do_sec,      tex)
    tex = re.sub(r'\\subsection\*?\{([^{}]*)\}',    do_ssec,     tex)
    tex = re.sub(r'\\subsubsection\*?\{([^{}]*)\}', do_sssec,    tex)

    tex = subst(tex)
    tex = inline(tex)

    # Block math \[...\]
    tex = re.sub(r'\\\[(.*?)\\\]',
                 lambda m: mk_eq(m.group(1)), tex, flags=re.DOTALL)

    # Split into paragraphs
    chunks = re.split(r'\n{2,}', tex.strip())
    out = []
    HTML_BLOCK = re.compile(r'^<(?:h[1-6]|hr|div|table|ul|ol|dl|figure|pre|blockquote)')
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        if HTML_BLOCK.match(ch):
            out.append(ch)
        else:
            ch = re.sub(r'\n', ' ', ch)
            ch = re.sub(r'  +', ' ', ch).strip()
            if ch:
                out.append(f'<p>{ch}</p>')
    return '\n'.join(out)

def _do_appendix():
    S.appendix = True; S.ch = 0; S.sec = 0; S.ssec = 0
    return ''

# ── Master env table ──────────────────────────────────────────────────────────
# (env_name, handler)  — order matters for same-position ties
_ENVS = [
    ('lstlisting',  lambda a,c: mk_listing(c, a)),
    ('table*',      lambda a,c: mk_table_env(c)),
    ('table',       lambda a,c: mk_table_env(c)),
    ('figure*',     lambda a,c: mk_figure(c)),
    ('figure',      lambda a,c: mk_figure(c)),
    ('infobox',     lambda a,c: mk_box('infobox',   a, c)),
    ('resultbox',   lambda a,c: mk_box('resultbox', a, c)),
    ('warnbox',     lambda a,c: mk_box('warnbox',   a, c)),
    ('itemize',     lambda a,c: mk_list('itemize',  c)),
    ('enumerate',   lambda a,c: mk_list('enumerate',c)),
    ('description', lambda a,c: mk_desc(c)),
    ('acronym',     lambda a,c: mk_acronym(c)),
    ('equation*',   lambda a,c: mk_eq(c)),
    ('equation',    lambda a,c: mk_eq(c)),
    ('align*',      lambda a,c: mk_eq(c)),
    ('align',       lambda a,c: mk_eq(c)),
    ('pmatrix',     lambda a,c: mk_eq(c)),
    ('titlepage',   lambda a,c: mk_titlepage(c)),
    ('tabularx',    lambda a,c: mk_table(a+c)),
    ('tabular',     lambda a,c: mk_table(a+c)),
    ('longtable',   lambda a,c: mk_table(a+c)),
    ('subfigure',   lambda a,c: mk_figure(c)),
]

_ENV_PATS = [(e, re.compile(r'\\begin\{' + re.escape(e) + r'\}'), h)
             for e, h in _ENVS]

def convert(tex):
    """Convert a block of LaTeX to HTML (main recursive function)."""
    result = []
    remaining = tex

    while remaining:
        # Find earliest environment start
        best_pos, best_env, best_pat, best_handler = len(remaining)+1, None, None, None
        for env, pat, handler in _ENV_PATS:
            m = pat.search(remaining)
            if m and m.start() < best_pos:
                best_pos, best_env, best_handler = m.start(), env, handler

        if best_env is None:
            result.append(mk_paragraphs(remaining))
            break

        r = find_env(remaining, best_env)
        if not r:
            result.append(mk_paragraphs(remaining))
            break

        pre, args, content, post = r
        result.append(mk_paragraphs(pre))
        result.append(best_handler(args, content))
        remaining = post

    return '\n'.join(x for x in result if x)

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    print("Lecture ...")
    tex = TEX_FILE.read_text(encoding='utf-8')

    # Strip LaTeX comments
    tex = re.sub(r'%.*', '', tex)

    # Extract document body
    m = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', tex, re.DOTALL)
    body = m.group(1) if m else tex

    # Mark appendix
    body = re.sub(r'\\appendix\b', '___APPENDIX___', body)

    print("Conversion …")
    body_html = convert(body)

    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8">
<title>Mémoire MSPR — Electio-Analytics</title>
<style>{CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""

    html_path = BASE / "memoire_debug.html"
    html_path.write_text(full_html, encoding='utf-8')
    print(f"HTML -> {html_path}")

    print("PDF weasyprint ...")
    try:
        from weasyprint import HTML as WP
        WP(filename=str(html_path), base_url=str(BASE)).write_pdf(str(PDF_FILE))
        print(f"OK  PDF -> {PDF_FILE}")
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        raise

if __name__ == '__main__':
    main()
