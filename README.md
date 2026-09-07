# BDO no Skyrim SE — Pacote Completo (Catálogo + Baixador + ZIPs de 1 GB)

Este repositório contém um pacote completo para colocar **conteúdo do Black Desert Online (BDO)** no
**The Elder Scrolls V: Skyrim Special Edition (SE/AE)** — armaduras, armas, cabelos, coleções etc.

## ⚠️ Leia antes de tudo (importante)

1. **Os arquivos NÃO foram baixados aqui dentro desta sandbox.** O ambiente de trabalho só tem
   acesso de rede ao GitHub; Nexus, Patreon, Mega, Google Drive, MediaFire, LoversLab, ModBooru,
   gamer-mods.ru etc. estão bloqueados nesta máquina. Tentar baixar daqui retorna erro de conexão.

2. Para comprovar o bloqueio, rodei os testes de conectividade: `curl` em `nexusmods.com`,
   `patreon.com`, `drive.google.com`, `mega.nz`, `mediafire.com`, `modbooru.com`, `archive.org`
   etc. → todos retornam `000/SSL_ERROR_SYSCALL`. Somente `github.com` e `api.github.com`
   respondem. Ou seja: **os mods precisam ser baixados em um PC comum, com internet normal.**

3. Por isso, o que fiz foi:

   - **Pesquisa minuciosa** de praticamente **todos** os mods existentes que adicionam conteúdo do
     BDO ao Skyrim SE (converte-se ~90% dos famosos "BDOR" do Team TAL, Kirax, dint999, NINI,
     THBG, immyneedscake etc.), incluindo fontes em **outros idiomas** (russo, chinês, coreano),
     que era exatamente a dificuldade do seu amigo.
   - Um **catálogo detalhado** (`CATALOGO_BDO_SKYRIM_SE.md`) com todos os nomes, autores,
     links diretos, tamanhos, requisitos e observações.
   - Uma **lista máquina-legível** (`MODS_BDO.csv`) usada pelo baixador automático.
   - Um **baixador automático** (`scripts/baixar_tudo_bdo.py`) — o Ghost roda no PC dele e baixa
     tudo de forma organizada, com retomada de downloads e verificação de integridade.
   - Um **empacotador de ZIPs de 1 GB** (`scripts/zipar_1gb.py`) — lê a pasta de downloads e gera
     arquivos `.zip` separados, cada um com no máximo ~1 GB, com manifesto explicando o conteúdo.

## Como usar (resumo, em PT-BR)

1. No PC do Ghost (recomendado: Windows 10/11, Python 3.10+, ter conta gratuita no
   [Nexus](https://www.nexusmods.com/), [LoversLab](https://www.loverslab.com/) e
   [Patreon](https://www.patreon.com/) para alguns links, e disco com ~80–120 GB livres).
2. `pip install requests` (só isso é obrigatório; `gdown` e `megatools` são opcionais para
   Google Drive/Mega em massa — ver `GUIA_INSTALACAO.md`).
3. Preencha `config_exemplo.ini` com a API Key do Nexus e os cookies do LoversLab (se quiser
   esses espelhos — passos explicados no guia).
4. Baixar tudo:
   ```bash
   python scripts/baixar_tudo_bdo.py --tudo
   # ou seletivo:  python scripts/baixar_tudo_bdo.py --so colecoes_kirax,pack_team_tal
   ```
5. Gerar os ZIPs de 1 GB:
   ```bash
   python scripts/zipar_1gb.py --limite-gb 1
   ```
   O resultado fica em `ZIP_1GB/` (ex.: `BDO_Skyrim_SE_Parte_001.zip`, `..._002.zip`...),
   acompanhado de `MANIFESTO.txt`.

## Arquivos deste pacote

| Arquivo | Descrição |
|---|---|
| `CATALOGO_BDO_SKYRIM_SE.md` | ⭐ Catálogo detalhado e comentado de todos os mods BDO p/ SE encontrados |
| `GUIA_INSTALACAO.md` | Guia passo a passo: requisitos, instalação, física, Bodyslide, resolução de problemas |
| `MODS_BDO.csv` | Lista completa (nome, autor, link, tamanho, prioridade) usada pelo baixador |
| `scripts/baixar_tudo_bdo.py` | Baixador automático (Nexus, LoversLab, MediaFire, Google Drive, Mega, ModBooru, Patreon, gamer-mods.ru) |
| `scripts/zipar_1gb.py` | Divide tudo em ZIPs separados de até 1 GB + manifesto |
| `config_exemplo.ini` | Modelo de configuração (API key, cookies, limites) |

## Aviso legal rápido

Os models são de terceiros, tirados do BDO (© Pearl Abyss). Muitos autores **proíbem
re-hospedar** — por isso este projeto **não hospeda nada**: ele apenas aponta para as fontes
originais e baixa no PC do usuário. Apoie os autores (Team TAL/Kirax etc. têm Patreon) e não
re-distribua os arquivos.
