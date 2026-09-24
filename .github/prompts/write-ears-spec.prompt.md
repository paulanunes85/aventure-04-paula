---
name: "write-ears-spec"
description: "Escreve o pacote de requisitos completo em .spec/<NNN>-<funcionalidade>/ (frd.md, nfrd.md e spec.md, mais CONSTITUTION.md se ausente) com requisitos EARS confirmados, linha origem:, registro SRC-###, critérios Dado/Quando/Então e verificação planejada via TDD, sem inventar regras."
argument-hint: "feature=NNN-nome-da-funcionalidade fonte=requisitos/requisitos.md"
agent: "requirements-engineer"
tools: ["read", "search", "edit"]
---
# /write-ears-spec

## Objetivo

Transformar apenas regras confirmadas da fonte em requisitos EARS formais em `.spec/<NNN>-<funcionalidade>/spec.md` e gravar, no mesmo diretório, `frd.md` e `nfrd.md` completos. Se o repositório não tiver `CONSTITUTION.md`, criar a constituição em `Rascunho`. Perguntas em aberto continuam perguntas; não preencha requisitos, critérios ou arquitetura com suposições.

## Quando invocar

Na Etapa 2 (especificação), depois que o time escolheu a funcionalidade e, opcionalmente, refinou histórias com `/refine-user-stories`.

> [!NOTE]
> Não use este prompt para refinar histórias (`/refine-user-stories`), revisar uma especificação existente (`/validate-spec`) ou desenhar módulos (`/plan-architecture`). Registre apenas requisitos sustentados por evidência.

## Pré-condições

- O documento de origem existe e foi lido pelo time
- O time identificou `.spec/<NNN>-<funcionalidade>/`
- As regras em escopo foram confirmadas pelo Product Owner (ou estão explícitas na fonte)

## Entradas que o time deve fornecer

- `feature=<NNN>-<nome-da-funcionalidade>`
- `fonte=<caminho do documento de origem>` e outras fontes (atas, issues, código existente)
- O subconjunto de regras **confirmadas** que pertence à funcionalidade
- Histórias refinadas, se existirem
- Justificativa confirmada para cada capacidade `[GREENFIELD]`

## O que vou fazer

- Carregar SDD/TDD e as instruções aplicáveis antes de escrever; usar o modo `Requisitos` e depois `Validação`, aplicando TDD apenas ao planejamento do aceite
- Confirmar escopo e registrar itens adiados em `Escopo e não objetivos` do `spec.md`
- Abrir cada fonte citada e confirmar seção e linhas
- Preservar IDs existentes e atribuir `REQ-NNN`/`NFR-NNN` únicos aos novos requisitos, com linha `origem:`
- Registrar padrão EARS, fonte `SRC-###`, prioridade justificada, justificativa, status e verificação planejada conforme o contrato da skill
- Escrever Dado/Quando/Então somente quando sustentado por evidência ou decisão de escopo
- Preservar perguntas não resolvidas com todos os campos
- Manter registro de fontes e matriz de rastreabilidade e aplicar `Validação` antes da entrega
- Gravar `frd.md` e `nfrd.md` com todas as seções dos modelos, referenciando os IDs de `spec.md` sem copiar declarações EARS
- Criar `CONSTITUTION.md` em `Rascunho` quando ausente, com princípios derivados de fontes verificáveis

## O que NÃO vou fazer

- Criar requisito sem `origem:` ou sem `[GREENFIELD]` justificado
- Promover, responder ou mudar o status de premissas e perguntas
- Exigir quantidade fixa de requisitos, diagramas, ADRs ou endpoints
- Criar especificação fora de `.spec/`, mudar o esquema `REQ-NNN` ou gerar `plan.md`/`tasks.md` para este pedido
- Omitir seções dos modelos de FRD, NFRD ou `spec.md`; seções sem conteúdo ficam `NÃO APLICÁVEL` com motivo
- Nomear tecnologia de implementação em requisito funcional
- Escrever testes executáveis, código de produto ou commits, nem reportar verificação planejada como resultado observado

