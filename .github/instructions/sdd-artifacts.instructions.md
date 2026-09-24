---
description: "Use ao criar ou editar artefatos SDD em .spec/ (SPECIFICATION, SOURCE_TRACEABILITY, FRD, NFRD, ANALYSIS, DESIGN, DECISIONS, TASKS, TESTING, TDD, CHECKLIST, CROSS_ANALYSIS, VERIFICATION, checkpoints, contracts, evidence), CONSTITUTION.md, CODEMAP.md e ADRs: estrutura obrigatória, decomposição em funcionalidades, completude, EARS, rastreabilidade, evidências e status."
applyTo: ".spec/**,docs/adr/**/*.md,docs/decisions/**/*.md,CONSTITUTION.md,CODEMAP.md"
---

# Artefatos de Spec-Driven Development (SDD)

A skill [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) é dona dos procedimentos, e os [modelos de artefatos](../skills/sdd-requirements-engineer/references/spec-templates.md) são donos do conteúdo de cada arquivo. Estas instruções são donas da estrutura, dos nomes, da completude e da validação. Toda especificação fica sempre em `.spec/` na raiz do repositório; não crie `specs/`, `.specs/` nem arquivos em minúsculas (`spec.md`, `plan.md`, `tasks.md`).

## Estrutura obrigatória de cada pacote

Todo pacote `.spec/<NNN>-<funcionalidade>/` tem exatamente esta estrutura:

```text
.spec/<NNN>-<funcionalidade>/
  checkpoints/   README.md, spec-to-plan.yaml, plan-to-tasks.yaml, test-coverage.yaml
  contracts/     README.md, manifest.yaml, <contratos>
  evidence/      README.md, <AAAA-MM-DD>-<assunto>.md
  ANALYSIS.md
  CHECKLIST.md
  CROSS_ANALYSIS.md
  DECISIONS.md
  DESIGN.md
  FRD.md
  NFRD.md
  SOURCE_TRACEABILITY.md
  SPECIFICATION.md
  TASKS.md
  TDD.md
  TESTING.md
  VERIFICATION.md
```

| Etapa | Prompt | Arquivos que produz |
| --- | --- | --- |
| Requisitos | `/write-ears-spec` | Cria a estrutura inteira; produz `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md` e os índices das três pastas |
| Validação | `/validate-spec` | Atualiza os quatro arquivos de requisitos e a seção `Validação` |
| Design | `/plan-architecture` | `ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `contracts/`, `checkpoints/spec-to-plan.yaml`, `CODEMAP.md` e ADRs |
| Tarefas | `/break-down-tasks` | `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`, `checkpoints/plan-to-tasks.yaml`, `checkpoints/test-coverage.yaml` |
| Construção | `/implement-task` | Código, testes, `evidence/`, registro de `TASKS.md`, resultados em `VERIFICATION.md` e `TDD.md` |
| Qualidade | `/verify-quality` | Testes, `evidence/`, `TESTING.md`, `VERIFICATION.md`, `checkpoints/test-coverage.yaml` |

No nível do repositório ficam `CONSTITUTION.md`, `CODEMAP.md`, o índice `.spec/README.md`, `docs/adr/` e `docs/ux/`.

## Arquivos de etapas futuras

- `/write-ears-spec` cria os 13 arquivos e as 3 pastas. Arquivos de etapas futuras recebem apenas o cabeçalho, com `- Status: Não iniciado` e `- Etapa dona: /<prompt>`.
- A etapa dona substitui o cabeçalho pelo modelo completo. Nenhum arquivo de uma etapa fica `Não iniciado` depois que uma etapa posterior começa.
- Todo arquivo tem `- Status:` com um destes valores: `Não iniciado`, `Rascunho`, `Pronto para revisão`, `Planejado`, `Aprovado`, `Implementado`, `Verificado`.

## Decomposição em funcionalidades

- Um pedido para criar as specs a partir de uma fonte cria **um pacote para cada funcionalidade** identificada na fonte, e não só o primeiro. Só um `feature=` explícito restringe o pedido a um pacote.
- Corte as funcionalidades por evidência da fonte (fase, capacidade, ator ou superfície de entrega) e registre o critério no índice. Numere em sequência (`001`, `002`...) preservando pacotes existentes.
- Todo ID da fonte (`RF-`, `RNF-`, `RN-` ou o esquema da fonte) tem disposição em exatamente um pacote, em `SOURCE_TRACEABILITY.md`: derivado, dividido, transferido para outro pacote, adiado, bloqueado ou aposentado.
- Funcionalidade inteiramente bloqueada também recebe pacote, em `Rascunho`, com os requisitos declarados e os bloqueios visíveis.
- `.spec/README.md` segue o modelo `ÍNDICE`: lista todo pacote, o critério de corte, os IDs da fonte, as dependências entre pacotes e o status.

## Completude

- Todo arquivo produzido contém todas as seções do seu modelo, na ordem do modelo. Não omita seções.
- Seção sem conteúdo aplicável fica `NÃO APLICÁVEL: <motivo>`. Valor desconhecido fica `PENDENTE` ou `BLOQUEADO`, com responsável e impacto.
- Completude não autoriza invenção: nenhuma meta, ator, regra, decisão, diagrama de comportamento inexistente, evidência ou aprovação é criada para preencher uma seção.
- `DESIGN.md` cobre as 14 visões do portfólio. Contexto do sistema, implantação, modelo de estados, sequências críticas e fluxo de dados levam diagrama Mermaid quando aplicáveis; caso contrário, `NÃO APLICÁVEL` com motivo.
- `contracts/manifest.yaml` declara cada contrato ou `nao-aplicavel` com motivo. Cada pasta tem `README.md` que lista seu conteúdo.

## Declaração canônica e referências

- A declaração EARS, os critérios `AC-<ID>-NN` e a verificação de cada requisito vivem somente em `SPECIFICATION.md`.
- `SOURCE_TRACEABILITY.md` é dono do registro `SRC-###`, da matriz, da cobertura da fonte e das disposições históricas.
- `FRD.md` e `NFRD.md` referenciam requisitos por ID e acrescentam só o que é deles (domínio, atores, justificativa, dependências, falha e recuperação, aplicabilidade e envelope de medição). O envelope de medição de cada NFR vive em `NFRD.md`.
- Os demais arquivos e os checkpoints referenciam IDs; resumos não redefinem significado.
- IDs, contagens e status concordam entre todos os arquivos do pacote e o índice.

