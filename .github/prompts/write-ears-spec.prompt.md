---
name: "write-ears-spec"
description: "Cria um pacote completo em .spec/<NNN>-<funcionalidade>/ para cada funcionalidade da fonte (ou só a de feature=), com 13 arquivos e 3 pastas: produz SPECIFICATION.md, SOURCE_TRACEABILITY.md, FRD.md e NFRD.md a partir de regras confirmadas (EARS, origem:, SRC-###, Dado/Quando/Então, verificação planejada), os índices das pastas, .spec/README.md e CONSTITUTION.md se ausente, sem inventar regras."
argument-hint: "fonte=requisitos/requisitos.md [feature=NNN-nome-da-funcionalidade]"
agent: "requirements-engineer"
tools: ["read", "search", "edit"]
---
# /write-ears-spec

## Objetivo

Decompor a fonte em funcionalidades e criar um pacote `.spec/<NNN>-<funcionalidade>/` para cada uma, sempre com a estrutura inteira: 13 arquivos em maiúsculas e as pastas `checkpoints/`, `contracts/` e `evidence/`. Esta etapa produz `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md` e o `README.md` de cada pasta; os arquivos de etapas futuras recebem apenas o cabeçalho. Também mantém o índice `.spec/README.md` e cria `CONSTITUTION.md` em `Rascunho` quando ausente. Só regras confirmadas viram requisitos; perguntas em aberto continuam perguntas.

## Quando invocar

Na Etapa 2 (especificação), depois de ler a fonte e, opcionalmente, refinar histórias com `/refine-user-stories`. Sem `feature=`, a invocação cobre todas as funcionalidades da fonte; com `feature=`, cria ou atualiza apenas aquele pacote. Reinvoque para incorporar candidatos de `/research-ux` ou achados de `/validate-spec`.

> [!NOTE]
> Não use este prompt para refinar histórias (`/refine-user-stories`), revisar uma especificação existente (`/validate-spec`) ou desenhar módulos (`/plan-architecture`). Registre apenas requisitos sustentados por evidência.

## Pré-condições

- O documento de origem existe e foi lido pelo time
- As regras em escopo estão explícitas na fonte ou foram confirmadas pelo Product Owner
- Com `feature=`, o pacote informado está no índice `.spec/README.md` ou corresponde a uma funcionalidade identificável na fonte

## Entradas que o time deve fornecer

- `fonte=<caminho do documento de origem>` (obrigatória) e outras fontes (atas, issues, código existente)
- `feature=<NNN>-<nome-da-funcionalidade>` (opcional): restringe a invocação a um pacote; sem ele, todas as funcionalidades da fonte são processadas
- Decisões do Product Owner que confirmem regras ou o corte em funcionalidades, se houver
- Histórias refinadas, se existirem
- Justificativa confirmada para cada capacidade `[GREENFIELD]`

## O que vou fazer

- Carregar SDD/TDD, as instruções aplicáveis e os modelos antes de escrever; usar o modo `Requisitos` e depois `Validação`, aplicando TDD apenas ao planejamento do aceite
- Ler a fonte inteira e decompor em funcionalidades por evidência (fase, capacidade, ator ou superfície de entrega), numerando em sequência e preservando pacotes existentes
- Criar em cada pacote os 13 arquivos e as 3 pastas; arquivos de etapas futuras ficam só com o cabeçalho (`- Status: Não iniciado`, `- Etapa dona: /<prompt>`)
- Dar a todo ID da fonte (`RF-`, `RNF-`, `RN-`) disposição em exatamente um pacote, na seção `Cobertura da fonte` de `SOURCE_TRACEABILITY.md`
- Registrar itens adiados ou de outro pacote em `Escopo e não objetivos` de `SPECIFICATION.md`
- Abrir cada fonte citada e confirmar seção e linhas
- Preservar IDs existentes e atribuir `REQ-NNN`/`NFR-NNN` únicos aos novos requisitos, com linha `origem:`
- Escrever declaração EARS, padrão, prioridade justificada, status, critérios `AC-<ID>-NN` e verificação planejada somente em `SPECIFICATION.md`
- Escrever Dado/Quando/Então somente quando sustentado por evidência ou decisão de escopo
- Preservar perguntas não resolvidas com todos os campos
- Manter em `SOURCE_TRACEABILITY.md` o registro `SRC-###`, a matriz de rastreabilidade, a cobertura da fonte e as disposições históricas
- Gravar `FRD.md` e `NFRD.md` com todas as seções dos modelos, referenciando IDs sem copiar declarações EARS; o envelope de medição de cada NFR fica em `NFRD.md`
- Escrever o `README.md` de `checkpoints/`, `contracts/` e `evidence/` e o índice `.spec/README.md` com todo pacote, critério de corte, IDs da fonte, dependências e status
- Criar pacote em `Rascunho` também para funcionalidade inteiramente bloqueada, com requisitos declarados e bloqueios visíveis
- Criar `CONSTITUTION.md` em `Rascunho` quando ausente, com princípios derivados de fontes verificáveis
- Aplicar `Validação` e registrar o resultado na seção `Validação` de `SPECIFICATION.md`

