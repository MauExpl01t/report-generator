"""Genera el informe HTML tipo dashboard: un solo archivo, sin dependencias ni recursos externos."""
from __future__ import annotations

import base64
import math
import re
from datetime import datetime
from html import escape as esc
from pathlib import Path
from urllib.parse import urlparse

from . import __version__
from . import knowledge as kb
from .model import SEV_LABEL, SEV_ORDER, SEV_WEIGHT, Finding, Report

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
LOGO_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
              ".webp": "image/webp", ".svg": "image/svg+xml"}
MAX_LOGO = 2 * 1024 * 1024

LIGHT = """--bg:#f4f6fb;--surface:#ffffff;--surface-2:#eef2f9;--text:#0f172a;--muted:#55607a;--line:#e1e6f0;
--link:#1d4ed8;--ok:#15803d;--ok-bg:#e3f4ea;
--sev-critical:#991b1b;--sev-critical-bg:#fbdcdc;--sev-high:#c0262d;--sev-high-bg:#fde8e8;
--sev-medium:#b45309;--sev-medium-bg:#ffedd5;--sev-low:#8a6a06;--sev-low-bg:#fef3c7;
--sev-info:#475569;--sev-info-bg:#e8edf3;--shadow:0 1px 2px rgba(15,23,42,.06),0 4px 14px rgba(15,23,42,.05);"""
DARK = """--bg:#0b1020;--surface:#141b2e;--surface-2:#1a2340;--text:#e8edf8;--muted:#a0acc5;--line:#263150;
--link:#8ab4ff;--ok:#4ade80;--ok-bg:#11301f;
--sev-critical:#fca5a5;--sev-critical-bg:#4a1d1d;--sev-high:#f87171;--sev-high-bg:#43201f;
--sev-medium:#fb923c;--sev-medium-bg:#43280f;--sev-low:#facc15;--sev-low-bg:#3b3210;
--sev-info:#a9b6cc;--sev-info-bg:#1f2a3d;--shadow:0 1px 2px rgba(0,0,0,.4);"""

