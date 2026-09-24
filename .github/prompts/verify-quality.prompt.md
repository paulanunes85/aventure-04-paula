---
name: "verify-quality"
description: "Audita a qualidade de uma funcionalidade: matriz REQ-teste, lacunas de cobertura por risco, testes faltantes escritos a partir da spec, E2E com Playwright quando aplicável e gates de CI executados, registrando resultados em tasks.md."
argument-hint: "feature=NNN-nome-da-funcionalidade [escopo=REQ-001,REQ-002]"
agent: "qa-engineer"
tools: ["read", "search", "edit", "execute", "playwright/*"]
---
# /verify-quality

## Objetivo

Provar que o código entrega o comportamento especificado. Cruzar requisitos e testes, priorizar lacunas por risco, escrever os testes que faltam a partir de `spec.md` e executar os gates, sem fabricar um pipeline verde.

## Quando invocar

Na Etapa 4, em paralelo à implementação ou ao fim de uma fase de `tasks.md`, e antes de declarar a funcionalidade verificada.

> [!NOTE]
> Não use este prompt para escrever código de produção (`/implement-task`) nem para corrigir requisitos (`/validate-spec`). Testes que falham por comportamento ausente são entregues ao `@implementer`.

## Pré-condições

- `spec.md` e `tasks.md` da funcionalidade existem
- Framework de testes e comandos com cobertura estão declarados em [copilot-instructions.md](../copilot-instructions.md)
- Para E2E, a aplicação pode ser executada localmente

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>`
- `escopo=<REQ-IDs>` quando a auditoria for parcial
- Riscos conhecidos ou incidentes recentes, se houver

## O que vou fazer

- Carregar as instruções de testes, a skill TDD e a skill SDD antes de testar
- Inventariar REQ/AC, testes existentes com comentário `REQ-NNN` e o relatório de cobertura atual
- Montar a matriz requisito-teste e classificar cada requisito como coberto, parcial ou descoberto
- Priorizar lacunas por risco: P0 primeiro, depois caminhos de erro, limites e exemplos do negócio
- Escrever testes faltantes a partir dos critérios de aceite, parametrizando tabelas de exemplos
- Checar com mentalidade de mutação se cada teste falha quando o comportamento muda
- Explorar fluxos críticos de UI com Playwright quando o servidor MCP estiver disponível e gerar o E2E correspondente
- Executar os gates e registrar resultados reais na tabela `Verificação` de `tasks.md`

## O que NÃO vou fazer

- Alterar código de produção para fazer um teste passar
- Pular, marcar como `skip` ou enfraquecer asserções para forçar o verde
- Perseguir percentual de cobertura em vez de risco
- Fazer mock de dependência cujo comportamento de dados importa
- Inventar valores esperados ausentes de `spec.md` ou da fonte em `origem:`
- Marcar requisito como `Verificado` sem execução registrada

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

### Lacunas por risco
1. <REQ-ID> - <lacuna> - <ação e responsável>
```

## Regras de SDD e rastreabilidade

- Todo teste de requisito tem comentário `REQ-NNN` e nome que descreve comportamento.
- Um teste só merece existir se falhar com comportamento errado; asserções que sempre passam são reescritas.
- Pirâmide: muitos unitários rápidos, menos de integração, poucos E2E para fluxos críticos.
- Instabilidade (tempo, aleatoriedade, ordem, rede) é isolada e reportada, não mascarada com retry.
- Resultados vão para a tabela `Verificação` de `tasks.md` com data e comando; lacunas vão para `Desvios` ou viram tarefa proposta.

## Definição de pronto

- [ ] Instruções de testes e skills TDD/SDD foram carregadas antes de testar
- [ ] Todo requisito em escopo aparece na matriz com status e risco
- [ ] Todo P0 tem pelo menos um teste que falha com comportamento errado
- [ ] Testes novos citam `REQ-NNN` e testes vermelhos foram encaminhados ao `@implementer`
- [ ] Os gates foram executados e os resultados reais estão reportados e registrados em `tasks.md`
- [ ] Nenhum teste foi pulado ou enfraquecido e lacunas estão reportadas por risco

## Corpo do prompt

Você é `@qa-engineer`. Prove o comportamento especificado com testes que falham em bugs reais.

**Passo 0 - Carregar skills e instruções.**
Leia as [instruções de testes](../instructions/tests.instructions.md), carregue as skills [tdd-workflow](../skills/tdd-workflow/SKILL.md) e [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e leia os [quality gates](../skills/sdd-requirements-engineer/references/quality-gates.md) e o [copilot-instructions.md](../copilot-instructions.md). Se os comandos ainda forem marcadores `<...>`, pare e pergunte ao time.

**Passo 1 - Inventariar.**
Leia `spec.md` e `tasks.md`. Busque testes que citam cada `REQ-NNN` e rode a suíte com cobertura para obter o estado atual.

**Passo 2 - Montar a matriz.**
Classifique cada requisito em escopo como coberto, parcial ou descoberto, com prioridade e risco.

**Passo 3 - Priorizar lacunas.**
Ordene por risco: P0 descobertos, caminhos de erro, limites e exemplos do negócio sem teste.

**Passo 4 - Escrever testes.**
Para cada lacuna priorizada, escreva o teste a partir do critério de aceite, com comentário `REQ-NNN`. Use dependência real quando o comportamento de dados importa. Se o teste falhar por comportamento ausente, mantenha-o e encaminhe ao `@implementer` com a tarefa correspondente.

**Passo 5 - Checar mutação e E2E.**
Para testes críticos, confirme que a asserção falha quando o comportamento muda. Para fluxos críticos de UI, explore a aplicação com Playwright, se disponível, e gere o E2E; caso contrário, reporte `NÃO APLICÁVEL` com motivo.

**Passo 6 - Executar gates e registrar.**
Rode os gates declarados, compare cobertura com os limites do projeto e registre resultados datados em `tasks.md`. Responda com o formato de saída.

## Exemplo de invocação

```text
/verify-quality feature=001-sala-do-eco escopo=REQ-001,REQ-002,REQ-003
```

Espere uma matriz requisito-teste, testes novos rastreados, gates executados com resultado real e lacunas priorizadas por risco.
