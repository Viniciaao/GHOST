# Guia de instalação · Skyrim SE/AE para PC

[← Início](../README.md) · [Catálogo](CATALOGO.md)

> Este guia é um roteiro de preparação, **não uma lista de mods testada em conjunto**. Não há Skyrim instalado ou teste de jogo registrado nesta entrega. As instruções específicas do autor e da versão do mod prevalecem.

## 1. Identifique sua instalação antes de baixar

Anote em um arquivo pessoal, fora do Git:

| Campo | O que anotar |
| --- | --- |
| Loja | Steam, GOG ou outra edição suportada pelas ferramentas escolhidas |
| Executável | Versão exata de `SkyrimSE.exe`, nas propriedades do arquivo |
| SKSE | Build que corresponde à loja e ao executável |
| Gerenciador | Mod Organizer 2 ou Vortex; escolha um para controlar a instalação |
| Corpo feminino | CBBE/3BA **ou** família UNP/BHUNP, conforme o perfil |
| Corpo masculino | Padrão ou refit específico, como HIMBO |
| Física | Implementação SMP/FSMP e, se solicitado pelo corpo, CBPC |
| Renderização | Configuração gráfica pretendida; PBR não é só uma textura comum |
| Combate | Vanilla, framework antigo ou MCO; não misturar sem planejamento |