CSS = """
:root{__LIGHT__--accent:__ACCENT__;}
@media (prefers-color-scheme:dark){:root{__DARK__}}
*{box-sizing:border-box}
[hidden]{display:none!important}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--link)}
h1,h2,h3,h4{line-height:1.25;margin:0}
h2{font-size:1.3rem;margin-bottom:.35rem}
.sec-lead{color:var(--muted);margin:0 0 1rem;max-width:70ch}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
.top{background:linear-gradient(135deg,var(--accent),color-mix(in srgb,var(--accent) 55%,#000));color:#fff;padding:28px 0 32px}
.top-row{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:14px}
.brand img{max-height:48px;max-width:160px;background:#fff;border-radius:8px;padding:6px}
.eyebrow{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;opacity:.85}
.top h1{font-size:clamp(1.5rem,3.5vw,2.2rem);margin-top:4px}
.meta{display:flex;flex-wrap:wrap;gap:6px 22px;margin-top:14px;font-size:.92rem;opacity:.95}
.meta b{font-weight:600}
.tools{display:flex;gap:8px;flex-wrap:wrap}
.btn{font:inherit;font-size:.88rem;background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.4);
border-radius:8px;padding:7px 12px;cursor:pointer}
.btn:hover{background:rgba(255,255,255,.28)}
nav.sticky{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--line)}
nav.sticky .wrap{display:flex;gap:4px;overflow-x:auto}
nav.sticky a{padding:12px 12px;text-decoration:none;color:var(--muted);font-size:.9rem;white-space:nowrap}
nav.sticky a:hover{color:var(--text)}
main{margin-top:24px;padding-bottom:40px}
section{margin-top:28px;scroll-margin-top:56px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;box-shadow:var(--shadow)}
.hero{display:grid;grid-template-columns:300px 1fr;gap:16px}
.gauge-card{text-align:center}
.gauge{width:190px;height:190px}
.g-track{fill:none;stroke:var(--line);stroke-width:12}
.g-val{fill:none;stroke-width:12;stroke-linecap:round}
.g-num{font-size:40px;font-weight:700;text-anchor:middle;fill:var(--text)}
.g-sub{font-size:11px;text-anchor:middle;fill:var(--muted)}
.grade{display:inline-block;margin-top:6px;padding:4px 14px;border-radius:999px;font-weight:700;color:#fff}
.note{color:var(--muted);font-size:.82rem;margin:10px 0 0}
.summary-card p{margin:.4rem 0}
.urgent-list{margin:.6rem 0 0;padding-left:1.2rem}
.urgent-list li{margin:.2rem 0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}
.kpi{padding:16px}
.kpi .n{font-size:2rem;font-weight:700;line-height:1.1}
.kpi .l{font-weight:600;margin-top:2px}
.kpi .s{color:var(--muted);font-size:.84rem}
.two{display:grid;grid-template-columns:minmax(260px,380px) 1fr;gap:16px}
.bar-row{display:grid;grid-template-columns:86px 1fr 28px;gap:10px;align-items:center;margin:10px 0;font-size:.92rem}
.bar{height:12px;border-radius:999px;background:var(--surface-2);overflow:hidden}
.bar i{display:block;height:100%;border-radius:999px}
.bar-n{text-align:right;font-weight:600}
.cats{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.cat{padding:14px;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
.cat svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.cat-h{display:flex;gap:8px;align-items:center;font-weight:600;font-size:.95rem}
.cat p{color:var(--muted);font-size:.8rem;margin:6px 0 8px}
.pill{display:inline-block;font-size:.76rem;font-weight:600;border-radius:999px;padding:2px 10px}
.pill.ok{color:var(--ok);background:var(--ok-bg)}
.pill.na{color:var(--sev-info);background:var(--sev-info-bg)}
.good{display:flex;flex-wrap:wrap;gap:8px}
.good .pill{font-size:.86rem;padding:5px 12px}
.plan{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.plan-col{border-top:5px solid var(--c);padding:16px}
.plan-col h3{font-size:1.05rem}
.plan-col h3 small{display:block;color:var(--muted);font-weight:400;font-size:.8rem}
.plan-col ol{margin:.8rem 0 0;padding:0;list-style:none}
.plan-col li{padding:10px 0;border-top:1px solid var(--line)}
.plan-col li:first-child{border-top:0}
.plan-col a{font-weight:600;text-decoration:none}
.plan-col a:hover{text-decoration:underline}
.empty{color:var(--muted);font-size:.9rem;margin:.8rem 0 0}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.tag{font-size:.74rem;color:var(--muted);background:var(--surface-2);border-radius:6px;padding:2px 8px}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}
.chip{font:inherit;font-size:.86rem;border:1px solid var(--line);background:var(--surface);color:var(--text);
border-radius:999px;padding:5px 14px;cursor:pointer}
.chip[aria-pressed=true]{background:var(--text);color:var(--bg);border-color:var(--text)}
details.finding{background:var(--surface);border:1px solid var(--line);border-left:6px solid var(--c);
border-radius:12px;margin:10px 0;box-shadow:var(--shadow)}
details.finding>summary{list-style:none;cursor:pointer;display:flex;gap:12px;align-items:center;padding:14px 16px}
details.finding>summary::-webkit-details-marker{display:none}
details.finding>summary::after{content:"";margin-left:auto;width:9px;height:9px;border-right:2px solid var(--muted);
border-bottom:2px solid var(--muted);transform:rotate(45deg);transition:transform .15s;flex:none}
details.finding[open]>summary::after{transform:rotate(-135deg)}
.sev{flex:none;font-size:.76rem;font-weight:700;border-radius:6px;padding:3px 9px;color:var(--c);background:var(--cb)}
.f-title{font-weight:600}
.f-cat{color:var(--muted);font-size:.8rem;margin-left:4px}
.f-body{padding:0 16px 16px}
.f-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.f-block{background:var(--surface-2);border-radius:10px;padding:12px 14px}
.f-block h4{font-size:.84rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:4px}
.f-block p{margin:0;font-size:.95rem}
.f-block.fix{background:var(--ok-bg)}
.f-block.fix h4{color:var(--ok)}
details.tech{margin-top:12px;border:1px dashed var(--line);border-radius:10px;padding:8px 14px}
details.tech summary{cursor:pointer;font-size:.88rem;color:var(--muted)}
details.tech dl{margin:10px 0 0;font-size:.9rem}
details.tech dt{font-weight:600;margin-top:8px}
details.tech dd{margin:2px 0 0}
pre{background:var(--surface-2);padding:10px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin:0;font-size:.84rem}
.code{font-family:ui-monospace,Consolas,monospace;font-size:.8rem;color:var(--muted)}
.scope{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.scope ul{margin:.5rem 0 0;padding-left:1.2rem}
.scope li{margin:.35rem 0;font-size:.94rem}
.warn{border-left:5px solid var(--sev-medium);background:var(--sev-medium-bg);border-radius:10px;padding:10px 14px;margin-top:14px;font-size:.9rem}
.gloss{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.gloss div{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:.9rem}
.gloss b{display:block}
footer{margin-top:36px;padding:20px 0 40px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line)}
@media screen and (max-width:900px){
 .hero,.two,.scope{grid-template-columns:1fr}
 .kpis{grid-template-columns:repeat(2,1fr)}
 .plan,.f-grid{grid-template-columns:1fr}
}
@page{size:A4;margin:10mm}
@media print{
 :root{__LIGHT__}
 body{background:#fff;font-size:12px}
 .hero{grid-template-columns:230px 1fr}
 .two{grid-template-columns:260px 1fr}
 .gauge{width:150px;height:150px}
 .cats{grid-template-columns:repeat(2,1fr)}
 .f-block p{font-size:.9rem}
 .tools,nav.sticky,.filters{display:none!important}
 .top{padding-bottom:24px;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 main{margin-top:12px}
 .card,details.finding{box-shadow:none}
 .kpi,.cat,details.finding,.plan-col li,.gloss div,.bar-row{break-inside:avoid}
 h2,h3{break-after:avoid}
 .plan{break-inside:avoid}
 .f-body{padding:0 12px 12px}
 details.finding>summary{padding:10px 12px}
 details.tech dt{margin-top:4px}
 details.tech{margin-top:8px;padding:6px 12px}
 details.finding{margin:8px 0}
 *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
 section{margin-top:20px}
}
"""

