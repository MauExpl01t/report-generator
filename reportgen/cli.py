"""Línea de comandos: python -m reportgen resultado.json -o informe.html"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .model import ReportDataError, decode_bytes, load_report, parse_report
from .pdf import html_to_pdf
from .render import render_html


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="reportgen",
        description="Convierte el JSON de un escaneo (por ejemplo `webscan --format json`) en un informe "
                    "HTML tipo dashboard, explicado en lenguaje simple para el cliente.")
    p.add_argument("--version", action="version", version=f"reportgen {__version__}")
    p.add_argument("input", help="Archivo JSON con el resultado del escaneo (o '-' para leer de la entrada estándar)")
    p.add_argument("-o", "--output", help="Archivo HTML de salida (por defecto: <entrada>.html)")
    p.add_argument("--pdf", metavar="ARCHIVO.pdf", help="Además, genera un PDF (requiere Edge o Chrome instalado)")
    p.add_argument("--client", default="", help="Nombre del cliente (aparece en el encabezado)")
    p.add_argument("--author", default="", help="Quién prepara el informe (tu nombre o empresa)")
    p.add_argument("--logo", default="", help="Ruta a un logo (PNG, JPG, SVG, WEBP) para el encabezado")
    p.add_argument("--accent", default="#2563eb", help="Color principal en formato #RRGGBB (por defecto #2563eb)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.input == "-":
            report = parse_report(json.loads(decode_bytes(sys.stdin.buffer.read())))
            default_out = "informe.html"
        else:
            report = load_report(args.input)
            default_out = str(Path(args.input).with_suffix(".html"))
        out = args.output or default_out
        html = render_html(report, client=args.client, author=args.author, logo_path=args.logo, accent=args.accent)
        Path(out).write_text(html, encoding="utf-8")
        print(f"Informe guardado en {out}")
        if args.pdf:
            html_to_pdf(render_html(report, client=args.client, author=args.author, logo_path=args.logo,
                                    accent=args.accent, expand=True), args.pdf)
            print(f"PDF guardado en {args.pdf}")
    except (ReportDataError, json.JSONDecodeError) as exc:
        print(f"Error en los datos: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
