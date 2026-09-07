# GHOST · Black Desert → Skyrim SE/AE

**Catálogo em português para planejar uma coleção pessoal de mods de Black Desert Online no Skyrim Special Edition / Anniversary Edition para PC.**

> **Esta é uma release de catálogo e documentação, não um modpack instalável.**
> **0 arquivos de mods baixados. 0 arquivos de mods redistribuídos.**
> O pedido de reunir os arquivos de “quase todos os mods” **não foi concluído**: não foi confirmada permissão para republicar os arquivos pesquisados no GitHub, e downloads binários não foram validados.

**Versão:** `0.1.0` · **Pesquisa:** 06/09/2026 · **Idioma:** PT-BR

## Abrir a coleção

- **[Release no GitHub](https://github.com/Viniciaao/GHOST/releases/tag/bdo-se-ae-catalogo-v0.1.0)** — ZIP documental, CSV, JSON, manifesto e checksums.
- **[Catálogo detalhado](docs/CATALOGO.md)** — todas as fichas, com fontes e ressalvas.
- **[Instalação e compatibilidade SE/AE](docs/INSTALACAO_SE_AE.md)** — preparação, escolha de corpo, física, combate, conflitos e testes.
- **[Relatório do que foi realmente feito](docs/RELATORIO.md)** — contagens e limites da verificação.

Para a interface com busca e seleção: baixe o ZIP da release, extraia e abra **`catalogo.html`** no navegador. Não exige servidor, Python, conta GHOST ou conexão para consultar os dados. Os links dos autores exigem internet. **Não importe esse ZIP como mod no MO2/Vortex.**

## O que foi catalogado

| Escopo | Registros | Interpretação |
| --- | ---: | --- |
| Principal | **49** | Há descrição de conteúdo; alguns registros ainda se apoiam em índices de busca |
| A aprofundar | **18** | Pistas pertinentes, sem verificação individual suficiente |
| Histórico / indisponíveis | **8** | Links antigos, ocultos, removidos ou sem download identificado |
| **Total** | **75** | Publicações e variantes; não são 75 arquivos baixados nem 75 conteúdos únicos |

Abrange packs, armaduras/roupas, conversões de corpo, cabelos, animações, patches, integrações no mundo e personagens. Não existe aqui uma estimativa verificável do total de mods existentes, portanto **não afirmamos cobrir “quase todos”**.

### Comece pelos packs, não por dezenas de ports sobrepostos

- **BDOR 2024 Female Collection, de Kirax:** a página anuncia **26 trajes**, corpo **3BA**, física HDT-SMP e obtenção por forja/AddItemMenu. [1](https://www.loverslab.com/files/file/34130-bdor-2024-female-collection-by-kirax/)
- **BDOR 2024 Male Collection, de Kirax:** a página anuncia **86 trajes**, HDT-SMP e uso do esqueleto XP32. [1](https://www.loverslab.com/files/file/34339-bdor-2024-male-collection-by-kirax/)

Essas são contagens **declaradas pelos autores**, não auditadas. Não representam 112 mods independentes, nem garantem ausência de sobreposição com outros packs. As páginas estão na categoria de mods regulares, mas o site também pode exibir conteúdo adulto.

Outros caminhos estão nas fichas: ports SE publicados pelo Team TAL, conversões de immyneedscake e urbon, série BDO Reborn de Kirax, cabelos de Dint999 e addons, Guardian/Sura Blade e integrações por chefes/SPID.

## Como usar para seus downloads pessoais

1. Abra `catalogo.html` e filtre por **categoria, corpo, escopo e nível de evidência**.
2. Marque os itens que quer pesquisar. A seleção é só um planejamento local: **não significa que algo foi baixado**.
3. Exporte a seleção em TXT ou JSON. O ZIP também inclui atalhos `.url` organizados em `links/`.
4. Abra a **página da fonte** de cada item; leia requisitos, permissões e aba de arquivos. Faça login **diretamente no site**, se necessário. Não compartilhe cookies, senhas ou tokens.
5. Baixe a versão correta para o seu corpo e executável. Se a página estiver retirada ou inacessível, deixe o item pendente — não use reuploads aleatórios.
6. Instale e teste em pequenos grupos, seguindo o [guia SE/AE](docs/INSTALACAO_SE_AE.md).

O catálogo não incorpora imagens dos mods, não carrega rastreadores e não abre páginas em lote. Sites externos têm regras e conteúdo próprios.

## Por que os arquivos não estão na release?

O repositório é público: anexar um arquivo a uma release publicada permitiria que outras pessoas o baixassem. O uso pessoal pretendido não transforma esse upload em armazenamento privado.

Nas páginas SE de Karlstein, Eclipse, Lemoria e Ram Horn Witch, o Team TAL proíbe expressamente o reupload. Outros registros possuem restrições próprias ou permissões não confirmadas. [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-29777641) [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-31633824) [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-33371502) [3](https://www.patreon.com/posts/se-dm-bdor-ram-34746196)

Detalhes e procedimento para revisar autorizações futuras: **[licenças e fontes](docs/LICENCAS_E_FONTES.md)**. Também houve falhas TLS em consultas diretas do ambiente; isso está documentado, sem declarar downloads inexistentes.

## Arquivos e ferramentas

```text
catalogo.html                 Interface offline, busca e seleção exportável
catalog/mods.json             Dados principais, evidências e permissões
catalog/mods.csv              Planilha UTF-8 com BOM
links/                        Atalhos das fontes, presentes no ZIP da release
CONTEUDO_DA_RELEASE.json       Manifesto documental, presente nos assets/ZIP
SHA256SUMS.txt                Hashes dos assets da release
CHECKSUMS_INTERNOS.sha256      Hashes dos documentos dentro do ZIP
```

Ferramentas opcionais: **Python 3.10+**, sem bibliotecas externas. Node.js só é necessário para os testes de JavaScript.

```sh
python tools/catalogo.py validar
python tools/catalogo.py listar --categoria cabelos --escopo principal
python tools/catalogo.py gerar
python tools/catalogo.py gerar --check
python -m unittest discover -s tests -v
node --test tests/catalogo.test.js
python tools/catalogo.py pacote
```

Para registrar arquivos que **você já baixou** em uma pasta local:

```sh
# Primeiro crie downloads/ e coloque seus arquivos nela.
python tools/catalogo.py inventario downloads > downloads/inventario.json
```

O inventário só calcula nome, tamanho e SHA-256 dos ZIP/7z/RAR diretamente nessa pasta. Não extrai, executa, envia ou valida licenças. `downloads/`, `local/`, arquivos de mods e `dist/` são ignorados pelo Git. O empacotador usa uma lista explícita de documentos, nunca a pasta de downloads.

## Documentação adicional

- [Método, fontes consultadas e lacunas](docs/PESQUISA.md)
- [Origens LE que não devem ser confundidas com ports SE](docs/REFERENCIAS_LE.md)
- [Formato dos dados e manutenção](docs/FORMATO_DOS_DADOS.md)
- [Notas desta release](RELEASE_NOTES.md)

**Nenhum teste dentro do Skyrim foi realizado.** Os testes do repositório verificam dados e ferramentas, não compatibilidade dos mods. Skyrim e Black Desert Online pertencem aos respectivos titulares. Este projeto não é afiliado a Bethesda, Pearl Abyss ou aos autores citados. A [licença MIT](LICENSE) cobre somente o trabalho original deste repositório, não os mods de terceiros.