JS = """
(function(){
  var t=document.querySelector('.tools'); if(t){t.hidden=false;}
  var chips=[].slice.call(document.querySelectorAll('[data-filter]'));
  var items=[].slice.call(document.querySelectorAll('details.finding'));
  chips.forEach(function(c){c.addEventListener('click',function(){
    var f=c.getAttribute('data-filter');
    chips.forEach(function(x){x.setAttribute('aria-pressed',x===c?'true':'false');});
    items.forEach(function(d){d.hidden=!(f==='ALL'||d.getAttribute('data-sev')===f);});
  });});
  var tog=document.getElementById('toggle-all'), open=false;
  if(tog){tog.addEventListener('click',function(){
    open=!open;
    [].forEach.call(document.querySelectorAll('details.finding'),function(d){d.open=open;});
    tog.textContent=open?'Contraer todo':'Expandir todo';
  });}
  var pr=document.getElementById('print-btn');
  if(pr){pr.addEventListener('click',function(){
    [].forEach.call(document.querySelectorAll('details'),function(d){d.open=true;});
    window.print();
  });}
  function show(){
    var id=location.hash.slice(1); if(!id){return;}
    var el=document.getElementById(id);
    if(el&&el.tagName==='DETAILS'){el.hidden=false;el.open=true;}
  }
  window.addEventListener('hashchange',show); show();
})();
"""

