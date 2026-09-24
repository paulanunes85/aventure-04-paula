---
name: "research-ux"
description: "Produz a pesquisa de UX de cada funcionalidade com interface em docs/ux/ (ou só a de feature=): declaração Jobs-to-be-Done, jornada, especificação de fluxo e contrato de acessibilidade WCAG 2.2 AA, sem código e sem detalhes inventados."
argument-hint: "fonte=requisitos/requisitos.md [feature=NNN-nome-da-funcionalidade]"
agent: "se-ux-ui-designer"
tools: ["read", "search", "edit"]
---
# /research-ux

## Objetivo

Descobrir a necessidade do usuário, a jornada e o contrato de acessibilidade das funcionalidades com interface e registrá-los em `docs/ux/<NNN>-<funcionalidade>-pesquisa.md`, um arquivo por pacote, para que requisitos, design e implementação partam da mesma intenção. Sem `feature=`, a pesquisa cobre todo pacote de `.spec/` com interface cujo `SPECIFICATION.md` esteja `Rascunho` ou `Pronto para revisão`; com `feature=`, só aquele pacote.

## Quando invocar

Na Etapa 2, depois do primeiro rascunho de `SPECIFICATION.md` e antes de `/plan-architecture`, sempre que uma funcionalidade tiver interface (terminal, web ou mobile).

> [!NOTE]
> Não use este prompt para escrever componentes ou estilos (`/implement-task`) nem requisitos EARS (`/write-ears-spec`). Os requisitos de UI candidatos que eu levantar recebem ID do `@requirements-engineer`.

## Pré-condições

- Ao menos um pacote em `.spec/` tem interface com o usuário (com `feature=`, o pacote informado)
- O `SPECIFICATION.md` desse pacote está em `Rascunho` ou `Pronto para revisão`
- O time tem evidência do público (fonte, entrevistas ou Product Owner)

## Entradas que o time deve fornecer

- `fonte=<documento de origem>` (obrigatória) e evidências do fluxo atual (planilhas, telas, processos manuais)
- `feature=<NNN>-<nome-da-funcionalidade>` (opcional): restringe a pesquisa a um pacote; sem ele, todos os pacotes com interface são pesquisados
- Público: faixa etária, letramento digital, idioma(s) e dispositivo(s)
- Regras de privacidade para dados pessoais ou de menores, se houver

## O que vou fazer

- Carregar a skill `user-story-refine` e as instruções de frontend antes de escrever
- Identificar os pacotes com interface pelo índice `.spec/README.md` e por `SPECIFICATION.md`, e listar os pacotes sem interface como `NÃO APLICÁVEL`
- Ler `SPECIFICATION.md`, `FRD.md` e `NFRD.md` de cada pacote, a fonte e as evidências do fluxo atual
- Escrever uma declaração Jobs-to-be-Done por tarefa-alvo
- Mapear a jornada por etapa (fazendo, pensando, sentindo, dificuldade, oportunidade)
- Especificar o fluxo com entrada, passos, estados (carregando, vazio, erro, excesso) e saídas (sucesso, parcial, bloqueado)
- Escrever o contrato WCAG 2.2 AA: ordem de teclado, anúncios, contraste, foco e alvos
- Listar requisitos de UI candidatos, sem ID, para o `@requirements-engineer`

## O que NÃO vou fazer

- Propor tela sem declaração de necessidade
- Inventar campo, rótulo, valor, persona ou regra
- Escrever componentes, classes de estilo ou código de framework
- Definir paleta, tipografia ou identidade visual sem aprovação humana
- Expor dados pessoais ou de menores sem máscara em jornadas e exemplos
- Editar arquivos em `.spec/`; a formalização dos candidatos é feita por `/write-ears-spec`

## Formato de saída

Um arquivo `docs/ux/<NNN>-<funcionalidade>-pesquisa.md` por pacote com interface, com as seções do agente:

```markdown
# UX: <NNN>-<funcionalidade>

- Status: Rascunho
- Pacote: .spec/<NNN>-<funcionalidade>/
- Fontes: SRC-001 (requisitos/requisitos.md#L<início>-L<fim>), <entrevistas>
- Requisitos relacionados: REQ-001, REQ-003

## Público
| Atributo | Valor | Fonte |
| --- | --- | --- |
| Faixa etária | <valor ou PENDENTE> | <fonte> |

## Declaração de necessidade
Quando [situação], eu quero [motivação], para que eu possa [resultado].

## Jornada - <tarefa>
| Etapa | Fazendo | Pensando | Sentindo | Dificuldade | Oportunidade |
| --- | --- | --- | --- | --- | --- |

## Especificação de fluxo
Ponto de entrada -> passos (ação principal + estado) -> saídas (sucesso / parcial / bloqueado)

## Contrato de acessibilidade (WCAG 2.2 AA)
| Critério | Exigência para este fluxo | Verificação planejada |
| --- | --- | --- |

## Requisitos de UI candidatos
| Candidato | Comportamento observável | Evidência | Encaminhamento |
| --- | --- | --- | --- |

## Perguntas em aberto
| ID | Pergunta | Evidência | Impacto | Responsável | Status |
| --- | --- | --- | --- | --- | --- |
```