## O que NÃO vou fazer

- Criar só o primeiro pacote quando o pedido é criar as specs a partir da fonte
- Criar requisito sem `origem:` ou sem `[GREENFIELD]` justificado
- Promover, responder ou mudar o status de premissas e perguntas
- Exigir quantidade fixa de requisitos, diagramas, ADRs ou endpoints
- Criar especificação fora de `.spec/`, usar os nomes proibidos em minúsculas (`spec.md`, `plan.md`, `tasks.md`, `frd.md`, `nfrd.md`) ou mudar o esquema `REQ-NNN`
- Preencher o conteúdo de arquivos de etapas futuras (`ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`, checkpoints e contratos)
- Copiar declarações EARS para fora de `SPECIFICATION.md`
- Omitir seções dos modelos; seções sem conteúdo ficam `NÃO APLICÁVEL: <motivo>`
- Nomear tecnologia de implementação em requisito funcional
- Escrever testes executáveis, código de produto ou commits, nem reportar verificação planejada como resultado observado
- Declarar validadores executados; sem ferramenta de execução, eles ficam `NÃO EXECUTADO (sem ferramenta de execução)`

## Formato de saída

Cada pacote segue a estrutura das [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md). Nesta etapa:

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `SPECIFICATION.md` | Modelo `SPECIFICATION` completo, com `Status: Rascunho` ou `Pronto para revisão` |
| `SOURCE_TRACEABILITY.md` | Modelo `SOURCE_TRACEABILITY` completo |
| `FRD.md`, `NFRD.md` | [Modelo de FRD](../skills/sdd-requirements-engineer/references/frd-template.md) e [modelo de NFRD](../skills/sdd-requirements-engineer/references/nfrd-template.md) completos |
| `checkpoints/README.md`, `contracts/README.md`, `evidence/README.md` | Índice do conteúdo atual de cada pasta |
| Demais nove arquivos | Só o cabeçalho, com `- Status: Não iniciado` e `- Etapa dona: /<prompt>` |

Siga o registro de requisito da [referência EARS](../skills/sdd-requirements-engineer/references/ears-notation.md) e o modelo `SPECIFICATION` dos [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md):

```markdown
### REQ-007: <título curto e imperativo>
origem: SRC-001 (requisitos/requisitos.md#L<início>-L<fim>)

- IDs da fonte: <RF-..>
- Padrão: indesejado
- Prioridade: <P0 | P1 | P2 | P3> - <justificativa pelo escopo confirmado>
- Status: Proposto
- Justificativa: <motivo sustentado pela regra confirmada>

> Se <condição indesejada confirmada>, então o <sistema> deve <uma resposta observável>.

**Sinais de aceite**
- AC-REQ-007-01: Dado <pré-condição evidenciada>, Quando <gatilho>, Então <resultado observável e testável>

**Verificação**
- teste: <menor verificação de comportamento>; falha antes da implementação porque <motivo>; passa quando <resultado esperado>; ciclo em TDD.md
```

Em `SOURCE_TRACEABILITY.md`, mantenha o registro de fontes, a matriz e a cobertura da fonte:

| ID | Classe | Local ou decisão | Data | Autoridade | Notas |
| --- | --- | --- | --- | --- | --- |
| SRC-001 | repositório | `requisitos/requisitos.md#L<início>-L<fim>` | <data> | <responsável> | <regra confirmada> |

| REQ-ID | Padrão EARS | origem | SRC-ID | ID na fonte | AC-ID | Verificação | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-007 | Indesejado | `requisitos/requisitos.md#L<início>-L<fim>` | SRC-001 | RF-.. | AC-REQ-007-01 | teste | Proposto |

| ID na fonte | Disposição | IDs neste pacote ou pacote de destino | Motivo |
| --- | --- | --- | --- |
| RF-.. | derivado/dividido/transferido/adiado/bloqueado/aposentado | REQ-007 ou <NNN>-<slug> | <motivo> |

Feche a resposta com o resumo por pacote:

| Pacote | Funcionalidade | IDs da fonte | Requisitos | Bloqueios | Status |
| --- | --- | --- | --- | --- | --- |
| `<NNN>-<slug>` | <nome> | <RF-.., RNF-..> | <REQ-.., NFR-..> | <IDs ou nenhum> | Rascunho/Pronto para revisão |