_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true">{}</svg>'


def fmt_date(iso: str) -> str:
    if not iso:
        return ""
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def grade(score: int, subject: str = "El sitio") -> tuple[str, str, str]:
    """(etiqueta, variable CSS de color, frase corta)"""
    if score >= 90:
        return "Excelente", "--ok", f"{subject} tiene una base de seguridad sólida; lo pendiente es menor."
    if score >= 75:
        return "Bueno", "--ok", f"{subject} tiene una buena base, con mejoras recomendables."
    if score >= 55:
        return "Mejorable", "--sev-low", "Hay varios puntos que conviene corregir pronto."
    if score >= 30:
        return "Riesgoso", "--sev-medium", "Hay problemas que un atacante podría aprovechar."
    return "Crítico", "--sev-critical", "Hay problemas graves que deben corregirse de inmediato."


def load_logo(path: str) -> str:
    p = Path(path)
    mime = LOGO_TYPES.get(p.suffix.lower())
    if not mime:
        raise ValueError("El logo debe ser PNG, JPG, GIF, WEBP o SVG.")
    data = p.read_bytes()
    if len(data) > MAX_LOGO:
        raise ValueError("El logo pesa más de 2 MB.")
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def _sev_vars(sev: str) -> str:
    s = sev.lower()
    return f"--c:var(--sev-{s});--cb:var(--sev-{s}-bg)"


def _plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def _host(target: str) -> str:
    return urlparse(target).netloc or target


def _gauge(score: int, color_var: str) -> str:
    r = 54
    c = 2 * math.pi * r
    off = c * (1 - score / 100)
    return (f'<svg class="gauge" viewBox="0 0 140 140" role="img" aria-label="Puntaje {score} de 100">'
            f'<circle class="g-track" cx="70" cy="70" r="{r}"/>'
            f'<circle class="g-val" cx="70" cy="70" r="{r}" transform="rotate(-90 70 70)" '
            f'style="stroke:var({color_var});stroke-dasharray:{c:.1f};stroke-dashoffset:{off:.1f}"/>'
            f'<text class="g-num" x="70" y="76">{score}</text><text class="g-sub" x="70" y="94">de 100</text></svg>')


def is_network_report(rep: Report) -> bool:
    """True si el informe viene de un escaneo de puertos (port-scanner) y no de una revisión de sitio web."""
    run = set(rep.checks_run)
    return bool(run & kb.CATEGORIES["ports"].checks) and not any(
        run & c.checks for k, c in kb.CATEGORIES.items() if k != "ports")


def _executive_summary(rep: Report, label: str, headline: str, active: bool, net: bool = False) -> str:
    counts = rep.counts()
    n = len(rep.findings)
    method = ("Realizamos un análisis que incluyó pruebas activas controladas"
              if active else "Realizamos un análisis pasivo: observamos cómo responde el sitio, sin intentar vulnerarlo")
    if net:
        method = ("Realizamos un escaneo de red: revisamos qué puertos y servicios responden en los equipos, sin "
                  "intentar vulnerarlos ni entrar en ellos")
    out = [f"{method} sobre <b>{esc(_host(rep.target))}</b>. El resultado general es <b>{label.lower()}</b> "
           f"({rep.score}/100). {esc(headline)}"]
    if n == 0:
        out.append("No encontramos puntos de mejora en lo que revisamos. Conviene repetir el análisis cada cierto "
                   "tiempo, porque la seguridad cambia con cada actualización del " + ("equipo." if net else "sitio."))
    else:
        urgent = counts["CRITICAL"] + counts["HIGH"]
        quick = sum(1 for f in rep.findings if f.severity != "INFO" and kb.explain(f.check).effort == 1)
        s = f"Detectamos <b>{_plural(n, 'punto', 'puntos')}</b> a revisar"
        s += f", de los cuales <b>{urgent}</b> {'es urgente' if urgent == 1 else 'son urgentes'}." if urgent else "; ninguno es urgente."
        if quick:
            s += (f" Buena noticia: <b>{quick}</b> {'se puede resolver' if quick == 1 else 'se pueden resolver'} "
                  f"en pocos minutos.")
        out.append(s)
    return "".join(f"<p>{p}</p>" for p in out)


