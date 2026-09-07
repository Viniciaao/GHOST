# Relatório de entrega e verificação

Data da pesquisa: **2026-09-06**. Catálogo **0.1.0**.

## O que foi e o que não foi feito

| Item | Resultado |
| --- | --- |
| Registros de mods/variantes | 75 |
| Catálogo principal | 49 |
| Referências a aprofundar | 18 |
| Histórico/indisponíveis | 8 |
| Arquivos de mods baixados | **0** |
| Arquivos de mods anexados à release | **0** |
| Downloads binários testados ponta a ponta | **0** |
| Instalações/testes no Skyrim | **0** |
| Percentual de todos os mods existentes | Desconhecido; não reivindicado |

## Nível de evidência

| Método | Registros |
| --- | --- |
| Texto da página lido | 28 |
| Somente índice de busca | 30 |
| Somente listagem do autor | 17 |

## Permissões registradas

| Estado | Registros |
| --- | --- |
| Reupload proibido | 17 |
| Permissão não confirmada | 56 |
| Permissão de terceiros pendente | 1 |
| Derivados condicionados ao Nexus | 1 |

## Limitações operacionais

- A pesquisa utilizou resultados de busca e texto de páginas públicas. O método de cada entrada está no JSON/CSV.
- Quatro consultas de metadados por HTTPS diretamente no ambiente (Nexus, Patreon, LoversLab e immyneedscake) falharam com erro TLS/EOF. Nenhum arquivo de mod foi recebido nessas consultas.
- As ferramentas de pesquisa retornaram texto de páginas apesar dessas falhas; isso não atesta que um download binário funcionaria neste ambiente.
- Não foram usadas credenciais pessoais, cookies, APIs privadas, bypass de login, mirrors de arquivos retirados ou assinaturas pagas.
- Não há checksum de mod inventado. SHA256SUMS.txt verifica apenas os arquivos documentais produzidos pelo GHOST.
- A decisão de não reenviar arquivos também depende de permissões, e não apenas de limitações de rede.

## Validações reproduzíveis

```sh
python tools/catalogo.py validar
python -m unittest discover -s tests -v
node --test tests/catalogo.test.js
python tools/catalogo.py gerar --check
python tools/catalogo.py pacote
```

Esses comandos validam dados, renderização, filtros, seleção local e empacotamento. **Não validam mods dentro do jogo.**

## Verificação extra da interface nesta entrega

- Chromium 149.0.7827.0, com visualizações de 1440 × 1000 e 390 × 844 pixels.
- Testados: montagem das fichas, três escopos, busca, estado vazio, seleção, exportação JSON, persistência após recarregar e navegação para ficha relacionada.
- Nenhum erro JavaScript observado; nenhuma rolagem horizontal nessas duas larguras; nenhuma requisição externa disparada pela interface durante esse teste.
- Essa checagem foi feita no HTML local, não nos sites dos autores nem no Skyrim.

O pacote documental é gerado por allowlist: pastas de downloads, .git, credenciais, malhas, texturas e plugins não são varridos nem adicionados.
