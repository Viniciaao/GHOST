#!/usr/bin/env python3
"""Catálogo offline GHOST. Python 3.10+, somente biblioteca padrão.

Não baixa, executa, extrai ou publica mods. O pacote usa allowlist de documentos;
um diretório local de mods nunca participa da release.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
import html
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'packs': 'Packs de conteúdo', 'armaduras': 'Armaduras e roupas',
    'conversoes': 'Conversões de corpo', 'cabelos': 'Cabelos e complementos',
    'animacoes': 'Animações de combate', 'patches': 'Patches',
    'integracoes': 'Integrações no mundo', 'personagens': 'Personagens',
}
SCOPES = {'principal': 'Catálogo principal', 'pendente': 'A aprofundar', 'historico': 'Histórico / indisponíveis'}
METHODS = {'page_read': 'Texto da página lido', 'search_index': 'Somente índice de busca', 'author_index': 'Somente listagem do autor'}
AVAILABILITY = {
    'page_available': 'Página lida; arquivo não testado',
    'unverified': 'Disponibilidade não verificada',
    'access_restricted': 'Acesso restrito / versão pública separada',
    'missing_download': 'Sem download identificado na página',
    'missing_page': 'Página não localizada', 'hidden': 'Oculto (índice)',
    'removed': 'Removido / não encontrado (índice)',
}
PERMISSIONS = {
    'forbidden': 'Reupload proibido', 'unverified': 'Permissão não confirmada',
    'permission_required': 'Permissão de terceiros pendente',
    'nexus_only': 'Derivados condicionados ao Nexus',
}
# Deliberadamente não há estado "autorizado" nesta edição do catálogo.
# Novos binários exigiriam revisão de licenças e um processo de publicação separado.
PACKAGE_FILES = (
    '.gitignore', 'README.md', 'LICENSE', 'RELEASE_NOTES.md', 'catalogo.html',
    'catalog/mods.json', 'catalog/mods.csv',
    'docs/CATALOGO.md', 'docs/INSTALACAO_SE_AE.md',
    'docs/LICENCAS_E_FONTES.md', 'docs/PESQUISA.md', 'docs/REFERENCIAS_LE.md',
    'docs/RELATORIO.md', 'docs/FORMATO_DOS_DADOS.md',
    'tools/catalogo.py', 'web/template.html', 'web/catalogo.js',
    'tests/test_catalogo.py', 'tests/catalogo.test.js',
)
ID_RE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
VERSION_RE = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+\Z')
MAX_TEXT_FILE = 4 * 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def text(value, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f'{label}: texto vazio/inválido')
    require(not any(ord(c) < 32 and c not in '\n\t' for c in value), f'{label}: caractere de controle')


def https_url(value, label: str) -> None:
    text(value, label)
    require(not any(c.isspace() for c in value), f'{label}: espaço na URL')
    parsed = urlsplit(value)
    require(parsed.scheme == 'https' and bool(parsed.hostname), f'{label}: use URL https absoluta')
    require(not parsed.username and not parsed.password, f'{label}: credenciais não permitidas')
    require(parsed.hostname not in ('localhost', '127.0.0.1', '::1'), f'{label}: host local não permitido')
    require(not any(k in parsed.query.lower() for k in ('token=', 'api_key=', 'apikey=', 'signature=')), f'{label}: URL assinada/segredo não permitido')


def canonical_source(url: str) -> tuple[str, str]:
    """Deduplica também aliases conhecidos de páginas de um mesmo mod/post."""
    parsed = urlsplit(url)
    host = parsed.hostname.lower().removeprefix('www.')
    path = parsed.path.rstrip('/').lower()
    if host == 'patreon.com' and '/posts/' in path:
        match = re.search(r'(?:/|-)([0-9]+)$', path)
        if match:
            path = '/posts/' + match.group(1)
    elif host == 'nexusmods.com':
        match = re.fullmatch(r'/(?:games/)?([^/]+)/mods/([0-9]+)', path)
        if match:
            path = '/' + match.group(1) + '/mods/' + match.group(2)
    elif host == 'loverslab.com':
        match = re.match(r'/files/file/([0-9]+)(?:-|$)', path)
        if match:
            path = '/files/file/' + match.group(1)
    return host, path


def text_list(value, label: str) -> None:
    require(isinstance(value, list), f'{label}: esperado array')
    for item in value:
        text(item, label)


def validate(data: dict) -> None:
    require(isinstance(data, dict), 'Raiz precisa ser objeto')
    require(type(data.get('schema_version')) is int and data['schema_version'] == 1, 'schema_version não suportado')
    require(isinstance(data.get('catalog_version'), str) and bool(VERSION_RE.fullmatch(data['catalog_version'])), 'catalog_version inválida')
    cutoff = date.fromisoformat(data['checked_on'])
    require(data.get('collection_type') == 'reference_catalog_not_installable_modpack', 'Este projeto só empacota catálogo')
    require(data.get('game_tests_performed') is False, 'Não declarar testes em jogo não realizados')
    for key in ('mod_archives_downloaded', 'mod_archives_redistributed'):
        require(type(data.get(key)) is int and data[key] == 0, f'{key}: este pacote não contém mods')
    require(isinstance(data.get('mods'), list) and bool(data['mods']), 'Lista de mods vazia/inválida')
    ids, urls = set(), set()
    for mod in data['mods']:
        require(isinstance(mod, dict), 'Entrada precisa ser objeto')
        ident = mod.get('id')
        require(isinstance(ident, str) and bool(ID_RE.fullmatch(ident)), f'ID inválido: {ident!r}')
        require(ident not in ids, f'ID duplicado: {ident}')
        ids.add(ident)
        for key in ('name', 'summary', 'runtime_note', 'family'):
            text(mod.get(key), f'{ident}.{key}')
        require(mod.get('category') in CATEGORIES, f'{ident}: categoria inválida')
        require(mod.get('scope') in SCOPES, f'{ident}: escopo inválido')
        require(mod.get('edition') == 'SE', f'{ident}: LE/VR não entram no catálogo SE')
        require(mod.get('availability') in AVAILABILITY, f'{ident}: disponibilidade inválida')
        for key in ('authors', 'body', 'requirements', 'related_ids', 'notes'):
            text_list(mod.get(key), f'{ident}.{key}')
        require(type(mod.get('requirements_complete')) is bool, f'{ident}: completude inválida')
        require(type(mod.get('external_site_may_show_adult_content')) is bool, f'{ident}: aviso inválido')
        require(mod.get('version_observed') is None or isinstance(mod['version_observed'], str), f'{ident}: versão inválida')
        source = mod['source']
        https_url(source['url'], ident + '.source')
        # Query não cria um mod diferente. IDs e URL canônica devem ser únicos.
        canonical = canonical_source(source['url'])
        require(canonical not in urls, f'URL duplicada: {source["url"]}')
        urls.add(canonical)
        require(source['verification'] in METHODS, f'{ident}: método inválido')
        require(source['kind'] in ('author_page', 'historical_page'), f'{ident}: tipo de fonte inválido')
        require(date.fromisoformat(source['checked_on']) <= cutoff, f'{ident}: consulta após o corte')
        sid = source.get('search_result_id')
        require(sid is None or (type(sid) is int and sid > 0), f'{ident}: número de fonte inválido')
        if source['verification'] == 'search_index':
            require(sid is not None, f'{ident}: resultado de busca sem referência numérica')
        if source['verification'] == 'author_index':
            require(bool(mod['evidence']), f'{ident}: falta a listagem que descobriu a URL')
            require(mod['scope'] == 'pendente', f'{ident}: título isolado não confirma o mod')
        require(isinstance(mod['evidence'], list), f'{ident}: evidências inválidas')
        for evidence in mod['evidence']:
            https_url(evidence['url'], ident + '.evidence')
            text(evidence['note'], ident + '.evidence.note')
            eid = evidence.get('search_result_id')
            require(eid is None or (type(eid) is int and eid > 0), f'{ident}: referência inválida')
        permission = mod['redistribution']
        require(permission['status'] in PERMISSIONS, f'{ident}: permissão não aprovada por este formato')
        text(permission['note'], ident + '.redistribution.note')
        if permission['status'] != 'unverified':
            https_url(permission['evidence_url'], ident + '.permission_evidence')
        elif permission.get('evidence_url') is not None:
            https_url(permission['evidence_url'], ident + '.permission_evidence')
        download = mod['download']
        require(download == dict(mode='manual_at_source', archive_in_release=False, archive_sha256=None, archive_size_bytes=None), f'{ident}: binário/hash de mod não permitido no catálogo')
        if mod['availability'] in ('removed', 'hidden', 'missing_page', 'missing_download'):
            require(mod['scope'] == 'historico', f'{ident}: indisponível precisa estar no histórico')
    for mod in data['mods']:
        for related in mod['related_ids']:
            require(related in ids and related != mod['id'], f'{mod["id"]}: relação inválida {related}')


def load(root: Path = ROOT) -> dict:
    data = json.loads((root / 'catalog/mods.json').read_text(encoding='utf-8'))
    validate(data)
    return data


def stats(data: dict) -> dict:
    return dict(total=len(data['mods']), scopes=dict(Counter(m['scope'] for m in data['mods'])),
                categories=dict(Counter(m['category'] for m in data['mods'])),
                verification=dict(Counter(m['source']['verification'] for m in data['mods'])),
                redistribution=dict(Counter(m['redistribution']['status'] for m in data['mods'])),
                mod_archives=0)


def citation(source: dict) -> str:
    return f'[{source.get("search_result_id") or 1}]({source["url"]})'


def md(value: str) -> str:
    # Textos do catálogo não podem injetar links/HTML nos documentos gerados.
    return html.escape(value, quote=False).replace('\\', '\\\\').replace('|', '\\|').replace('[', '\\[').replace(']', '\\]').replace('*', '\\*').replace('`', '\\`').replace('\n', ' ')


def render_markdown(data: dict) -> str:
    s = stats(data)
    lines = ['# Black Desert → Skyrim SE/AE — catálogo', '',
             '> **Não é um modpack instalável. Nenhum arquivo de mod foi baixado ou incluído.**', '',
             f'Pesquisa: **{data["checked_on"]}** · Catálogo **{data["catalog_version"]}** · PC SE/AE', '',
             f'**{s["total"]} registros**: {s["scopes"].get("principal",0)} principais, '
             f'{s["scopes"].get("pendente",0)} a aprofundar e {s["scopes"].get("historico",0)} históricos. '
             'São publicações/variantes, não uma contagem de conteúdo único ou downloads funcionando.', '',
             '[Início](../README.md) · [Instalação](INSTALACAO_SE_AE.md) · [Fontes e permissões](LICENCAS_E_FONTES.md) · [Pesquisa](PESQUISA.md)', '',
             '## Como interpretar', '',
             '- **Principal:** há descrição além de um título. Ainda pode depender de informação indexada, login e outras verificações.',
             '- **A aprofundar:** referência pertinente, mas ainda não há dados suficientes de instalação. Não instalar só com base no título.',
             '- **Histórico:** página oculta, removida, não localizada ou sem download identificado.',
             '- **Página lida** não significa arquivo baixado, íntegro, seguro ou testado em SE/AE.',
             '- **Requisitos parciais:** campos vazios significam não conferido, nunca “sem requisitos”.',
             '- **Relacionados** são pistas de variantes/patches; não formam uma ordem automática de instalação.',
             '- Downloads devem ser feitos pelo usuário nos sites indicados. Alguns podem mostrar conteúdo adulto e exigir conta.', '',
             '## Navegação', '']
    for scope, label in SCOPES.items():
        lines.append(f'- [{label}](#{scope})')
    for scope, scope_label in SCOPES.items():
        lines += ['', f'<a id="{scope}"></a>', f'## {scope_label}', '']
        for category, cat_label in CATEGORIES.items():
            entries = [m for m in data['mods'] if m['scope'] == scope and m['category'] == category]
            if not entries:
                continue
            lines += [f'### {cat_label}', '']
            for m in entries:
                p, source = m['redistribution'], m['source']
                lines += [f'<a id="{m["id"]}"></a>', f'#### {md(m["name"])}', '',
                          md(m['summary']) + ' ' + citation(source), '',
                          f'- **ID:** `{m["id"]}` · **Família:** `{m["family"]}`',
                          '- **Autor/portador identificado:** ' + (md('; '.join(m['authors'])) or 'não confirmado'),
                          '- **Versão observada:** ' + md(m['version_observed'] or 'não fixada / não conferida'),
                          '- **Corpo:** ' + (md('; '.join(m['body'])) or 'não confirmado'),
                          '- **SE/AE:** ' + md(m['runtime_note']),
                          '- **Acesso:** ' + AVAILABILITY[m['availability']],
                          '- **Verificação:** ' + METHODS[source['verification']] + f' em {source["checked_on"]}',
                          '- **Redistribuição:** ' + PERMISSIONS[p['status']] + '. ' + md(p['note']),
                          '- **Arquivo na release:** não. **Hash/tamanho do mod:** desconhecidos, pois não houve download.',
                          '- **Fonte:** ' + citation(source), '']
                completeness = 'Lista publicada consultada; verificar requisitos transitivos' if m['requirements_complete'] else 'Lista parcial / não auditada'
                lines += [f'**Requisitos — {completeness}:**', '']
                lines += ['- ' + md(r) for r in m['requirements']] or ['- Não conferidos integralmente; abrir a fonte.']
                if m['notes']:
                    lines += ['', '**Observações:**', ''] + ['- ' + md(n) for n in m['notes']]
                if m['related_ids']:
                    lines += ['', '**Ver também (não substitui o requisito original):** ' + ', '.join(f'[{ident}](#{ident})' for ident in m['related_ids'])]
                for e in m['evidence']:
                    lines += ['', 'Evidência complementar: ' + md(e['note']) + ' ' + citation(e)]
                if m['external_site_may_show_adult_content']:
                    lines += ['', '**Aviso:** site externo pode exibir conteúdo adulto. O catálogo não incorpora imagens desse site.']
                lines += ['']
    return '\n'.join(lines).rstrip() + '\n'


def csv_cell(value: str) -> str:
    # Evita fórmulas se metadados futuros forem abertos em Excel/LibreOffice.
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def render_csv(data: dict) -> str:
    buf = io.StringIO(newline='')
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(['id','nome','categoria','escopo','autores','corpo','versao_observada','disponibilidade','verificacao','consultado_em','requisitos_parciais','lista_requisitos_consultada','redistribuicao','url_fonte','observacoes','arquivo_na_release'])
    for m in data['mods']:
        writer.writerow([csv_cell(str(v)) for v in [m['id'],m['name'],m['category'],m['scope'],'; '.join(m['authors']),'; '.join(m['body']),m['version_observed'] or '',m['availability'],m['source']['verification'],m['source']['checked_on'],'; '.join(m['requirements']),'sim' if m['requirements_complete'] else 'nao',m['redistribution']['status'],m['source']['url'],' | '.join(m['notes']),'nao']])
    return '\ufeff' + buf.getvalue()  # BOM para compatibilidade com Excel no Windows.


def render_report(data: dict) -> str:
    s = stats(data)
    lines = ['# Relatório de entrega e verificação', '',
        f'Data da pesquisa: **{data["checked_on"]}**. Catálogo **{data["catalog_version"]}**.', '',
        '## O que foi e o que não foi feito', '',
        '| Item | Resultado |', '| --- | --- |',
        f'| Registros de mods/variantes | {s["total"]} |',
        f'| Catálogo principal | {s["scopes"].get("principal", 0)} |',
        f'| Referências a aprofundar | {s["scopes"].get("pendente", 0)} |',
        f'| Histórico/indisponíveis | {s["scopes"].get("historico", 0)} |',
        '| Arquivos de mods baixados | **0** |',
        '| Arquivos de mods anexados à release | **0** |',
        '| Downloads binários testados ponta a ponta | **0** |',
        '| Instalações/testes no Skyrim | **0** |',
        '| Percentual de todos os mods existentes | Desconhecido; não reivindicado |', '',
        '## Nível de evidência', '', '| Método | Registros |', '| --- | --- |']
    lines += [f'| {label} | {s["verification"].get(key, 0)} |' for key, label in METHODS.items()]
    lines += ['', '## Permissões registradas', '', '| Estado | Registros |', '| --- | --- |']
    lines += [f'| {label} | {s["redistribution"].get(key, 0)} |' for key, label in PERMISSIONS.items()]
    lines += ['', '## Limitações operacionais', '',
        '- A pesquisa utilizou resultados de busca e texto de páginas públicas. O método de cada entrada está no JSON/CSV.',
        '- Quatro consultas de metadados por HTTPS diretamente no ambiente (Nexus, Patreon, LoversLab e immyneedscake) falharam com erro TLS/EOF. Nenhum arquivo de mod foi recebido nessas consultas.',
        '- As ferramentas de pesquisa retornaram texto de páginas apesar dessas falhas; isso não atesta que um download binário funcionaria neste ambiente.',
        '- Não foram usadas credenciais pessoais, cookies, APIs privadas, bypass de login, mirrors de arquivos retirados ou assinaturas pagas.',
        '- Não há checksum de mod inventado. SHA256SUMS.txt verifica apenas os arquivos documentais produzidos pelo GHOST.',
        '- A decisão de não reenviar arquivos também depende de permissões, e não apenas de limitações de rede.', '',
        '## Validações reproduzíveis', '',
        '```sh', 'python tools/catalogo.py validar', 'python -m unittest discover -s tests -v',
        'node --test tests/catalogo.test.js', 'python tools/catalogo.py gerar --check', 'python tools/catalogo.py pacote', '```', '',
        'Esses comandos validam dados, renderização, filtros, seleção local e empacotamento. **Não validam mods dentro do jogo.**', '',
        '## Verificação extra da interface nesta entrega', '',
        '- Chromium 149.0.7827.0, com visualizações de 1440 × 1000 e 390 × 844 pixels.',
        '- Testados: montagem das fichas, três escopos, busca, estado vazio, seleção, exportação JSON, persistência após recarregar e navegação para ficha relacionada.',
        '- Nenhum erro JavaScript observado; nenhuma rolagem horizontal nessas duas larguras; nenhuma requisição externa disparada pela interface durante esse teste.',
        '- Essa checagem foi feita no HTML local, não nos sites dos autores nem no Skyrim.', '',
        'O pacote documental é gerado por allowlist: pastas de downloads, .git, credenciais, malhas, texturas e plugins não são varridos nem adicionados.', '']
    return '\n'.join(lines)


def render_html(data: dict, root: Path = ROOT) -> str:
    template = (root / 'web/template.html').read_text(encoding='utf-8')
    js = (root / 'web/catalogo.js').read_text(encoding='utf-8')
    payload = dict(catalog=data, stats=stats(data), labels=dict(categories=CATEGORIES, scopes=SCOPES, methods=METHODS, availability=AVAILABILITY, permissions=PERMISSIONS))
    # Escapa fechamento de script e separadores Unicode antes de embutir JSON.
    encoded = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    return template.replace('@@PAYLOAD@@', encoded).replace('@@SCRIPT@@', js)


def generated(data: dict, root: Path = ROOT) -> dict[str, bytes]:
    return {name: content.encode('utf-8') for name, content in {
        'docs/CATALOGO.md': render_markdown(data),
        'catalog/mods.csv': render_csv(data),
        'docs/RELATORIO.md': render_report(data),
        'catalogo.html': render_html(data, root),
    }.items()}


def generate(data: dict, root: Path = ROOT, check: bool = False) -> None:
    mismatches = []
    for name, content in generated(data, root).items():
        path = root / name
        if check:
            if not path.exists() or path.read_bytes() != content:
                mismatches.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    require(not mismatches, 'Arquivos gerados desatualizados: ' + ', '.join(mismatches))


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def package(data: dict, output: Path, root: Path = ROOT) -> list[Path]:
    """Build determinístico, sem glob/rglob de pastas do usuário."""
    validate(data)
    generate(data, root, check=True)
    payload = {}
    root = root.resolve()
    for name in PACKAGE_FILES:
        path = root / name
        require(path.is_file() and not path.is_symlink(), f'Arquivo regular obrigatório: {name}')
        require(path.resolve().is_relative_to(root), f'Arquivo fora do projeto: {name}')
        require(path.stat().st_size <= MAX_TEXT_FILE, f'Arquivo documental grande demais: {name}')
        content = path.read_bytes()
        content.decode('utf-8')  # Recusar binários mesmo se renomeados para .md.
        require(b'\x00' not in content, f'Arquivo binário inesperado: {name}')
        payload[name] = content
    for m in data['mods']:
        if m['scope'] == 'historico':
            continue
        # Atalhos contêm só página pública, nunca URL de executável ou link assinado.
        name = f'links/{m["scope"]}/{m["category"]}/{m["id"]}.url'
        payload[name] = f'[InternetShortcut]\r\nURL={m["source"]["url"]}\r\n'.encode('utf-8')
    manifest = dict(catalog_version=data['catalog_version'], type='documentation_only',
        third_party_mod_archives=0, entries=stats(data),
        files=[dict(path=name, bytes=len(content), sha256=sha256(content)) for name,content in sorted(payload.items())])
    payload['CONTEUDO_DA_RELEASE.json'] = (json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    payload['CHECKSUMS_INTERNOS.sha256'] = ''.join(f'{sha256(blob)}  {name}\n' for name,blob in sorted(payload.items())).encode('utf-8')
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'ghost-bdo-se-ae-catalogo-v{data["catalog_version"]}.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (2026,9,6,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            z.writestr(info,content,compresslevel=9)
    assets = [archive]
    for name,content in [('mods.json',payload['catalog/mods.json']),('mods.csv',payload['catalog/mods.csv']),('CONTEUDO_DA_RELEASE.json',payload['CONTEUDO_DA_RELEASE.json'])]:
        path = output / name
        path.write_bytes(content)
        assets.append(path)
    checksums = output / 'SHA256SUMS.txt'
    checksums.write_text(''.join(f'{sha256(path.read_bytes())}  {path.name}\n' for path in assets),encoding='utf-8')
    return assets + [checksums]


def inventory(directory: Path) -> dict:
    """Apenas nomes/tamanhos/hash de arquivos locais. Não extrai nem faz rede."""
    require(directory.is_dir(), 'Pasta de downloads não existe')
    require(not directory.is_symlink(), 'Pasta de inventário não pode ser symlink')
    files = []
    for path in sorted(directory.iterdir()):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in ('.zip','.7z','.rar'):
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        files.append(dict(file=path.name, bytes=path.stat().st_size, sha256=digest.hexdigest()))
    return dict(type='local_inventory_not_permission_or_safety_proof',files=files,
        notice='Hash identifica bytes; não comprova autoria, licença, segurança ou compatibilidade. Nenhum arquivo foi enviado.')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validar', help='Verificar o catálogo, offline')
    gen = sub.add_parser('gerar', help='Gerar Markdown, CSV, HTML e relatório')
    gen.add_argument('--check',action='store_true',help='Falhar se os gerados divergirem; não escrever')
    pack = sub.add_parser('pacote', help='Gerar apenas documentos e atalhos, nunca mods')
    pack.add_argument('--saida',type=Path,default=ROOT/'dist')
    ls = sub.add_parser('listar',help='Listar fontes por escopo/categoria')
    ls.add_argument('--categoria',choices=CATEGORIES)
    ls.add_argument('--escopo',choices=SCOPES)
    inv = sub.add_parser('inventario',help='Calcular hashes de ZIP/7z/RAR locais sem extrair/enviar')
    inv.add_argument('pasta',type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inventario':
            print(json.dumps(inventory(args.pasta),ensure_ascii=False,indent=2))
            return 0
        data = load()
        if args.command == 'validar':
            print(json.dumps(stats(data),ensure_ascii=False,indent=2))
        elif args.command == 'gerar':
            generate(data,check=args.check)
            print('Gerados consistentes.' if args.check else 'Markdown, CSV, HTML e relatório gerados.')
        elif args.command == 'pacote':
            for path in package(data,args.saida):
                print(path)
        elif args.command == 'listar':
            for m in data['mods']:
                if (not args.categoria or m['category']==args.categoria) and (not args.escopo or m['scope']==args.escopo):
                    print(f'{m["id"]}\t{m["name"]}\t{m["source"]["url"]}')
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'Erro: {exc}',file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
