import copy
import csv
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('catalogo', ROOT / 'tools/catalogo.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.scripts.append(dict(attrs))


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = c.load(ROOT)

    def test_real_catalog_and_stats(self):
        c.validate(self.data)
        s = c.stats(self.data)
        self.assertEqual(s['total'], 75)
        self.assertEqual(s['scopes'], {'principal':49,'pendente':18,'historico':8})
        self.assertEqual(s['mod_archives'], 0)

    def test_duplicate_id_rejected(self):
        self.data['mods'][1]['id'] = self.data['mods'][0]['id']
        with self.assertRaisesRegex(ValueError, 'ID duplicado'):
            c.validate(self.data)

    def test_duplicate_source_tab_is_not_a_new_mod(self):
        self.data['mods'][1]['source']['url'] = self.data['mods'][0]['source']['url'] + '?tab=files'
        with self.assertRaisesRegex(ValueError, 'URL duplicada'):
            c.validate(self.data)

    def test_source_aliases_are_deduplicated(self):
        pairs = [
            ('https://www.patreon.com/takealook/posts/se-dm-bdor-by-33371502', 'https://patreon.com/posts/33371502?l=pt'),
            ('https://www.nexusmods.com/skyrimspecialedition/mods/132879', 'https://www.nexusmods.com/games/skyrimspecialedition/mods/132879?tab=files'),
            ('https://www.loverslab.com/files/file/34130-bdor-2024-female-collection-by-kirax/', 'https://www.loverslab.com/files/file/34130-another-title/'),
        ]
        for left, right in pairs:
            with self.subTest(left=left):
                self.assertEqual(c.canonical_source(left), c.canonical_source(right))

    def test_path_traversal_id_rejected(self):
        self.data['mods'][0]['id'] = '../../private'
        with self.assertRaisesRegex(ValueError, 'ID inválido'):
            c.validate(self.data)

    def test_legacy_not_smuggled_into_se(self):
        self.data['mods'][0]['edition'] = 'LE'
        with self.assertRaisesRegex(ValueError, 'LE/VR'):
            c.validate(self.data)

    def test_future_evidence_rejected(self):
        self.data['mods'][0]['source']['checked_on'] = '2026-09-07'
        with self.assertRaisesRegex(ValueError, 'após o corte'):
            c.validate(self.data)

    def test_title_only_is_pending(self):
        mod = next(m for m in self.data['mods'] if m['source']['verification']=='author_index')
        mod['scope'] = 'principal'
        with self.assertRaisesRegex(ValueError, 'título isolado'):
            c.validate(self.data)

    def test_author_index_requires_discovery_evidence(self):
        mod = next(m for m in self.data['mods'] if m['source']['verification']=='author_index')
        mod['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'falta a listagem'):
            c.validate(self.data)

    def test_no_false_downloads_or_hashes(self):
        for field, value in [('archive_in_release',True),('archive_sha256','a'*64),('archive_size_bytes',42)]:
            data = copy.deepcopy(self.data)
            data['mods'][0]['download'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'binário/hash'):
                c.validate(data)

    def test_no_false_global_download_claim(self):
        self.data['mod_archives_downloaded'] = 1
        with self.assertRaisesRegex(ValueError, 'não contém mods'):
            c.validate(self.data)

    def test_no_false_game_test_claim(self):
        self.data['game_tests_performed'] = True
        with self.assertRaisesRegex(ValueError, 'testes em jogo'):
            c.validate(self.data)

    def test_no_permission_without_evidence(self):
        mod = next(m for m in self.data['mods'] if m['redistribution']['status']=='forbidden')
        mod['redistribution']['evidence_url'] = None
        with self.assertRaises(ValueError):
            c.validate(self.data)

    def test_cannot_silently_add_approved_binaries(self):
        self.data['mods'][0]['redistribution']['status'] = 'allowed'
        with self.assertRaisesRegex(ValueError, 'não aprovada'):
            c.validate(self.data)

    def test_unsafe_urls(self):
        for url in ['javascript:alert(1)', 'file:///tmp/test', 'http://example.com/mod', 'https://user:pass@example.com/mod', 'https://example.com/mod\nInjected=1','https://example.com/mod?token=private','https://localhost/mod']:
            data = copy.deepcopy(self.data)
            data['mods'][0]['source']['url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                c.validate(data)

    def test_related_ids_must_exist(self):
        self.data['mods'][0]['related_ids'] = ['does-not-exist']
        with self.assertRaisesRegex(ValueError, 'relação inválida'):
            c.validate(self.data)

    def test_unavailable_must_be_historical(self):
        self.data['mods'][0]['availability'] = 'removed'
        with self.assertRaisesRegex(ValueError, 'histórico'):
            c.validate(self.data)

    def test_csv_round_trip(self):
        result = c.render_csv(self.data)
        self.assertTrue(result.startswith('\ufeff'))
        rows = list(csv.DictReader(io.StringIO(result.lstrip('\ufeff'))))
        self.assertEqual(len(rows), 75)
        self.assertEqual(rows[0]['nome'], self.data['mods'][0]['name'])
        self.assertTrue(all(row['arquivo_na_release']=='nao' for row in rows))

    def test_csv_formula_injection(self):
        for text in ['=HYPERLINK("evil")','+SUM(1)','-1','@test','   =1']:
            with self.subTest(text=text):
                self.assertTrue(c.csv_cell(text).startswith("'"))
        self.assertEqual(c.csv_cell('BDO armor'), 'BDO armor')

    def test_json_script_injection_cannot_break_out(self):
        self.data['mods'][0]['summary'] = '</script><script>alert("not executed")</script>'
        output = c.render_html(self.data)
        parser = ScriptParser(); parser.feed(output)
        self.assertEqual(len(parser.scripts),2)
        self.assertNotIn(self.data['mods'][0]['summary'],output)
        self.assertIn('\\u003c/script\\u003e',output)
        self.assertNotIn('@@PAYLOAD@@',output)
        self.assertNotIn('@@SCRIPT@@',output)

    def test_markdown_text_is_not_html(self):
        self.assertEqual(c.md('<img src=x>'), '&lt;img src=x&gt;')
        self.assertIn('\\[', c.md('[bad](url)'))
        self.assertIn('\\|', c.md('pipe|test'))
        self.assertEqual(c.render_markdown(self.data).count('\n#### '),75)

    def test_generated_files_are_current(self):
        c.generate(self.data,ROOT,check=True)

    def test_generated_check_catches_manual_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT/'web',root/'web')
            c.generate(self.data,root)
            (root/'docs/CATALOGO.md').write_text('changed')
            with self.assertRaisesRegex(ValueError,'desatualizados'):
                c.generate(self.data,root,check=True)

    def copy_package_root(self, root):
        for name in c.PACKAGE_FILES:
            target = root / name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)

    def test_package_determinism_allowlist_and_checksums(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'; root.mkdir()
            self.copy_package_root(root)
            (root/'downloads').mkdir()
            (root/'downloads/private-mod.esp').write_bytes(b'EXCLUDED TEST FIXTURE')
            (root/'downloads/private-mod.zip').write_bytes(b'EXCLUDED TEST FIXTURE')
            (root/'.env').write_text('TEST_SECRET_DO_NOT_PACKAGE=123')
            (root/'docs/private-note.md').write_text('not in allowlist')
            assets1 = c.package(self.data,Path(tmp)/'one',root)
            assets2 = c.package(self.data,Path(tmp)/'two',root)
            self.assertEqual([p.read_bytes() for p in assets1],[p.read_bytes() for p in assets2])
            with zipfile.ZipFile(assets1[0]) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertTrue(all(not n.startswith(('downloads/','.git/','.env')) for n in names))
                self.assertNotIn('docs/private-note.md',names)
                self.assertFalse(any(Path(n).suffix in ('.esp','.esm','.esl','.bsa','.nif','.dds','.7z','.rar','.exe','.dll') for n in names))
                self.assertEqual(len([n for n in names if n.endswith('.url')]),67)
                self.assertFalse(any('/historico/' in n for n in names if n.endswith('.url')))
                for name in names:
                    self.assertFalse(name.startswith('/'))
                    self.assertNotIn('..',Path(name).parts)
                manifest = json.loads(archive.read('CONTEUDO_DA_RELEASE.json'))
                self.assertEqual(manifest['third_party_mod_archives'],0)
                for record in manifest['files']:
                    blob=archive.read(record['path'])
                    self.assertEqual(record['sha256'],hashlib.sha256(blob).hexdigest())
                    self.assertEqual(record['bytes'],len(blob))
                for line in archive.read('CHECKSUMS_INTERNOS.sha256').decode().splitlines():
                    digest,name=line.split('  ',1)
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),digest)
            for line in assets1[-1].read_text().splitlines():
                digest,name=line.split('  ',1)
                self.assertEqual(hashlib.sha256((assets1[-1].parent/name).read_bytes()).hexdigest(),digest)

    def test_package_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'project'; root.mkdir(); self.copy_package_root(root)
            external=Path(tmp)/'external.md'; external.write_text('private')
            (root/'README.md').unlink(); (root/'README.md').symlink_to(external)
            with self.assertRaisesRegex(ValueError,'Arquivo regular'):
                c.package(self.data,Path(tmp)/'out',root)

    def test_local_inventory_hashes_only_archives_no_recursion(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'a.zip').write_bytes(b'zip fixture')
            (path/'b.7Z').write_bytes(b'7z fixture')
            (path/'c.rar').write_bytes(b'rar fixture')
            (path/'ignore.exe').write_bytes(b'not executed')
            (path/'nested').mkdir(); (path/'nested/hidden.zip').write_bytes(b'not scanned')
            (path/'link.zip').symlink_to(path/'a.zip')
            result=c.inventory(path)
            self.assertEqual([x['file'] for x in result['files']],['a.zip','b.7Z','c.rar'])
            self.assertEqual(result['files'][0]['sha256'],hashlib.sha256(b'zip fixture').hexdigest())
            self.assertEqual(result['files'][0]['bytes'],11)
            self.assertFalse((path/'extracted').exists())

    def test_inventory_missing_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'não existe'):
                c.inventory(Path(tmp)/'missing')

    def test_document_internal_links(self):
        for path in [ROOT/'README.md',ROOT/'RELEASE_NOTES.md',*(ROOT/'docs').glob('*.md')]:
            content=path.read_text(encoding='utf-8')
            for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^\s)]+)\)',content):
                if urlsplit(link).scheme:
                    continue
                target,_,fragment=link.partition('#')
                dest=path.parent/target if target else path
                with self.subTest(file=path.name,link=link):
                    self.assertTrue(dest.is_file(),str(dest))
                    if fragment:
                        self.assertIn(f'id="{fragment}"',dest.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
