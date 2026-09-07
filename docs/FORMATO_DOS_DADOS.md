# Dados e manutenção

[← Início](../README.md)

## Fonte de verdade

`catalog/mods.json` é o arquivo editável principal, em UTF-8. `catalog/mods.csv`, `docs/CATALOGO.md`, `docs/RELATORIO.md` e `catalogo.html` são derivados. Não os edite à mão: use `python tools/catalogo.py gerar`.

O formato atual é **somente de referência**. Seu validador não aceita declarar arquivos de mods incluídos. Permitir binários exigiria revisão explícita da política, dos dados e do processo de release, não apenas trocar um booleano.

## Campos relevantes

| Campo | Semântica |
| --- | --- |
| `id` | Identificador estável ASCII, seguro para âncoras e atalhos |
| `name` | Título da publicação ou título contextualizado no catálogo |
| `category` | Pack, armadura, conversão, cabelo, animação, patch, integração ou personagem |
| `scope` | `principal`, `pendente` ou `historico`; não é selo de compatibilidade |
| `family` | Agrupa variantes do mesmo conjunto; não determina conflitos automaticamente |
| `authors` | Créditos identificados; array vazio significa não confirmado |
| `edition` | `SE`; runtime AE exato não é inferido automaticamente |
| `runtime_note` | Ressalva ou teste histórico declarado pelo autor; não teste do GHOST |
| `body` | Corpo/variante encontrados na evidência; vazio não significa universal |
| `version_observed` | Versão textual observada, ou `null`; não garante versão mais recente |
| `requirements` | Requisitos anotados, geralmente parciais; vazio não significa nenhum |
| `requirements_complete` | Lista da página foi consultada integralmente; não certifica a cadeia transitiva |
| `related_ids` | “Veja também”: base, refit ou patch relacionado, **não um grafo de dependências resolvido** |
| `availability` | Estado da publicação observado, não sucesso de download |
| `source` | URL, método e data de consulta; índice de busca não é leitura da página |
| `evidence` | Páginas complementares, incluindo a listagem que permitiu descobrir um título |
| `redistribution` | Estado conservador, resumo da evidência e URL quando aplicável |
| `download` | Download manual na fonte; `archive_in_release` é sempre `false` nesta edição |
| `external_site_may_show_adult_content` | Aviso de conteúdo potencial do site, não descrição sexual do mod |

### Métodos

- `page_read`: o texto relevante da publicação foi retornado pela ferramenta de consulta e lido. Não exige que todos os comentários ou menus tenham sido lidos. Não prova download.
- `search_index`: informação obtida de resultado indexado da URL. Pode estar desatualizada.
- `author_index`: título e URL identificados em listagem pública do autor. O corpo da publicação não foi conferido.

As referências numéricas de busca são locais às consultas; **a URL identifica a fonte**. Para páginas abertas diretamente, a referência numérica funciona apenas como link de citação.

## Adicionar ou corrigir um registro

1. Ache a publicação do autor/portador e verifique que o tema realmente é BDO em Skyrim SE.
2. Registre a evidência e o nível de leitura real. Não atribua `page_read` a um título encontrado em sitemap.
3. Não invente autores, versão, runtime, tamanho, SHA-256 ou requisitos.
4. Se conhecer só o título, use `scope: pendente` e informe a listagem em `evidence`.
5. Se o arquivo foi removido/ocultado, mantenha histórico sem recuperar mirrors.
6. Não duplique um registro por `?tab=files`, idioma, cor ou novo nome do mesmo post.
7. Execute validação, geração e testes.
8. Documente mudanças de escopo/versão nas notas da próxima release.

## Reprodução

```sh
python tools/catalogo.py validar
python tools/catalogo.py gerar
python -m unittest discover -s tests -v
node --test tests/catalogo.test.js
python tools/catalogo.py gerar --check
python tools/catalogo.py pacote --saida dist
```

O ZIP possui ordenação, permissões e timestamp fixos para produzir os mesmos bytes a partir dos mesmos arquivos, na mesma versão de Python/zlib. Não depende da data de execução. O manifesto interno lista nome, tamanho e hash dos documentos; ele não prova as licenças dos mods referenciados.

## Inventário pessoal

```sh
python tools/catalogo.py inventario downloads > downloads/inventario.json
```

Só lê ZIP/7z/RAR **diretamente** na pasta especificada, ignora symlinks, não percorre subdiretórios, não extrai arquivos e não faz rede. O resultado vai para stdout para você decidir onde armazená-lo. Não há upload automático nem comparação com hashes que nunca foram obtidos.

A pasta `downloads/` é ignorada pelo Git. O empacotador não usa `git add .`, glob de todo o repositório ou varredura dessa pasta: `PACKAGE_FILES` é a lista explícita de arquivos documentais autorizados a entrar no ZIP.
