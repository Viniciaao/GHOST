#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baixar_tudo_bdo.py — Baixador automático do catálogo BDO p/ Skyrim SE.
========================================================
Uso (no PC do usuário, com internet normal):

    python scripts/baixar_tudo_bdo.py --tudo
    python scripts/baixar_tudo_bdo.py --so COL01,COL02,COL04
    python scripts/baixar_tudo_bdo.py --categoria modbooru
    python scripts/baixar_tudo_bdo.py --fonte gnomad --somente-se
    python scripts/baixar_tudo_bdo.py --dry-run          (só mostra o plano)

Dependências:
  - Python 3.8+
  - OPCIONAL `requests` (recomendado):  pip install requests
  - OPCIONAL `gdown`  (Google Drive mais simples):  pip install gdown
  - OPCIONAL `megatools`/`megadl`  (Mega): instale Mega Tools p/ sua SO
  - Para Nexus/LoversLab/Baidu: configure credenciais em config.ini (ver GUIA)

Os arquivos baixados vão para `baixados/` (ou --dir). Rode depois:
    python scripts/zipar_1gb.py
para gerar os ZIPs de ~1 GB.
"""

import argparse, csv, http.cookiejar, os, re, shutil, subprocess, sys, time, json
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urljoin, quote
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "MODS_BDO.csv"
CFG_PATH = ROOT / "config.ini"
DEFAULT_OUT = ROOT / "baixados"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
SE_MARKERS = ("[se]", "se_", "_se", "3ba", "bhunp", "smp", "cbbe se", "skyrim se", "ss.e")
SE_BAD = ("uunp le", "[le]", "_le", "lе", "unp le", "legendary")

try:
    import requests  # type: ignore
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False


# --------------------------------------------------------------------------- #
#  Configuração                                                               #
# --------------------------------------------------------------------------- #
def load_config(path=None) -> dict:
    cfg = {"nexus_api_key": "", "nexus_cookies": "", "loverslab_cookies": "",
           "baidu_cookie": "", "timeout": 60, "retries": 3}
    cfg_file = Path(path) if path else CFG_PATH
    if cfg_file.exists():
        raw = cfg_file.read_text(encoding="utf-8", errors="ignore")
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", ";")) or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip().lower()] = v.strip().strip('"')
    return cfg


def session(cfg):
    """Retorna uma sessão HTTP (requests se disponível, senão urllib)."""
    if HAS_REQUESTS:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.8,ru;q=0.7,zh;q=0.6"})
        return s
    return None


def get_bytes(url, s=None, cfg=None, referer=None, allow_redirects=True, timeout=None):
    """GET e devolve bytes (usa requests quando possível)."""
    cfg = cfg or {}
    timeout = timeout or int(cfg.get("timeout", 60))
    if s is not None and HAS_REQUESTS:
        hdrs = {"User-Agent": UA}
        if referer:
            hdrs["Referer"] = referer
        r = s.get(url, headers=hdrs, timeout=timeout, allow_redirects=allow_redirects)
        r.raise_for_status()
        return r.content
    req = Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


# --------------------------------------------------------------------------- #
#  Catálogo                                                                   #
# --------------------------------------------------------------------------- #
def load_catalog() -> list:
    rows = []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            r["id"] = r["id"].strip()
            rows.append(r)
    return rows


def printf(*a, **k):
    print(*a, **k)
    sys.stdout.flush()


# --------------------------------------------------------------------------- #
#  Baixadores por plataforma                                                  #
# --------------------------------------------------------------------------- #
def download_file(url, dest: Path, s=None, cfg=None, referer=None):
    """Baixa um arquivo qualquer em `dest`, com retomada quando possível."""
    cfg = cfg or {}
    retries = int(cfg.get("retries", 3))
    timeout = int(cfg.get("timeout", 60))
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    if not HAS_REQUESTS or s is None:
        # urllib simples
        for i in range(retries):
            try:
                req = Request(url, headers={"User-Agent": UA})
                with urlopen(req, timeout=timeout * 5) as resp, open(part, "wb") as f:
                    shutil.copyfileobj(resp, f)
                part.replace(dest)
                return dest
            except Exception as e:
                printf("   ! tentativa %d falhou: %s" % (i + 1, e))
                time.sleep(2)
        raise RuntimeError("Falha ao baixar %s" % url)
    # requests com resume
    hdrs = {"User-Agent": UA}
    if referer:
        hdrs["Referer"] = referer
    if part.exists() and part.stat().st_size > 0:
        hdrs["Range"] = "bytes=%d-" % part.stat().st_size
    for i in range(retries):
        try:
            r = s.get(url, headers=hdrs, timeout=timeout * 5, stream=True)
            r.raise_for_status()
            mode = "ab" if (r.status_code == 206 and part.exists()) else "wb"
            with open(part, mode) as f:
                for chunk in r.iter_content(1024 * 256):
                    if chunk:
                        f.write(chunk)
            part.replace(dest)
            return dest
        except HTTPError as e:
            if e.code == 416:  # já completo
                part.replace(dest)
                return dest
            printf("   ! tentativa %d falhou (HTTP %s)" % (i + 1, e.code))
            time.sleep(2)
        except Exception as e:
            printf("   ! tentativa %d falhou: %s" % (i + 1, e))
            time.sleep(2)
    raise RuntimeError("Falha ao baixar %s" % url)


def dl_mediafire(url, dest, s, cfg):
    page = get_bytes(url, s, cfg).decode("utf-8", "ignore")
    m = re.search(r'https://download[0-9]*\.mediafire\.com/[^"\'\s<>]+', page)
    if m:
        return download_file(m.group(0).replace("&amp;", "&"), dest, s, cfg, referer=url)
    # fallback: URL de download do MediaFire via /file/
    if "/file/" in url:
        return download_file(url, dest, s, cfg, referer=url)
    raise RuntimeError("Não achei link de download MediaFire")


def dl_googledrive(url, dest, s, cfg):
    """Google Drive: usa gdown se instalado, senão implementa o fluxo de confirmação."""
    fid = None
    m = re.search(r"/file/d/([^/?#]+)", url)
    if m:
        fid = m.group(1)
    else:
        m = re.search(r"id=([A-Za-z0-9_-]+)", url)
        if m:
            fid = m.group(1)
    if not fid:
        # pasta: pede gdown
        raise RuntimeError("Pasta do Drive: instale `gdown` e use `gdown --folder URL` (ver GUIA)")
    if shutil.which("gdown") or True:
        try:
            import gdown  # type: ignore
            gdown.download(id=fid, output=str(dest), quiet=False, use_cookies=False)
            return dest
        except Exception:
            pass
    # fluxo direto
    first = "https://drive.usercontent.google.com/download?id=%s&export=download&confirm=t" % fid
    r = s.get(first, headers={"User-Agent": UA}, timeout=90) if HAS_REQUESTS else None
    if r is not None and r.status_code == 200 and "content-disposition" in r.headers:
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        return dest
    # confirmação via cookie/HTML
    html = None
    if r is not None and "text/html" in (r.headers.get("content-type") or ""):
        html = r.text
    if html and "confirm" in html:
        mm = re.search(r'name="(confirm|uuid|id)"\s+value="([^"]+)"', html)
        pairs = re.findall(r'name="([^"]+)"\s+value="([^"]+)"', html)
        action = "https://drive.usercontent.google.com/download"
        data = dict(pairs)
        data.setdefault("confirm", "t")
        rr = s.post(action, data=data, headers={"User-Agent": UA}, timeout=90)
        rr.raise_for_status()
        with open(dest, "wb") as f:
            f.write(rr.content)
        return dest
    raise RuntimeError("Drive: use gdown (pip install gdown) para este arquivo")


def dl_mega(url, dest, cfg):
    """Mega: usa megadl/megatools em linha de comando (instalação no GUIA)."""
    for tool in ("megadl", "megatools"):
        if shutil.which(tool):
            cmd = [tool] + (["dl", "--path", str(dest.parent)] if tool == "megatools" else ["--path", str(dest.parent)])
            cmd += [url]
            subprocess.run(cmd, check=False)
            if dest.exists():
                return dest
    # fallback: queremos pelo menos a URL mpegada
    raise RuntimeError("Mega precisa de Mega Tools (megadl/megatools) — veja GUIA_INSTALACAO.md ou baixe manualmente")


def dl_loverslab(url, dest, s, cfg):
    cookies = cfg.get("loverslab_cookies", "")
    if HAS_REQUESTS and cookies:
        for pair in cookies.split(";"):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                s.cookies.set(k, v, domain=".loverslab.com")
    page = get_bytes(url, s, cfg).decode("utf-8", "ignore")
    m = re.search(r'href="([^"]*\?do=download[^"]*)"', page)
    if m:
        durl = urljoin("https://www.loverslab.com", m.group(1).replace("&amp;", "&"))
        if HAS_REQUESTS:
            s.headers["Referer"] = url
        return download_file(durl, dest, s, cfg, referer=url)
    raise RuntimeError("LoversLab: não achei botão de download (faça login e coloque os cookies no config.ini)")


def dl_nexus(url, dest, s, cfg):
    key = cfg.get("nexus_api_key", "")
    if not key:
        raise RuntimeError("Nexus: configure NEXUS_API_KEY no config.ini (conta gratuita)")
    m = re.search(r"/skyrimspecialedition/mods/(\d+)", url)
    if not m:
        raise RuntimeError("URL Nexus inválida")
    mod_id = m.group(1)
    base = "https://api.nexusmods.com/v1/games/skyrimspecialedition/mods/%s/files" % mod_id
    hdrs = {"apikey": key, "User-Agent": UA}
    files = s.get(base, headers=hdrs, timeout=60).json()
    # escolher o primeiro main/update que não seja "old version"
    pick = None
    for f in files.get("files", []):
        if f.get("category_name") in ("Main files", "Updates"):
            pick = f
            break
    if not pick and files.get("files"):
        pick = files["files"][0]
    if not pick:
        raise RuntimeError("Nexus: nenhum arquivo")
    fid = pick["file_id"]
    link = s.get("%s/%s/download_link.json" % (base, fid), headers=hdrs, timeout=60).json()
    if HAS_REQUESTS:
        cookies = cfg.get("nexus_cookies", "")
        if cookies:
            for pair in cookies.split(";"):
                if "=" in pair:
                    k, v = pair.strip().split("=", 1)
                    s.cookies.set(k, v, domain=".nexusmods.com")
    # expandir link de download (requer cookies Nexus)
    r = s.get(link[0]["short_link"], headers={"User-Agent": UA}, allow_redirects=False)
    while r.status_code in (301, 302, 303, 307, 308):
        r = s.get(r.headers["Location"], headers={"User-Agent": UA}, allow_redirects=False)
    if r.status_code == 200:
        with open(dest, "wb") as f:
            f.write(r.content)
        return dest
    raise RuntimeError("Nexus: download bloqueado — abra manualmente: " + link[0]["short_link"])


def dl_modbooru(url, dest, s, cfg):
    page = get_bytes(url, s, cfg).decode("utf-8", "ignore")
    # procurar âncoras de downloads (preferir SE!)
    anchors = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(?:<[^>]+>)*([^<]{2,80})</a>', page, re.I)
    cands = []
    for href, label in anchors:
        low = label.lower()
        if any(k in href.lower() for k in ("download", "/dl", "/file/")):
            cands.append((href, label))
        elif "skyrim se" in low or "cbbe" in low or "3ba" in low:
            cands.append((href, label))
    se = [c for c in cands if any(k in c[0].lower() + c[1].lower() for k in ("se", "3ba", "cbbe se"))]
    pool = se or cands
    if not pool:
        raise RuntimeError("ModBooru: nenhum link de download encontrado na página")
    href = pool[0][0]
    durl = urljoin(url, href.replace("&amp;", "&"))
    return download_file(durl, dest, s, cfg, referer=url)


def dl_patreon(url, dest, s, cfg, collect_keywords=("bdo", "bdor"), only_se=False):
    """Baixa o post do Patreon (grátis) e/ou coleta links internos."""
    page = get_bytes(url, s, cfg).decode("utf-8", "ignore")
    links = re.findall(r'https?://[^\s"\'<>]+', page)
    collected = []
    for l in links:
        l = l.replace("&amp;", "&")
        low = l.lower()
        if not any(k in low for k in collect_keywords):
            continue
        if any(x in low for x in ("mediafire.com", "drive.google.com", "mega.nz", "mega.co.nz",
                                  "patreonusercontent.com", "patreon.com/file")):
            collected.append(l)
        elif "modbooru.com" in low and any(k in low for k in ("bdo", "bdor")):
            collected.append(l)
    if only_se:
        collected = [l for l in collected if any(k in l.lower() for k in ("[se]", "se_", "_se", "3ba", "bhunp", "smp"))]
    # links diretos de anexo do Patreon
    pat = re.findall(r'(?:https://www\.patreon\.com/file\?id=\d+|https://www\.patreon\.com/posts/[^"\s]+\?postAttachmentId=\d+)', page)
    files_out = []
    dest.parent.mkdir(parents=True, exist_ok=True)
    for i, l in enumerate(pat):
        try:
            r = s.get(l, headers={"User-Agent": UA}, allow_redirects=True, timeout=120)
            # o anexo vira um link CDN
            furl = r.url if r.status_code == 200 else None
            if furl and "patreonusercontent" in furl:
                name = "patreon_%s_%s" % (i, furl.split("/")[-1].split("?")[0] or "anexo")
                out = dest.parent / name
                download_file(furl, out, s, cfg, referer=l)
                files_out.append(out)
        except Exception as e:
            printf("   ! anexo %d falhou: %s" % (i, e))
    if not collected and not files_out:
        printf("   ! Nenhum link BDO encontrado no post (post pode exigir login).")
    return {"colecionados": collected, "arquivos": files_out}


def dl_gamermods(url, dest, s, cfg):
    """gamer-mods.ru: página DLE; acha o botão 'Перейти к скачиванию'."""
    page = get_bytes(url, s, cfg).decode("utf-8", "ignore")
    # botões de download apontam para /index.php?do=download...
    m = re.search(r'href="([^"]*do=download[^"]*)"', page)
    if not m:
        m = re.search(r'href="([^"]*/load/[^"]*)"', page)
    if m:
        durl = urljoin("https://gamer-mods.ru", m.group(1).replace("&amp;", "&"))
        page2 = get_bytes(durl, s, cfg, referer=url).decode("utf-8", "ignore")
        m2 = re.search(r'(href="[^"]*(?:download|\.rar|\.7z|\.zip)[^"]*")', page2, re.I)
        if m2:
            f = urljoin(durl, m2.group(1).strip('"').replace("&amp;", "&"))
            return download_file(f, dest, s, cfg, referer=durl)
    raise RuntimeError("gamer-mods.ru: não achei link — login pode ser necessário; baixar manualmente")


def dl_baidu(url, dest, cfg):
    raise RuntimeError(
        "Baidu pan exige conta Baidu + app. Baixe manualmente: abra o link, faça login, "
        "clique em '下载' (baixar) e instale o app 'Baidu Netdisk'.")


HANDLERS = {
    "mediafire": dl_mediafire,
    "googledrive": dl_googledrive,
    "google": dl_googledrive,
    "mega": dl_mega,
    "loverslab": dl_loverslab,
    "nexus": dl_nexus,
    "modbooru": dl_modbooru,
    "gamer-mods": dl_gamermods,
    "baidu": dl_baidu,
    "generic": lambda u, d, s, c: download_file(u, d, s, c),
}


def safe_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)[:150].strip()


# --------------------------------------------------------------------------- #
#  Main                                                                       #
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Baixador BDO Skyrim SE")
    ap.add_argument("--tudo", action="store_true", help="baixa todas as entradas")
    ap.add_argument("--so", help="lista de ids separados por vírgula: COL01,COL04")
    ap.add_argument("--categoria", help="filtra por tipo: colecao_feminina, set_individual, pack_thbg...")
    ap.add_argument("--fonte", help="filtra por plataforma: modbooru, loverslab, mediafire, gamer-mods...")
    ap.add_argument("--prioridade", help="até qual prioridade baixar (1=principais)")
    ap.add_argument("--somente-se", action="store_true", help="filtra coletas que sejam SE")
    ap.add_argument("--dir", default=str(DEFAULT_OUT), help="pasta de saída")
    ap.add_argument("--dry-run", action="store_true", help="mostra o plano sem baixar")
    ap.add_argument("--config", default=str(CFG_PATH))
    args = ap.parse_args()

    cfg = load_config(args.config)
    s = session(cfg)
    rows = load_catalog()

    # filtros
    if args.so:
        ids = {x.strip().upper() for x in args.so.split(",")}
        rows = [r for r in rows if r["id"].upper() in ids]
    if args.categoria:
        rows = [r for r in rows if args.categoria.lower() in r["tipo"].lower()]
    if args.fonte:
        rows = [r for r in rows if args.fonte.lower() in r["plataforma"].lower()]
    if args.prioridade:
        rows = [r for r in rows if int(r["prioridade"]) <= int(args.prioridade)]
    if args.dry_run:
        printf("PLANO (dry-run): %d entradas" % len(rows))
        for r in rows:
            printf("  %-6s %-55s %-12s %s" % (r["id"], r["nome"][:54], r["plataforma"], r["url"]))
        return

    out = Path(args.dir)
    out.mkdir(parents=True, exist_ok=True)
    report = []
    ok, fail = 0, 0
    printf("Iniciando download de %d itens -> %s" % (len(rows), out))
    for idx, r in enumerate(rows, 1):
        name = safe_name(r["nome"])
        dest = out / (name + ".7z" if r["plataforma"] in ("mega",) or ".7z" in name.lower() else name + ".bin")
        printf("\n[%d/%d] %s (%s)" % (idx, len(rows), r["nome"], r["plataforma"]))
        if dest.exists() and dest.stat().st_size > 0:
            printf("   = já baixado, pulando (use --forcar p/ refazer)")
            report.append((r["id"], r["nome"], "ok", str(dest)))
            ok += 1
            continue
        try:
            plat = r["plataforma"]
            if plat == "patreon-collect":
                res = dl_patreon(r["url"], dest, s, cfg, only_se=args.somente_se)
                for curl in res.get("colecionados", []):
                    printf("   -> link coletado: %s" % curl[:120])
                    d2 = out / (safe_name(r["nome"]) + "___" + safe_name(curl.split("/")[-1]) + ".bin")
                    if "mediafire.com" in curl:
                        dl_mediafire(curl, d2, s, cfg)
                    elif "drive.google" in curl:
                        dl_googledrive(curl, d2, s, cfg)
                    elif "mega" in curl:
                        dl_mega(curl, d2, cfg)
                    else:
                        download_file(curl, d2, s, cfg)
                    report.append((r["id"], r["nome"], "ok", str(d2)))
                ok += 1
            elif plat == "patreon":
                dl_patreon(r["url"], dest, s, cfg, only_se=args.somente_se)
                ok += 1
            else:
                handler = HANDLERS.get(plat, HANDLERS["generic"])
                handler(r["url"], dest, s, cfg)
                ok += 1
            report.append((r["id"], r["nome"], "ok", str(dest)))
        except Exception as e:
            printf("   !! ERRO: %s" % e)
            report.append((r["id"], r["nome"], "erro", str(e)))
            fail += 1
    # relatório
    rep = out / "download_report.csv"
    with rep.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "nome", "status", "resultado"])
        w.writerows(report)
    printf("\nFeito: %d ok, %d erros. Relatório: %s" % (ok, fail, rep))
    if fail:
        printf("Dica: muitos links são espelhos; se um falhar, tente outro da tabela no CATALOGO.")


if __name__ == "__main__":
    main()
