---
name: "plan-architecture"
description: "Produz, para cada pacote pronto em .spec/ (ou só o de feature=), ANALYSIS.md, DESIGN.md completo com as 14 visões do portfólio, DECISIONS.md, contracts/ com manifest.yaml e checkpoints/spec-to-plan.yaml, e mantém CODEMAP.md e ADRs, com contextos por evidência e rastreio REQ-componente."
argument-hint: "[feature=NNN-nome-da-funcionalidade]"
agent: "software-architect"
tools: ["read", "search", "edit"]
---
# /plan-architecture

## Objetivo

Definir como cada funcionalidade será construída: estilo arquitetural proporcional ao problema, contextos e módulos justificados por evidência, contratos, modelo de erros e estratégia de testes, com cada requisito mapeado a um componente. Por pacote, esta etapa produz `ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `contracts/` (`manifest.yaml` e contratos) e `checkpoints/spec-to-plan.yaml`; no repositório, mantém `CODEMAP.md` e propõe ADRs em `docs/adr/`. Sem `feature=`, processa todo pacote cujo `SPECIFICATION.md` esteja `Pronto para revisão` ou `Aprovado`; com `feature=`, só aquele. O design não cria tarefas; isso é `/break-down-tasks`.

## Quando invocar

Na Etapa 3 (design), depois que `/validate-spec` deixou as especificações `Pronto para revisão` ou após aprovação humana registrada. Reinvoque quando `SPECIFICATION.md`, `FRD.md` ou `NFRD.md` mudarem.

> [!NOTE]
> Não use este prompt para escrever requisitos (`/write-ears-spec`), quebrar tarefas (`/break-down-tasks`) ou implementar (`/implement-task`). Integrações com sistemas externos pertencem a quem o projeto designar.

## Pré-condições

- Ao menos um pacote em `.spec/` tem `SPECIFICATION.md` em `Pronto para revisão` ou `Aprovado` com evidência (com `feature=`, o pacote informado), com `SOURCE_TRACEABILITY.md`, `FRD.md` e `NFRD.md` produzidos
- Stack, frameworks e comandos estão preenchidos em [copilot-instructions.md](../copilot-instructions.md)
- `docs/ux/<NNN>-<funcionalidade>-pesquisa.md` existe quando a funcionalidade tem interface

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>` (opcional): restringe o design a um pacote; sem ele, todos os pacotes prontos são processados
- Restrições não funcionais já decididas (plataforma, hospedagem, integrações)
- ADRs existentes em `docs/adr/`, se houver

## O que vou fazer

- Carregar a skill SDD, as instruções SDD, os modelos e o padrão de documentos e Mermaid antes de escrever
- Selecionar os pacotes prontos pelo índice `.spec/README.md` e listar os demais com o motivo
- Ler `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md`, `docs/ux/`, ADRs, `CODEMAP.md` e o código existente relevante
- Registrar em `ANALYSIS.md` evidências, lacunas, opções e riscos
- Classificar o contexto do projeto e escolher o estilo mais simples que atende aos requisitos, justificando cada camada
- Definir contextos e módulos por coesão, acoplamento e frequência de mudança, considerando dependências entre pacotes
- Escrever `DESIGN.md` com todas as seções do modelo (as 14 visões do portfólio), incluindo interfaces, modelo de dados, modelo de erros e estratégia de testes aplicáveis
- Declarar os contratos de interface em `contracts/` e em `contracts/manifest.yaml`, ou `nao-aplicavel` com motivo
- Mapear cada requisito ativo a componentes, testes previstos e estado atual versus alvo em `DESIGN.md` e em `checkpoints/spec-to-plan.yaml`
- Registrar decisões `DEC-NNN` em `DECISIONS.md` e propor ADR em `docs/adr/` apenas para decisão estrutural que exija aprovação humana
- Criar ou atualizar `CODEMAP.md` com módulos, fluxo de dados, integrações e cobertura de REQ-IDs de todos os pacotes
- Atualizar os índices `contracts/README.md` e `checkpoints/README.md` e o status no índice `.spec/README.md`

## O que NÃO vou fazer

- Supor stack, framework ou dependência que não esteja em `copilot-instructions.md` sem ADR proposto
- Definir contextos por nome sem evidência ou impor camadas sem justificativa
- Organizar a raiz por camada técnica (`controller / service / repository`)
- Alterar requisitos de `SPECIFICATION.md`, `FRD.md` ou `NFRD.md`; lacunas voltam ao `@requirements-engineer`
- Preencher `TASKS.md`, `TESTING.md`, `TDD.md` ou demais arquivos de `/break-down-tasks`, código ou testes
- Criar arquivos com os nomes proibidos em minúsculas (`plan.md`, `tasks.md`)
- Produzir diagramas sem fonte ou omitir seções do modelo; seções sem conteúdo ficam `NÃO APLICÁVEL` com motivo
- Declarar validadores executados; sem ferramenta de execução, eles ficam `NÃO EXECUTADO (sem ferramenta de execução)`

