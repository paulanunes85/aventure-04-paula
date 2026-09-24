---
name: "implement-task"
description: "Implementa uma única tarefa de .spec/<NNN>-<funcionalidade>/TASKS.md com TDD red-green-refactor, comentários REQ-NNN, gates do projeto e validadores SDD executados, evidência datada em evidence/ e registro em TASKS.md, TDD.md e VERIFICATION.md."
argument-hint: "feature=NNN-nome-da-funcionalidade tarefa=T001[,T002]"
agent: "implementer"
tools: ["read", "search", "edit", "execute"]
---
# /implement-task

## Objetivo

Entregar exatamente uma tarefa (ou um par RED/GREEN) de `TASKS.md` como código funcionando e testado, rastreável ao requisito, com os gates do projeto e os validadores SDD executados e a evidência salva em `evidence/`. Nada além da tarefa em escopo. `feature=` e `tarefa=` são obrigatórios.

## Quando invocar

Na Etapa 4 (construção), para a próxima tarefa desbloqueada indicada por `/break-down-tasks`. Uma invocação por tarefa ou par, em um único pacote.

> [!NOTE]
> Não use este prompt para planejar (`/plan-architecture`), criar tarefas (`/break-down-tasks`) ou auditar cobertura (`/verify-quality`). Pedido sem `REQ-NNN` volta com pergunta sobre critérios de aceite.

## Pré-condições

- `TASKS.md` do pacote está `Planejado` e as dependências da tarefa estão concluídas com evidência em `evidence/`
- `python3 -B .github/scripts/validate-sdd.py --require-full --strict` passou para o pacote, com o resultado em `VERIFICATION.md`; se ainda estiver `NÃO EXECUTADO`, eu o executo no Passo 1
- Stack, comandos de lint, typecheck, testes com cobertura e build estão preenchidos em [copilot-instructions.md](../copilot-instructions.md)
- Os requisitos rastreados pela tarefa não estão bloqueados

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>` (obrigatória)
- `tarefa=<T001>` ou o par `T001,T002` (obrigatória)
- Decisões pendentes que afetem a tarefa, se houver

## O que vou fazer

- Carregar a skill TDD e as instruções de testes, SDD e (se houver UI) frontend antes de codar
- Ler a tarefa em `TASKS.md`, o ciclo em `TDD.md`, os testes em `TESTING.md`, os REQ/AC em `SPECIFICATION.md`, os componentes em `DESIGN.md`, os contratos em `contracts/`, o `CODEMAP.md` e o código existente
- RED: escrever o menor teste que falha, com comentário `REQ-NNN`, executá-lo e confirmar que falha pelo motivo certo
- GREEN: escrever o mínimo de código de produção que faz o teste passar
- REFACTOR: melhorar o design com a suíte verde
- Executar os gates declarados (lint, typecheck, testes com cobertura, build) e os validadores SDD, e registrar o resultado real
- Salvar a saída resumida em `evidence/<AAAA-MM-DD>-<assunto>.md` e listá-la em `evidence/README.md`
- Atualizar `TASKS.md` (marcar `[x]` somente com evidência e acrescentar a entrada datada no registro de execução), o estado do ciclo em `TDD.md` e os resultados e execuções de validadores em `VERIFICATION.md`
- Sugerir a sequência de commits da skill TDD, sem commitar salvo pedido do time

## O que NÃO vou fazer

- Implementar outra tarefa, funcionalidade extra ou refatoração fora do escopo
- Escrever código de produção sem teste falhando antes
- Adicionar dependência, framework ou serviço fora de `copilot-instructions.md` sem ADR
- Pular, enfraquecer ou desativar testes, ou adicionar `any`/supressão de lint sem justificativa
- Criar imports que cruzem fronteiras de contexto de `DESIGN.md`
- Inventar regra para preencher lacuna; exponho a pergunta
- Registrar segredos ou dados pessoais em código, logs ou evidências
- Declarar gate ou validador aprovado sem ter executado o comando
- Criar arquivos com os nomes proibidos em minúsculas (`tasks.md`, `spec.md`, `plan.md`) ou alterar `SPECIFICATION.md` e `DESIGN.md`

## Formato de saída

```markdown
## Resultado da tarefa T001

- Pacote: <NNN>-<funcionalidade>
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
  | Autoteste do validador | `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` | PASS/FAIL |
  | Validador SDD | `python3 -B .github/scripts/validate-sdd.py --package <NNN>` | PASS/FAIL - <erros>/<avisos> |
  | Diagramas | `python3 -B .github/scripts/validate-design-diagrams.py` | PASS/FAIL/NÃO APLICÁVEL (nenhum diagrama mudou) |
- Evidência: `evidence/<AAAA-MM-DD>-<assunto>.md`
- TASKS.md: T001 marcada | não marcada (<motivo>)
- TDD.md: AC-REQ-001-01 <estado do ciclo>
- VERIFICATION.md: VER-001 <PASS/FAIL/PENDENTE>
- Commits sugeridos: `test: add failing test for REQ-001` -> `feat: make REQ-001 pass` -> `refactor: <melhoria>`
- Pendências: <perguntas ou bloqueios, ou nenhuma>
```

## Regras de SDD e rastreabilidade

- Todo teste que verifica um requisito cita o ID em comentário, conforme as instruções de testes.
- Cada unidade de regra de negócio recebe teste de caminho feliz e de erro.
- O vermelho vale apenas se falhar pela ausência do comportamento, não por sintaxe, import ou configuração.
- Evidência é saída real de comando, resumida, datada, com o ID verificado e sem dados sensíveis, salva em `evidence/`; plano não é evidência.
- Execute os validadores a partir da raiz ao fim da tarefa: `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'`, `python3 -B .github/scripts/validate-sdd.py --package <NNN>` e, quando um diagrama mudar, `python3 -B .github/scripts/validate-design-diagrams.py`. Registre comando, data, código de saída e resumo em `Execuções de validadores` de `VERIFICATION.md`.
- Desvio entre tarefa e realidade vai para a tabela `Desvios` de `TASKS.md`, não é corrigido em silêncio.

