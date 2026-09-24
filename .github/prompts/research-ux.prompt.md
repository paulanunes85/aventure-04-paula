---
name: "research-ux"
description: "Produz a pesquisa de UX de uma funcionalidade em docs/ux/: declaração Jobs-to-be-Done, jornada, especificação de fluxo e contrato de acessibilidade WCAG 2.2 AA, sem código e sem detalhes inventados."
argument-hint: "feature=NNN-nome-da-funcionalidade fonte=requisitos/requisitos.md"
agent: "se-ux-ui-designer"
tools: ["read", "search", "edit"]
---
# /research-ux

## Objetivo

Descobrir a necessidade do usuário, a jornada e o contrato de acessibilidade de uma funcionalidade com interface, e registrá-los em `docs/ux/<funcionalidade>-*.md` para que requisitos, plano e implementação partam da mesma intenção.

## Quando invocar

Na Etapa 2, depois do primeiro rascunho de `spec.md` e antes de `/plan-architecture`, sempre que a funcionalidade tiver interface (terminal, web ou mobile).

> [!NOTE]
> Não use este prompt para escrever componentes ou estilos (`/implement-task`) nem requisitos EARS (`/write-ears-spec`). Os requisitos de UI candidatos que eu levantar recebem ID do `@requirements-engineer`.

## Pré-condições

- A funcionalidade tem interface com o usuário
- `.spec/<NNN>-<funcionalidade>/spec.md` existe em `Rascunho` ou `Pronto para revisão`
- O time tem evidência do público (fonte, entrevistas ou Product Owner)

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>`
- `fonte=<documento de origem>` e evidências do fluxo atual (planilhas, telas, processos manuais)
- Público: faixa etária, letramento digital, idioma(s) e dispositivo(s)
- Regras de privacidade para dados pessoais ou de menores, se houver

## O que vou fazer

- Carregar a skill `user-story-refine` e as instruções de frontend antes de escrever
- Ler `spec.md`, a fonte e as evidências do fluxo atual
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

## Formato de saída

Arquivo `docs/ux/<funcionalidade>-pesquisa.md` com as seções do agente:

```markdown
# UX: <funcionalidade>

- Status: Rascunho
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

## Regras de SDD e rastreabilidade

- Cite a fonte de cada afirmação sobre público, fluxo atual ou regra; o que não tiver fonte fica `PENDENTE`.
- Referencie requisitos por ID; não copie texto normativo de `spec.md`.
- Interfaces de terminal também têm contrato de acessibilidade (leitores de tela, contraste do terminal, mensagens claras).
- Gamificação serve ao objetivo de aprendizagem; registre padrões manipulativos como antipadrão rejeitado.
- A pesquisa é entrada de `spec.md` e `plan.md`; não aprove nem altere requisitos.

## Definição de pronto

- [ ] Skill e instruções de frontend foram carregadas antes da escrita
- [ ] Existe declaração Jobs-to-be-Done para cada tarefa-alvo
- [ ] A jornada registra ações, pensamentos, sentimentos, dificuldades e oportunidades por etapa
- [ ] O fluxo lista entrada, estados e saídas de sucesso, parcial e bloqueado
- [ ] O contrato WCAG 2.2 AA cobre teclado, anúncios, contraste, foco e alvos
- [ ] Nenhum dado sensível aparece sem máscara
- [ ] Requisitos de UI candidatos e perguntas em aberto estão listados para o `@requirements-engineer`

## Corpo do prompt

Você é `@se-ux-ui-designer`. Pesquise a intenção do usuário e produza artefatos que o implementador possa construir sem redescobrir nada.

**Passo 0 - Carregar skill e instruções.**
Carregue a skill [user-story-refine](../skills/user-story-refine/SKILL.md) e leia as instruções de [frontend](../instructions/frontend.instructions.md) (estados, fluxos e acessibilidade) e de [plataforma frontend](../instructions/frontend-spec.instructions.md) (linha de base de acessibilidade), além do [copilot-instructions.md](../copilot-instructions.md). Se o carregamento de skills não estiver disponível, leia o `SKILL.md` diretamente.

**Passo 1 - Ler as evidências.**
Leia `spec.md`, a fonte e as evidências do fluxo atual. Liste o que se sabe sobre público, contexto e dificuldades, com fonte. Entrada ausente vira pergunta.

**Passo 2 - Declarar necessidades.**
Escreva uma declaração Jobs-to-be-Done por tarefa-alvo, ligada aos requisitos relacionados.

**Passo 3 - Mapear a jornada.**
Para cada tarefa, preencha a jornada por etapa. Não invente emoções ou dificuldades sem evidência; marque `PENDENTE` quando não houver.

**Passo 4 - Especificar o fluxo.**
Descreva entrada, ação principal e estado de cada passo, incluindo carregando, vazio, erro e excesso, e as saídas de sucesso, parcial e bloqueado.

**Passo 5 - Escrever o contrato de acessibilidade.**
Para cada fluxo, defina ordem de teclado, anúncios de leitor de tela, contraste, foco visível e alvos mínimos, com a verificação planejada.

**Passo 6 - Encaminhar.**
Liste requisitos de UI candidatos e perguntas em aberto. Grave `docs/ux/<funcionalidade>-pesquisa.md` como `Rascunho` e indique o que o `@requirements-engineer` deve formalizar com `/write-ears-spec`.

## Exemplo de invocação

```text
/research-ux feature=001-sala-do-eco fonte=requisitos/requisitos.md
```

Espere `docs/ux/001-sala-do-eco-pesquisa.md` com necessidade, jornada, fluxo, contrato WCAG 2.2 AA, requisitos de UI candidatos e perguntas em aberto.