## Constituição

Reutilize `CONSTITUTION.md` quando existir. Se não existir, `/write-ears-spec` cria `CONSTITUTION.md` na raiz com o modelo `CONSTITUTION`, status `Rascunho`, derivando cada princípio `CON-NNN` de uma fonte verificável, como [copilot-instructions.md](../copilot-instructions.md) e as instruções em `.github/instructions/`. Não crie princípios sem fonte nem declare aprovação. `SPECIFICATION.md` registra o caminho da constituição.

## Requisitos e evidências

- Use `REQ-NNN` para requisitos funcionais e `NFR-NNN` para não funcionais, salvo se o repositório já tiver outro esquema. Preserve IDs existentes.
- Classifique o padrão EARS e escreva uma única resposta observável usando `deve` (ou `shall` em projetos em inglês).
- Coloque uma linha `origem:` até 20 linhas após a declaração de cada requisito. Ela cita `SRC-###` do registro de fontes, caminho de arquivo existente com âncora `#Lx-Ly` ou `[GREENFIELD]` com justificativa explícita.
- Dê aos critérios de aceite IDs estáveis `AC-<ID>-NN` em formato Dado/Quando/Então, e a cada critério um ciclo em `TDD.md`.
- Evidências executadas ficam em `evidence/` com data, comando ou origem e o ID verificado, sem segredos, credenciais ou dados pessoais.
- Mantenha separados rascunho, aprovação, implementação e verificação. Registre `PENDENTE`, `BLOQUEADO` ou `NÃO APLICÁVEL` com motivo em vez de inventar execução ou aceite.

## Apresentação de diagramas e tarefas

- Aplique o [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md) a todo diagrama: tema claro universal e classes canônicas.
- Em `DESIGN.md`, mapeie requisitos para componentes, tarefas, dependências, testes/evidências e estado atual versus alvo.
- Em `TASKS.md`, use checkboxes com ID estável, `[S]`/`[P]`, rastreio de requisito, superfície de mudança e aceite. Uma tarefa marcada exige evidência em `evidence/` e entrada no registro datado.
- Mantenha o grafo de tarefas consistente com a lista e com `checkpoints/plan-to-tasks.yaml`.

## Verificações executáveis

Execute a partir da raiz, nesta ordem, e registre comando, data, código de saída e resumo em `VERIFICATION.md` (ou na seção `Validação` de `SPECIFICATION.md` antes de existir a etapa de tarefas), com a saída salva em `evidence/`:

| Ordem | Comando | O que prova | Quando |
| --- | --- | --- | --- |
| 1 | `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` | O próprio validador detecta cada defeito do contrato | Antes de confiar no resultado e após mudar o validador |
| 2 | `python3 -B .github/scripts/validate-sdd.py` | Estrutura de 13 arquivos e 3 pastas, `Status` e etapas, completude de seções, `origem:`, `SRC-###`, âncoras `#Lx-Ly` no documento de origem, disposição de todo ID da fonte em algum pacote, índice `.spec/README.md`, IDs entre arquivos e checkpoints, ciclos de `TDD.md`, tarefas, grafo, registro, evidências citadas, `CONSTITUTION.md`, `CODEMAP.md`, Mermaid e links | Ao fim de cada etapa |
| 3 | `python3 -B .github/scripts/validate-sdd.py --require-full --strict` | Pacote inteiro produzido e sem avisos | Antes do handoff para `/implement-task` e em PR |
| 4 | `python3 -B .github/scripts/validate-design-diagrams.py` | Tema claro universal e ausência de cores cromáticas em `.spec/` e nas customizações de `.github/` | Sempre que um diagrama mudar |

