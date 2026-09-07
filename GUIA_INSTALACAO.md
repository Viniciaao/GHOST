# GUIA DE INSTALAÇÃO — Mods do Black Desert Online no Skyrim Special Edition

Guia completo, em português, para instalar tudo que está no `CATALOGO_BDO_SKYRIM_SE.md`.
Siga na ordem. Onde tiver `>[arquivo]` é para consultar o arquivo correspondente deste pacote.

---

## 1. Prepare o jogo

- ⚠️ **Versão:** esses mods funcionam no **Skyrim SE 1.5.97** e no **Anniversary Edition (1.6.x)**.
  Em 1.6.640+ (AE atual) use **FSMP (Faster HDT-SMP)** no lugar do HDT-SMP antigo (seção 5).
- Sempre **backup** de saves antes de mexer em mods.
- Prefira **Mod Organizer 2 (MO2)** — instala e desinstala sem poluir a pasta do jogo.
- Recomendado: **SKSE64** (pegue a versão exata do seu jogo em skse.silverlock.org) e jogue sempre
  pelo `skse64_loader.exe`.

## 2. Instale os frameworks (OBRIGATÓRIO para todo o conteúdo abaixo)

| Ordem | Mod | Onde | Por quê |
|---|---|---|---|
| 1 | **XP32 Maximum Skeleton Special Extended (XPMSSE)** | Nexus (skyrimspecialedition / 1988) | esqueleto com ossos de física |
| 2 | **CBBE 3BA (3BBB)** — p/ coleções Kirax/3BA | Nexus (16666) | corpo feminino com física |
| 3 | **UNP/UUNP (ou BHUNP)** — p/ pack Team TAL v1.6 (840 MB) | Nexus (UNP/Naturalistic) | corpo base do pack clássico |
| 4 | **Bodyslide and Outfit Studio** | Nexus (1) | gera os shapes/roupas para o seu corpo |
| 5 | **HDT-SMP** (ou **FSMP** em AE) | Nexus (skinned mesh physics) / GitHub (FSMP) | capas, saias, cabelos com física |
| 6 | **AddItemMenu SSE** | Nexus (17537) | pegar itens no jogo sem craft |
| 7 | **RaceMenu** (opcional, p/ high heels/sliders) | Nexus (19080) | ajustes extras |
| 8 | **SkyUI + MCM** | Nexus (12604) | menu de configuração |

> Não instale mods de "body" conflitantes: ou **CBBE 3BA** ou **UNP/UUNP** (o pack Team TAL v1.6
> exige UNP; as coleções Kirax exigem 3BA). Na dúvida, use as versões **3BA** dos mods e o
> **pack Team TAL v2.0 SMP** (que já tem suporte CBBE) em vez do v1.6.

## 3. Baixe os mods (no PC do Ghost, com internet normal)

### 3.1 Instale o Python e dependências
```bat
:: Windows
winget install Python.Python.3.11
pip install requests gdown
:: (opcional, para links Mega)
:: instale Mega Tools: https://megatools.megous.com/  (no Windows: winget install megatools)
```

### 3.2 Configure as contas (opcional, mas recomendado)
1. **Nexus** — crie conta em nexusmods.com → Account → API Keys → copie a chave.
2. **LoversLab** — crie conta em loverslab.com (gratuita) e faça login no navegador.
3. Copie `config_exemplo.ini` → `config.ini` e preencha (cookies do LoversLab: F12 →
   Network → clique numa requisição → copie o campo `Cookie`).

### 3.3 Baixe tudo
```bat
cd caminho\do\GHOST
python scripts\baixar_tudo_bdo.py --tudo
```
- Para baixar só as fontes principais (recomendado p/ começar):
```bat
python scripts\baixar_tudo_bdo.py --so COL01,COL02,COL03,COL04,COL05 --prioridade 1
```
- O baixador salva em `baixados/` e gera `download_report.csv` (mostra o que falhou).
- Se um link cair (morre com o tempo), procure o **espelho alternativo** da mesma linha na
  tabela 3.2 do catálogo.

## 4. Gere os ZIPs de 1 GB (como você pediu 🎯)

```bat
python scripts\zipar_1gb.py --dir baixados --saida ZIP_1GB --limite-gb 1
```
Resultado em `ZIP_1GB/`:
- `BDO_Skyrim_SE_Parte_001.zip` … cada um com **até ~1 GB**;
- se algum mod sozinho passar de 1 GB, ele é dividido em `...zip.001/.002` (junte com
  `JUNTAR_PARTES.py` ou `copy /b` antes de extrair);
- `MANIFESTO.txt` diz exatamente o que tem em cada ZIP (nomes, tamanhos, SHA-256);
- `conteudo.csv` com a tabela completa.

> Os ZIPs são um **arquivo de transporte** (pra mandar pro amigo, colocar em HD/pendrive).
> Depois de extrair, instale os mods pelo MO2/Vortex normalmente.

## 5. Física (HDT-SMP × FSMP)