## Formato de saída

Siga o registro de requisito da [referência EARS](../skills/sdd-requirements-engineer/references/ears-notation.md) e o modelo de `spec.md` dos [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md):

```markdown
### REQ-007: <título curto e imperativo>
origem: SRC-001 (requisitos/requisitos.md#L<início>-L<fim>)

- Padrão: indesejado
- Prioridade: <P0 | P1 | P2 | P3> - <justificativa pelo escopo confirmado>
- Status: Proposto
- Justificativa: <motivo sustentado pela regra confirmada>

> Se <condição indesejada confirmada>, então o <sistema> deve <uma resposta observável>.

**Sinais de aceite**
- AC-REQ-007-01: Dado <pré-condição evidenciada>, Quando <gatilho>, Então <resultado observável e testável>

**Verificação**
- teste: <menor verificação de comportamento>; falha antes da implementação porque <motivo>; passa quando <resultado esperado>
```

Mantenha no mesmo `spec.md` o registro de fontes e a matriz:

| ID | Classe | Local ou decisão | Data | Autoridade | Notas |
| --- | --- | --- | --- | --- | --- |
| SRC-001 | repositório | `requisitos/requisitos.md#L<início>-L<fim>` | <data> | <responsável> | <regra confirmada> |

| REQ-ID | Padrão EARS | origem | SRC-ID | AC-ID | Verificação |
| --- | --- | --- | --- | --- | --- |
| REQ-007 | Indesejado | `requisitos/requisitos.md#L<início>-L<fim>` | SRC-001 | AC-REQ-007-01 | teste |

## Regras de SDD e rastreabilidade

- As instruções SDD valem para `.spec/**`; leia-as explicitamente antes de escrever para que evidência, atomicidade EARS, rastreabilidade e status governem a tarefa.
- Use `deve` nas cláusulas normativas e as palavras-chave em português da referência EARS. Preserve significado e IDs ao normalizar requisitos existentes.
- `SRC-###` complementa, mas não substitui, a linha `origem:` com caminho verificável.
- Não invente prioridade, métrica, aprovação ou resultado de teste. Campos sem evidência ficam `PENDENTE` ou `BLOQUEADO`, com impacto e responsável; requisitos bloqueados não são apresentados como prontos.
- Um NFR só é normativo quando métrica, carga, janela de observação, ambiente e responsável estão definidos.
- Carregue apenas os recursos do modo selecionado. Não suponha que validadores citados pela skill existam; registre verificações não executadas e o motivo.

## Definição de pronto

- [ ] SDD/TDD e as instruções aplicáveis foram carregados e aplicados em `Requisitos` e `Validação`, com TDD limitado ao aceite planejado
- [ ] `spec.md` contém apenas requisitos da funcionalidade
- [ ] `frd.md` e `nfrd.md` existem com todas as seções dos modelos, e seus resumos batem com `spec.md`
- [ ] `CONSTITUTION.md` existe (reutilizada ou criada em `Rascunho`) e `spec.md` registra o caminho
- [ ] Todo requisito tem resposta EARS observável com `deve`, metadados da skill, ID de aceite estável e `origem:` válida ou `[GREENFIELD]` justificado
- [ ] Perguntas em aberto estão fora dos requisitos e mantêm seu status
- [ ] A matriz liga cada REQ-ID à evidência revisada
- [ ] Critérios verificáveis por teste identificam a verificação planejada e a evidência esperada; outros métodos têm justificativa
- [ ] Gates e bloqueios estão registrados; a especificação fica `Rascunho` ou `Pronto para revisão` até aprovação humana explícita

## Corpo do prompt

Você é `@requirements-engineer`. Promova regras confirmadas a requisitos EARS formais sem inventar evidência.