Opções de `validate-sdd.py`: `--package 001` limita a um pacote (cobertura da fonte e índice continuam globais); `--source-id-pattern '<regex>'` troca o padrão de IDs do documento de origem; `--format json` gera saída para CI. Códigos de saída: `0` sem erros, `1` com erros (ou avisos com `--strict`), `2` sem pacote em `.spec/`.

Scripts de apoio (independentes de stack, só biblioteca padrão; testes em `python3 -B -m unittest discover -s .github/scripts -p 'test_sdd_tools.py'`):

| Script | Uso |
| --- | --- |
| `format-sdd-mermaid.py [--check]` | Aplica a diretiva de tema claro aos blocos Mermaid; `--check` só reporta (CI) |
| `validate-red-phase.py --expect-output '<REQ-ID>' -- <comando de teste>` | Evidência da fase RED: passa só quando o teste alvo falha com a saída esperada |
| `validate-doc-references.py` | Caminhos e comandos citados em código inline existem (ignora planos, exemplos, `.spec/` e customizações) |
| `verify-hooks-loaded.py [--require-runtime] [--session <id>]` | Descritores de `.github/hooks/` carregáveis, scripts existentes, `disableAllHooks` desligado e registro `sessionStart` na auditoria |

Sem acesso a terminal, reporte os validadores como `NÃO EXECUTADO (sem ferramenta de execução)` e faça a verificação manual:

- Todo pacote tem os 13 arquivos e as 3 pastas com `README.md`; arquivos produzidos têm todas as seções do modelo.
- Todo ID da fonte tem disposição em algum pacote e todo pacote está no índice.
- Todo `REQ-NNN`/`NFR-NNN` ativo tem `origem:` válida e aparece em `SOURCE_TRACEABILITY.md`, `FRD.md` ou `NFRD.md`, `DESIGN.md`, `TASKS.md`, `TESTING.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md` e nos checkpoints; todo AC tem ciclo em `TDD.md`.
- Todo teste que verifica um requisito referencia o ID em comentário (ver [tests.instructions.md](tests.instructions.md)).

Validação textual não verifica semântica EARS, aprovações humanas, renderização Mermaid, se a âncora aponta o trecho certo ou equivalência comportamental. Revise esses pontos explicitamente e não reporte validação de artefatos como sucesso de implementação.

## Convenções

- Arquivos do pacote em MAIÚSCULAS, exatamente com os nomes acima; diretórios de funcionalidade com zero à esquerda (`001-`, `002-`) e slug em minúsculas.
- Preserve a rastreabilidade bidirecional: fonte → requisito → design → tarefa → teste → evidência → resultado.
- Trate afirmações sobre estado real como evidência datada, não como plano ou saída esperada.
- Oculte credenciais, dados pessoais e saídas sensíveis de comandos nas evidências.

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Crie um pacote completo para cada funcionalidade da fonte | Criar só o primeiro pacote quando o pedido é criar as specs |
| Mantenha os 13 arquivos e as 3 pastas em todo pacote | Usar `spec.md`/`plan.md`/`tasks.md`, `specs/` ou `.specs/` |
| Declare `NÃO APLICÁVEL` com motivo em seções sem conteúdo | Omitir seções do modelo ou preenchê-las com conteúdo inventado |
| Mantenha a declaração EARS só em `SPECIFICATION.md` e referencie por ID | Copiar declarações normativas em outros arquivos |
| Use `validate-sdd.py` e declare seus limites | Declarar validação sem a saída da execução |
| Registre decisões humanas, evidências datadas ou bloqueios explícitos | Marcar trabalho planejado como concluído ou simular aprovação |

## Checklist de PR

- [ ] Toda funcionalidade da fonte tem pacote e está no índice `.spec/README.md`.
- [ ] Todo pacote tem a estrutura completa; arquivos produzidos têm todas as seções ou `NÃO APLICÁVEL` justificado.
- [ ] IDs, fontes, critérios e checkpoints são consistentes; nenhum arquivo redefine declarações de `SPECIFICATION.md`.
- [ ] `validate-sdd.py` (com `--require-full --strict` antes do handoff) e `validate-design-diagrams.py` foram executados e a saída está em `evidence/`.
- [ ] Significado EARS, aprovação de escopo, renderização de diagramas e evidências de runtime foram revisados separadamente.
- [ ] Validação de artefatos não é reportada como sucesso de implementação.