## Formato de saída

Siga os modelos `ANALYSIS`, `DESIGN`, `DECISIONS`, `Checkpoints` e `Contratos` dos [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) e inclua todas as seções, na ordem do modelo; seções sem conteúdo ficam `NÃO APLICÁVEL: <motivo>`. A rastreabilidade é obrigatória em `DESIGN.md`:

```markdown
## Visão de entrega e rastreabilidade
| Requisitos | Componentes de design | Tarefas ou plano | Dependências | Testes ou evidências | Atual versus alvo |
| --- | --- | --- | --- | --- | --- |
| REQ-001 | <contexto>/<módulo> | P1.1 | nenhuma | TST-C001 (planejado) | planejado |
```

Decisões ficam em `DECISIONS.md`:

```markdown
### DEC-001: <decisão>
- Status: proposta
- Data: <AAAA-MM-DD>
- IDs de requisitos: REQ-001
- Contexto: <evidência>
- Opções: <A> / <B>
- Decisão: <escolha>
- Consequências: <trade-offs>
- Evidência: <fontes>
- Gatilho de revisão: <quando reabrir>
- ADR: docs/adr/<NNNN>-<slug>.md (Proposto) | não necessário
```

O mapa legível por máquina fica em `checkpoints/spec-to-plan.yaml`, com todo ID ativo:

```yaml
feature: {id: "001", slug: "sala-do-eco"}
mapping_status: complete   # complete | partial | blocked
requirements:
  REQ-001: {components: ["<componente>"], plan: "P1.1", status: planejado}
```

Feche a resposta com o resumo por pacote:

| Pacote | Requisitos mapeados | Contratos | Decisões e ADRs | Validadores | Status | Pode seguir para `/break-down-tasks` |
| --- | --- | --- | --- | --- | --- | --- |
| `<NNN>-<slug>` | <n de m> | <arquivos ou nao-aplicavel> | <DEC-.., ADR-..> | NÃO EXECUTADO (sem ferramenta de execução) | Planejado | sim/não |

## Regras de SDD e rastreabilidade

- Leia as instruções SDD antes de editar `.spec/**`, `CODEMAP.md` e `docs/adr/**`.
- Todo requisito ativo aparece em `DESIGN.md` e em `checkpoints/spec-to-plan.yaml`; componente sem requisito é órfão e deve ser removido ou justificado.
- `DESIGN.md` referencia requisitos por ID e não redefine declarações de `SPECIFICATION.md`; NFRs usam o envelope de medição de `NFRD.md`.
- Diagramas Mermaid usam o tema claro universal e as classes canônicas do padrão; contexto, implantação, estados, sequências e fluxo de dados levam diagrama quando aplicáveis, ou `NÃO APLICÁVEL` com motivo.
- `contracts/manifest.yaml` declara cada contrato ou `nao-aplicavel` com motivo; `feature.id` dos YAML repete o número do pacote.
- Prioridades de decisão: estabilidade de contrato > elegância; observabilidade > abstração; simplicidade operacional > completude; escolha a opção mais fácil de reverter.
- Nenhum import cruza fronteira de contexto sem interface pública justificada.
- Status de `ANALYSIS.md`, `DESIGN.md` e `DECISIONS.md`: `Planejado`. ADRs novos ficam `Proposto` até aprovação humana.
- Este prompt não tem ferramenta de execução: registre os validadores como `NÃO EXECUTADO (sem ferramenta de execução)` na seção `Validação` de `SPECIFICATION.md` (somente essa seção), faça a verificação manual das instruções SDD e liste para o time, a partir da raiz, `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'`, `python3 -B .github/scripts/validate-sdd.py` (`--package NNN` para restringir) e `python3 -B .github/scripts/validate-design-diagrams.py`, com a saída salva em `evidence/<AAAA-MM-DD>-<assunto>.md`.

## Definição de pronto