def _category_blocks(rep: Report) -> tuple[str, str]:
    """(tarjetas de categorías, chips 'lo que está bien')"""
    by_cat: dict[str, list[Finding]] = {}
    for f in rep.findings:
        by_cat.setdefault(kb.category_of(f.check), []).append(f)
    run = set(rep.checks_run)
    # Un informe de escaneo de puertos no revisó el sitio web: no mostramos esas áreas como "No evaluado".
    ports_only = is_network_report(rep)
    cards, good = [], []
    for key, cat in kb.CATEGORIES.items():
        fs = by_cat.get(key, [])
        evaluated = bool(fs) or (not run and key not in ("active", "other", "ports")) or bool(run & cat.checks)
        if key == "other" and not fs:
            continue
        if key in ("active", "ports") and not fs and not (run & cat.checks):
            continue
        if ports_only and not evaluated:
            continue
        icon = _ICON.format(cat.icon)
        if not evaluated:
            cards.append(f'<div class="cat"><div class="cat-h">{icon}{esc(cat.name)}</div><p>{esc(cat.blurb)}</p>'
                         f'<span class="pill na">No evaluado</span></div>')
            continue
        penalty = sum(SEV_WEIGHT[f.severity] for f in fs)
        health = max(0, 100 - penalty)
        if not fs:
            good.append(f'<span class="pill ok">{esc(cat.name)}</span>')
            status = '<span class="pill ok">Sin problemas</span>'
            col = "--ok"
        else:
            worst = min((SEV_ORDER.index(f.severity) for f in fs))
            sv = SEV_ORDER[worst].lower()
            col = f"--sev-{sv}"
            status = (f'<span class="pill" style="color:var({col});background:var(--sev-{sv}-bg)">'
                      f'{_plural(len(fs), "punto", "puntos")} a revisar</span>')
        cards.append(f'<div class="cat"><div class="cat-h" style="color:var({col})">{icon}'
                     f'<span style="color:var(--text)">{esc(cat.name)}</span></div><p>{esc(cat.blurb)}</p>'
                     f'<div class="bar" style="margin-bottom:8px"><i style="width:{health}%;background:var({col})"></i></div>'
                     f'{status}</div>')
    return "".join(cards), "".join(good)