## Regras de SDD e rastreabilidade

- As instruções SDD valem para `.spec/**`; leia-as explicitamente antes de escrever para que estrutura, completude, evidência, atomicidade EARS, rastreabilidade e status governem a tarefa.
- Todo arquivo produzido contém todas as seções do seu modelo, na ordem do modelo; completude não autoriza invenção.
- A declaração EARS, os critérios e a verificação vivem só em `SPECIFICATION.md`; `FRD.md`, `NFRD.md` e `SOURCE_TRACEABILITY.md` referenciam IDs.
- Use `deve` nas cláusulas normativas e as palavras-chave em português da referência EARS. Preserve significado e IDs ao normalizar requisitos existentes.
- `SRC-###` complementa, mas não substitui, a linha `origem:` com caminho verificável.
- Não invente prioridade, métrica, aprovação ou resultado de teste. Campos sem evidência ficam `PENDENTE` ou `BLOQUEADO`, com impacto e responsável; requisitos bloqueados não são apresentados como prontos.
- Um NFR só é normativo quando métrica, carga, janela de observação, ambiente e responsável estão definidos em `NFRD.md`.
- IDs, contagens e status concordam entre os arquivos do pacote e o índice `.spec/README.md`.
- Este prompt não tem ferramenta de execução: registre os validadores como `NÃO EXECUTADO (sem ferramenta de execução)` na seção `Validação`, faça a verificação manual das instruções SDD e liste para o time, a partir da raiz, `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` e `python3 -B .github/scripts/validate-sdd.py` (`--package NNN` para restringir), com a saída salva em `evidence/<AAAA-MM-DD>-validate-sdd.md`.

## Definição de pronto

- [ ] SDD/TDD, as instruções aplicáveis e os modelos foram carregados e aplicados em `Requisitos` e `Validação`, com TDD limitado ao aceite planejado
- [ ] Toda funcionalidade da fonte tem pacote (ou só a de `feature=`), e o índice `.spec/README.md` lista todo pacote
- [ ] Todo pacote tem os 13 arquivos e as 3 pastas com `README.md`; arquivos de etapas futuras estão `Não iniciado` com a etapa dona
- [ ] Todo ID da fonte tem disposição em exatamente um pacote, em `SOURCE_TRACEABILITY.md`
- [ ] `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md` e `NFRD.md` têm todas as seções dos modelos, com `NÃO APLICÁVEL` justificado onde couber
- [ ] `CONSTITUTION.md` existe (reutilizada ou criada em `Rascunho`) e `SPECIFICATION.md` registra o caminho
- [ ] Todo requisito tem resposta EARS observável com `deve`, metadados da skill, ID de aceite estável e `origem:` válida ou `[GREENFIELD]` justificado
- [ ] Perguntas em aberto estão fora dos requisitos e mantêm seu status
- [ ] A matriz liga cada REQ-ID à evidência revisada
- [ ] Critérios verificáveis por teste identificam a verificação planejada e a evidência esperada; outros métodos têm justificativa
- [ ] Gates, bloqueios e validadores (`NÃO EXECUTADO` com os comandos) estão na seção `Validação`; cada pacote fica `Rascunho` ou `Pronto para revisão` até aprovação humana explícita

## Corpo do prompt

Você é `@requirements-engineer`. Promova regras confirmadas a requisitos EARS formais sem inventar evidência.

**Passo 0 - Carregar SDD, TDD e instruções.**
Antes de ler as entradas, leia as [instruções de artefatos SDD](../instructions/sdd-artifacts.instructions.md) e carregue as skills [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) e [tdd-workflow](../skills/tdd-workflow/SKILL.md). Se o carregamento de skills não estiver disponível, leia cada `SKILL.md` diretamente. Leia as [instruções de testes](../instructions/tests.instructions.md) para planejar o aceite. Selecione `Requisitos` e leia a [referência EARS](../skills/sdd-requirements-engineer/references/ears-notation.md), o [modelo de FRD](../skills/sdd-requirements-engineer/references/frd-template.md), o [modelo de NFRD](../skills/sdd-requirements-engineer/references/nfrd-template.md), os [modelos de artefatos SDD](../skills/sdd-requirements-engineer/references/spec-templates.md) e os [quality gates](../skills/sdd-requirements-engineer/references/quality-gates.md).

**Passo 1 - Decompor a fonte em funcionalidades.**
Leia a fonte inteira. Sem `feature=`, identifique toda funcionalidade por evidência (fase, capacidade, ator ou superfície de entrega) e registre o critério de corte; com `feature=`, limite-se àquele pacote. Reutilize pacotes existentes em `.spec/` e numere os novos em sequência. Atribua cada ID da fonte (`RF-`, `RNF-`, `RN-`) a exatamente um pacote.

