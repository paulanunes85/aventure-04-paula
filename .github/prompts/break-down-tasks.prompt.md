---
name: "break-down-tasks"
description: "Quebra o DESIGN.md de cada pacote planejado em .spec/ (ou só o de feature=) em TASKS.md, TESTING.md, TDD.md, CHECKLIST.md, CROSS_ANALYSIS.md, VERIFICATION.md e nos checkpoints plan-to-tasks.yaml e test-coverage.yaml, com tarefas RED/GREEN ordenadas por dependência, marcadores [S]/[P], rastreio REQ/AC e análise cruzada entre todos os arquivos do pacote."
argument-hint: "[feature=NNN-nome-da-funcionalidade]"
agent: "software-architect"
tools: ["read", "search", "edit"]
---
# /break-down-tasks

## Objetivo

Transformar o design planejado em tarefas pequenas, ordenadas por dependência e rastreáveis, em que cada comportamento começa por um teste que falha. Por pacote, esta etapa produz `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`, `checkpoints/plan-to-tasks.yaml` e `checkpoints/test-coverage.yaml`. Sem `feature=`, processa todo pacote cujo `DESIGN.md` esteja `Planejado`; com `feature=`, só aquele. Antes de entregar, detectar divergências entre todos os arquivos do pacote.

## Quando invocar

No fim da Etapa 3, depois de `/plan-architecture` e antes de `/implement-task`. Reinvoque quando `SPECIFICATION.md`, `DESIGN.md` ou `contracts/` mudarem.

> [!NOTE]
> Não use este prompt para mudar o design (`/plan-architecture`) nem para executar tarefas (`/implement-task`). Tarefas ficam desmarcadas até existir evidência de execução.

## Pré-condições

- Ao menos um pacote em `.spec/` tem `DESIGN.md` em `Planejado` (com `feature=`, o pacote informado)
- O `SPECIFICATION.md` desse pacote está `Pronto para revisão` ou `Aprovado` com evidência
- `DESIGN.md` e `checkpoints/spec-to-plan.yaml` mapeiam todo requisito ativo
- Comandos de teste e build estão declarados em [copilot-instructions.md](../copilot-instructions.md)

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>` (opcional): restringe a quebra a um pacote; sem ele, todos os pacotes planejados são processados
- Prioridade de entrega entre requisitos P0/P1 e entre pacotes, se o design não definir
- Restrições de paralelismo do time (duplas, áreas de código)

## O que vou fazer

- Carregar SDD/TDD, as instruções aplicáveis e os modelos antes de escrever
- Selecionar os pacotes planejados pelo índice `.spec/README.md` e listar os demais com o motivo
- Derivar tarefas das fases de `DESIGN.md`, com ID estável `T001`, `T002`...
- Emparelhar cada comportamento em tarefas `RED` (teste que falha) e `GREEN` (mínimo que passa), com `REFACTOR` quando o design justificar
- Marcar `[S]` para sequencial e `[P]` apenas quando dependências e superfície de mudança forem independentes
- Registrar em cada tarefa: referência ao plano, requisitos e AC rastreados, arquivos previstos e aceite
- Escrever em `TASKS.md` o gate pré-implementação, as regras de execução, o grafo, as fases, os desvios, o gate de conclusão e o registro de execução com `0 de N`
- Escrever em `TESTING.md` a estratégia, o catálogo `TST-...` e o mapa de testes
- Escrever em `TDD.md` um ciclo RED/GREEN/REFACTOR para cada critério de aceite
- Escrever `CHECKLIST.md` e, em `VERIFICATION.md`, as verificações `VER-NNN` planejadas e a tabela de execuções de validadores
- Escrever `checkpoints/plan-to-tasks.yaml` e `checkpoints/test-coverage.yaml` e atualizar `checkpoints/README.md`
- Fazer a análise cruzada em `CROSS_ANALYSIS.md` e reportar órfãos e divergências

## O que NÃO vou fazer

- Criar tarefa sem requisito ou requisito ativo sem tarefa
- Marcar qualquer tarefa `[x]` ou preencher evidência de execução
- Usar `[P]` em tarefas que tocam os mesmos arquivos ou dependem uma da outra
- Criar tarefas horizontais por camada sem comportamento verificável
- Alterar `SPECIFICATION.md`, `DESIGN.md` ou `contracts/`; divergências voltam ao responsável
- Criar arquivos com os nomes proibidos em minúsculas (`tasks.md`, `plan.md`)
- Escrever código ou testes
- Declarar validadores executados; sem ferramenta de execução, eles ficam `NÃO EXECUTADO (sem ferramenta de execução)`

## Formato de saída

Siga os modelos `TASKS`, `TESTING`, `TDD`, `CHECKLIST`, `CROSS_ANALYSIS`, `VERIFICATION` e `Checkpoints` dos [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) e o contrato de tarefas do [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md). Em `TASKS.md`:

```markdown
## Fase 1
- [ ] **T001 [S] [Plano:P1.1] RED** Adicionar teste que falha para <comportamento>. Rastreia REQ-001 / AC-REQ-001-01.
  - Arquivos: `<caminho do teste>`.
  - Aceite: TST-C001 falha pela ausência do comportamento.

