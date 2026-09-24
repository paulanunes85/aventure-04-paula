---
description: "Use ao criar ou editar artefatos SDD (CONSTITUTION.md, frd.md, nfrd.md, spec.md, plan.md, tasks.md, CODEMAP.md, ADRs, decisões de escopo) que exigem pacote completo, convenções de nomenclatura, EARS, rastreabilidade, evidências ou status."
applyTo: ".spec/**/*.md,.spec/**/*.yaml,.spec/**/*.json,docs/adr/**/*.md,docs/decisions/**/*.md,CONSTITUTION.md,CODEMAP.md"
---

# Artefatos de Spec-Driven Development (SDD)

A skill [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) é dona dos procedimentos e dos modelos. Estas instruções são donas do layout, dos nomes de arquivo, da completude e das decisões de apoio. Toda especificação fica sempre dentro da pasta `.spec/` na raiz do repositório. Não crie árvores paralelas (por exemplo, `specs/` ou `.specs/`).

## Pacote de artefatos

Todo artefato abaixo é obrigatório na etapa que o produz e segue o modelo completo da skill. Os modelos estão em [spec-templates.md](../skills/sdd-requirements-engineer/references/spec-templates.md), [frd-template.md](../skills/sdd-requirements-engineer/references/frd-template.md) e [nfrd-template.md](../skills/sdd-requirements-engineer/references/nfrd-template.md).

### Nível do repositório

| Artefato | Modelo | Etapa que cria ou atualiza | Responsabilidade |
| --- | --- | --- | --- |
| `CONSTITUTION.md` (ou a constituição existente) | `CONSTITUTION` | `/write-ears-spec`, quando ainda não existir | Princípios `CON-NNN`, governança e regras de emenda |
| `CODEMAP.md` | Contrato de `/plan-architecture` | `/plan-architecture` | Módulos, fluxo de dados, integrações e cobertura de REQ-IDs |
| `docs/adr/NNNN-<slug>.md` | `DECISIONS` | `/plan-architecture` | Decisão estrutural ou nova dependência que exige aprovação humana |

### Por funcionalidade (`.spec/<NNN>-<funcionalidade>/`)

| Arquivo | Modelo | Etapa que cria ou atualiza | Responsabilidade |
| --- | --- | --- | --- |
| `frd.md` | FRD | `/write-ears-spec`, `/validate-spec` | Problema, resultados, sinais de sucesso, escopo, atores e permissões, domínio e ciclo de vida, requisitos por domínio, interações externas, resumo, disposições, incrementos, perguntas e revisão |
| `nfrd.md` | NFRD | `/write-ears-spec`, `/validate-spec` | Aplicabilidade de todas as categorias de qualidade, contextos de medição, envelope de medição por NFR, segurança e conformidade, restrições tecnológicas, resumo, bloqueios e revisão |
| `spec.md` | `SPECIFICATION` e `SOURCE_TRACEABILITY` | `/write-ears-spec`, `/validate-spec` | Declaração EARS canônica, `origem:`, aceite, verificação planejada, registro de fontes, matriz de rastreabilidade, premissas, bloqueios, perguntas, disposições, validação e aprovação |
| `plan.md` | `ANALYSIS`, `DESIGN` e `DECISIONS` | `/plan-architecture` | Análise (evidências, lacunas, opções, riscos), portfólio de design completo, decisões, estratégia de testes, visão de entrega e fases |
| `tasks.md` | `TASKS`, `TESTING`, `CHECKLIST`, `CROSS_ANALYSIS` e `VERIFICATION` | `/break-down-tasks`; evidências por `/implement-task` e `/verify-quality` | Gate pré-implementação, tarefas RED/GREEN, grafo, mapa de testes, checklist, análise cruzada, verificação, desvios, gate de conclusão e registro de execução |

A pesquisa de UX (`docs/ux/<funcionalidade>-pesquisa.md`, de `/research-ux`) é insumo do pacote quando houver interface. Plano de implementação separado, plano de testes separado e manifesto de testes legível por máquina são os únicos artefatos adicionais; crie-os apenas quando rollout, migração, ambientes de teste ou automação existente exigirem, e vincule-os a partir do artefato dono.

Preserve especificações existentes e seus IDs; não as renomeie como parte de uma nova funcionalidade. Quando um pacote existente não tiver algum dos arquivos acima, crie o arquivo ausente na próxima execução da etapa dona sem reescrever o que já existe.

## Completude

