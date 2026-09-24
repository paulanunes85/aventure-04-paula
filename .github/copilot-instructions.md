# Instruções do repositório

Estas instruções valem para todo o repositório. Substitua os marcadores `<...>` ao adotar este kit em um projeto. Enquanto um marcador não for preenchido, pergunte ao time em vez de supor o valor.

## Projeto

| Campo | Valor |
| --- | --- |
| Nome | <nome do projeto> |
| Objetivo | <uma frase sobre o problema resolvido> |
| Documento de requisitos de origem | <caminho, por exemplo `requisitos/requisitos.md`> |
| Idioma da documentação e da interface | Português (pt-BR), salvo decisão diferente registrada |

## Stack e comandos

| Item | Valor |
| --- | --- |
| Linguagem e runtime | <por exemplo, Node.js 22 + JavaScript/TypeScript> |
| Framework(s) | <por exemplo, nenhum (CLI), React + Vite, Next.js> |
| Testes | <por exemplo, `node:test`, Vitest, JUnit 5, pytest> |
| Instalar dependências | `<comando>` |
| Lint / typecheck | `<comando>` |
| Testes com cobertura | `<comando>` |
| Build | `<comando>` |
| Limites de cobertura | <por exemplo, 80% linhas / 70% branches> |

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
| Instruções por arquivo | [.github/instructions/](instructions/) | Artefatos SDD, testes, frontend (plataforma e componentes), autoria de skills |

Fluxo sugerido: `@requirements-engineer` (spec) → `@se-ux-ui-designer` (quando houver UI) → `@software-architect` (plan) → `@implementer` + `@qa-engineer` (tasks, código e testes).