- [ ] **T002 [S] [Plano:P1.1] GREEN** Implementar o mínimo para <comportamento>. Rastreia REQ-001 / AC-REQ-001-01.
  - Depende de: T001.
  - Arquivos: `<caminho da implementação>`, `<caminho do teste>`.
  - Aceite: TST-C001 passa com evidência em `evidence/`.
```

Em `TDD.md`, um ciclo por critério de aceite:

| AC-ID | Teste | Entrada | Por que falha antes | Resultado esperado | RED | GREEN | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AC-REQ-001-01 | TST-C001 | <entrada> | <comportamento ausente> | <saída> | T001 | T002 | planejado |

Feche com o resultado da análise cruzada, também registrado em `CROSS_ANALYSIS.md`:

| Verificação | Resultado | Evidência ou achado |
| --- | --- | --- |
| Todo requisito ativo tem tarefa | PASS/FAIL | <IDs faltantes> |
| Toda tarefa rastreia requisito | PASS/FAIL | <tarefas órfãs> |
| Todo requisito está em `DESIGN.md` e nos checkpoints | PASS/FAIL | <IDs> |
| Todo AC tem ciclo em `TDD.md` e teste em `TESTING.md` | PASS/FAIL | <IDs> |
| Grafo, lista e `plan-to-tasks.yaml` concordam | PASS/FAIL | <divergências> |
| `[P]` sem conflito de arquivos | PASS/FAIL | <pares conflitantes> |
| IDs, contagens e status concordam entre arquivos e índice | PASS/FAIL | <achados> |

## Regras de SDD e rastreabilidade

- Leia as instruções SDD antes de editar `.spec/**`.
- Todo arquivo produzido contém todas as seções do seu modelo, na ordem do modelo; seções sem conteúdo ficam `NÃO APLICÁVEL: <motivo>`.
- RED precede GREEN para o mesmo comportamento; um ciclo planejado em `TDD.md` não prova que testes rodaram.
- Cada tarefa entrega um comportamento revisável em um PR pequeno.
- `[x]` exige evidência de aceite em `evidence/` e entrada no registro de execução datado; este prompt não marca tarefas.
- O grafo de dependências usa o tema Mermaid claro universal e bate com a lista e com `checkpoints/plan-to-tasks.yaml`.
- Requisitos bloqueados geram tarefa de desbloqueio com responsável, não tarefa de implementação escondida.
- Este prompt não tem ferramenta de execução: registre os validadores em `VERIFICATION.md` (`Execuções de validadores`) como `NÃO EXECUTADO (sem ferramenta de execução)`, faça a verificação manual das instruções SDD e liste para o time, a partir da raiz, `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'`, `python3 -B .github/scripts/validate-sdd.py`, `python3 -B .github/scripts/validate-sdd.py --require-full --strict` (obrigatório antes do handoff para `/implement-task`) e `python3 -B .github/scripts/validate-design-diagrams.py`, com a saída salva em `evidence/<AAAA-MM-DD>-validate-sdd.md`.

## Definição de pronto

- [ ] SDD/TDD, as instruções aplicáveis e os modelos foram carregados antes da escrita
- [ ] Todo pacote em escopo tem `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`, `checkpoints/plan-to-tasks.yaml` e `checkpoints/test-coverage.yaml` com todas as seções dos modelos
- [ ] Toda tarefa tem ID estável, marcador `[S]`/`[P]`, referência ao plano, REQ/AC, arquivos e aceite
- [ ] Todo comportamento tem par RED/GREEN e todo AC tem ciclo em `TDD.md`
- [ ] Grafo, mapa de testes, verificação, checklist, análise cruzada, gate de conclusão, registro de execução e checkpoints estão presentes e consistentes
- [ ] Nenhuma tarefa está marcada como concluída
- [ ] A análise cruzada não tem `FAIL` sem achado encaminhado
- [ ] Os validadores estão em `VERIFICATION.md` como `NÃO EXECUTADO` com os comandos, incluindo `--require-full --strict` antes do handoff

## Corpo do prompt

Você é `@software-architect`. Quebre o design em tarefas rastreáveis e test-first, sem executar nada.

**Passo 0 - Carregar SDD, TDD e instruções.**
Leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) e as [instruções de testes](../instructions/tests.instructions.md), carregue as skills [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e [tdd-workflow](../skills/tdd-workflow/SKILL.md) e leia os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) e o [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md).

**Passo 1 - Selecionar pacotes e ler especificação e design.**
Sem `feature=`, liste os pacotes do índice `.spec/README.md` e selecione os que têm `DESIGN.md` em `Planejado`; registre os demais com o motivo. Com `feature=`, só aquele. Para cada pacote, leia `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md`, `ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `contracts/` e `checkpoints/spec-to-plan.yaml`. Liste requisitos ativos, AC, componentes e fases. Requisito sem componente ou bloqueado é registrado como achado.

**Passo 2 - Derivar tarefas.**
Para cada comportamento, crie o par RED/GREEN seguindo a ordem da skill TDD: caso não trivial mais simples primeiro, depois variações, bordas e erros. Inclua tarefas de gate (lint, build, cobertura) quando o design pedir.

**Passo 3 - Ordenar e paralelizar.**
Defina dependências, inclusive entre pacotes, e marque `[P]` apenas quando não houver dependência nem arquivo compartilhado.

**Passo 4 - Mapear testes, ciclos e verificação.**
Atribua IDs de teste `TST-...` em `TESTING.md`, um ciclo por AC em `TDD.md` e verificações `VER-NNN` em `VERIFICATION.md`, ligados a REQ/AC, com método, resultado esperado e status `planejado`.

**Passo 5 - Montar os artefatos.**
Escreva todas as seções de `TASKS.md` (metadados, gate pré-implementação, regras de execução, grafo, fases, desvios, gate de conclusão, registro de execução com `0 de N` tarefas concluídas e histórico), `TESTING.md`, `TDD.md`, `CHECKLIST.md` e `VERIFICATION.md`. Escreva `checkpoints/plan-to-tasks.yaml` e `checkpoints/test-coverage.yaml` com todo ID ativo e atualize `checkpoints/README.md`.

**Passo 6 - Analisar e gravar.**
Execute a análise cruzada entre `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md`, `DESIGN.md`, `TASKS.md`, `TESTING.md`, `TDD.md`, `VERIFICATION.md` e os checkpoints, e registre cada verificação em `CROSS_ANALYSIS.md`. Registre os validadores como `NÃO EXECUTADO (sem ferramenta de execução)` e liste os comandos para o time. Grave os arquivos como `Planejado`, atualize o status no índice `.spec/README.md` e indique, por pacote, a primeira tarefa desbloqueada para `/implement-task`.

## Exemplo de invocação

```text
/break-down-tasks
/break-down-tasks feature=001-sala-do-eco
```

Na primeira forma, espere as tarefas de todo pacote planejado. Na segunda, só de `.spec/001-sala-do-eco/`. Em ambas, espere `TASKS.md` com pares RED/GREEN ordenados e grafo, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `VERIFICATION.md`, os checkpoints e um `CROSS_ANALYSIS.md` sem órfãos.