- Cada arquivo contém todas as seções do seu modelo, na ordem do modelo. Não omita seções.
- Seção sem conteúdo aplicável permanece com `NÃO APLICÁVEL: <motivo>`. Valor desconhecido fica `PENDENTE` ou `BLOQUEADO`, com responsável e impacto.
- Completude não autoriza invenção: nenhuma meta, ator, regra, decisão, diagrama de comportamento inexistente ou aprovação é criado para preencher uma seção.
- `plan.md` tem todas as seções dos modelos `ANALYSIS` e `DESIGN`, cobrindo as 14 visões do portfólio de design. Contexto do sistema, implantação, modelo de estados, sequências críticas e fluxo de dados levam diagrama Mermaid quando aplicáveis; caso contrário, `NÃO APLICÁVEL` com motivo.
- O modo `Requisitos` produz `frd.md`, `nfrd.md` e `spec.md` completos (e `CONSTITUTION.md`, se ausente) e não cria `plan.md` nem `tasks.md`. O modo `SDD completo` produz o pacote inteiro, respeitando a ordem das etapas e os status.

## Declaração canônica e referências

- A declaração EARS, os critérios `AC-<ID>-NN` e a verificação de cada requisito vivem somente em `spec.md`.
- `frd.md` e `nfrd.md` referenciam requisitos por ID e acrescentam apenas o que é deles: domínio, atores, justificativa, dependências, falha e recuperação, aplicabilidade e envelope de medição. Não copiam nem redefinem a declaração normativa.
- O envelope de medição de cada NFR vive em `nfrd.md`; o NFR correspondente em `spec.md` aponta para ele.
- `plan.md` e `tasks.md` referenciam IDs; resumos não redefinem significado.
- IDs, contagens e status concordam entre `frd.md`, `nfrd.md`, `spec.md`, `plan.md` e `tasks.md`.

## Constituição

Reutilize `CONSTITUTION.md` quando existir. Se não existir, crie `CONSTITUTION.md` na raiz com o modelo `CONSTITUTION`, status `Rascunho`, derivando cada princípio `CON-NNN` de uma fonte verificável, como [copilot-instructions.md](../copilot-instructions.md) e as instruções em `.github/instructions/`. Não crie princípios sem fonte nem declare aprovação. `spec.md` registra o caminho da constituição.

## Requisitos e evidências

- Use `REQ-NNN` para requisitos funcionais e `NFR-NNN` para não funcionais, salvo se o repositório já tiver outro esquema (por exemplo, `RF-01`/`RNF-01`). Preserve IDs existentes.
- Classifique o padrão EARS e escreva uma única resposta observável usando `deve` (ou `shall` em projetos em inglês).
- Coloque uma linha `origem:` até 20 linhas após a declaração de cada requisito e antes do próximo. Ela deve citar ao menos uma fonte verificável: `SRC-###` do registro de fontes, caminho de arquivo existente (documento de requisitos, código legado, ata, issue) ou `[GREENFIELD]` com justificativa explícita.
- Dê aos novos critérios de aceite IDs estáveis `AC-<ID>-NN` (por exemplo, `AC-REQ-001-01`) em formato Dado/Quando/Então. Preserve IDs de aceite existentes.
- Mantenha separados os estados de rascunho, aprovação, implementação e verificação. Registre `PENDENTE`, `BLOQUEADO` ou `NÃO APLICÁVEL` com motivo em vez de inventar execução ou aceite.

## Apresentação de diagramas e tarefas

- Aplique o [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md) a todo diagrama: tema claro universal e classes canônicas. Todo diagrama representa comportamento ou estrutura com fonte; seções sem esse conteúdo ficam `NÃO APLICÁVEL`.
- Em `frd.md`, adicione diagrama de estados quando uma entidade tiver ciclo de vida.
- Em `plan.md`, mapeie requisitos para componentes de design, tarefas, dependências, testes/evidências e estado atual versus alvo.
- Em `tasks.md`, use checkboxes com ID estável de tarefa, metadados de dependência/paralelismo, rastreio de requisito e aceite, superfície de mudança e evidência planejada ou executada. Uma tarefa marcada exige evidência real de aceite no registro de execução datado.
- Mantenha o grafo de tarefas consistente com a lista. Um ciclo red-green-refactor planejado não prova que os testes rodaram.

## Verificações executáveis

Execute a partir da raiz, nesta ordem, e registre comando, data, código de saída e resumo em `spec.md` (seção `Validação`) ou no registro de execução de `tasks.md`:

