---
name: "validate-spec"
description: "Revisa SPECIFICATION.md, SOURCE_TRACEABILITY.md, FRD.md e NFRD.md de cada pacote em .spec/ (ou só o de feature=) contra estrutura, completude dos modelos, EARS, linha origem:, cobertura da fonte, contradições e quality gates; esclarece bloqueios com o Product Owner e decide se cada pacote fica Pronto para revisão, sem aprovar em nome de humanos."
argument-hint: "[feature=NNN-nome-da-funcionalidade]"
agent: "requirements-engineer"
tools: ["read", "search", "edit"]
---
# /validate-spec

## Objetivo

Validar as especificações existentes e esclarecer suas ambiguidades antes do design. Sem `feature=`, a revisão cobre todo pacote de `.spec/` cujo `SPECIFICATION.md` esteja `Rascunho` ou `Pronto para revisão`, além da cobertura global da fonte e do índice `.spec/README.md`; com `feature=`, só aquele pacote. O resultado é uma lista de achados por severidade, correções de forma que preservam significado nos quatro arquivos de requisitos e uma decisão de prontidão por pacote, registrada na seção `Validação` de `SPECIFICATION.md`.

## Quando invocar

Ao fim da Etapa 2, depois de `/write-ears-spec` (e de `/research-ux`, quando houver UI) e antes de `/plan-architecture`. Reinvoque sempre que uma especificação mudar.

> [!NOTE]
> Não use este prompt para escrever requisitos novos (`/write-ears-spec`) nem para validar `DESIGN.md` ou `TASKS.md` (`/break-down-tasks` faz a análise cruzada em `CROSS_ANALYSIS.md`). Não aprove a especificação: aprovação é decisão humana registrada.

## Pré-condições

- Existe ao menos um pacote em `.spec/` com `SPECIFICATION.md` em `Rascunho` ou `Pronto para revisão` (com `feature=`, o pacote informado)
- O pacote tem a estrutura completa; arquivo ou pasta ausente vira achado e volta para `/write-ears-spec`
- As fontes citadas nas linhas `origem:` estão acessíveis no repositório
- O Product Owner (ou revisor responsável) está disponível para responder bloqueios

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>` (opcional): restringe a revisão a um pacote; sem ele, todos os pacotes prontos para validação são revisados
- Respostas do Product Owner a perguntas já registradas, se houver
- Artefatos de `docs/ux/` das funcionalidades com UI, quando houver

## O que vou fazer

- Carregar SDD/TDD, as instruções aplicáveis e os modelos e usar o modo `Validação`
- Conferir a estrutura de 13 arquivos e 3 pastas, os cabeçalhos `Status` e `Etapa dona` e a completude de seções de `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md` e `NFRD.md`
- Conferir cada requisito contra o contrato EARS, a linha `origem:` e a fonte citada
- Conferir que `FRD.md` e `NFRD.md` referenciam os IDs de `SPECIFICATION.md` sem redefini-los, que `NFRD.md` tem o envelope de medição de cada NFR e que resumos e contagens são coerentes
- Conferir que todo ID da fonte tem disposição em exatamente um pacote e que o índice `.spec/README.md` lista todo pacote
- Detectar requisitos compostos, termos vagos, tecnologia em requisito funcional, NFR sem envelope de medição e contradições entre fontes ou entre pacotes
- Fazer no máximo três perguntas sobre bloqueios por invocação, uma por vez, ao Product Owner
- Corrigir apenas defeitos de forma (redação EARS, metadado com evidência, ID de aceite ausente, seção ausente com `NÃO APLICÁVEL` justificado), preservando ID e significado
- Registrar respostas humanas como fonte `SRC-###` de classe `usuário` em `SOURCE_TRACEABILITY.md`, com data e autoridade
- Classificar cada gate como `PASS`, `FAIL`, `BLOQUEADO` ou `NÃO APLICÁVEL` na seção `Validação` de `SPECIFICATION.md`

## O que NÃO vou fazer

- Mudar o significado de um requisito sem decisão do Product Owner
- Escolher uma interpretação de regra ambígua
- Marcar a especificação como `Aprovado` sem evidência de aprovação humana
- Renumerar IDs ou apagar requisitos sem linha em `Disposições históricas`
- Preencher arquivos de etapas futuras (`ANALYSIS.md`, `DESIGN.md`, `TASKS.md` e demais), código ou testes
- Criar arquivos com os nomes proibidos em minúsculas (`spec.md`, `frd.md`, `nfrd.md`)
- Declarar validadores executados; sem ferramenta de execução, eles ficam `NÃO EXECUTADO (sem ferramenta de execução)`

## Formato de saída

Tabela de achados por pacote seguida do modelo de saída da skill SDD:

| ID | Severidade | Gate | Pacote | Requisito | Achado | Correção aplicada ou proposta | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | Alta | EARS atômico | 001-sala-do-eco | REQ-004 | Duas respostas em uma declaração | Dividir em REQ-004 e REQ-012 (disposição registrada) | Corrigido |
| F-002 | Bloqueio | Contradição | 001-sala-do-eco | REQ-002, REQ-009 | Fontes divergem sobre autenticação | Pergunta Q-003 ao Product Owner | Aberto |

Severidades: `Bloqueio` (impede design), `Alta` (requisito não verificável), `Média` (metadado, rastreio, estrutura ou seção incompleta), `Baixa` (forma).

Feche com a decisão por pacote:

| Pacote | Bloqueios em P0 | Validadores | Status | Pode seguir para `/plan-architecture` |
| --- | --- | --- | --- | --- |
| `<NNN>-<slug>` | <IDs ou nenhum> | NÃO EXECUTADO (sem ferramenta de execução) | Rascunho/Pronto para revisão | sim/não |

