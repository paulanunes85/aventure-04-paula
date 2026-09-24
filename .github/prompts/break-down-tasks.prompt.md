---
name: "break-down-tasks"
description: "Quebra o plan.md em .spec/<NNN>-<funcionalidade>/tasks.md completo, com tarefas RED/GREEN ordenadas por dependência, marcadores [S]/[P], rastreio REQ/AC, mapa de testes, checklist, verificação planejada e análise cruzada frd-nfrd-spec-plan-tasks."
argument-hint: "feature=NNN-nome-da-funcionalidade"
agent: "software-architect"
tools: ["read", "search", "edit"]
---
# /break-down-tasks

## Objetivo

Transformar o plano aprovado em tarefas pequenas, ordenadas por dependência e rastreáveis, em que cada comportamento começa por um teste que falha. Antes de entregar, detectar divergências entre `spec.md`, `plan.md` e `tasks.md`.

## Quando invocar

No fim da Etapa 3, depois de `/plan-architecture` e antes de `/implement-task`. Reinvoque quando `spec.md` ou `plan.md` mudarem.

> [!NOTE]
> Não use este prompt para mudar o design (`/plan-architecture`) nem para executar tarefas (`/implement-task`). Tarefas ficam desmarcadas até existir evidência de execução.

## Pré-condições

- `spec.md` está `Pronto para revisão` ou `Aprovado` com evidência
- `plan.md` está `Planejado` e mapeia todo requisito ativo
- Comandos de teste e build estão declarados em [copilot-instructions.md](../copilot-instructions.md)

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>`
- Prioridade de entrega entre requisitos P0/P1, se o plano não definir
- Restrições de paralelismo do time (duplas, áreas de código)

## O que vou fazer

- Carregar SDD/TDD e as instruções aplicáveis antes de escrever
- Derivar tarefas do plano em fases, com ID estável `T001`, `T002`...
- Emparelhar cada comportamento em tarefas `RED` (teste que falha) e `GREEN` (mínimo que passa), com `REFACTOR` quando o plano justificar
- Marcar `[S]` para sequencial e `[P]` apenas quando dependências e superfície de mudança forem independentes
- Registrar em cada tarefa: referência ao plano, requisitos e AC rastreados, arquivos previstos e aceite
- Montar grafo de dependências, mapa de testes, tabela de verificação, gate de conclusão e registro de execução vazio
- Fazer a análise cruzada e reportar órfãos e divergências

## O que NÃO vou fazer

- Criar tarefa sem requisito ou requisito ativo sem tarefa
- Marcar qualquer tarefa `[x]` ou preencher evidência de execução
- Usar `[P]` em tarefas que tocam os mesmos arquivos ou dependem uma da outra
- Criar tarefas horizontais por camada sem comportamento verificável
- Alterar `spec.md` ou `plan.md`; divergências voltam ao responsável
- Escrever código ou testes

## Formato de saída

Siga a seção de `tasks.md` dos [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) e o contrato de tarefas do [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md):

```markdown
## Fase 1
- [ ] **T001 [S] [Plano:P1.1] RED** Adicionar teste que falha para <comportamento>. Rastreia REQ-001 / AC-REQ-001-01.
  - Arquivos: `<caminho do teste>`.
  - Aceite: TST-C001 falha pela ausência do comportamento.

- [ ] **T002 [S] [Plano:P1.1] GREEN** Implementar o mínimo para <comportamento>. Rastreia REQ-001 / AC-REQ-001-01.
  - Depende de: T001.
  - Arquivos: `<caminho da implementação>`, `<caminho do teste>`.
  - Aceite: TST-C001 passa com evidência retida.
```

Feche com o resultado da análise cruzada:

| Verificação | Resultado | Evidência ou achado |
| --- | --- | --- |
| Todo requisito ativo tem tarefa | PASS/FAIL | <IDs faltantes> |
| Toda tarefa rastreia requisito | PASS/FAIL | <tarefas órfãs> |
| Todo requisito está em `plan.md` | PASS/FAIL | <IDs> |
| Grafo e lista concordam | PASS/FAIL | <divergências> |
| `[P]` sem conflito de arquivos | PASS/FAIL | <pares conflitantes> |

## Regras de SDD e rastreabilidade

- Leia as instruções SDD antes de editar `.spec/**`.
- RED precede GREEN para o mesmo comportamento; um ciclo planejado não prova que testes rodaram.
- Cada tarefa entrega um comportamento revisável em um PR pequeno.
- `[x]` exige evidência de aceite completa e entrada no registro de execução datado; este prompt não marca tarefas.
- O grafo de dependências usa o tema Mermaid claro universal e bate com a lista.
- Requisitos bloqueados geram tarefa de desbloqueio com responsável, não tarefa de implementação escondida.

## Definição de pronto

- [ ] SDD/TDD e as instruções aplicáveis foram carregados antes da escrita
- [ ] Toda tarefa tem ID estável, marcador `[S]`/`[P]`, referência ao plano, REQ/AC, arquivos e aceite
- [ ] Todo comportamento tem par RED/GREEN
- [ ] Grafo, mapa de testes, verificação, checklist, análise cruzada, gate de conclusão e registro de execução estão presentes e consistentes
- [ ] Nenhuma tarefa está marcada como concluída
- [ ] A análise cruzada não tem `FAIL` sem achado encaminhado

## Corpo do prompt

Você é `@software-architect`. Quebre o plano em tarefas rastreáveis e test-first, sem executar nada.

**Passo 0 - Carregar SDD, TDD e instruções.**
Leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) e as [instruções de testes](../instructions/tests.instructions.md), carregue as skills [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e [tdd-workflow](../skills/tdd-workflow/SKILL.md) e leia o [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md).

**Passo 1 - Ler spec e plano.**
Liste requisitos ativos, AC, componentes e fases do plano. Requisito sem componente ou bloqueado é registrado como achado.

**Passo 2 - Derivar tarefas.**
Para cada comportamento, crie o par RED/GREEN seguindo a ordem da skill TDD: caso não trivial mais simples primeiro, depois variações, bordas e erros. Inclua tarefas de gate (lint, build, cobertura) quando o plano pedir.

**Passo 3 - Ordenar e paralelizar.**
Defina dependências e marque `[P]` apenas quando não houver dependência nem arquivo compartilhado.

**Passo 4 - Mapear testes e verificação.**
Atribua IDs de teste `TST-...` e verificação `VER-NNN` ligados a REQ/AC, com método, resultado esperado e status `planejado`.

**Passo 5 - Montar o artefato.**
Escreva todas as seções de `TASKS`, `CHECKLIST` e `CROSS_ANALYSIS` dos modelos: metadados, gate pré-implementação, regras de execução, grafo, mapa de testes, fases, verificação, desvios, checklist, análise cruzada, gate de conclusão, registro de execução com `0 de N` tarefas concluídas e histórico de mudanças.

**Passo 6 - Analisar e gravar.**
Execute a análise cruzada entre `frd.md`, `nfrd.md`, `spec.md`, `plan.md` e `tasks.md` e registre cada verificação. Grave `.spec/<NNN>-<funcionalidade>/tasks.md` e indique a primeira tarefa desbloqueada para `/implement-task`.

## Exemplo de invocação

```text
/break-down-tasks feature=001-sala-do-eco
```

Espere um `tasks.md` com pares RED/GREEN ordenados, grafo de dependências, mapa de testes e uma análise cruzada sem órfãos.