**Passo 2 - Criar a estrutura.**
Em cada pacote, crie os 13 arquivos e as pastas `checkpoints/`, `contracts/` e `evidence/`, cada uma com `README.md`. Os arquivos de etapas futuras recebem apenas o cabeçalho do modelo, com `- Status: Não iniciado` e `- Etapa dona: /plan-architecture` ou `/break-down-tasks`. Os YAML de checkpoints e o `contracts/manifest.yaml` são criados pelas etapas donas.

**Passo 3 - Confirmar escopo.**
Por pacote, liste apenas regras **confirmadas**. Registre itens adiados ou de outro pacote em `Escopo e não objetivos`. Não inclua regras inferidas nem perguntas. Funcionalidade inteiramente bloqueada segue com os requisitos declarados, os bloqueios visíveis e status `Rascunho`.

**Passo 4 - Validar cada fonte.**
Abra cada fonte citada e confirme seção e linhas. Referência inválida vira pergunta em aberto. Associe cada fonte primária a um `SRC-###` estável e mantenha o caminho completo na linha `origem:`.

**Passo 5 - Escrever o requisito EARS.**
Preserve IDs existentes e atribua `REQ-NNN` (ou `NFR-NNN`) único a cada novo requisito em `SPECIFICATION.md`. Aplique o contrato da skill: exatamente uma classificação e uma resposta observável com `deve`. Não mantenha modelos EARS concorrentes neste prompt. Para capacidade nova sem fonte, use `[GREENFIELD]` seguido apenas da justificativa fornecida pelo time.

**Passo 6 - Registrar critérios de aceite.**
Escreva Dado/Quando/Então só para comportamento evidenciado. Use `AC-REQ-NNN-NN` para critérios novos. Para cada critério verificável por teste, aplique TDD para identificar a menor verificação de comportamento, sua entrada, por que deve falhar antes da implementação e o resultado esperado. Mantenha isso como verificação planejada em `SPECIFICATION.md`; o ciclo detalhado é escrito em `TDD.md` por `/break-down-tasks`. Para inspeção, análise, demonstração ou medição, registre o método e marque o ciclo TDD `NÃO APLICÁVEL` com motivo.

**Passo 7 - Preservar perguntas em aberto.**
Copie itens não validados para `Premissas, bloqueios e perguntas em aberto`, com evidência `caminho#Lx-Ly`, impacto, interpretações, responsável e status. Não os responda nem altere.

**Passo 8 - Montar a rastreabilidade.**
Em `SOURCE_TRACEABILITY.md`, mantenha o registro de fontes, a matriz `REQ-ID | Padrão EARS | origem | SRC-ID | ID na fonte | AC-ID | Verificação | Estado`, a `Cobertura da fonte` com a disposição de cada ID da fonte atribuído ao pacote e as `Disposições históricas`. Confira os vínculos bidirecionais entre fontes, requisitos e aceite.

**Passo 9 - Montar FRD, NFRD, índices e constituição.**
Preencha todas as seções de `FRD.md` e `NFRD.md` a partir das mesmas fontes, referenciando IDs sem copiar declarações. Registre em `NFRD.md` a aplicabilidade de cada categoria e o envelope de medição de cada NFR. Escreva o `README.md` de cada pasta e o índice `.spec/README.md` com o mapa de funcionalidades e a cobertura da fonte de todos os pacotes. Se `CONSTITUTION.md` não existir, crie-a em `Rascunho` com princípios `CON-NNN` que citam sua fonte.

**Passo 10 - Validar e gravar.**
Aplique `Validação` aos gates de estrutura, completude, requisito e rastreabilidade de cada pacote. Registre cada resultado na seção `Validação` de `SPECIFICATION.md` como `PASS`, `FAIL`, `BLOQUEADO` ou `NÃO APLICÁVEL`, com evidência ou motivo. Registre os validadores como `NÃO EXECUTADO (sem ferramenta de execução)`, faça a verificação manual e liste os comandos para o time. Grave cada pacote como `Rascunho` ou `Pronto para revisão` e responda com o resumo por pacote e o modelo de saída da skill SDD.

## Exemplo de invocação

```text
/write-ears-spec fonte=requisitos/requisitos.md
/write-ears-spec fonte=requisitos/requisitos.md feature=001-sala-do-eco
```

Na primeira forma, espere um pacote completo para cada funcionalidade da fonte e o índice `.spec/README.md` com a disposição de todo ID da fonte. Na segunda, espere apenas `.spec/001-sala-do-eco/` criado ou atualizado, com `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md` e `NFRD.md` produzidos, os demais arquivos só com cabeçalho e as perguntas em aberto preservadas.
