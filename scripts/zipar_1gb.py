#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zipar_1gb.py — Divide os mods baixados em ZIPs separados de (no máx.) ~1 GB.

Uso:
    python scripts/zipar_1gb.py                     # pasta padrão 'baixados' -> 'ZIP_1GB'
    python scripts/zipar_1gb.py --dir baixados --saida ZIP_1GB --limite-gb 1
    python scripts/zipar_1gb.py --compressao 3      # compacta (mais lento)

Lógica:
  1. Lê todos os arquivos de 'baixados/'.
  2. Agrupa em ZIPs de modo que NENHUM ZIP passe do limite (por padrão 1 GB; usa
     0,97 * limite para sobrar espaço).
  3. Se UM ARQUIVO sozinho for maior que o limite, ele é empacotado e o ZIP é
     dividido em partes .001/.002/... (estilo multi-part). Junte com:
         Windows:  copy /b arquivo.zip.001+arquivo.zip.002 arquivo.zip
         Linux:    cat arquivo.zip.001 arquivo.zip.002 > arquivo.zip
         ou use o script JUNTAR_PARTES.py gerado automático.
  4. Gera MANIFESTO.txt com conteúdo, tamanhos e SHA-256 de cada mod.
"""

import argparse, csv, hashlib, shutil, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha256(p: Path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def list_files(d: Path):
    files = []
    for p in sorted(d.iterdir()):
        if p.is_file() and not p.name.endswith((".part", ".crdownload")):
            files.append(p)
    return files


def grupo_fit(files, limit):
    """Agrupa arquivos em listas cuja soma de tamanhos <= limit."""
    groups, cur, cur_size = [], [], 0
    for f in files:
        sz = f.stat().st_size
        if sz > limit:
            if cur:
                groups.append(cur)
            groups.append([f])
            cur, cur_size = [], 0
            continue
        if cur_size + sz > limit and cur:
            groups.append(cur)
            cur, cur_size = [], 0
        cur.append(f)
        cur_size += sz
    if cur:
        groups.append(cur)
    return groups


def split_file(src: Path, part_size: int):
    """Divide `src` em partes .001, .002... e retorna a lista de partes."""
    parts = []
    idx = 1
    with src.open("rb") as f:
        while True:
            out = src.with_name("%s.%03d" % (src.name, idx))
            with out.open("wb") as g:
                remaining = part_size
                while remaining > 0:
                    b = f.read(min(1024 * 1024, remaining))
                    if not b:
                        break
                    g.write(b)
                    remaining -= len(b)
                if out.stat().st_size == 0:
                    out.unlink(missing_ok=True)
                    break
            parts.append(out)
            idx += 1
            if f.tell() >= src.stat().st_size:
                break
    src.unlink(missing_ok=True)
    return parts


def gerar_juntador(out: Path, partes: dict):
    """Gera script para juntar os arquivos divididos."""
    lines = [
        "#!/usr/bin/env python3",
        "# JUNTA os arquivos divididos (.001/.002/...) de volta em um .zip único.",
        "import sys, shutil",
        "from pathlib import Path",
        "",
        "def juntar(raiz):",
        "    for part in sorted(Path(raiz).glob('*.zip.0*')):",
        "        base = part.name.rsplit('.', 2)[0]",
        "        alvo = Path(raiz) / base",
        "        if alvo.exists() and alvo.stat().st_size > 0:",
        "            continue",
        "        print('Juntando', part.name, '->', base)",
        "        with alvo.open('wb') as out_f, part.open('rb') as in_f:",
        "            shutil.copyfileobj(in_f, out_f)",
        "    print('Pronto! Descompacte os .zip gerados com 7-Zip')",
        "",
        "if __name__ == '__main__':",
        "    juntar(sys.argv[1] if len(sys.argv) > 1 else '.')",
        "",
    ]
    j = out / "JUNTAR_PARTES.py"
    j.write_text("\n".join(lines), encoding="utf-8")
    return j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(ROOT / "baixados"))
    ap.add_argument("--saida", default=str(ROOT / "ZIP_1GB"))
    ap.add_argument("--limite-gb", type=float, default=1.0)
    ap.add_argument("--compressao", type=int, default=0, choices=range(0, 10),
                    help="0 = sem compressão (rápido, indicado p/ .7z), 1-9 = deflate")
    args = ap.parse_args()

    src = Path(args.dir)
    out = Path(args.saida)
    out.mkdir(parents=True, exist_ok=True)
    limit = int(args.limite_gb * 1024 ** 3 * 0.97)

    files = list_files(src)
    if not files:
        print("Nada para zipar em", src)
        return
    groups = grupo_fit(files, limit)
    mode = zipfile.ZIP_STORED if args.compressao == 0 else zipfile.ZIP_DEFLATED

    manifesto = []
    partes_geradas = {}
    total_mods = 0
    for gi, group in enumerate(groups, 1):
        zname = out / ("BDO_Skyrim_SE_Parte_%03d.zip" % gi)
        print("Criando %s (%d arquivos)..." % (zname.name, len(group)))
        with zipfile.ZipFile(zname, "w", mode) as z:
            for f in group:
                z.write(f, arcname=f.name)
                total_mods += 1
        size = zname.stat().st_size
        entry = {
            "parte": zname.name,
            "tamanho_gb": round(size / 1024 ** 3, 3),
            "arquivos": [f.name for f in group],
        }
        manifesto.append(entry)
        if size > limit:
            parts = split_file(zname, limit)
            partes_geradas[zname.name] = parts
            entry["dividido_em"] = [p.name for p in parts]
        print("   %s  (%.2f GB)" % (zname.name, size / 1024 ** 3))

    # manifesto
    man = out / "MANIFESTO.txt"
    lines = [
        "MANIFESTO — BDO Skyrim SE (ZIPs de ~1 GB)",
        "Gerado em: " + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Total de mods empacotados: %d" % total_mods,
        "",
        "COMO USAR:",
        "  1. Se houver arquivos .zip.001/.002 (multi-part):",
        "     Windows:  copy /b BDO_Skyrim_SE_Parte_XXX.zip.001+BDO_Skyrim_SE_Parte_XXX.zip.002 BDO_Skyrim_SE_Parte_XXX.zip",
        "     (ou rode JUNTAR_PARTES.py na pasta)",
        "  2. Extraia cada .zip no seu mod manager (MO2/Vortex) ou na pasta Data.",
        "  3. Depois siga o GUIA_INSTALACAO.md (Bodyslide + AddItemMenu + física).",
        "",
        "== ZIPS ==",
    ]
    for e in manifesto:
        lines.append("")
        lines.append("### %s  (%.2f GB%s)" % (
            e["parte"], e["tamanho_gb"],
            "  -> dividido: " + ", ".join(e["dividido_em"]) if "dividido_em" in e else ""))
        for a in e["arquivos"]:
            p = src / a
            lines.append("  - %s  (%.1f MB, sha256=%s)" % (
                a, p.stat().st_size / 1024 ** 2, sha256(p)))
    man.write_text("\n".join(lines), encoding="utf-8")
    print("Manifesto:", man)
    if partes_geradas:
        j = gerar_juntador(out, partes_geradas)
        print("Gerado também:", j, "(junta partes multi-part)")

    # resumo CSV
    csv_out = out / "conteudo.csv"
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parte_zip", "mod", "tamanho_mb", "sha256"])
        for e in manifesto:
            for a in e["arquivos"]:
                p = src / a
                w.writerow([e["parte"], a, round(p.stat().st_size / 1024 ** 2, 2), sha256(p)])
    print("Detalhes:", csv_out)


if __name__ == "__main__":
    main()
