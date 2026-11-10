"""Exportación a PDF usando el Edge/Chrome ya instalado (modo headless). Sin dependencias de Python."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

_WINDOWS_CANDIDATES = [
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
]
_MAC_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
_NAMES = ["msedge", "microsoft-edge", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"]


def find_browsers() -> list[str]:
    """Todos los Edge/Chrome instalados, en orden de preferencia (sin repetidos)."""
    found: list[str] = []
    for raw in _WINDOWS_CANDIDATES:
        p = os.path.expandvars(raw)
        if "%" not in p and os.path.isfile(p):
            found.append(p)
    found += [p for p in _MAC_CANDIDATES if os.path.isfile(p)]
    for name in _NAMES:
        p = shutil.which(name)
        if p:
            found.append(p)
    return list(dict.fromkeys(found))


def find_browser() -> str | None:
    browsers = find_browsers()
    return browsers[0] if browsers else None


def _print_with(browser: str, html: str, tmp_root: str, out: Path) -> str:
    """Intenta crear el PDF con un navegador. Devuelve '' si salió bien o el motivo del fallo."""
    with tempfile.TemporaryDirectory(prefix="reportgen-", dir=tmp_root, ignore_cleanup_errors=True) as tmp:
        src = Path(tmp) / "informe.html"
        src.write_text(html, encoding="utf-8")
        # El navegador escribe primero en una ruta temporal sin espacios y después copiamos al destino.
        tmp_pdf = Path(tmp) / "salida.pdf"
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
               f"--user-data-dir={Path(tmp) / 'profile'}", f"--print-to-pdf={tmp_pdf}", src.as_uri()]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            return "tardó demasiado"
        except subprocess.CalledProcessError as exc:
            return f"falló (código {exc.returncode})"
        if not tmp_pdf.exists() or tmp_pdf.stat().st_size == 0:
            return "terminó sin generar el archivo"
        shutil.copyfile(tmp_pdf, out)
    return ""


def html_to_pdf(html: str, out_pdf: str) -> None:
    """Convierte el HTML (con todos los detalles abiertos) en PDF. Lanza RuntimeError si falla.

    Si el primer navegador (por ejemplo Edge) no genera el PDF, se prueba con el siguiente (Chrome).
    """
    browsers = find_browsers()
    if not browsers:
        raise RuntimeError("No encontré Edge ni Chrome para crear el PDF. "
                           "Abre el HTML y usa 'Imprimir / guardar PDF'.")
    out = Path(out_pdf).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    problems = []
    with tempfile.TemporaryDirectory(prefix="reportgen-root-", ignore_cleanup_errors=True) as root:
        for browser in browsers:
            why = _print_with(browser, html, root, out)
            if not why:
                return
            problems.append(f"{Path(browser).name}: {why}")
    raise RuntimeError("No se pudo crear el PDF (" + "; ".join(problems) + "). "
                       "Abre el HTML y usa 'Imprimir / guardar PDF'.")
