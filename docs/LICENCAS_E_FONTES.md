# Licenças, fontes e redistribuição

[← Início](../README.md)

## Regra desta release

**Somente documentação, metadados e links. Nenhum arquivo de mod de terceiros é distribuído.**

Disponibilidade para download, uso pessoal, crédito ao autor e permissão de reupload são questões diferentes. Este documento registra decisões práticas de publicação; não é um parecer jurídico sobre todos os mods ou sobre a legislação aplicável ao usuário.

O repositório `Viniciaao/GHOST` foi consultado pelo GitHub CLI e estava **público**. Uma release publicada nele não é uma pasta privada. Não alteramos a visibilidade do repositório.

## Estados registrados por item

| Estado no JSON | Significado nesta curadoria | Tratamento |
| --- | --- | --- |
| `forbidden` | A fonte consultada proíbe upload em outros sites ou reupload | Somente link para a fonte |
| `nexus_only` | Há autorização condicionada para derivados no Nexus, não para este mirror | Somente link para a fonte |
| `permission_required` | Depende das permissões de outros titulares não confirmadas | Somente link para a fonte |
| `unverified` | Não foi encontrada autorização suficiente para o GitHub | Somente link; não interpretar como licença aberta |

O estado expressa **o que foi possível confirmar**, não uma conclusão de que o mod em si é ilegal. Uma publicação feita por um portador também não constitui, por si só, permissão irrestrita dos titulares dos modelos, texturas, animações e demais componentes.

### Exemplos diretamente documentados

- **Karlstein, Eclipse, Lemoria e Ram Horn Witch SE:** as publicações do Team TAL contêm proibição expressa de reupload. [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-29777641) [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-31633824) [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-33371502) [3](https://www.patreon.com/posts/se-dm-bdor-ram-34746196)
- **Sura Blade Moveset:** a página distingue permissão de modificação/uso de assets da proibição de upload em outros sites. Uma não anula a outra. [4](https://www.nexusmods.com/skyrimspecialedition/mods/132879)
- **NightWarden PBR:** as instruções autorizam determinados derivados condicionados a publicação no Nexus, dependência do original e créditos. Isso não autoriza copiar o pacote para esta release. [2](https://www.nexusmods.com/skyrimspecialedition/mods/136047)
- **BDOR Hair / Salt and Wind:** a página informa autorização para divulgar links da base e condiciona o uso das alterações às permissões de Dint999. Não interpretamos “publicar links” como “hospedar cópias”. [5](https://www.nexusmods.com/skyrimspecialedition/mods/188732)

As fontes do Team TAL também creditam Pearl Abyss pelo conteúdo original. A autorização de um portador não deve ser presumida como cobrindo automaticamente os assets de terceiros. [1](https://www.patreon.com/takealook/posts/se-dm-bdor-by-33371502)

## Como baixar para uso pessoal

Use a página do autor ou portador indicada na ficha. Leia as condições, selecione o arquivo certo e realize autenticação apenas no próprio serviço. Se houver assinatura, restrição de acesso ou arquivo retirado, não usamos mecanismos para contorná-los.

O projeto **não** inclui:

- cookies, senhas, chaves de API ou contas compartilhadas;
- cópias encontradas em drives de pessoas não relacionadas ao autor;
- recuperação de arquivos ocultos por IDs antigos;
- ferramentas para remover paywalls ou driblar CAPTCHA;
- imagens promocionais copiadas dos autores;
- declarações de “livre redistribuição” deduzidas apenas de um botão de download.

## Para incluir arquivos em uma eventual release futura

Seria necessário revisar **cada arquivo**, em um processo distinto do empacotador documental atual:

1. Identificar nome, versão, autor, portador e URL de origem.
2. Conferir o arquivo efetivo, tamanho e SHA-256.
3. Obter licença pública ou autorização que cubra expressamente a distribuição pretendida, incluindo **GitHub público**, eventuais modificações e arquivos opcionais.
4. Verificar restrições de assets de terceiros, dependências, créditos, preservação de avisos e monetização.
5. Guardar a evidência de modo apropriado. Não publicar correspondência privada ou dados pessoais sem autorização para isso.
6. Revisar o conteúdo e os limites técnicos antes de qualquer upload.

**Modelo de pedido ao autor — não enviado automaticamente:**

> Olá! Gostaria de incluir o arquivo [nome e versão] em uma coleção de Skyrim SE/AE no repositório público https://github.com/Viniciaao/GHOST, como asset de uma GitHub Release, sem cobrança. Você autoriza redistribuir esse arquivo nesse local? Quais créditos, avisos e condições devo preservar? Há componentes de terceiros cuja autorização precise ser obtida separadamente?

Sem resposta suficiente, o item continua como link. Tornar um repositório privado, por si só, não muda as condições da licença do arquivo.

## Licença do GHOST

A licença MIT do repositório cobre **apenas código, interface e textos originais produzidos para o GHOST**. Nomes de produtos, títulos de mods, links e referências identificam trabalhos de seus respectivos titulares. Não estamos relicenciando arquivos externos.

Não há afiliação ou endosso de Bethesda, Pearl Abyss, Nexus Mods, Patreon ou dos autores listados.
