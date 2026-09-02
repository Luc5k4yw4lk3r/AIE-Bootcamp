#!/usr/bin/env python3
"""Chequeos de integridad del vault.

Ver la sección "Verificación" de AGENTS.md para el porqué de cada exclusión:
los falsos positivos de este vault son específicos y quitarlos rompe el chequeo.

Uso:  .scripts/verificar-vault.py   (en Windows: python .scripts\\verificar-vault.py)
No necesita instalar nada. Con PyYAML instalado, el chequeo de frontmatter
además valida el YAML; sin él, chequea la estructura.
Sale con 1 si encuentra algo.
"""

import pathlib
import re
import sys

try:
    # Opcional a propósito: no todo el equipo lo tiene instalado. Sin PyYAML el
    # chequeo 6 corre en modo estructural (ver frontmatter_invalido).
    import yaml
except ImportError:
    yaml = None

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IGNORAR = {".git", ".obsidian", ".scripts", ".opencode", ".claude"}
# Archivos de agente: viven en la raíz pero no son notas del vault.
NO_SON_NOTAS = {"AGENTS.md", "CLAUDE.md", "README.md"}

NEGRITA = "\033[1m"
FIN_COLOR = "\033[0m"

HEX32 = re.compile(r"[0-9a-f]{32}")
ENLACE_LOCAL = re.compile(r"\]\([^)]+\.(?:md|png|pdf)\)")
URL_DESNUDA = re.compile(r"^https?://")
# Un target con forma de timestamp no es un wikilink: es el artefacto de Notion
# [[03:29](url), [03:51](url)], un enlace Markdown envuelto en corchetes.
TIMESTAMP = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")


def relativo(p):
    return str(p.relative_to(RAIZ))


def archivos(patron):
    return [p for p in RAIZ.rglob(patron) if not IGNORAR & set(p.relative_to(RAIZ).parts)]


NOTAS = sorted(archivos("*.md"), key=relativo)


def lineas_utiles(nota):
    """(numero, texto) por línea, con los bloques de código vaciados y los code
    spans borrados. Sin esto, CONVENCIONES.md se denuncia a sí misma: documenta
    los antipatrones citándolos."""
    utiles = []
    dentro_de_bloque = False
    for numero, linea in enumerate(nota.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"^\s*```", linea):
            dentro_de_bloque = not dentro_de_bloque
            utiles.append((numero, ""))
        elif dentro_de_bloque:
            utiles.append((numero, ""))
        else:
            utiles.append((numero, re.sub(r"`[^`]*`", "", linea)))
    return utiles


def por_linea(patron, filtro=None):
    """Hallazgos de un patrón sobre todas las notas, ya neutralizadas."""
    return [
        f"{relativo(p)}:{numero}: {linea.strip()[:120]}"
        for p in NOTAS
        for numero, linea in lineas_utiles(p)
        if patron.search(linea) and (filtro is None or filtro(linea))
    ]


# --- Chequeos -------------------------------------------------------------

def nombres_con_residuo_notion():
    """Sufijo hexadecimal de 32 caracteres en un nombre de archivo."""
    return [relativo(p) for p in archivos("*") if HEX32.search(p.name)]


def contenido_con_residuo_notion():
    """Hex de 32 en el texto. Fuera de URLs: hay PDFs externos que lo llevan en
    el nombre (el paper de NeurIPS) y son falsos positivos."""
    return por_linea(HEX32, lambda linea: "http" not in linea)


def enlaces_markdown_locales():
    """Enlaces Markdown a archivos del vault: deberían ser wikilinks o embeds.
    El %20 era solo un síntoma; el defecto es el enlace Markdown en sí."""
    return por_linea(ENLACE_LOCAL, lambda linea: "http" not in linea)


def urls_desnudas():
    """Todo enlace externo lleva etiqueta y un porqué."""
    return por_linea(URL_DESNUDA)