**SE/AE no nome não basta.** Versões como `1.5.97`, `1.6.640` e `1.6.1170` são exemplos de executáveis, não uma recomendação de atualizar ou fazer downgrade. Ter o pacote comercial Anniversary Upgrade não basta para selecionar uma DLL compatível. Consulte o distribuidor oficial do SKSE: [1](https://skse.silverlock.org/).

No caso dos ports SE antigos do Team TAL deste catálogo, a página registra testes em **SSE 1.5.80**. Isso é um dado histórico do autor, não uma certificação para AE atual. [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-33371502)

## 2. Monte um perfil de teste separado

1. Faça backup dos saves e das configurações atuais.
2. Crie um perfil no gerenciador, preferencialmente com saves e INIs separados.
3. Confirme que o jogo funciona antes de adicionar mods BDO.
4. Instale as dependências escolhidas conforme suas instruções oficiais.
5. Execute o jogo pelo carregador adequado quando um mod exigir SKSE.
6. Registre o estado funcional antes de adicionar o próximo grupo.

Não limpe ou desative plugins de uma partida importante para experimentar um pack. Para comparação, use um save de teste ou uma nova partida. O catálogo não modifica automaticamente seus saves ou a pasta `Data`.

## 3. Escolha uma base de corpo e esqueleto

### Roupas femininas

- **CBBE, CBBE SMP e 3BA:** não suponha que um arquivo anunciado apenas como CBBE traga todos os refits.
- **UNP/UUNP/BHUNP:** confira tanto a malha quanto as texturas e a geração de BodySlide escolhidas.
- Não instale duas versões de corpo-base para disputar os mesmos arquivos sem saber qual deverá vencer.
- Um refit BHUNP de uma armadura 3BA pode exigir o arquivo principal. O nome “conversão” não garante que malhas/texturas completas estejam incluídas.

Exemplo concreto: o post **Hyperion de urbon** orienta usuários BHUNP a usar o arquivo principal e a conversão, distinguindo a base 3BA. [7](https://www.patreon.com/posts/bdor-hyperion-81118176?l=es)

### Roupas masculinas

Selecione as conversões adequadas ao corpo usado no perfil. HIMBO no título é uma indicação de refit, não garantia de que qualquer versão de HIMBO ou esqueleto funcionará. No pack masculino de Kirax, a página pede HDT-SMP e que XP32 prevaleça sobre arquivos conflitantes de esqueleto. [1](https://www.loverslab.com/files/file/34339-bdor-2024-male-collection-by-kirax/)

### Referências técnicas úteis

Não são “mods de Black Desert” e **não entram na contagem de 75 registros**:

| Ferramenta | Papel a conferir | Fonte |
| --- | --- | --- |
| BodySlide and Outfit Studio | Gerar roupas e corpo para o preset escolhido | [3](https://www.nexusmods.com/skyrimspecialedition/mods/201) |
| CBBE | Família de corpo usada por algumas conversões | [1](https://www.nexusmods.com/skyrimspecialedition/mods/198) |
| CBBE 3BA | Variante de corpo usada em várias roupas do catálogo | [1](https://www.nexusmods.com/skyrimspecialedition/mods/30174) |
| BHUNP | Outra família de corpo/refits; não presumir equivalência com CBBE | [1](https://www.nexusmods.com/skyrimspecialedition/mods/31126) |
| XPMSSE | Esqueleto solicitado por vários ports SE | [1](https://www.nexusmods.com/skyrimspecialedition/mods/1988) |
| RaceMenu | Personalização; também aparece como dependência de NiOverride | [1](https://www.nexusmods.com/skyrimspecialedition/mods/19080) |
| FSMP | Física de tecido/cabelo onde solicitada | [1](https://www.nexusmods.com/skyrimspecialedition/mods/57339) |
| CBPC | Física solicitada por determinadas opções de corpo/roupa | [1](https://www.nexusmods.com/skyrimspecialedition/mods/21224) |

Esses links são referências de requisitos encontrados nas publicações. **Não se recomenda instalar toda a tabela sem necessidade.** Confira também os requisitos transitivos e as builds para seu executável.

## 4. Instale uma armadura antes de instalar um pack inteiro

1. Escolha uma única publicação/variante da armadura.
2. Baixe pela página de origem e preserve o arquivo original e o número da versão.
3. Importe o arquivo pelo gerenciador; examine o FOMOD quando existir.
4. Escolha corpo, cores e física conscientemente. Opções podem ser alternativas, não cumulativas.
5. Confirme que não faltam masters e que o plugin esperado está ativo.
6. Se o autor exigir BodySlide, execute-o no ambiente do gerenciador, selecione o preset correto e gere as peças.
7. Guarde os arquivos gerados em um mod de saída separado, como `GHOST - BodySlide Output`, para facilitar reversão.
8. Teste no jogo antes de adicionar outros conjuntos.

No **Hanbok Revised**, o autor orienta filtrar por `hanbok` e usar **Batch Build**. [1](https://www.nexusmods.com/skyrimspecialedition/mods/158294)

No **Ram Horn Witch SE publicado pelo Team TAL**, o autor avisa que a conversão é CBBE e pede gerar as peças no BodySlide. [3](https://www.patreon.com/posts/se-dm-bdor-ram-34746196)

**Não execute Batch Build de tudo indiscriminadamente.** Isso pode gerar versões indesejadas de outras roupas ou sobrescrever saídas usadas no seu perfil.

## 5. Trate a física como uma camada própria

- HDT-PE de LE não se torna SMP de SE renomeando a pasta ou trocando uma DLL.
- Verifique runtime, requisitos e opções do instalador da implementação de física escolhida.
- Confira se o esqueleto, as malhas e os arquivos XML correspondem à mesma conversão.
- CBPC e SMP têm funções/configurações diferentes; não remova um simplesmente por ter instalado o outro.
- Capas, saias e cabelos em muitos NPCs podem elevar o custo de processamento. Meça seu perfil com poucos personagens antes de distribuir para uma cidade inteira.

O patch de **Dreadstorm** alerta especificamente para possível queda de desempenho associada ao capacete SMP e à tempestade. [2](https://www.nexusmods.com/skyrimspecialedition/mods/97780)

**Eclipse SE** é um exemplo de diferença entre edições: o autor removeu a capa nessa versão. Não tente corrigir isso copiando a capa LE para dentro do port SE. [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-31633824)

## 6. Cabelos: base primeiro, complementos depois

Ordem de raciocínio, não receita universal de load order:

1. Versão do pack BDOR Hair obtida pelo canal autorizado do autor.
2. Addon compatível, se desejado.
3. Patch unissex compatível com essa versão da base.
4. Texturas alternativas, escolhendo conscientemente qual arquivo deve prevalecer.

O addon de **Caenarvon** exige o pack de Dint999; o addon sozinho não o substitui. [1](https://www.patreon.com/Caenarvon/posts/happy-new-year-119283988)

A página de **Salt and Wind (Sassy)** informa base BDOR Hair 0.24, orienta escolher uma das opções de textura e declara ter autorização do autor para divulgar os links ali. Isso não transfere ao GHOST o direito de reenviar o pack. [5](https://www.nexusmods.com/skyrimspecialedition/mods/188732)

## 7. Combate: não confunda os movesets

| Opção | Atenção principal | Fonte |
| --- | --- | --- |
| Guardian | Machado de uma mão; OAR e Attack MCO/DXP com seus requisitos | [3](https://www.nexusmods.com/skyrimspecialedition/mods/107863) |
| Guardian Awakening | Machados de duas mãos, opções de martelo; módulos de esquiva/ataques laterais são condicionais | [1](https://www.nexusmods.com/skyrimspecialedition/mods/117071) |
| Sura Blade | Arma e bainha específicas; não é substituto genérico para qualquer espada | [4](https://www.nexusmods.com/skyrimspecialedition/mods/132879) |
| Awakened Warrior | Frameworks antigos DAR/Dynamic Combat Module; SkySA aparece como recomendação | [1](https://www.nexusmods.com/skyrimspecialedition/mods/40216) |

O requisito **MCO 1.6+** do Sura Blade refere-se à versão do framework MCO, **não ao executável AE 1.6.x**. O autor também pede que não sejam substituídos os arquivos de ação e que sejam equipadas a arma e a bainha próprias. [4](https://www.nexusmods.com/skyrimspecialedition/mods/132879)

Depois de instalar mods que alteram behavior, execute o gerador indicado pelas suas versões e documentação. Não aplique FNIS, Nemesis e Pandora juntos por tentativa e erro. Não suponha que todo pacote DAR seja automaticamente um moveset MCO.

Teste ataques normais, fortes, movimentação, bloqueio, esquiva e transições. Para NPCs, verifique se o suporte exigido pelo moveset/patch foi instalado; não adicione SCAR apenas porque ele existe no catálogo.

## 8. Como obter os itens

- **Forja:** use quando o autor informa receitas.
- **AddItemMenu/Modex ou alternativa:** selecione uma ferramenta compatível com seu runtime; não copie a DLL de um tutorial antigo.
- **Console de teste:** `help "BDOR" 4` pode ajudar a localizar itens que usam esse nome. O FormID depende da sua ordem de carregamento. Não reutilize números copiados de outra instalação.
- **SPID ou chefes:** só use o patch depois de instalar e testar sua base.

Exemplos importantes:

- **Velkaviore:** o patch precisa do Arditer SE e a página afirma não fornecer assets da armadura. [1](https://www.nexusmods.com/skyrimspecialedition/mods/100648)
- **Courier Poetica:** requer Courier Replacer, SPID e a roupa Poetica separadamente. [7](https://www.nexusmods.com/skyrimspecialedition/mods/156140)
- **Mountain Spirit SPID:** a dependência da página aponta para um post LE. Isso exige atenção extra para encontrar o port SE esperado, não instalar o original LE diretamente. [1](https://www.nexusmods.com/skyrimspecialedition/mods/99701)

Patches podem referenciar nome de plugin e FormIDs específicos. Compactar, renomear ou fazer merge de uma base pode quebrar essas referências. Um refit de outro autor não é necessariamente substituto compatível com o patch.

## 9. Ordem e conflitos: dois problemas diferentes

- **Prioridade de arquivos:** decide qual malha, textura, XML ou script prevalece.
- **Ordem dos plugins:** determina resolução de registros e disponibilidade de masters.

Uma ferramenta de ordenação pode ajudar, mas não corrige automaticamente conversão errada, roupa gerada para outro corpo ou dependência ausente. Examine conflitos com o gerenciador e, quando tiver experiência, com xEdit. Não “limpe” todos os plugins de um pack sem orientação específica.

No caso de **NightWarden PBR**, o autor exige Community Shaders e informa que os materiais não funcionarão como pretendido em uma instalação sem CS. Não instale a variante PBR como simples atualização universal do port convencional. [2](https://www.nexusmods.com/skyrimspecialedition/mods/136047)

## 10. Checklist de aceitação de cada grupo

- [ ] Versão do mod e fonte anotadas.
- [ ] Corpo e variante de física corretos.
- [ ] Nenhum master ausente; nenhum plugin duplicado por engano.
- [ ] Jogo abre sem erro de DLL/SKSE.
- [ ] Itens equipam e desequipam sem travamento.
- [ ] Texturas aparecem; mãos, pés e pescoço não têm emendas inesperadas.
- [ ] Peso e preset do personagem conferidos.
- [ ] Primeira e terceira pessoa testadas.
- [ ] Corrida, combate e física testados em interior e exterior.
- [ ] Save de teste pode ser fechado e carregado novamente.
- [ ] Distribuição em NPCs só adicionada depois que o item-base funciona.
- [ ] Desempenho comparado com o perfil anterior.

## 11. Diagnóstico inicial

| Sintoma | Verificações iniciais, sem garantia de diagnóstico |
| --- | --- |
| Roupa invisível | Saída BodySlide, opção do FOMOD, malha instalada, slots e sexo suportado |
| Textura roxa | Arquivos de textura ausentes ou caminhos incorretos |
| Saia/cabelo esticado | Build de SMP, esqueleto, XML e conversão correta de SE |
| T-pose | Framework/behavior e saída do gerador; conferir versão das animações |
| Jogo fecha ao iniciar | Masters, mensagens de SKSE/DLL e último grupo adicionado |
| Fecha ao equipar | Isolar a peça, malha e física em perfil de teste |
| Item não aparece na forja | Pode não ter receita; consultar o método de obtenção na fonte |
| Cor errada | Opção do FOMOD e textura vencedora em conflito |
| NPC não recebe roupa | Base esperada pelo patch, versão de SPID, nome do plugin e regras |
| Metal PBR estranho | Pipeline gráfico e requisitos da variante; não trocar por ENB/CS ao acaso |

Não desative seu antivírus para fazer um arquivo suspeito rodar. Não execute instaladores anunciados por pop-ups no lugar do arquivo do mod. Se não conseguir validar a origem, deixe o item fora da coleção.