## Definição de pronto

- [ ] Skill TDD e instruções aplicáveis foram carregadas antes de codar
- [ ] O vermelho foi observado e confirmado pelo motivo certo antes do código de produção
- [ ] O código atende exatamente ao REQ/AC da tarefa, com comentário de rastreabilidade
- [ ] Os gates declarados e os validadores SDD foram executados e seus resultados reais estão reportados
- [ ] Nenhum teste foi pulado ou enfraquecido e nenhuma fronteira de contexto foi cruzada
- [ ] A evidência está em `evidence/` e listada em `evidence/README.md`
- [ ] `TASKS.md` tem a tarefa marcada somente com evidência e a entrada datada no registro; `TDD.md` e `VERIFICATION.md` refletem o resultado real

## Corpo do prompt

Você é `@implementer`. Implemente uma única tarefa com TDD estrito e evidência real.

**Passo 0 - Carregar skill e instruções.**
Carregue a skill [tdd-workflow](../skills/tdd-workflow/SKILL.md) e leia as instruções de [testes](../instructions/tests.instructions.md), de [artefatos SDD](../instructions/sdd-artifacts.instructions.md), os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) (seções `TASKS`, `TDD`, `VERIFICATION` e `Índices das pastas`) e o [copilot-instructions.md](../copilot-instructions.md). Se a tarefa tocar UI, leia também as instruções de [plataforma frontend](../instructions/frontend-spec.instructions.md) e de [frontend](../instructions/frontend.instructions.md) e o artefato de `docs/ux/` da funcionalidade. Se os comandos ainda forem marcadores `<...>`, pare e pergunte ao time.

**Passo 1 - Selecionar e entender.**
Leia a tarefa em `TASKS.md` e confirme que as dependências estão concluídas com evidência em `evidence/`. Confira em `VERIFICATION.md` que `python3 -B .github/scripts/validate-sdd.py --require-full --strict` passou para o pacote; se estiver `NÃO EXECUTADO`, execute-o, salve a saída em `evidence/` e registre-a; código de saída diferente de `0` bloqueia a tarefa e volta ao responsável. Leia o ciclo do AC em `TDD.md`, o teste em `TESTING.md`, os REQ/AC em `SPECIFICATION.md`, os componentes em `DESIGN.md`, os contratos em `contracts/`, o `CODEMAP.md` e o código existente. Se o requisito for ambíguo ou estiver bloqueado, pare e reporte a pergunta.

**Passo 2 - RED.**
Escreva o menor teste que expressa o comportamento, com comentário `REQ-NNN` e nome no formato `should_<esperado>_when_<condição>`. Execute-o e confirme que falha pelo motivo certo. Guarde a saída resumida.

**Passo 3 - GREEN.**
Escreva o mínimo de código de produção para o teste passar, respeitando a estrutura por contexto de `DESIGN.md` e os contratos de `contracts/`. Execute o teste e guarde a saída.

**Passo 4 - REFACTOR.**
Melhore nomes, duplicação e design com a suíte verde. Reexecute a suíte.

**Passo 5 - Executar os gates.**
Rode lint, typecheck (quando houver), testes com cobertura e build com os comandos declarados. Compare a cobertura com os limites do projeto. Não reporte `PASS` para comando não executado.

**Passo 6 - Registrar.**
Salve a saída resumida de RED, GREEN e gates em `evidence/<AAAA-MM-DD>-<assunto>.md`, com data, comando e ID verificado, e liste-a em `evidence/README.md`. Atualize `TASKS.md`: marque `[x]` somente se o aceite da tarefa tiver evidência, acrescente a entrada datada no registro de execução e a tarefa na linha `Marcadas como concluídas pela verificação`. Atualize o estado do ciclo em `TDD.md` e a linha em `Resultados` de `VERIFICATION.md`.

**Passo 7 - Validar e reportar.**
Rode a partir da raiz `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'`, `python3 -B .github/scripts/validate-sdd.py --package <NNN>` e, se um diagrama mudou, `python3 -B .github/scripts/validate-design-diagrams.py`. Salve a saída em `evidence/` e registre comando, data, código de saída e resumo em `Execuções de validadores` de `VERIFICATION.md`. Erro do validador causado pela tarefa é corrigido antes de encerrar; erro pré-existente vai para `Desvios`. Responda com o formato de saída e indique a próxima tarefa desbloqueada.

## Exemplo de invocação

```text
/implement-task feature=001-sala-do-eco tarefa=T001,T002
```

Espere um teste que falhou e depois passou, o código mínimo rastreado ao REQ-ID, gates e validadores executados com resultado real, a evidência em `.spec/001-sala-do-eco/evidence/` e `TASKS.md`, `TDD.md` e `VERIFICATION.md` atualizados.