## Regras de SDD e rastreabilidade

- Leia as instruções SDD antes de editar `.spec/**`; elas governam estrutura, completude, evidência, atomicidade, rastreio e status.
- A declaração EARS, os critérios e a verificação só mudam em `SPECIFICATION.md`; os demais arquivos referenciam IDs.
- Divisão, fusão, transferência ou aposentadoria de requisito exige linha em `Disposições históricas` de `SOURCE_TRACEABILITY.md` e, quando envolve outro pacote, atualização da `Cobertura da fonte` e do índice.
- Uma resposta do Product Owner vira fonte: registre-a no `Registro de fontes` e cite-a na `origem:` do requisito afetado.
- `Pronto para revisão` exige zero bloqueios abertos em requisitos P0 do pacote; caso contrário, ele fica `Rascunho` com bloqueios listados. O status concorda entre os quatro arquivos e o índice.
- Este prompt não tem ferramenta de execução: registre os validadores como `NÃO EXECUTADO (sem ferramenta de execução)` na seção `Validação`, faça a verificação manual das instruções SDD e liste para o time, a partir da raiz, `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` e `python3 -B .github/scripts/validate-sdd.py` (`--package NNN` para restringir), com a saída salva em `evidence/<AAAA-MM-DD>-validate-sdd.md`.
- Validação textual não prova significado EARS nem aprovação; declare o que foi revisado manualmente.

## Definição de pronto

- [ ] SDD/TDD, as instruções aplicáveis e os modelos foram carregados antes da revisão
- [ ] Todo pacote em escopo teve estrutura, cabeçalhos e completude de seções conferidos
- [ ] Todo requisito ativo foi conferido contra a fonte citada
- [ ] A cobertura global da fonte e o índice `.spec/README.md` foram conferidos
- [ ] Todo achado tem severidade, gate, pacote, correção e status
- [ ] Correções preservam ID e significado ou têm decisão humana registrada
- [ ] Bloqueios restantes têm responsável e impacto
- [ ] A seção `Validação` de cada `SPECIFICATION.md` registra os gates e os validadores `NÃO EXECUTADO` com os comandos
- [ ] O status de cada pacote reflete a evidência (`Rascunho` ou `Pronto para revisão`)

## Corpo do prompt

Você é `@requirements-engineer`. Valide a especificação sem alterar seu significado e sem simular aprovação.

**Passo 0 - Carregar SDD, TDD e instruções.**
Leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) e carregue as skills [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e [tdd-workflow](../skills/tdd-workflow/SKILL.md). Selecione `Validação` e leia os [quality gates](../skills/sdd-requirements-engineer/references/quality-gates.md), o [catálogo de antipadrões](../skills/sdd-requirements-engineer/references/anti-patterns.md), a [referência EARS](../skills/sdd-requirements-engineer/references/ears-notation.md), os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md), o [modelo de FRD](../skills/sdd-requirements-engineer/references/frd-template.md) e o [modelo de NFRD](../skills/sdd-requirements-engineer/references/nfrd-template.md).

**Passo 1 - Inventariar.**
Sem `feature=`, liste os pacotes do índice `.spec/README.md` e selecione os que têm `SPECIFICATION.md` em `Rascunho` ou `Pronto para revisão`; com `feature=`, só aquele. Em cada pacote, confira os 13 arquivos, as 3 pastas com `README.md` e os cabeçalhos. Leia `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md` e `NFRD.md` inteiros. Liste requisitos, fontes, critérios, perguntas e disposições. Abra cada fonte citada e confirme seção e linhas.

**Passo 2 - Aplicar os gates.**
Confira que cada arquivo tem todas as seções do modelo, na ordem do modelo. Para cada requisito, verifique padrão EARS, resposta única e observável, `deve`, neutralidade tecnológica, prioridade justificada, `origem:` válida, aceite Dado/Quando/Então e verificação planejada. Para NFRs, verifique o envelope de medição em `NFRD.md`.

**Passo 3 - Detectar conflitos e lacunas de cobertura.**
Compare requisitos entre si, entre pacotes e com as fontes. Confira que todo ID da fonte tem disposição em exatamente um pacote. Registre contradições como `Bloqueio` com as interpretações possíveis.

**Passo 4 - Esclarecer.**
Faça no máximo três perguntas focadas sobre bloqueios, uma por vez, e espere a resposta. Priorize bloqueios em requisitos P0. Não pergunte o que o repositório já responde. Registre cada resposta como `SRC-###` em `SOURCE_TRACEABILITY.md`.

**Passo 5 - Corrigir.**
Aplique apenas correções de forma ou decorrentes de respostas registradas, nos quatro arquivos de requisitos. Registre disposições para divisões, fusões e transferências e atualize o índice. Deixe o restante como achado aberto.

**Passo 6 - Decidir e reportar.**
Registre na seção `Validação` de cada `SPECIFICATION.md` os gates e os validadores como `NÃO EXECUTADO (sem ferramenta de execução)`, com os comandos para o time. Defina o status de cada pacote conforme as regras acima e atualize o índice. Responda com a tabela de achados, a decisão por pacote e o modelo de saída da skill SDD.

## Exemplo de invocação

```text
/validate-spec
/validate-spec feature=001-sala-do-eco
```

Na primeira forma, espere a revisão de todos os pacotes prontos para validação e da cobertura global da fonte. Na segunda, só de `.spec/001-sala-do-eco/`. Em ambas, espere uma tabela de achados, correções de forma aplicadas, perguntas ao Product Owner e a decisão `Rascunho` ou `Pronto para revisão` por pacote.