**Passo 0 - Carregar SDD, TDD e instruções.**
Antes de ler as entradas, leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) e carregue as skills [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e [tdd-workflow](../skills/tdd-workflow/SKILL.md). Se o carregamento de skills não estiver disponível, leia cada `SKILL.md` diretamente. Leia as [instruções de testes](../instructions/tests.instructions.md) para planejar o aceite. Selecione `Requisitos` e leia a [referência EARS](../skills/sdd-requirements-engineer/references/ears-notation.md), o [modelo de FRD](../skills/sdd-requirements-engineer/references/frd-template.md), o [modelo de NFRD](../skills/sdd-requirements-engineer/references/nfrd-template.md), os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) e os [quality gates](../skills/sdd-requirements-engineer/references/quality-gates.md).

**Passo 1 - Confirmar escopo.**
Liste apenas regras **confirmadas** atribuídas à funcionalidade. Registre itens adiados em `Escopo e não objetivos`. Não inclua regras inferidas nem perguntas.

**Passo 2 - Validar cada fonte.**
Abra cada fonte citada e confirme seção e linhas. Referência inválida vira pergunta em aberto. Associe cada fonte primária a um `SRC-###` estável e mantenha o caminho completo na linha `origem:`.

**Passo 3 - Escrever o requisito EARS.**
Preserve IDs existentes e atribua `REQ-NNN` (ou `NFR-NNN`) único a cada novo requisito. Aplique o contrato da skill: exatamente uma classificação e uma resposta observável com `deve`. Não mantenha modelos EARS concorrentes neste prompt. Para capacidade nova sem fonte, use `[GREENFIELD]` seguido apenas da justificativa fornecida pelo time.

**Passo 4 - Registrar critérios de aceite.**
Escreva Dado/Quando/Então só para comportamento evidenciado. Use `AC-REQ-NNN-NN` para critérios novos. Para cada critério verificável por teste, aplique TDD para identificar a menor verificação de comportamento, sua entrada, por que deve falhar antes da implementação e o resultado esperado. Mantenha isso como verificação planejada em `spec.md`. Para inspeção, análise, demonstração ou medição, registre o método e marque o ciclo TDD `NÃO APLICÁVEL` com motivo.

**Passo 5 - Preservar perguntas em aberto.**
Copie itens não validados para `Premissas, bloqueios e perguntas em aberto`, com evidência `caminho#Lx-Ly`, impacto, interpretações, responsável e status. Não os responda nem altere.

**Passo 6 - Montar a matriz.**
Mantenha o registro de fontes e a tabela `REQ-ID | Padrão EARS | origem | SRC-ID | AC-ID | Verificação`. Confira os vínculos bidirecionais entre fontes, requisitos e aceite.

**Passo 7 - Montar FRD, NFRD e constituição.**
Preencha todas as seções de `frd.md` e `nfrd.md` a partir das mesmas fontes, referenciando os IDs de `spec.md` sem copiar declarações. Registre em `nfrd.md` a aplicabilidade de cada categoria e o envelope de medição de cada NFR. Se `CONSTITUTION.md` não existir, crie-a em `Rascunho` com princípios `CON-NNN` que citam sua fonte.

**Passo 8 - Validar e gravar.**
Aplique `Validação` aos gates de requisito e rastreabilidade. Registre cada resultado como `PASS`, `FAIL`, `BLOQUEADO` ou `NÃO APLICÁVEL`, com evidência ou motivo. Verifique se algum validador citado existe e cobre este artefato; com apenas leitura/busca/edição, reporte comandos como não executados. Grave `.spec/<NNN>-<funcionalidade>/frd.md`, `nfrd.md` e `spec.md` como `Rascunho` ou `Pronto para revisão` e responda com o modelo de saída da skill SDD.

## Exemplo de invocação

```text
/write-ears-spec feature=001-sala-do-eco fonte=requisitos/requisitos.md
```

Espere `frd.md`, `nfrd.md` e `spec.md` completos em `.spec/001-sala-do-eco/`, com requisitos EARS sustentados por evidência, linha `origem:`, registro de fontes, matriz de rastreabilidade e perguntas em aberto preservadas.
