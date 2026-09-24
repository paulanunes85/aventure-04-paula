# Instruções do repositório

Estas instruções valem para todo o repositório. Substitua os marcadores `<...>` ao adotar este kit em um projeto. Enquanto um marcador não for preenchido, pergunte ao time em vez de supor o valor.

## Projeto

| Campo | Valor |
| --- | --- |
| Nome | Echo Chamber (nome provisório, pendente de validação do marketing) |
| Objetivo | Ajudar alunos a aprender sequências numéricas de forma lúdica: o aluno informa uma sequência e o sistema devolve o próximo número |
| Documento de requisitos de origem | `requisitos/requisitos.md` (v0.4, rascunho em revisão) |
| Idioma da documentação e da interface | Português (pt-BR), salvo decisão diferente registrada |

## Stack e comandos

| Item | Valor |
| --- | --- |
| Linguagem e runtime | Node.js 24 LTS + JavaScript (ESM); arquivo principal `index.js` (RNF-01) |
| Framework(s) | Nenhum na Fase 1 (CLI no terminal); a Fase 2 (web) segue pendente de decisão |
| Testes | `node:test` e `node:assert` (nativos, sem dependências) |
| Instalar dependências | `npm install` (quando existir `package.json`; hoje não há dependências) |
| Lint / typecheck | `find . -name '*.js' -not -path './node_modules/*' -exec node --check {} +` (apenas sintaxe; sem typecheck) |
| Testes com cobertura | `node --test --experimental-test-coverage --test-coverage-lines=80 --test-coverage-branches=70` |
| Build | Não aplicável (JavaScript executado diretamente com `node index.js`) |
| Limites de cobertura | 80% linhas / 70% branches |
| Quality gate (hook `agentStop`) | Desativado até a primeira tarefa criar `package.json`; então ativar em `.github/hooks/config/policy.json` com os comandos de lint e testes acima |

Não adicione dependências, frameworks ou serviços que não estejam nesta tabela sem um ADR em `docs/adr/`.

## Convenções

- Siga Spec-Driven Development: requisito aprovado em `specs/<NNN>-<funcionalidade>/spec.md` antes de código.
- IDs: `REQ-NNN` (funcional), `NFR-NNN` (não funcional), `AC-<ID>-NN` (aceite), `SRC-###` (fonte). Preserve IDs já existentes no documento de origem.
- Todo requisito tem uma linha `origem:` apontando para uma fonte verificável ou `[GREENFIELD]` com justificativa.
- Todo teste que verifica um requisito cita o ID em comentário.
- Nunca registre segredos, credenciais ou dados pessoais em código, logs ou evidências.
- Não declare aprovação, execução de testes ou métricas sem evidência.

## Customizações do Copilot neste repositório

| Tipo | Local | Conteúdo |
| --- | --- | --- |
| Agentes | [.github/agents/](agents/) | `@requirements-engineer`, `@software-architect`, `@se-ux-ui-designer`, `@implementer`, `@qa-engineer` |
| Skills | [.github/skills/](skills/) | `sdd-requirements-engineer`, `tdd-workflow`, `user-story-refine` |
| Prompts | [.github/prompts/](prompts/) | `/refine-user-stories`, `/write-ears-spec`, `/validate-spec`, `/research-ux`, `/plan-architecture`, `/break-down-tasks`, `/implement-task`, `/verify-quality` |
| Instruções por arquivo | [.github/instructions/](instructions/) | Artefatos SDD, testes, frontend (plataforma e componentes), autoria de skills e de hooks |
| Hooks | [.github/hooks/](hooks/) | Guardrails em `preToolUse`, contexto em `sessionStart`, auditoria sem conteúdo sensível e quality gate opcional; política em `hooks/config/policy.json` |

Fluxo sugerido: `@requirements-engineer` (spec) → `@se-ux-ui-designer` (quando houver UI) → `@software-architect` (plan) → `@implementer` + `@qa-engineer` (tasks, código e testes).

| Etapa | Prompt | Agente | Artefato |
| --- | --- | --- | --- |
| 1. Descoberta | `/refine-user-stories` | `@requirements-engineer` | Histórias INVEST e perguntas em aberto |
| 2. Especificação | `/write-ears-spec` | `@requirements-engineer` | `specs/<NNN>-<funcionalidade>/spec.md` |
| 2. Especificação (UI) | `/research-ux` | `@se-ux-ui-designer` | `docs/ux/<funcionalidade>-pesquisa.md` |
| 2. Especificação | `/validate-spec` | `@requirements-engineer` | Achados e status `Pronto para revisão` |
| 3. Design | `/plan-architecture` | `@software-architect` | `plan.md`, `CODEMAP.md`, ADRs propostos |
| 3. Design | `/break-down-tasks` | `@software-architect` | `tasks.md` com pares RED/GREEN |
| 4. Construção | `/implement-task` | `@implementer` | Código, testes e evidência em `tasks.md` |
| 4. Construção | `/verify-quality` | `@qa-engineer` | Matriz requisito-teste e gates |

Ordem de execução detalhada e atuação dos hooks por etapa: [prompts/README.md](prompts/README.md).

Quando um hook bloquear ou pedir confirmação, não tente contornar a regra; explique ao usuário qual regra disparou e, se a operação for legítima, proponha o ajuste em `.github/hooks/config/policy.json`.