- [ ] Skill, instruções, modelos e padrão de documentos foram carregados antes da escrita
- [ ] Todo pacote em escopo tem `ANALYSIS.md`, `DESIGN.md` e `DECISIONS.md` com todas as seções dos modelos, com `NÃO APLICÁVEL` justificado onde couber
- [ ] `contracts/manifest.yaml`, os contratos declarados e `checkpoints/spec-to-plan.yaml` existem, e os `README.md` das pastas os listam
- [ ] O estilo arquitetural é proporcional e justificado
- [ ] Contextos e módulos têm evidência de coesão e acoplamento
- [ ] Todo requisito ativo está mapeado a componente, teste previsto e estado em `DESIGN.md` e no checkpoint
- [ ] Decisões têm opções, consequências e gatilho de revisão; ADR só quando necessário
- [ ] `CODEMAP.md` reflete módulos, fluxo de dados, integrações e cobertura de REQ-IDs
- [ ] O status está atualizado no índice `.spec/README.md` e os validadores estão registrados como `NÃO EXECUTADO` com os comandos
- [ ] Lacunas de requisito estão listadas para o `@requirements-engineer`

## Corpo do prompt

Você é `@software-architect`. Desenhe a estrutura interna de cada funcionalidade a partir da evidência, sem expandir o escopo.

**Passo 0 - Carregar skill e instruções.**
Leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md), o [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md), os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md), o [modelo de NFRD](../skills/sdd-requirements-engineer/references/nfrd-template.md) e o [copilot-instructions.md](../copilot-instructions.md), e carregue a skill [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md). Se a stack ou os comandos ainda estiverem como marcadores `<...>`, pare e pergunte ao time.

**Passo 1 - Selecionar pacotes e ler os insumos.**
Sem `feature=`, liste os pacotes do índice `.spec/README.md` e selecione os que têm `SPECIFICATION.md` em `Pronto para revisão` ou `Aprovado`; registre os demais com o motivo. Com `feature=`, só aquele. Para cada pacote, leia `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md`, `docs/ux/` da funcionalidade, ADRs, `CODEMAP.md` e o código existente relevante. Liste requisitos em escopo, NFRs, bloqueios e dependências entre pacotes. Requisito bloqueado não entra no design como decidido.

**Passo 2 - Analisar.**
Preencha `ANALYSIS.md` com inventário de evidências, lacunas `GAP-NNN`, opções e trade-offs e riscos `RISK-NNN`.

**Passo 3 - Escolher o estilo.**
Classifique o contexto (por exemplo, ferramenta CLI, web, educacional) e escolha o estilo mais simples que atende. Justifique cada camada pelo custo que ela evita. Se houver mais de uma interface prevista (CLI e web), avalie separar núcleo de domínio e entrega.

**Passo 4 - Definir contextos e módulos.**
Nomeie contextos por capacidade de negócio com evidência de coesão e acoplamento. Defina a estrutura de pacotes por contexto e, quando necessário, camadas dentro dele.

**Passo 5 - Especificar design, contratos e qualidade.**
Escreva todas as seções de `DESIGN.md`: interfaces, modelo de dados, modelo de erros, invariantes, segurança, ameaças, observabilidade e a estratégia de testes (pirâmide e dependências reais). Referencie NFRs por ID. Declare os contratos em `contracts/` e em `contracts/manifest.yaml`.

**Passo 6 - Rastrear.**
Preencha a visão de entrega e rastreabilidade de `DESIGN.md` e `checkpoints/spec-to-plan.yaml` para todo requisito ativo. Sinalize requisitos sem componente e componentes sem requisito.

**Passo 7 - Registrar decisões.**
Escreva `DEC-NNN` curtos em `DECISIONS.md`. Proponha ADR em `docs/adr/` apenas para decisão estrutural ou nova dependência e liste-o em `ADRs vinculados`.

**Passo 8 - Atualizar o CODEMAP e validar.**
Crie ou atualize `CODEMAP.md` (na raiz, salvo convenção diferente do repositório) e os índices `contracts/README.md`, `checkpoints/README.md` e `.spec/README.md`. Aplique a definição de pronto e os gates aplicáveis dos [quality gates](../skills/sdd-requirements-engineer/references/quality-gates.md), registrando `PASS`, `FAIL`, `BLOQUEADO` ou `NÃO APLICÁVEL`. Registre os validadores como `NÃO EXECUTADO (sem ferramenta de execução)`, faça a verificação manual e liste os comandos para o time. Grave os arquivos como `Planejado`, responda com o resumo por pacote e indique quais seguem para `/break-down-tasks`.

## Exemplo de invocação

```text
/plan-architecture
/plan-architecture feature=001-sala-do-eco
```

Na primeira forma, espere o design de todo pacote pronto e a lista dos pacotes ainda bloqueados. Na segunda, só de `.spec/001-sala-do-eco/`. Em ambas, espere `ANALYSIS.md`, `DESIGN.md` e `DECISIONS.md` completos, `contracts/manifest.yaml`, `checkpoints/spec-to-plan.yaml`, rastreio requisito-componente e um `CODEMAP.md` atualizado.