Feche a resposta com a cobertura por pacote:

| Pacote | Interface | Arquivo de pesquisa | Candidatos | Perguntas |
| --- | --- | --- | --- | --- |
| `<NNN>-<slug>` | terminal/web/mobile/NÃO APLICÁVEL | `docs/ux/<NNN>-<slug>-pesquisa.md` ou nenhum | <quantidade> | <IDs ou nenhuma> |

## Regras de SDD e rastreabilidade

- Cite a fonte de cada afirmação sobre público, fluxo atual ou regra; o que não tiver fonte fica `PENDENTE`.
- Referencie requisitos por ID; não copie texto normativo de `SPECIFICATION.md`.
- Interfaces de terminal também têm contrato de acessibilidade (leitores de tela, contraste do terminal, mensagens claras).
- Gamificação serve ao objetivo de aprendizagem; registre padrões manipulativos como antipadrão rejeitado.
- A pesquisa é entrada de `SPECIFICATION.md` (via `/write-ears-spec`) e de `DESIGN.md` (via `/plan-architecture`); não aprove nem altere requisitos.
- Esta etapa não altera `.spec/`; os validadores SDD não se aplicam a ela.

## Definição de pronto

- [ ] Skill e instruções de frontend foram carregadas antes da escrita
- [ ] Todo pacote em escopo com interface tem arquivo em `docs/ux/`, e os sem interface estão listados como `NÃO APLICÁVEL`
- [ ] Existe declaração Jobs-to-be-Done para cada tarefa-alvo
- [ ] A jornada registra ações, pensamentos, sentimentos, dificuldades e oportunidades por etapa
- [ ] O fluxo lista entrada, estados e saídas de sucesso, parcial e bloqueado
- [ ] O contrato WCAG 2.2 AA cobre teclado, anúncios, contraste, foco e alvos
- [ ] Nenhum dado sensível aparece sem máscara
- [ ] Requisitos de UI candidatos e perguntas em aberto estão listados para o `@requirements-engineer`

## Corpo do prompt

Você é `@se-ux-ui-designer`. Pesquise a intenção do usuário e produza artefatos que o implementador possa construir sem redescobrir nada.

**Passo 0 - Carregar skill e instruções.**
Carregue a skill [user-story-refine](../skills/user-story-refine/SKILL.md) e leia as instruções de [frontend](../instructions/frontend.instructions.md) (estados, fluxos e acessibilidade) e de [plataforma frontend](../instructions/frontend-spec.instructions.md) (linha de base de acessibilidade), as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) (estrutura dos pacotes) e o [copilot-instructions.md](../copilot-instructions.md). Se o carregamento de skills não estiver disponível, leia o `SKILL.md` diretamente.

**Passo 1 - Selecionar pacotes e ler as evidências.**
Sem `feature=`, liste os pacotes do índice `.spec/README.md` e selecione os que têm interface e `SPECIFICATION.md` em `Rascunho` ou `Pronto para revisão`; com `feature=`, só aquele. Para cada pacote, leia `SPECIFICATION.md`, `FRD.md`, `NFRD.md`, a fonte e as evidências do fluxo atual. Liste o que se sabe sobre público, contexto e dificuldades, com fonte. Entrada ausente vira pergunta.

**Passo 2 - Declarar necessidades.**
Escreva uma declaração Jobs-to-be-Done por tarefa-alvo, ligada aos requisitos relacionados.

**Passo 3 - Mapear a jornada.**
Para cada tarefa, preencha a jornada por etapa. Não invente emoções ou dificuldades sem evidência; marque `PENDENTE` quando não houver.

**Passo 4 - Especificar o fluxo.**
Descreva entrada, ação principal e estado de cada passo, incluindo carregando, vazio, erro e excesso, e as saídas de sucesso, parcial e bloqueado.

**Passo 5 - Escrever o contrato de acessibilidade.**
Para cada fluxo, defina ordem de teclado, anúncios de leitor de tela, contraste, foco visível e alvos mínimos, com a verificação planejada.

**Passo 6 - Encaminhar.**
Liste requisitos de UI candidatos e perguntas em aberto. Grave `docs/ux/<NNN>-<funcionalidade>-pesquisa.md` de cada pacote como `Rascunho`, responda com a cobertura por pacote e indique o que o `@requirements-engineer` deve formalizar com `/write-ears-spec`.

## Exemplo de invocação

```text
/research-ux fonte=requisitos/requisitos.md
/research-ux fonte=requisitos/requisitos.md feature=001-sala-do-eco
```

Na primeira forma, espere um arquivo em `docs/ux/` para cada pacote com interface e a lista dos pacotes sem interface. Na segunda, espere `docs/ux/001-sala-do-eco-pesquisa.md` com necessidade, jornada, fluxo, contrato WCAG 2.2 AA, requisitos de UI candidatos e perguntas em aberto.