| Seu jogo | Use |
|---|---|
| SE 1.5.97 | HDT-SMP (link no Nexus/GitHub) |
| AE 1.6.640+ | **FSMP — Faster HDT-SMP** (github.com/PhantomGamers/FSMP) |

Depois de instalar, rode **FNIS/Nemesis** se algum mod pedir animações (a maioria dos armors
não pede; os cabelos do dint999 pedem FNIS só se você usar física de cabelo com idles).

## 6. Bodyslide (para os conjuntos que têm slider)

1. Abra **Bodyslide** (pelo MO2 → executáveis → "Bodyslide" bat/64-bit).
2. Na aba *Outfit/Body*, escolha o preset (ex.: `CBBE 3BA` ou `UUNP` do pack).
3. Marque **Batch Build** (Build + Build All).
4. Selecione os outfits de BDO (procure "BDOR"/"BDO" na lista) e clique **Build**.
5. **Não** pule essa etapa se o mod tiver `meshes` em Bodyslide: sem gerar, as roupas podem
   ficar invisíveis/travadas.

## 7. Como pegar os itens no jogo

- **AddItemMenu SSE** → abra com `AddItemMenu` (hotkey/item) → digite `BDO`/`BDOR` ou o nome do
  set (ex.: `Valoren`, `Danharum`, `La Orzeca`) → adicione ao inventário.
- Na maioria, os conjuntos também são **fabricáveis**: Team TAL no pack adiciona receitas de
  forja/ferreiro; THBG usa categoria **élfico**.
- Coleções Kirax: no *forge* (ferreiro) ou AddItemMenu.

## 8. Ordem de carregamento sugerida

```
(esses 5 "requisitos" em cima)
1  XPMSSE
2  CBBE 3BA / UNP (um só!)
3  FSMP/HDT-SMP
4  AddItemMenu
5  [SE] BDOR Pack by Team TAL v2.0 SMP         (ou v1.6 + esps)
6  BDOR 2024 Female Collection by Kirax
7  BDOR 2024 Male Collection by Kirax
8  THBG packs (Armors Collection, Dark Knight, Sorceress)
9  immyneedscake (Valoren, Sin Terrna)
10 individuais do ModBooru/Drive/Mega (tabela 3.1 e 3.2 do catálogo)
```
- As coleções do Kirax **não sobrepõem** o pack do Team TAL (o autor garante) → podem ficar juntas.
- Se algum `.esp` repetir FormIDs, abra o **xEdit/SSEEdit** (roda com o mod instalado) e confira;
  raramente acontece (Team TAL usa 0D6x, Kirax usa os próprios IDs).
- Em caso de dúvida de patches: nenhum requisito de patch extra entre os BDO.

## 9. Quer ainda MAIS sets BDO? (convertendo mods LE)

Muitos sets clássicos (NINI/dint999) só existem para **Skyrim LE**. Converta com:

1. **Cathedral Assets Optimizer (CAO)** — abre o pacote LE → "Skyrim SE" → otimiza meshes/texturas;
2. **NIF Optimizer** (se necessário);
3. Abra o `.esp` no **SSEEdit** e salve como SE (muita gente não precisa);
4. Rode o **Bodyslide** pro corpo escolhido.

Fontes LE (referência): projeto **BDOscrolls** <https://pastebin.com/zQP1bGcw> e o post de
preservação do gnomadgnomod (o script `--fonte gnomad --somente-se` já coleta os SE).

## 10. Problemas comuns e soluções

| Sintoma | Causa provável | Solução |
|---|---|---|
| CTD ao carregar save | versão errada / falta framework | confira SKSE e XPMSSE; ative logs |
| Armadura invisível | Bodyslide não rodou | rode *Batch Build* no Bodyslide |
| Peças "piscando"/estourando | falta física ou colisão | instale FSMP/HDT-SMP; no AE use FSMP |
| Capa/saia travada no ar | XML de física ausente | reabra o FOMOD e escolha SMP; cheque FSMP |
| Tela preta no RaceMenu | RaceMenu 1.6.x x AE antigo | use RaceMenu+SE compatível ou desative sliders |
| Download falhou no Mega | falta chave/ferramenta | instale megatools ou baixe manualmente |
| Link morreu | mirror removido | use o espelho da tabela (ModBooru/gamer-mods) |
| Baidu não baixa | exige app chinês | use Baidu Netdisk; alternativa: espelhos |

## 11. Espaço em disco

- Conjuntos BDO (todos): **~10–15 GB baixados**; descompactado/Bodyslide **+10–15 GB**.
- Reserve **60 GB** de folga no SSD.

## 12. Apoie os autores (importante) ❤️

- Team TAL: patreon.com/takealook · Kirax: patreon.com/KiraxWorkShop
- THBG: patreon.com/THBossGamer · immyneedscake: immyneedscake.com
- dint999 (cabelos): Patreon do dint999

E **não re-hospede** os arquivos — os portadores proíbem e a Pearl Abyss detém os assets originais.