def wikilinks_rotos():
    destinos = {p.stem for p in NOTAS}
    destinos |= {p.name for p in archivos("*") if p.is_file()}

    rotos = []
    for p in NOTAS:
        texto = "\n".join(linea for _, linea in lineas_utiles(p))
        for bruto in re.findall(r"\[\[([^\]|#^]+)", texto):
            destino = bruto.strip()
            if not destino or TIMESTAMP.match(destino):
                continue
            if destino in destinos or pathlib.Path(destino).stem in destinos:
                continue
            rotos.append(f"{relativo(p)}: [[{destino}]]")
    return rotos


def frontmatter_invalido():
    """Toda nota abre con un bloque YAML y `tipo` es obligatorio.

    Con PyYAML se parsea de verdad, lo que además caza YAML sintácticamente
    inválido. Sin PyYAML se chequea la estructura: que abra, que cierre y que
    la clave `tipo` esté. Un YAML roto pero bien delimitado pasa desapercibido
    en ese modo — de ahí el aviso al final del reporte.
    """
    malas = []
    for p in NOTAS:
        if p.name in NO_SON_NOTAS:
            continue
        texto = p.read_text(encoding="utf-8")
        if not texto.startswith("---"):
            malas.append(f"{relativo(p)}: sin frontmatter")
            continue
        fin = texto.find("\n---", 3)
        if fin == -1:
            malas.append(f"{relativo(p)}: bloque de frontmatter sin cerrar")
            continue

        bloque = texto[3:fin]
        if yaml is None:
            if not re.search(r"^tipo\s*:", bloque, re.M):
                malas.append(f'{relativo(p)}: falta la propiedad obligatoria "tipo"')
            continue

        try:
            datos = yaml.safe_load(bloque)
        except yaml.YAMLError as e:
            malas.append(f"{relativo(p)}: YAML inválido ({e.__class__.__name__})")
            continue
        if not isinstance(datos, dict) or "tipo" not in datos:
            malas.append(f'{relativo(p)}: falta la propiedad obligatoria "tipo"')
    return malas


CHEQUEOS = [
    ("Residuo de Notion en nombres de archivo", nombres_con_residuo_notion),
    ("Residuo de Notion en contenido", contenido_con_residuo_notion),
    ("Enlaces Markdown a archivos locales", enlaces_markdown_locales),
    ("URLs desnudas", urls_desnudas),
    ("Wikilinks rotos", wikilinks_rotos),
    (
        "Notas sin frontmatter válido"
        + (" (YAML parseado)" if yaml else " (modo estructural, sin PyYAML)"),
        frontmatter_invalido,
    ),
]

# Los dos que no pueden fallar nunca, por índice en CHEQUEOS.
INVARIANTES = {4, 5}


def main():
    con_hallazgos = []
    for i, (titulo, chequeo) in enumerate(CHEQUEOS):
        hallazgos = chequeo()
        marca = "!" if hallazgos else "·"
        print(f"\n{NEGRITA}{marca} {i + 1}. {titulo}{FIN_COLOR}")
        if not hallazgos:
            print("   sin hallazgos")
            continue
        con_hallazgos.append(i)
        for h in hallazgos:
            print(f"   {h}")
        print(f"   → {len(hallazgos)} hallazgo(s)")

    print(f"\n{len(NOTAS)} notas revisadas.")
    if yaml is None:
        print("PyYAML no está instalado: el frontmatter se chequeó solo por estructura.")
        print("Para la validación YAML completa: pip install pyyaml")
    if not con_hallazgos:
        print(f"{NEGRITA}Vault limpio: 6/6 chequeos sin hallazgos.{FIN_COLOR}")
        return 0

    print(f"{NEGRITA}{len(con_hallazgos)} de 6 chequeos con hallazgos.{FIN_COLOR}")
    if INVARIANTES & set(con_hallazgos):
        print("Hay invariantes rotos (wikilinks o frontmatter): arreglar antes de commitear.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
