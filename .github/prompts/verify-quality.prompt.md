---
name: "verify-quality"
description: "Audita a qualidade de cada pacote em construção em .spec/ (ou só o de feature=): matriz REQ-teste, lacunas de cobertura por risco, testes faltantes escritos a partir de SPECIFICATION.md, E2E com Playwright quando aplicável, gates e validadores SDD executados, com resultados em TESTING.md, VERIFICATION.md, checkpoints/test-coverage.yaml e evidence/."
argument-hint: "[feature=NNN-nome-da-funcionalidade] [escopo=REQ-001,REQ-002]"
agent: "qa-engineer"
tools: ["read", "search", "edit", "execute", "playwright/*"]
---
# /verify-quality

## Objetivo

Provar que o código entrega o comportamento especificado. Cruzar requisitos e testes, priorizar lacunas por risco, escrever os testes que faltam a partir de `SPECIFICATION.md` e executar os gates e os validadores SDD, sem fabricar um pipeline verde. Sem `feature=`, a auditoria cobre todo pacote de `.spec/` com `TASKS.md` produzido e ao menos uma tarefa concluída com evidência; com `feature=`, só aquele. Os resultados vão para `TESTING.md`, `VERIFICATION.md`, `checkpoints/test-coverage.yaml` e `evidence/`.

## Quando invocar

Na Etapa 4, em paralelo à implementação ou ao fim de uma fase de `TASKS.md`, e antes de declarar a funcionalidade verificada.

> [!NOTE]
> Não use este prompt para escrever código de produção (`/implement-task`) nem para corrigir requisitos (`/validate-spec`). Testes que falham por comportamento ausente são entregues ao `@implementer`.

## Pré-condições

- Ao menos um pacote em `.spec/` tem `TASKS.md`, `TESTING.md`, `TDD.md` e `VERIFICATION.md` produzidos e uma tarefa concluída com evidência (com `feature=`, o pacote informado)
- Framework de testes e comandos com cobertura estão declarados em [copilot-instructions.md](../copilot-instructions.md)
- Para E2E, a aplicação pode ser executada localmente

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>` (opcional): restringe a auditoria a um pacote; sem ele, todos os pacotes em construção são auditados
- `escopo=<REQ-IDs>` quando a auditoria for parcial; exige `feature=`, porque os IDs são do pacote
- Riscos conhecidos ou incidentes recentes, se houver

## O que vou fazer

- Carregar as instruções de testes, a skill TDD e a skill SDD antes de testar
- Selecionar os pacotes em construção pelo índice `.spec/README.md` e listar os demais com o motivo
- Inventariar REQ/AC em `SPECIFICATION.md`, o catálogo de `TESTING.md`, os ciclos de `TDD.md`, os testes existentes com comentário `REQ-NNN` e o relatório de cobertura atual
- Montar a matriz requisito-teste e classificar cada requisito como coberto, parcial ou descoberto
- Priorizar lacunas por risco: P0 primeiro, depois caminhos de erro, limites e exemplos do negócio
- Escrever testes faltantes a partir dos critérios de aceite, parametrizando tabelas de exemplos
- Checar com mentalidade de mutação se cada teste falha quando o comportamento muda
- Explorar fluxos críticos de UI com Playwright quando o servidor MCP estiver disponível e gerar o E2E correspondente
- Executar os gates e os validadores SDD e salvar a saída em `evidence/<AAAA-MM-DD>-<assunto>.md`
- Atualizar o catálogo de `TESTING.md`, os `Resultados` e as `Execuções de validadores` de `VERIFICATION.md`, `checkpoints/test-coverage.yaml` e `evidence/README.md`

## O que NÃO vou fazer

- Alterar código de produção para fazer um teste passar
- Pular, marcar como `skip` ou enfraquecer asserções para forçar o verde
- Perseguir percentual de cobertura em vez de risco
- Fazer mock de dependência cujo comportamento de dados importa
- Inventar valores esperados ausentes de `SPECIFICATION.md` ou da fonte em `origem:`
- Marcar requisito como `Verificado` sem execução registrada
- Alterar `SPECIFICATION.md`, `DESIGN.md` ou `TASKS.md`, ou criar arquivos com os nomes proibidos em minúsculas (`spec.md`, `tasks.md`)

## Formato de saída

```markdown
## Qualidade: <NNN>-<funcionalidade>

### Matriz requisito-teste
| REQ-ID | AC-ID | Prioridade | Testes | Tipo | Status | Risco se falhar |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | AC-REQ-001-01 | P0 | `<arquivo>#<teste>` | unitário | coberto | <impacto> |
| REQ-004 | AC-REQ-004-01 | P1 | nenhum | - | descoberto | <impacto> |

### Testes adicionados
| Teste | REQ/AC | Resultado | Encaminhamento |
| --- | --- | --- | --- |
| `<arquivo>#<teste>` | REQ-004 / AC-REQ-004-01 | FAIL (comportamento ausente) | `@implementer` via T00N |

### Gates
| Gate | Comando | Resultado |
| --- | --- | --- |
| Testes + cobertura | `<comando>` | PASS/FAIL - <linhas>% / <branches>% (limite <x>% / <y>%) |
| E2E | `<comando>` | PASS/FAIL/NÃO APLICÁVEL (motivo) |
| Autoteste do validador | `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` | PASS/FAIL |
| Validador SDD | `python3 -B .github/scripts/validate-sdd.py --package <NNN>` | PASS/FAIL - <erros>/<avisos> |
| Validador SDD completo | `python3 -B .github/scripts/validate-sdd.py --require-full --strict` | PASS/FAIL (antes do PR) |

### Lacunas por risco
1. <REQ-ID> - <lacuna> - <ação e responsável>

