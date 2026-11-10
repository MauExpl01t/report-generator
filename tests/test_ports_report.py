"""El informe también entiende los resultados de port-scanner (ids ports.*)."""
from reportgen import knowledge as kb
from reportgen.model import parse_report
from reportgen.render import is_network_report, render_html

PORT_IDS = [
    "ports.telnet", "ports.ftp", "ports.smb", "ports.rdp", "ports.vnc", "ports.docker", "ports.mysql",
    "ports.postgresql", "ports.redis", "ports.mongodb", "ports.snmp", "ports.smtp", "ports.many-open",
    "ports.inventory", "ports.script.redis-noauth", "ports.script.mongodb-noauth", "ports.script.vnc-noauth",
    "ports.script.ftp-anonymous", "ports.script.smb-v1", "ports.script.docker-api-exposed",
    "ports.script.cert-expired", "ports.script.cert-self-signed", "ports.script.tls-old-protocols",
    "ports.script.ssh-v1", "ports.script.snmp-public", "ports.script.dns-open-resolver",
    "ports.script.http-version-disclosure", "ports.script.smtp-no-starttls",
]


def test_ids_de_port_scanner_tienen_explicacion_propia():
    for check in PORT_IDS:
        assert kb.explain(check) is not kb.GENERIC, check
        assert kb.category_of(check) == "ports"
    assert kb.explain("ports.algo-nuevo") is kb.KB["ports.exposed"]


def test_terminos_de_glosario_existen():
    for exp in kb.KB.values():
        for term in exp.terms:
            assert term in kb.GLOSSARY, term


def sample():
    return parse_report({
        "target": "192.168.1.10", "started_at": "2026-11-09T10:00:00+00:00",
        "checks_run": ["host-discovery", "tcp-connect", "service-detection"], "errors": [],
        "findings": [{"check": "ports.rdp", "title": "Escritorio remoto (RDP) está expuesto", "severity": "HIGH",
                      "description": "d", "recommendation": "r"}],
    })


def test_informe_de_red_usa_textos_de_red():
    rep = sample()
    assert is_network_report(rep)
    out = render_html(rep, client="Cliente", author="Yo")
    assert "Informe de seguridad de red" in out and "Equipos:" in out
    assert "No evaluado" not in out                       # no mostrar áreas web como "no evaluadas"
    assert "Escritorio Remoto" in out or "Escritorio remoto" in out


def test_informe_web_no_cambia():
    rep = parse_report({"target": "https://x.cl/", "started_at": "2026-11-09T10:00:00+00:00",
                        "checks_run": ["tls", "headers"], "errors": [], "findings": []})
    assert not is_network_report(rep)
    assert "Informe de seguridad web" in render_html(rep)
