# Ordem de execução dos prompts

Este guia mostra em que ordem executar os prompts de [.github/prompts/](./) e o que o harness do repositório faz em cada etapa: hooks, instruções, agentes e skills. Cada prompt faz uma tarefa, e a saída de uma etapa é a entrada da próxima.

Toda especificação fica em `.spec/`, com um pacote `.spec/<NNN>-<funcionalidade>/` por funcionalidade da fonte. Todo pacote tem sempre a mesma estrutura: 13 arquivos em maiúsculas (`SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md`, `ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`) e as pastas `checkpoints/`, `contracts/` e `evidence/`. `/write-ears-spec` cria a estrutura inteira, e cada etapa preenche os arquivos de que é dona. As [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) são autoritativas sobre nomes, etapa dona e completude.

## Como o harness age em cada invocação

Toda execução de prompt passa pelas mesmas camadas, nesta ordem:

| Ordem | Camada | Onde fica | O que faz |
| --- | --- | --- | --- |
| 1 | Hook `sessionStart` | [20-session-context.json](../hooks/20-session-context.json) | Injeta branch, arquivos alterados, especificações em `.spec/` e as regras de `session_context.extra` da [política](../hooks/config/policy.json) |
| 2 | Instruções do repositório | [copilot-instructions.md](../copilot-instructions.md) | Stack, comandos, convenções de IDs e fluxo SDD, sempre carregados |
| 3 | Prompt | `.github/prompts/*.prompt.md` | Seleciona o agente (`agent:`), restringe as ferramentas (`tools:`) e define entradas, passos e saída |
| 4 | Agente | [.github/agents/](../agents/) | Missão, limites e definição de pronto do papel |
| 5 | Passo 0 do prompt | [.github/skills/](../skills/) e [.github/instructions/](../instructions/) | Carrega as skills e instruções explicitamente, inclusive as que o `applyTo` não carregaria sozinho |
| 6 | Hook `preToolUse` | [10-guardrails.json](../hooks/10-guardrails.json) | Nega ou pede confirmação para caminhos protegidos, arquivos de segredo, escrita fora do workspace e comandos destrutivos |
| 7 | Hooks `postToolUse` / `sessionEnd` | [30-audit.json](../hooks/30-audit.json) | Auditoria sem conteúdo sensível em `.github/hooks/.logs/` e contagem de escritas da sessão |
| 8 | Hook `agentStop` | [40-quality-gate.json](../hooks/40-quality-gate.json) | Se `quality_gate.enabled` for `true` e a sessão tiver escrito arquivos, roda `quality_gate.commands` e bloqueia o encerramento quando falham (até `max_blocks` vezes) |

> [!NOTE]
> Quando um hook bloquear ou pedir confirmação, não contorne a regra. Explique qual regra disparou e, se a operação for legítima, proponha o ajuste em [policy.json](../hooks/config/policy.json).

## Visão geral do fluxo

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF","primaryColor":"#FFFFFF","primaryTextColor":"#222222","primaryBorderColor":"#777777","lineColor":"#555555","secondaryColor":"#F2F2F2","tertiaryColor":"#E8E8E8"}}}%%
flowchart TD
  classDef default fill:#FFFFFF,stroke:#777777,color:#222222
  classDef zone fill:#F2F2F2,stroke:#999999,color:#222222
  classDef external fill:#E8E8E8,stroke:#555555,color:#222222

  S0["0. Preparar o harness"]:::zone
  S1["1. /refine-user-stories"]
  S2["2. /write-ears-spec"]
  UI{"Tem interface?"}
  S3["3. /research-ux"]
  S4["4. /validate-spec"]
  S5["5. /plan-architecture"]
  S6["6. /break-down-tasks"]
  S7["7. /implement-task"]
  S8["8. /verify-quality"]
  H["Revisão humana e PR"]:::external

  S0 --> S1 --> S2 --> UI
  UI -- sim --> S3 --> S4
  UI -- não --> S4
  S3 -. candidatos de UI .-> S2
  S4 -. Rascunho com bloqueios .-> S2
  S4 -- Pronto para revisão --> S5 --> S6 --> S7
  S7 -- próxima tarefa --> S7
  S7 --> S8
  S8 -. lacunas e testes vermelhos .-> S7
  S8 -- fase verificada --> H