### Registro
- Evidência: `evidence/<AAAA-MM-DD>-<assunto>.md`
- Atualizados: `TESTING.md`, `VERIFICATION.md`, `checkpoints/test-coverage.yaml`, `evidence/README.md`
```

Sem `feature=`, repita o bloco para cada pacote auditado.

## Regras de SDD e rastreabilidade

- Todo teste de requisito tem comentário `REQ-NNN` e nome que descreve comportamento.
- Um teste só merece existir se falhar com comportamento errado; asserções que sempre passam são reescritas.
- Pirâmide: muitos unitários rápidos, menos de integração, poucos E2E para fluxos críticos.
- Instabilidade (tempo, aleatoriedade, ordem, rede) é isolada e reportada, não mascarada com retry.
- Resultados vão para `Resultados` de `VERIFICATION.md` com data, comando e evidência em `evidence/`; o status de cada teste vai para o catálogo de `TESTING.md` e o mapa requisito-teste para `checkpoints/test-coverage.yaml`.
- Lacunas ficam registradas em `VERIFICATION.md` e viram tarefa proposta para `/break-down-tasks`; desvios de tarefa são reportados ao `@implementer`.
- Execute os validadores a partir da raiz: `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'`, `python3 -B .github/scripts/validate-sdd.py` (`--package NNN` para restringir), `python3 -B .github/scripts/validate-sdd.py --require-full --strict` antes do PR e `python3 -B .github/scripts/validate-design-diagrams.py` quando um diagrama mudar. Validação de artefatos não é sucesso de implementação.

## Definição de pronto

- [ ] Instruções de testes e skills TDD/SDD foram carregadas antes de testar
- [ ] Todo pacote em escopo foi auditado, e os pacotes fora de escopo estão listados com motivo
- [ ] Todo requisito em escopo aparece na matriz com status e risco
- [ ] Todo P0 tem pelo menos um teste que falha com comportamento errado
- [ ] Testes novos citam `REQ-NNN` e testes vermelhos foram encaminhados ao `@implementer`
- [ ] Os gates e os validadores SDD foram executados, com resultados reais em `VERIFICATION.md` e saída em `evidence/`
- [ ] `TESTING.md` e `checkpoints/test-coverage.yaml` refletem os testes existentes
- [ ] Nenhum teste foi pulado ou enfraquecido e lacunas estão reportadas por risco

## Corpo do prompt

Você é `@qa-engineer`. Prove o comportamento especificado com testes que falham em bugs reais.

**Passo 0 - Carregar skills e instruções.**
Leia as [instruções de testes](../instructions/tests.instructions.md) e as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md), carregue as skills [tdd-workflow](../skills/tdd-workflow/SKILL.md) e [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e leia os [quality gates](../skills/sdd-requirements-engineer/references/quality-gates.md), os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) (seções `TESTING`, `VERIFICATION` e `Checkpoints`) e o [copilot-instructions.md](../copilot-instructions.md). Se os comandos ainda forem marcadores `<...>`, pare e pergunte ao time.

**Passo 1 - Selecionar pacotes e inventariar.**
Sem `feature=`, liste os pacotes do índice `.spec/README.md` e selecione os que têm `TASKS.md` produzido e ao menos uma tarefa concluída com evidência; registre os demais com o motivo. Com `feature=`, só aquele (e `escopo=`, se informado). Para cada pacote, leia `SPECIFICATION.md`, `TASKS.md`, `TESTING.md`, `TDD.md`, `VERIFICATION.md` e `checkpoints/test-coverage.yaml`. Busque testes que citam cada `REQ-NNN` e rode a suíte com cobertura para obter o estado atual.

**Passo 2 - Montar a matriz.**
Classifique cada requisito em escopo como coberto, parcial ou descoberto, com prioridade e risco.

**Passo 3 - Priorizar lacunas.**
Ordene por risco: P0 descobertos, caminhos de erro, limites e exemplos do negócio sem teste.

**Passo 4 - Escrever testes.**
Para cada lacuna priorizada, escreva o teste a partir do critério de aceite, com comentário `REQ-NNN`. Use dependência real quando o comportamento de dados importa. Se o teste falhar por comportamento ausente, mantenha-o e encaminhe ao `@implementer` com a tarefa correspondente.

**Passo 5 - Checar mutação e E2E.**
Para testes críticos, confirme que a asserção falha quando o comportamento muda. Para fluxos críticos de UI, explore a aplicação com Playwright, se disponível, e gere o E2E; caso contrário, reporte `NÃO APLICÁVEL` com motivo.

**Passo 6 - Executar gates, validar e registrar.**
Rode os gates declarados e compare cobertura com os limites do projeto. Atualize o catálogo de `TESTING.md`, `checkpoints/test-coverage.yaml` e os `Resultados` de `VERIFICATION.md`. Rode os validadores SDD a partir da raiz e registre comando, data, código de saída e resumo em `Execuções de validadores`. Salve a saída de gates e validadores em `evidence/<AAAA-MM-DD>-<assunto>.md` e liste-a em `evidence/README.md`. Responda com o formato de saída.

## Exemplo de invocação

```text
/verify-quality
/verify-quality feature=001-sala-do-eco escopo=REQ-001,REQ-002,REQ-003
```

Na primeira forma, espere a auditoria de todo pacote em construção. Na segunda, só dos requisitos informados de `.spec/001-sala-do-eco/`. Em ambas, espere uma matriz requisito-teste, testes novos rastreados, gates e validadores executados com resultado real, `TESTING.md`, `VERIFICATION.md` e `checkpoints/test-coverage.yaml` atualizados e lacunas priorizadas por risco.