def _plan(sorted_f: list[Finding]) -> str:
    groups = [
        ("Urgente", "esta semana", "--sev-critical", {"CRITICAL", "HIGH"}),
        ("Importante", "durante este mes", "--sev-medium", {"MEDIUM"}),
        ("Mejora continua", "cuando haya oportunidad", "--sev-info", {"LOW", "INFO"}),
    ]
    cols = []
    for title, when, color, sevs in groups:
        items = [(i, f) for i, f in enumerate(sorted_f, 1) if f.severity in sevs]
        items.sort(key=lambda p: (SEV_ORDER.index(p[1].severity) // 2, kb.explain(p[1].check).effort, p[0]))
        if items:
            lis = ""
            for i, f in items:
                ex = kb.explain(f.check)
                lis += (f'<li><a href="#f-{i}">{esc(f.title)}</a><div class="tags">'
                        f'<span class="tag">{esc(kb.EFFORT[ex.effort])}</span>'
                        f'<span class="tag">{esc(kb.WHO[ex.who])}</span></div></li>')
            body = f"<ol>{lis}</ol>"
        else:
            body = '<p class="empty">Nada pendiente en este grupo.</p>'
        cols.append(f'<div class="card plan-col" style="--c:var({color})"><h3>{title}<small>{when}</small></h3>{body}</div>')
    return "".join(cols)


def _finding(i: int, f: Finding, expand: bool) -> str:
    ex = kb.explain(f.check)
    cat = kb.CATEGORIES[kb.category_of(f.check)]
    op = " open" if expand else ""
    tech = []
    if f.description:
        tech.append(f"<dt>Lo que detectó el análisis</dt><dd>{esc(f.description)}</dd>")
    if f.evidence:
        tech.append(f"<dt>Evidencia</dt><dd><pre>{esc(f.evidence)}</pre></dd>")
    if f.recommendation:
        tech.append(f"<dt>Recomendación técnica</dt><dd>{esc(f.recommendation)}</dd>")
    if f.reference and urlparse(f.reference).scheme in ("http", "https"):
        tech.append(f'<dt>Más información</dt><dd><a href="{esc(f.reference, quote=True)}" '
                    f'rel="noopener noreferrer" target="_blank">{esc(f.reference)}</a></dd>')
    tech.append(f'<dt>Identificador</dt><dd><span class="code">{esc(f.check)}</span></dd>')
    return (
        f'<details class="finding" id="f-{i}" data-sev="{f.severity}" style="{_sev_vars(f.severity)}"{op}>'
        f'<summary><span class="sev">{SEV_LABEL[f.severity]}</span>'
        f'<span><span class="f-title">{esc(f.title)}</span><span class="f-cat"> · {esc(cat.name)}</span></span></summary>'
        f'<div class="f-body"><div class="f-grid">'
        f'<div class="f-block"><h4>¿Qué significa?</h4><p>{esc(ex.what)}</p></div>'
        f'<div class="f-block"><h4>¿Por qué importa?</h4><p>{esc(ex.why)}</p></div>'
        f'<div class="f-block fix"><h4>¿Cómo se arregla?</h4><p>{esc(ex.fix)}</p><div class="tags">'
        f'<span class="tag">{esc(kb.EFFORT[ex.effort])}</span><span class="tag">{esc(kb.WHO[ex.who])}</span></div></div>'
        f'</div><details class="tech"{op}><summary>Detalle técnico (para quien implementa)</summary>'
        f'<dl>{"".join(tech)}</dl></details></div></details>')


def render_html(rep: Report, client: str = "", author: str = "", logo_path: str = "",
                accent: str = "#2563eb", expand: bool = False) -> str:
    if not HEX.match(accent):
        raise ValueError("El color de acento debe tener formato #RRGGBB (por ejemplo #2563eb).")
    logo = load_logo(logo_path) if logo_path else ""

    net = is_network_report(rep)
    label, gcolor, headline = grade(rep.score, "La red revisada" if net else "El sitio")
    run = set(rep.checks_run)
    active = bool(run & kb.CATEGORIES["active"].checks)
    sorted_f = rep.sorted_findings()
    counts = rep.counts()
    host = _host(rep.target)
    date = fmt_date(rep.finished_at or rep.started_at)
    urgent = counts["CRITICAL"] + counts["HIGH"]
    quick = sum(1 for f in sorted_f if f.severity != "INFO" and kb.explain(f.check).effort == 1)
    cats_html, good_html = _category_blocks(rep)

    # --- cabecera ---
    brand = f'<img src="{esc(logo, quote=True)}" alt="Logo">' if logo else ""
    meta = [f"<span><b>{'Equipos' if net else 'Sitio'}:</b> {esc(rep.target)}</span>"]
    if client:
        meta.insert(0, f"<span><b>Cliente:</b> {esc(client)}</span>")
    if date:
        meta.append(f"<span><b>Fecha:</b> {esc(date)}</span>")
    if author:
        meta.append(f"<span><b>Preparado por:</b> {esc(author)}</span>")

    # --- top 3 urgentes ---
    top = [f for f in sorted_f if f.severity in ("CRITICAL", "HIGH")][:3]
    top_html = ""
    if top:
        top_html = ('<p style="margin-top:.8rem"><b>Lo primero que hay que atender:</b></p><ul class="urgent-list">'
                    + "".join(f"<li>{esc(f.title)}</li>" for f in top) + "</ul>")

    # --- severidad ---
    mx = max(max(counts.values()), 1)
    sev_rows = "".join(
        f'<div class="bar-row"><span>{SEV_LABEL[s]}</span><div class="bar"><i style="width:{counts[s] / mx * 100:.0f}%;'
        f'background:var(--sev-{s.lower()})"></i></div><span class="bar-n">{counts[s]}</span></div>' for s in SEV_ORDER)

    # --- hallazgos ---
    chips = ['<button class="chip" data-filter="ALL" aria-pressed="true">Todos ({})</button>'.format(len(sorted_f))]
    chips += [f'<button class="chip" data-filter="{s}" aria-pressed="false">{SEV_LABEL[s]} ({counts[s]})</button>'
              for s in SEV_ORDER if counts[s]]
    findings_html = ("".join(_finding(i, f, expand) for i, f in enumerate(sorted_f, 1))
                     or '<div class="card">No se detectaron hallazgos en los controles revisados.</div>')

    # --- alcance ---
    checks_li = "".join(f"<li><b>{esc(c)}</b>: {esc(kb.CHECK_INFO.get(c, 'Chequeo adicional.'))}</li>"
                        for c in rep.checks_run) or "<li>No se informaron los controles ejecutados.</li>"
    limits = ["Es una fotografía del momento: el estado puede cambiar con cada actualización del sitio.",
              "Un puntaje alto no garantiza que no existan vulnerabilidades; solo indica que lo revisado está bien.",
              "No se revisó el código interno, la base de datos ni los sistemas de la empresa fuera del sitio.",
              "El puntaje es una guía orientativa para priorizar, no una certificación."]
    limits.insert(0, "Se realizaron pruebas activas controladas sobre los formularios y parámetros." if active else
                  "Fue un análisis pasivo: no se intentó vulnerar el sitio ni se enviaron ataques de prueba.")
    if net:
        limits = ["Es una fotografía del momento: los puertos abiertos pueden cambiar cuando se enciende, apaga o "
                  "actualiza un servicio.",
                  "Solo se revisó lo visible desde donde se hizo el escaneo; un puerto cerrado aquí puede estar abierto "
                  "para otras redes (y al revés).",
                  "No se probaron contraseñas ni se intentó entrar a los servicios: solo se detectó qué hay y si está expuesto.",
                  "El puntaje es una guía orientativa para priorizar, no una certificación."]
    warn = ""
    if rep.errors:
        warn = ('<div class="warn"><b>Avisos del análisis:</b> algunos controles no pudieron completarse, por lo que '
                'el resultado podría estar incompleto.<ul>' + "".join(f"<li>{esc(e)}</li>" for e in rep.errors)
                + "</ul></div>")

    # --- glosario ---
    terms: list[str] = []
    for f in sorted_f:
        for t in kb.explain(f.check).terms:
            if t in kb.GLOSSARY and t not in terms:
                terms.append(t)
    gloss = ""
    if terms:
        gloss = ('<section id="glosario"><h2>Glosario</h2><p class="sec-lead">Términos técnicos que aparecen en este '
                 'informe, explicados en simple.</p><div class="gloss">'
                 + "".join(f"<div><b>{esc(t)}</b>{esc(kb.GLOSSARY[t])}</div>" for t in terms) + "</div></section>")

    good_section = ""
    if good_html:
        good_section = (f'<section><h2>Lo que está bien</h2><p class="sec-lead">Áreas revisadas donde no encontramos '
                        f'problemas.</p><div class="good">{good_html}</div></section>')

    css = CSS.replace("__LIGHT__", LIGHT).replace("__DARK__", DARK).replace("__ACCENT__", accent)
    footer_by = f" por {esc(author)}" if author else ""
    title = f"Informe de seguridad - {host}"

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{esc(title)}</title>
<style>{css}</style></head>
<body>
<header class="top"><div class="wrap">
 <div class="top-row">
  <div class="brand">{brand}<div><div class="eyebrow">{'Informe de seguridad de red' if net else 'Informe de seguridad web'}</div><h1>{esc(host)}</h1></div></div>
  <div class="tools" hidden><button class="btn" id="toggle-all" type="button">Expandir todo</button>
  <button class="btn" id="print-btn" type="button">Imprimir / guardar PDF</button></div>
 </div>
 <div class="meta">{"".join(meta)}</div>
</div></header>
<nav class="sticky" aria-label="Secciones"><div class="wrap">
 <a href="#resumen">Resumen</a><a href="#plan">Plan de acción</a><a href="#hallazgos">Hallazgos</a>
 <a href="#alcance">Alcance</a>{'<a href="#glosario">Glosario</a>' if terms else ''}
</div></nav>
<main><div class="wrap">
<section id="resumen" style="margin-top:0">
 <div class="hero">
  <div class="card gauge-card">{_gauge(rep.score, gcolor)}
   <div><span class="grade" style="background:var({gcolor})">{label}</span></div>
   <p class="note">Puntaje de seguridad, de 0 a 100. Es orientativo y sirve para priorizar.</p></div>
  <div class="card summary-card"><h2>Resumen para la gerencia</h2>
   {_executive_summary(rep, label, headline, active, net)}{top_html}</div>
 </div>
 <div class="kpis">
  <div class="card kpi"><div class="n">{len(sorted_f)}</div><div class="l">Puntos a revisar</div><div class="s">en total, de todas las severidades</div></div>
  <div class="card kpi"><div class="n" style="color:var({'--sev-critical' if urgent else '--ok'})">{urgent}</div><div class="l">Urgentes</div><div class="s">severidad crítica o alta</div></div>
  <div class="card kpi"><div class="n">{quick}</div><div class="l">Arreglos rápidos</div><div class="s">se resuelven en minutos</div></div>
  <div class="card kpi"><div class="n">{len(rep.checks_run)}</div><div class="l">Controles ejecutados</div><div class="s">áreas de seguridad revisadas</div></div>
 </div>
</section>
<section>
 <div class="two">
  <div class="card"><h2>Por severidad</h2><p class="sec-lead">Cuántos puntos hay según qué tan grave es cada uno.</p>{sev_rows}</div>
  <div class="card"><h2>Por área</h2><p class="sec-lead">Estado de cada área de seguridad revisada.</p><div class="cats">{cats_html}</div></div>
 </div>
</section>
{good_section}
<section id="plan"><h2>Plan de acción</h2>
 <p class="sec-lead">Qué corregir y en qué orden. Dentro de cada grupo, lo más rápido de resolver va primero.
 Haz clic en un punto para ver su explicación.</p>
 <div class="plan">{_plan(sorted_f)}</div></section>
<section id="hallazgos"><h2>Detalle de hallazgos</h2>
 <p class="sec-lead">Cada punto explica qué significa, por qué importa y cómo se corrige, sin tecnicismos.
 El detalle técnico está al final de cada uno, para quien lo implemente.</p>
 <div class="filters" role="group" aria-label="Filtrar por severidad">{"".join(chips)}</div>
 {findings_html}</section>
<section id="alcance"><h2>Alcance de este informe</h2>
 <div class="scope">
  <div class="card"><h3>Qué se revisó</h3><ul>{checks_li}</ul></div>
  <div class="card"><h3>Qué debes tener en cuenta</h3><ul>{"".join(f"<li>{esc(l)}</li>" for l in limits)}</ul></div>
 </div>{warn}</section>
{gloss}
<footer>Informe generado{footer_by}{(' el ' + esc(date)) if date else ''}. Creado con report-generator v{__version__}.
 Este documento es confidencial y está dirigido a {esc(client) if client else ('el responsable de los equipos' if net else 'el responsable del sitio')}.</footer>
</div></main>
<script>{JS}</script>
</body></html>"""
