---
name: "implement-task"
description: "Implementa uma única tarefa de .spec/<NNN>-<funcionalidade>/tasks.md com TDD red-green-refactor, comentários REQ-NNN, gates do projeto executados e evidência datada no registro de execução."
argument-hint: "feature=NNN-nome-da-funcionalidade tarefa=T001[,T002]"
agent: "implementer"
tools: ["read", "search", "edit", "execute"]
---
# /implement-task

## Objetivo

Entregar exatamente uma tarefa (ou um par RED/GREEN) de `tasks.md` como código funcionando e testado, rastreável ao requisito, com os gates do projeto executados e a evidência registrada. Nada além da tarefa em escopo.

## Quando invocar

Na Etapa 4 (construção), para a próxima tarefa desbloqueada indicada por `/break-down-tasks`. Uma invocação por tarefa ou par.

> [!NOTE]
> Não use este prompt para planejar (`/plan-architecture`), criar tarefas (`/break-down-tasks`) ou auditar cobertura (`/verify-quality`). Pedido sem `REQ-NNN` volta com pergunta sobre critérios de aceite.

## Pré-condições

- `tasks.md` existe e as dependências da tarefa estão concluídas com evidência
- Stack, comandos de lint, typecheck, testes com cobertura e build estão preenchidos em [copilot-instructions.md](../copilot-instructions.md)
- Os requisitos rastreados pela tarefa não estão bloqueados

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>`
- `tarefa=<T001>` ou o par `T001,T002`
- Decisões pendentes que afetem a tarefa, se houver

## O que vou fazer

- Carregar a skill TDD e as instruções de testes, SDD e (se houver UI) frontend antes de codar
- Ler a tarefa, os REQ/AC rastreados em `spec.md`, os componentes em `plan.md`, o `CODEMAP.md` e o código existente
- RED: escrever o menor teste que falha, com comentário `REQ-NNN`, executá-lo e confirmar que falha pelo motivo certo
- GREEN: escrever o mínimo de código de produção que faz o teste passar
- REFACTOR: melhorar o design com a suíte verde
- Executar os gates declarados (lint, typecheck, testes com cobertura, build) e registrar o resultado real
- Atualizar `tasks.md`: marcar `[x]` somente com evidência e acrescentar a entrada datada no registro de execução
- Sugerir a sequência de commits da skill TDD, sem commitar salvo pedido do time

## O que NÃO vou fazer

- Implementar outra tarefa, funcionalidade extra ou refatoração fora do escopo
- Escrever código de produção sem teste falhando antes
- Adicionar dependência, framework ou serviço fora de `copilot-instructions.md` sem ADR
- Pular, enfraquecer ou desativar testes, ou adicionar `any`/supressão de lint sem justificativa
- Criar imports que cruzem fronteiras de contexto do plano
- Inventar regra para preencher lacuna; exponho a pergunta
- Registrar segredos ou dados pessoais em código, logs ou evidências
- Declarar gate aprovado sem ter executado o comando

## Formato de saída

```markdown
## Resultado da tarefa T001

- Requisitos: REQ-001 / AC-REQ-001-01
- RED: `<arquivo de teste>` falhou com `<mensagem resumida>` (comando: `<comando>`)
- GREEN: `<arquivo de produção>`; teste passou (comando: `<comando>`)
- REFACTOR: <melhoria ou nenhuma>
- Gates:
  | Gate | Comando | Resultado |
  | --- | --- | --- |
  | Lint | `<comando>` | PASS/FAIL/NÃO EXECUTADO (motivo) |
  | Typecheck | `<comando>` | PASS/FAIL/NÃO APLICÁVEL |
  | Testes + cobertura | `<comando>` | PASS/FAIL - <linhas>% / <branches>% |
  | Build | `<comando>` | PASS/FAIL/NÃO APLICÁVEL |
- tasks.md: T001 marcada | não marcada (<motivo>)
- Commits sugeridos: `test: add failing test for REQ-001` -> `feat: make REQ-001 pass` -> `refactor: <melhoria>`
- Pendências: <perguntas ou bloqueios, ou nenhuma>
```

## Regras de SDD e rastreabilidade

- Todo teste que verifica um requisito cita o ID em comentário, conforme as instruções de testes.
- Cada unidade de regra de negócio recebe teste de caminho feliz e de erro.
- O vermelho vale apenas se falhar pela ausência do comportamento, não por sintaxe, import ou configuração.
- Evidência é saída real de comando, resumida e sem dados sensíveis; plano não é evidência.
- Desvio entre tarefa e realidade vai para a tabela `Desvios` de `tasks.md`, não é corrigido em silêncio.

## Definição de pronto

- [ ] Skill TDD e instruções aplicáveis foram carregadas antes de codar
- [ ] O vermelho foi observado e confirmado pelo motivo certo antes do código de produção
- [ ] O código atende exatamente ao REQ/AC da tarefa, com comentário de rastreabilidade
- [ ] Os gates declarados foram executados e seus resultados reais estão reportados
- [ ] Nenhum teste foi pulado ou enfraquecido e nenhuma fronteira de contexto foi cruzada
- [ ] `tasks.md` tem a tarefa marcada somente com evidência e a entrada datada no registro

## Corpo do prompt

Você é `@implementer`. Implemente uma única tarefa com TDD estrito e evidência real.

**Passo 0 - Carregar skill e instruções.**
Carregue a skill [tdd-workflow](../skills/tdd-workflow/SKILL.md) e leia as instruções de [testes](../instructions/tests.instructions.md), de [artefatos SDD](../instructions/sdd-artifacts.instructions.md) e o [copilot-instructions.md](../copilot-instructions.md). Se a tarefa tocar UI, leia também as instruções de [plataforma frontend](../instructions/frontend-spec.instructions.md) e de [frontend](../instructions/frontend.instructions.md) e o artefato de `docs/ux/` da funcionalidade. Se os comandos ainda forem marcadores `<...>`, pare e pergunte ao time.

**Passo 1 - Selecionar e entender.**
Leia a tarefa em `tasks.md` e confirme que as dependências estão concluídas com evidência. Leia os REQ/AC em `spec.md`, os componentes em `plan.md`, o `CODEMAP.md` e o código existente. Se o requisito for ambíguo ou estiver bloqueado, pare e reporte a pergunta.

**Passo 2 - RED.**
Escreva o menor teste que expressa o comportamento, com comentário `REQ-NNN` e nome no formato `should_<esperado>_when_<condição>`. Execute-o e confirme que falha pelo motivo certo. Guarde a saída resumida.

**Passo 3 - GREEN.**
Escreva o mínimo de código de produção para o teste passar, respeitando a estrutura por contexto do plano. Execute o teste e guarde a saída.

**Passo 4 - REFACTOR.**
Melhore nomes, duplicação e design com a suíte verde. Reexecute a suíte.

**Passo 5 - Executar os gates.**
Rode lint, typecheck (quando houver), testes com cobertura e build com os comandos declarados. Compare a cobertura com os limites do projeto. Não reporte `PASS` para comando não executado.

**Passo 6 - Registrar e reportar.**
Atualize `tasks.md`: marque `[x]` somente se o aceite da tarefa tiver evidência, preencha a linha em `Verificação` e acrescente a entrada datada no registro de execução. Responda com o formato de saída e indique a próxima tarefa desbloqueada.

## Exemplo de invocação

```text
/implement-task feature=001-sala-do-eco tarefa=T001,T002
```

Espere um teste que falhou e depois passou, o código mínimo rastreado ao REQ-ID, gates executados com resultado real e `tasks.md` atualizado com evidência datada.