```

## Etapa 0 - Preparar o harness

Faça uma vez por projeto, antes do primeiro prompt:

- [ ] Preencha os marcadores `<...>` de [copilot-instructions.md](../copilot-instructions.md): nome, objetivo, documento de origem, stack, comandos e limites de cobertura. Os prompts `/plan-architecture`, `/implement-task` e `/verify-quality` param e perguntam enquanto stack ou comandos estiverem como marcadores.
- [ ] Confirme que `python3` está disponível, porque todos os hooks chamam [hook.py](../hooks/scripts/hook.py) e os validadores SDD são scripts Python.
- [ ] Rode `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` a partir da raiz para confirmar que o validador detecta os defeitos do contrato.
- [ ] Revise [policy.json](../hooks/config/policy.json): caminhos protegidos, padrões de segredo e comandos que pedem confirmação.
- [ ] Quando os comandos de lint e testes existirem, ative o quality gate (`quality_gate.enabled: true` e `commands`) para que o `agentStop` bloqueie sessões de construção com gates vermelhos.

## Sequência de execução

`feature=` é opcional em todos os prompts de `.spec/`, exceto `/implement-task`. Sem ele, o prompt processa todo pacote cuja etapa anterior esteja pronta (em `/write-ears-spec`, toda funcionalidade da fonte); com ele, só aquele pacote.

| # | Prompt | Agente | Entrada | Saída | Critério para avançar |
| --- | --- | --- | --- | --- | --- |
| 1 | [/refine-user-stories](refine-user-stories.prompt.md) | `@requirements-engineer` | `fonte=`, `epico=` | Histórias INVEST agrupadas por funcionalidade e perguntas em aberto (no chat ou em `saida=`) | Histórias com fonte e perguntas encaminhadas ao Product Owner |
| 2 | [/write-ears-spec](write-ears-spec.prompt.md) | `@requirements-engineer` | `fonte=` (`feature=` opcional) | Um pacote por funcionalidade com a estrutura completa; `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md` e índices das pastas produzidos; `.spec/README.md`; `CONSTITUTION.md`, se ausente | Todo ID da fonte tem disposição em um pacote; todo requisito tem `origem:`, aceite e verificação planejada |
| 3 | [/research-ux](research-ux.prompt.md) (só com UI) | `@se-ux-ui-designer` | `fonte=` (`feature=` opcional) | `docs/ux/<NNN>-<funcionalidade>-pesquisa.md` por pacote com interface | Candidatos de UI levados de volta a `/write-ears-spec` |
| 4 | [/validate-spec](validate-spec.prompt.md) | `@requirements-engineer` | nenhuma (`feature=` opcional) | Achados por severidade na seção `Validação` de `SPECIFICATION.md` e status por pacote | Pacote em `Pronto para revisão` sem bloqueios em P0 |
| 5 | [/plan-architecture](plan-architecture.prompt.md) | `@software-architect` | nenhuma (`feature=` opcional) | `ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `contracts/`, `checkpoints/spec-to-plan.yaml`, `CODEMAP.md`, ADRs `Proposto` | Todo requisito ativo mapeado a componente em `DESIGN.md` e no checkpoint |
| 6 | [/break-down-tasks](break-down-tasks.prompt.md) | `@software-architect` | nenhuma (`feature=` opcional) | `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`, `checkpoints/plan-to-tasks.yaml`, `checkpoints/test-coverage.yaml` | `CROSS_ANALYSIS.md` sem órfãos e `validate-sdd.py --require-full --strict` executado pelo time com saída `0` |
| 7 | [/implement-task](implement-task.prompt.md) | `@implementer` | `feature=`, `tarefa=` (obrigatórias) | Código, testes, `evidence/` e atualização de `TASKS.md`, `TDD.md` e `VERIFICATION.md` | Gates e validadores executados e tarefa marcada com evidência |
| 8 | [/verify-quality](verify-quality.prompt.md) | `@qa-engineer` | nenhuma (`feature=` e `escopo=` opcionais) | Matriz requisito-teste, testes novos, `evidence/`, `TESTING.md`, `VERIFICATION.md`, `checkpoints/test-coverage.yaml` | Todo P0 coberto por teste que falha com comportamento errado |

## Validação dos artefatos

Execute a partir da raiz e registre comando, data, código de saída e resumo em `VERIFICATION.md` (ou na seção `Validação` de `SPECIFICATION.md` antes da etapa de tarefas), com a saída salva em `evidence/`:

| Comando | Quando |
| --- | --- |
| `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` | Antes de confiar no validador e após mudá-lo |
| `python3 -B .github/scripts/validate-sdd.py` (`--package NNN` para restringir) | Ao fim de cada etapa |
| `python3 -B .github/scripts/validate-sdd.py --require-full --strict` | Antes do handoff para `/implement-task` e em PR |
| `python3 -B .github/scripts/validate-design-diagrams.py` | Sempre que um diagrama mudar |

