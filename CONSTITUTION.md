# Constituição: Echo Chamber

- Status: Rascunho
- Responsável: PENDENTE (Product Owner não identificado; ver Q-016 em [SPECIFICATION.md](.spec/001-sala-do-eco/SPECIFICATION.md))
- Última revisão: não-revisado

## Escopo

Governa como requisitos, design, código, testes e evidências são produzidos neste repositório. Exclui decisões de produto (escopo, prioridades e aprovação de requisitos), que pertencem ao Product Owner, e as regras de automação dos hooks, definidas em `.github/hooks/config/policy.json`.

Todo princípio abaixo deriva de uma fonte verificável do repositório. Nenhum princípio foi aprovado; o status permanece `Rascunho` até a decisão da autoridade de aprovação.

## Princípios

### CON-001: Especificação antes do código

- Regra: nenhum código de produto é escrito sem um requisito aprovado no `SPECIFICATION.md` de um pacote em `.spec/`.
- Justificativa: mantém o escopo sob controle do Product Owner e evita trabalho sem necessidade aprovada.
- Evidência: `.github/copilot-instructions.md#L33`
- Aplicação: `@implementer` recusa tarefa sem requisito; revisão de PR confere o REQ-ID rastreado.
- Autoridade de exceção: Product Owner (PENDENTE)

### CON-002: Rastreabilidade por ID e origem

- Regra: todo requisito usa `REQ-NNN` ou `NFR-NNN`, critérios `AC-<ID>-NN` e fontes `SRC-###`, e tem uma linha `origem:` com fonte verificável ou `[GREENFIELD]` justificado. IDs existentes são preservados.
- Justificativa: permite ligar fonte, requisito, design, tarefa, teste e evidência nos dois sentidos.
- Evidência: `.github/copilot-instructions.md#L34-L35`
- Aplicação: `python3 -B .github/scripts/validate-sdd.py` ao fim de cada etapa SDD.
- Autoridade de exceção: Product Owner (PENDENTE)

### CON-003: Testes primeiro e ligados ao requisito

- Regra: comportamento novo nasce de um teste que falha (RED) antes da implementação (GREEN); todo teste que verifica um requisito cita o ID em comentário; a cobertura mínima é 80% de linhas e 70% de branches.
- Justificativa: prova o comportamento exigido e mantém a matriz requisito-teste verificável.
- Evidência: `.github/copilot-instructions.md#L36`, `.github/copilot-instructions.md#L23-L26`, [tests.instructions.md](.github/instructions/tests.instructions.md)
- Aplicação: comando de testes com cobertura de `.github/copilot-instructions.md` e `python3 -B .github/scripts/validate-red-phase.py` como evidência da fase RED.
- Autoridade de exceção: Product Owner (PENDENTE), com issue e justificativa registradas

### CON-004: Sem segredos nem dados pessoais

- Regra: segredos, credenciais e dados pessoais nunca aparecem em código, logs, artefatos ou evidências.
- Justificativa: o público inclui alunos, e a classificação dos dados ainda não foi decidida (Q-009 do pacote 001).
- Evidência: `.github/copilot-instructions.md#L37`
- Aplicação: hooks `preToolUse` e revisão de PR.
- Autoridade de exceção: nenhuma

### CON-005: Nada declarado sem evidência

- Regra: aprovação, execução de testes, métricas e status `Aprovado`, `Implementado` ou `Verificado` só são registrados com evidência datada.
- Justificativa: validação textual e planos não provam comportamento nem decisão humana.
- Evidência: `.github/copilot-instructions.md#L38`
- Aplicação: gates de `CHECKLIST.md` e `VERIFICATION.md`; evidências em `evidence/` de cada pacote.
- Autoridade de exceção: nenhuma

### CON-006: Stack aprovada e dependências com ADR

- Regra: o produto usa Node.js 24 LTS com JavaScript (ESM) e testes nativos (`node:test`, `node:assert`); dependências, frameworks ou serviços fora dessa stack exigem um ADR aprovado.
- Justificativa: RNF-01 declara o padrão aprovado pela TI, e a Fase 2 ainda não tem stack decidida.
- Evidência: `.github/copilot-instructions.md#L18-L20`, `.github/copilot-instructions.md#L29`, `requisitos/requisitos.md#L78`
- Aplicação: `/plan-architecture` propõe ADR para toda nova dependência; revisão de PR.
- Autoridade de exceção: TI e Product Owner (PENDENTE)

### CON-007: Português do Brasil na documentação e na interface

- Regra: documentação e mensagens exibidas ao usuário são escritas em português do Brasil, salvo decisão diferente registrada.
- Justificativa: RNF-09 exige interface em português; a versão em outro idioma está em aberto (Q-015 do pacote 001).
- Evidência: `.github/copilot-instructions.md#L12`, `requisitos/requisitos.md#L86`
- Aplicação: revisão de conteúdo e inspeção do catálogo de mensagens (NFR-003 do pacote 001).
- Autoridade de exceção: Product Owner (PENDENTE)

## Governança

- Autoridade de aprovação: Product Owner, ainda não identificado (Q-016 do pacote 001); até lá, nenhum princípio está aprovado.
- Processo de emenda: PR que altera este arquivo, cita a fonte de cada princípio novo ou alterado e registra a aprovação da autoridade no histórico abaixo.
- Gatilho de revisão: mudança em `.github/copilot-instructions.md` ou em `.github/instructions/`, decisão sobre a Fase 2 (Q-012) ou nova versão de `requisitos/requisitos.md`.

## Histórico de mudanças

| Versão | Data | Mudança |
| --- | --- | --- |
| 0.1.0 | 2026-09-24 | Constituição inicial em Rascunho, derivada de `.github/copilot-instructions.md` e `requisitos/requisitos.md`. |