| Ordem | Comando | O que prova | Quando |
| --- | --- | --- | --- |
| 1 | `python3 -B -m unittest discover -s .github/scripts -p 'test_validate_sdd.py'` | O próprio validador detecta cada defeito do contrato | Antes de confiar no resultado e após mudar o validador |
| 2 | `python3 -B .github/scripts/validate-sdd.py` | Pacote em `.spec/`, `CONSTITUTION.md`, completude de seções, `origem:`, `SRC-###`, âncoras `#Lx-Ly` dentro do documento de origem, disposição de todo ID da fonte (`RF-`, `RNF-`, `RN-`), IDs entre `frd.md`/`nfrd.md`/`spec.md`/`plan.md`/`tasks.md`, EARS não copiado, tarefas, grafo, registro e links relativos | Ao fim de `/write-ears-spec`, `/validate-spec`, `/plan-architecture` e `/break-down-tasks` |
| 3 | `python3 -B .github/scripts/validate-sdd.py --require-full --strict` | Pacote inteiro sem avisos | Antes do handoff para `/implement-task` e em PR |
| 4 | `python3 -B .github/scripts/validate-design-diagrams.py` | Tema claro universal e ausência de cores cromáticas em `.spec/` e nas customizações de `.github/` | Sempre que um diagrama mudar |

Opções de `validate-sdd.py`: `--package 001` limita a um pacote; `--source-id-pattern '<regex>'` troca o padrão de IDs do documento de origem; `--format json` gera saída para CI. Códigos de saída: `0` sem erros, `1` com erros (ou avisos com `--strict`), `2` sem pacote em `.spec/` (aprovação vazia recusada).

Os demais scripts de `.github/scripts/` vieram de outro projeto (esperam `.specs/`, arquivos em maiúsculas e títulos em inglês) e não validam este repositório; não os cite como evidência. Nunca registre um validador como aprovado sem a saída da execução. Sem acesso a terminal, reporte-o como `NÃO EXECUTADO (sem ferramenta de execução)` e faça a verificação manual abaixo:

- Todo arquivo do pacote da etapa existe e tem todas as seções do modelo, com `NÃO APLICÁVEL`, `PENDENTE` ou `BLOQUEADO` justificados.
- Todo `REQ-NNN`/`NFR-NNN` ativo tem linha `origem:` válida em `spec.md`, e cada âncora `#Lx-Ly` existe no documento de origem.
- Todo ID do documento de origem tem requisito ou disposição em `spec.md`.
- Todo `REQ-NNN` ativo aparece no resumo de `frd.md` e todo `NFR-NNN` ativo aparece no resumo de `nfrd.md`, sem declaração EARS copiada.
- Todo requisito ativo aparece em `plan.md` e em pelo menos uma tarefa de `tasks.md`.
- Todo teste que verifica um requisito referencia o ID em comentário (ver [tests.instructions.md](tests.instructions.md)).

Validação textual não verifica semântica EARS, aprovações humanas, renderização Mermaid, se a âncora aponta o trecho certo ou equivalência comportamental. Revise esses pontos explicitamente e não reporte validação de artefatos como sucesso de implementação.

## Convenções

- Preserve nomes de arquivo em minúsculas e diretórios de funcionalidade com zero à esquerda (`001-`, `002-`).
- Preserve a rastreabilidade bidirecional: fonte → requisito → design → tarefa → teste → resultado.
- Trate afirmações sobre estado real como evidência datada, não como plano ou saída esperada.
- Oculte credenciais, dados pessoais e saídas sensíveis de comandos nas evidências.

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Mantenha `frd.md`, `nfrd.md`, `spec.md`, `plan.md` e `tasks.md` completos em `.spec/<NNN>-<funcionalidade>/` | Gerar arquivos em maiúsculas por seção (`DESIGN.md`, `TASKS.md`) ou especificações fora de `.spec/` |
| Declare `NÃO APLICÁVEL` com motivo em seções sem conteúdo | Omitir seções do modelo ou preenchê-las com conteúdo inventado |
| Mantenha a declaração EARS só em `spec.md` e referencie por ID | Copiar ou reescrever declarações normativas em `frd.md`, `nfrd.md`, `plan.md` ou `tasks.md` |
| Use os validadores existentes e declare seus limites | Exigir scripts inexistentes ou declarar validação semântica a partir de busca textual |
| Registre decisões humanas, evidências datadas ou bloqueios explícitos | Marcar trabalho planejado como concluído ou simular aprovação |

## Checklist de PR

- [ ] O pacote da etapa está completo: todo arquivo existe e toda seção do modelo está presente ou justificada como `NÃO APLICÁVEL`.
- [ ] Os artefatos usam caminhos canônicos e IDs, fontes e critérios de aceite consistentes; `frd.md` e `nfrd.md` não redefinem declarações de `spec.md`.
- [ ] `validate-sdd.py` (com `--require-full --strict` antes do handoff) e `validate-design-diagrams.py` foram executados e a saída está registrada.
- [ ] Todo requisito ativo mapeia para verificações planejadas ou executadas, com lacunas explícitas.
- [ ] Toda declaração `origem:` é válida e o relatório de referências em testes foi revisado.
- [ ] Significado EARS, aprovação de escopo, renderização de diagramas e evidências de runtime foram revisados separadamente quando aplicável.
- [ ] Validação de artefatos não é reportada como sucesso de implementação.