Os prompts sem ferramenta de execução que escrevem em `.spec/` (`/write-ears-spec`, `/validate-spec`, `/plan-architecture` e `/break-down-tasks`) registram os validadores como `NÃO EXECUTADO (sem ferramenta de execução)`, fazem a verificação manual e listam os comandos para o time. `/implement-task` e `/verify-quality` executam os validadores. `/refine-user-stories` e `/research-ux` não alteram `.spec/`.

## Detalhe por etapa

### 1. Descoberta - `/refine-user-stories`

- **Carrega:** skill `user-story-refine` e instruções de artefatos SDD.
- **Ferramentas:** `read`, `search` e `edit`. Não grava arquivo sem `saida=` e não escreve em `.spec/`.
- **Hooks relevantes:** `preToolUse` nega a leitura de arquivos de segredo e aplica as regras de caminhos protegidos a toda escrita.
- **Saída:** histórias agrupadas pela funcionalidade da fonte, para que a etapa 2 crie um pacote por funcionalidade.
- **Repita** quando o Product Owner responder às perguntas em aberto.

### 2. Especificação - `/write-ears-spec`

- **Escopo:** sem `feature=`, decompõe a fonte e cria um pacote para cada funcionalidade; todo ID da fonte (`RF-`, `RNF-`, `RN-`) recebe disposição em exatamente um pacote. Funcionalidade inteiramente bloqueada também recebe pacote, em `Rascunho`.
- **Carrega:** skills `sdd-requirements-engineer` e `tdd-workflow`, instruções de artefatos SDD e de testes, referência EARS, modelos de artefatos, modelos de FRD e NFRD e quality gates.
- **Ferramentas:** `read`, `search` e `edit`. Não roda comandos.
- **Saída:** a estrutura completa de cada pacote; `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md` e os `README.md` das pastas produzidos em `Rascunho` ou `Pronto para revisão`; os demais arquivos só com cabeçalho `Não iniciado`; o índice `.spec/README.md`; `CONSTITUTION.md`, se ausente. Nunca `Aprovado` sem evidência humana.
- **Repita** para incorporar os candidatos de UI da etapa 3 ou os achados da etapa 4.

### 3. Pesquisa de UX - `/research-ux` (condicional)

- **Quando:** algum pacote tem interface (terminal, web ou mobile). Sem interface, pule para a etapa 4.
- **Escopo:** sem `feature=`, todo pacote com interface; os pacotes sem interface são listados como `NÃO APLICÁVEL`.
- **Carrega:** skill `user-story-refine`, instruções de frontend, de plataforma frontend e de artefatos SDD.
- **Handoff:** os requisitos de UI candidatos voltam para `/write-ears-spec`, que atribui os IDs em `SPECIFICATION.md`.

### 4. Validação - `/validate-spec`

- **Escopo:** sem `feature=`, todo pacote com `SPECIFICATION.md` em `Rascunho` ou `Pronto para revisão`, além da cobertura global da fonte e do índice.
- **Carrega:** skills SDD e TDD, quality gates, catálogo de antipadrões, referência EARS e modelos de artefatos, FRD e NFRD.
- **Interação:** faz no máximo três perguntas de bloqueio, uma por vez. Responda no chat; a resposta vira fonte `SRC-###` em `SOURCE_TRACEABILITY.md`.
- **Saída:** achados e gates na seção `Validação` de `SPECIFICATION.md`. Com bloqueio em P0 o pacote fica `Rascunho` e volta à etapa 2; sem bloqueios, segue para a etapa 5.

### 5. Design - `/plan-architecture`

- **Escopo:** sem `feature=`, todo pacote com `SPECIFICATION.md` em `Pronto para revisão` ou `Aprovado`.
- **Pré-condição do harness:** stack e comandos preenchidos em `copilot-instructions.md`.
- **Carrega:** skill SDD, instruções de artefatos SDD, padrão de documentos e Mermaid e modelos de artefatos e de NFRD.
- **Saída:** `ANALYSIS.md`, `DESIGN.md` (14 visões do portfólio) e `DECISIONS.md` em `Planejado`, `contracts/manifest.yaml` e contratos, `checkpoints/spec-to-plan.yaml`, `CODEMAP.md` e, somente para decisões estruturais, ADRs `Proposto` em `docs/adr/`.

### 6. Tarefas - `/break-down-tasks`

- **Escopo:** sem `feature=`, todo pacote com `DESIGN.md` em `Planejado`.
- **Carrega:** skills SDD e TDD, instruções de artefatos SDD e de testes, modelos de artefatos e padrão de documentos e Mermaid.
- **Saída:** `TASKS.md` com IDs `T001...`, marcadores `[S]`/`[P]`, grafo e registro de execução com `0 de N`; `TESTING.md`, `TDD.md` (um ciclo por AC), `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`, `checkpoints/plan-to-tasks.yaml` e `checkpoints/test-coverage.yaml`.
- **Handoff:** o time executa `validate-sdd.py --require-full --strict` antes da etapa 7; se não executar, `/implement-task` o executa no Passo 1.
- **Repita** sempre que `SPECIFICATION.md`, `DESIGN.md` ou `contracts/` mudarem.

