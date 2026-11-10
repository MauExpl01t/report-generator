import json
from pathlib import Path

import pytest

from reportgen import knowledge as kb
from reportgen.cli import main
from reportgen.model import ReportDataError, parse_report
from reportgen.render import grade, render_html

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "ejemplo.json"


def make(findings, **extra):
    return parse_report({"target": "https://x.test/", "findings": findings, **extra})


def f(check="headers.hsts", title="T", severity="LOW", **kw):
    return {"check": check, "title": title, "severity": severity, **kw}


def test_example_renders_all_sections():
    rep = parse_report(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    html = render_html(rep, client="ACME", author="Yo")
    for text in ["Resumen para la gerencia", "Plan de acción", "Detalle de hallazgos", "Glosario",
                 "¿Qué significa?", "¿Cómo se arregla?", "ACME", "Riesgoso"]:
        assert text in html
    assert "http://" not in html.split("<style>")[0]  # sin recursos externos en <head>
    assert "<script src" not in html


def test_score_is_computed_when_missing():
    assert make([f(severity="CRITICAL"), f(severity="HIGH")]).score == 55
    assert make([]).score == 100


def test_score_clamped_and_unknown_severity_becomes_info():
    rep = make([f(severity="banana")], score=500)
    assert rep.findings[0].severity == "INFO"
    assert rep.score == 100


def test_html_escapes_untrusted_text():
    evil = '<script>alert(1)</script>'
    html = render_html(make([f(title=evil, description=evil, evidence=evil, recommendation=evil)]),
                       client=evil, author=evil)
    assert evil not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_non_http_reference_is_not_linked():
    html = render_html(make([f(reference="javascript:alert(1)")]))
    assert "javascript:alert(1)" not in html
    ok = render_html(make([f(reference="https://owasp.org/")]))
    assert 'href="https://owasp.org/"' in ok


def test_invalid_accent_rejected():
    with pytest.raises(ValueError):
        render_html(make([]), accent="red;}</style>")


def test_empty_report_is_friendly():
    html = render_html(make([], checks_run=["headers"]))
    assert "No se detectaron hallazgos" in html
    assert "Excelente" in html


def test_expand_opens_details():
    assert "<details class=\"finding\"" in render_html(make([f()]), expand=True)
    assert " open>" in render_html(make([f()]), expand=True)
    assert " open>" not in render_html(make([f()]), expand=False).split("</style>")[1].split("<script>")[0]


def test_grade_boundaries():
    assert grade(100)[0] == "Excelente" and grade(90)[0] == "Excelente"
    assert grade(89)[0] == "Bueno" and grade(75)[0] == "Bueno"
    assert grade(74)[0] == "Mejorable" and grade(55)[0] == "Mejorable"
    assert grade(54)[0] == "Riesgoso" and grade(30)[0] == "Riesgoso"
    assert grade(29)[0] == "Crítico" and grade(0)[0] == "Crítico"


@pytest.mark.parametrize("check,key", [
    ("tls.legacy_10", "tls.legacy"), ("headers.disclosure.server", "headers.disclosure"),
    ("exposure.env", "exposure.sensitive"), ("exposure.git_HEAD", "exposure.sensitive"),
    ("exposure.dir_listing", "exposure.dir_listing"), ("headers.csp", "headers.csp")])
def test_knowledge_lookup(check, key):
    assert kb.explain(check) is kb.KB[key]


def test_unknown_check_uses_generic_and_other_category():
    assert kb.explain("mi.herramienta") is kb.GENERIC
    html = render_html(make([f(check="mi.herramienta", title="Algo raro")]))
    assert "Otros hallazgos" in html


def test_every_webscan_prefix_has_category():
    for cid in ["tls.expired", "transport.plain_http", "headers.csp", "cookies.secure", "cors.wildcard",
                "content.mixed", "dns.spf_missing", "exposure.env", "active.sqli_error"]:
        assert kb.category_of(cid) != "other"


@pytest.mark.parametrize("bad", [[], {"findings": []}, {"target": "x", "findings": {}},
                                 {"target": "x", "findings": [{"severity": "LOW"}]}])
def test_bad_input_raises(bad):
    with pytest.raises(ReportDataError):
        parse_report(bad)


def test_cli_writes_html(tmp_path):
    out = tmp_path / "salida.html"
    assert main([str(EXAMPLE), "-o", str(out), "--client", "ACME"]) == 0
    assert "ACME" in out.read_text(encoding="utf-8")


def test_cli_reads_utf16_with_bom(tmp_path):
    src = tmp_path / "ps.json"
    src.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-16")
    out = tmp_path / "o.html"
    assert main([str(src), "-o", str(out)]) == 0


def test_cli_errors_are_reported(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("no es json", encoding="utf-8")
    assert main([str(bad)]) == 1
    assert "JSON" in capsys.readouterr().err
    assert main([str(tmp_path / "no-existe.json")]) == 1
    assert main([str(EXAMPLE), "-o", str(tmp_path / "x.html"), "--accent", "azul"]) == 1
