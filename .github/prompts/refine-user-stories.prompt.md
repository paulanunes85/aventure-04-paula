---
name: "refine-user-stories"
description: "Refina o documento de requisitos ou um épico em histórias de usuário INVEST com critérios Dado/Quando/Então e perguntas em aberto, sem inventar regras, preparando a entrada de /write-ears-spec."
argument-hint: "fonte=requisitos/requisitos.md epico=<seção ou objetivo> [saida=<caminho>]"
agent: "requirements-engineer"
tools: ["read", "search", "edit"]
---
# /refine-user-stories

## Objetivo

Transformar o documento de requisitos de origem (ou um épico dele) em histórias de usuário verticais, INVEST, com critérios de aceite Dado/Quando/Então e perguntas em aberto explícitas. Histórias expressam intenção; elas não substituem os requisitos EARS de `SPECIFICATION.md`.

## Quando invocar

Na Etapa 1 (descoberta), antes de `/write-ears-spec`, quando o insumo é prosa informal, um épico grande ou um documento com fases, termos vagos ou contradições.

> [!NOTE]
> Não use este prompt para escrever requisitos normativos (`/write-ears-spec`), pesquisar UX (`/research-ux`) ou planejar arquitetura (`/plan-architecture`). Registre apenas o que a fonte sustenta.

## Pré-condições

- O documento de origem existe e está declarado em [copilot-instructions.md](../copilot-instructions.md) ou é informado na invocação
- O time definiu qual épico, fase ou seção entra no refinamento

## Entradas que o time deve fornecer

- `fonte=<caminho do documento de origem>`
- `epico=<seção, fase ou objetivo>`
- Persona(s) e objetivo de negócio, quando não estiverem na fonte
- Restrições conhecidas (regulatórias, técnicas, de UX, faixa etária do público)
- `saida=<caminho>` apenas se o time quiser gravar as histórias em arquivo

## O que vou fazer

- Carregar a skill `user-story-refine` e as instruções SDD antes de escrever
- Ler a fonte inteira e citar a seção e as linhas que sustentam cada história
- Aplicar INVEST e dividir verticalmente com os padrões de divisão da skill
- Escrever caminho feliz, caso de borda e caminho de erro em Dado/Quando/Então
- Registrar contradições, termos vagos e fases sem decisão como perguntas em aberto com responsável
- Ligar cada história a um `REQ-NNN` existente ou marcá-la `REQ pendente` para `/write-ears-spec`

## O que NÃO vou fazer

- Inventar persona, regra, valor, prioridade ou estimativa ausente da fonte
- Resolver ambiguidade escolhendo uma interpretação em silêncio
- Dividir horizontalmente (história de backend + história de UI) ou escrever histórias como tarefas técnicas
- Criar ou editar arquivos em `.spec/` (a estrutura dos pacotes é criada por `/write-ears-spec`), código ou testes
- Gravar arquivos quando `saida=` não foi informado

## Formato de saída

Use o modelo de saída da skill `user-story-refine`, acrescentando a linha de fonte:

```markdown
### US-001: <título curto>
**Como** <persona>
**Eu quero** <capacidade>
**Para que** <resultado de negócio>

**Critérios de aceite**
- Dado <contexto>, Quando <ação>, Então <resultado>
- Dado <caso de borda>, Quando <ação>, Então <resultado>
- Dado <condição de erro>, Quando <ação>, Então <resultado>

**Fonte**: requisitos/requisitos.md#L<início>-L<fim>
**Rastreia para**: REQ-NNN | REQ pendente
**Esforço**: P / M / G | PENDENTE (sem evidência)
**Dependências**: US-NNN | nenhuma
**Perguntas em aberto**: Q-001 | nenhuma
```

Feche com a tabela de perguntas em aberto:

| ID | Pergunta | Evidência (`caminho#Lx-Ly`) | Interpretações possíveis | Impacto | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 | <pergunta> | `<caminho>#L10-L12` | <A> / <B> | <impacto> | Product Owner | Aberta |

## Regras de SDD e rastreabilidade

- Histórias não usam `deve` normativo; a redação EARS pertence a `/write-ears-spec`.
- Preserve IDs de requisitos existentes na fonte; não renumere.
- Exemplos com resultado ambíguo viram perguntas, não critérios de aceite.
- Termos vagos ("bonito", "rápido", "inteligente") viram perguntas com pedido de critério verificável.
- Dados de menores, pessoais ou sensíveis citados na fonte geram pergunta sobre privacidade, nunca um valor suposto.

## Definição de pronto

- [ ] A skill `user-story-refine` e as instruções aplicáveis foram carregadas antes da escrita
- [ ] Toda história cita a fonte com caminho e linhas
- [ ] Toda história atende ao INVEST e está dividida verticalmente
- [ ] Toda história tem caminho feliz, borda e erro em Dado/Quando/Então
- [ ] Toda história rastreia para um `REQ-NNN` ou está marcada `REQ pendente`
- [ ] Contradições, termos vagos e entradas ausentes estão na tabela de perguntas, com responsável

## Corpo do prompt

Você é `@requirements-engineer`. Refine o épico em histórias sem inventar regras.

**Passo 0 - Carregar skill e instruções.**
Carregue a skill [user-story-refine](../skills/user-story-refine/SKILL.md) e leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) e o [copilot-instructions.md](../copilot-instructions.md). Se o carregamento de skills não estiver disponível, leia o `SKILL.md` diretamente.

**Passo 1 - Ler a fonte e delimitar o épico.**
Leia a fonte inteira, não apenas a seção citada. Liste as seções do épico com linhas. Se a fonte declara fases com decisão pendente, registre a decisão como pergunta e refine apenas o que está inequivocamente no épico.

**Passo 2 - Confirmar personas e resultado.**
Extraia personas, objetivo de negócio e restrições da fonte. Entrada ausente vira pergunta em aberto; não suponha.

**Passo 3 - Rascunhar e dividir.**
Escreva uma história por resultado de usuário. Aplique INVEST; se uma história falhar em "pequena" ou "testável", divida com os padrões da skill (etapas do fluxo, regra de negócio, variação de dados, caminho feliz versus borda, interface).

**Passo 4 - Escrever critérios de aceite.**
Para cada história, escreva caminho feliz, borda e erro. Use apenas exemplos da fonte; exemplos com resultado em aberto viram perguntas.

**Passo 5 - Registrar perguntas.**
Monte a tabela de perguntas com evidência, interpretações, impacto e responsável. Não responda nem escolha interpretações.

**Passo 6 - Validar e entregar.**
Aplique o gate de qualidade da skill a cada história e reporte `PASS` ou `FAIL` com motivo. Grave em `saida=` somente se informado; caso contrário, devolva no chat. Agrupe as histórias pela funcionalidade da fonte a que pertencem, para que `/write-ears-spec` crie um pacote por funcionalidade. Indique quais histórias estão prontas para `/write-ears-spec` e quais dependem de resposta do Product Owner.

## Exemplo de invocação

```text
/refine-user-stories fonte=requisitos/requisitos.md epico="Fase 1 - versão no terminal"
```

Espere histórias INVEST com fonte, critérios Dado/Quando/Então e uma tabela de perguntas em aberto para o Product Owner.