### 7. Construção - `/implement-task` (em ciclo)

- **Uma invocação por tarefa ou par RED/GREEN**, na ordem do grafo de `TASKS.md`. `feature=` e `tarefa=` são obrigatórios.
- **Carrega:** skill `tdd-workflow`, instruções de testes e de artefatos SDD, modelos de artefatos e, com UI, instruções de frontend e o artefato de `docs/ux/`.
- **Saída:** código, testes, evidência em `evidence/`, registro em `TASKS.md`, estado do ciclo em `TDD.md` e resultados e execuções de validadores em `VERIFICATION.md`.
- **Ferramentas:** incluem `execute`. Aqui o harness atua mais:
  - `preToolUse` pede confirmação para `git push`, `rm -rf`, `--no-verify` e outros comandos da política. Também nega a leitura de arquivos de segredo, pede confirmação para escrevê-los, nega escrita em `.git/` e pede confirmação para escrita em `.github/hooks/` e `.github/workflows/`.
  - `postToolUse` conta as escritas da sessão.
  - `agentStop` roda o quality gate, se ativo, e impede o encerramento com lint ou testes vermelhos.
- **Commits:** o prompt sugere a sequência `test:` → `feat:` → `refactor:` e só commita quando o time pede.

### 8. Qualidade - `/verify-quality`

- **Quando:** em paralelo à construção ou ao fim de cada fase de `TASKS.md`.
- **Escopo:** sem `feature=`, todo pacote com ao menos uma tarefa concluída com evidência; `escopo=` exige `feature=`.
- **Carrega:** instruções de testes e de artefatos SDD, skills TDD e SDD, quality gates e modelos de artefatos.
- **Ferramentas:** incluem `execute` e `playwright/*` para E2E de fluxos críticos de UI.
- **Saída:** testes novos, evidência em `evidence/`, `TESTING.md`, `VERIFICATION.md` e `checkpoints/test-coverage.yaml` atualizados, com os validadores executados.
- **Handoff:** testes vermelhos por comportamento ausente voltam para `/implement-task`; lacunas sem tarefa viram proposta para `/break-down-tasks`.

## Exemplo de sessão completa

```text
/refine-user-stories fonte=requisitos/requisitos.md epico="Fase 1 - versão no terminal"
/write-ears-spec fonte=requisitos/requisitos.md
/research-ux fonte=requisitos/requisitos.md
/write-ears-spec fonte=docs/ux/001-sala-do-eco-pesquisa.md feature=001-sala-do-eco
/validate-spec
/plan-architecture
/break-down-tasks
/implement-task feature=001-sala-do-eco tarefa=T001,T002
/implement-task feature=001-sala-do-eco tarefa=T003,T004
/verify-quality
```

A primeira invocação de `/write-ears-spec` cria todos os pacotes da fonte. `/validate-spec`, `/plan-architecture`, `/break-down-tasks` e `/verify-quality` sem `feature=` processam todo pacote cuja etapa anterior está pronta; acrescente `feature=` para restringir a um pacote. `/implement-task` sempre recebe `feature=` e `tarefa=`.

Prefira uma sessão de chat nova por etapa. Assim o `sessionStart` injeta o estado atualizado de `.spec/`, e o contador de escritas usado pelo quality gate vale só para a etapa atual.

## Regras que valem para todas as etapas

- Não pule etapas para a frente. Código sem requisito em `SPECIFICATION.md` é rejeitado pelo `@implementer`.
- Todo pacote mantém os 13 arquivos e as 3 pastas; os nomes em minúsculas (`spec.md`, `plan.md`, `tasks.md`, `frd.md`, `nfrd.md`) são proibidos.
- Todo arquivo produzido contém todas as seções do seu modelo; seção sem conteúdo fica `NÃO APLICÁVEL: <motivo>`, sem conteúdo inventado.
- Status só avança com evidência: `Não iniciado` → `Rascunho` → `Pronto para revisão` → `Aprovado` (decisão humana) → `Implementado` → `Verificado`. Arquivos de design e de tarefas ficam `Planejado` ao serem produzidos.
- Perguntas em aberto continuam abertas até o Product Owner responder; nenhum prompt as resolve sozinho.
- Nenhum prompt registra segredos, credenciais ou dados pessoais em artefatos, logs ou evidências.
