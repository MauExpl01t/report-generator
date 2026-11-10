"""Modelo de datos del informe y lectura/validación del JSON de entrada."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SEV_LABEL = {"CRITICAL": "Crítica", "HIGH": "Alta", "MEDIUM": "Media", "LOW": "Baja", "INFO": "Informativo"}
SEV_WEIGHT = {"CRITICAL": 30, "HIGH": 15, "MEDIUM": 7, "LOW": 2, "INFO": 0}


class ReportDataError(ValueError):
    """El JSON de entrada no tiene el formato esperado."""


@dataclass
class Finding:
    check: str
    title: str
    severity: str
    description: str = ""
    recommendation: str = ""
    evidence: str = ""
    reference: str = ""


@dataclass
class Report:
    target: str
    started_at: str = ""
    finished_at: str = ""
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    checks_run: list[str] = field(default_factory=list)
    score: int = 100

    def sorted_findings(self) -> list[Finding]:
        return sorted(self.findings, key=lambda f: (SEV_ORDER.index(f.severity), f.check))

    def counts(self) -> dict[str, int]:
        out = {s: 0 for s in SEV_ORDER}
        for f in self.findings:
            out[f.severity] += 1
        return out


def compute_score(findings: list[Finding]) -> int:
    return max(0, 100 - sum(SEV_WEIGHT[f.severity] for f in findings))


def _text(value: object) -> str:
    return "" if value is None else str(value)


def parse_report(data: object) -> Report:
    """Convierte el dict (formato de `webscan --format json`) en un Report validado."""
    if not isinstance(data, dict):
        raise ReportDataError("El JSON debe ser un objeto con 'target' y 'findings'.")
    if not data.get("target"):
        raise ReportDataError("Falta el campo 'target' (sitio analizado).")
    raw_findings = data.get("findings", [])
    if not isinstance(raw_findings, list):
        raise ReportDataError("'findings' debe ser una lista.")

    findings: list[Finding] = []
    for i, raw in enumerate(raw_findings, 1):
        if not isinstance(raw, dict) or not raw.get("title"):
            raise ReportDataError(f"El hallazgo #{i} no es válido (necesita al menos 'title').")
        sev = _text(raw.get("severity")).upper()
        findings.append(Finding(
            check=_text(raw.get("check")) or f"custom.{i}",
            title=_text(raw["title"]),
            severity=sev if sev in SEV_ORDER else "INFO",
            description=_text(raw.get("description")),
            recommendation=_text(raw.get("recommendation")),
            evidence=_text(raw.get("evidence")),
            reference=_text(raw.get("reference")),
        ))

    score = data.get("score")
    if not isinstance(score, int) or isinstance(score, bool):
        score = compute_score(findings)
    return Report(
        target=_text(data["target"]),
        started_at=_text(data.get("started_at")),
        finished_at=_text(data.get("finished_at")),
        findings=findings,
        errors=[_text(e) for e in data.get("errors", []) if e],
        checks_run=[_text(c) for c in data.get("checks_run", []) if c],
        score=max(0, min(100, score)),
    )


def decode_bytes(raw: bytes) -> str:
    """PowerShell 5 puede guardar con BOM o en UTF-16; probamos ambos."""
    for enc in ("utf-8-sig", "utf-16"):
        try:
            return raw.decode(enc)
        except UnicodeError:
            continue
    raise ReportDataError("No se pudo leer el archivo como texto (usa UTF-8).")


def load_report(path: str) -> Report:
    with open(path, "rb") as fh:
        text = decode_bytes(fh.read())
    try:
        return parse_report(json.loads(text))
    except json.JSONDecodeError as exc:
        raise ReportDataError(f"El archivo no es un JSON válido: {exc}") from exc
