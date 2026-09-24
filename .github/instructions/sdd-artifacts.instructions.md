---
description: "Use ao editar artefatos SDD (spec.md, plan.md, tasks.md, ADRs, decisões de escopo) que exigem convenções de nomenclatura, EARS, rastreabilidade, evidências ou status."
applyTo: "specs/**/*.md,specs/**/*.yaml,specs/**/*.json,docs/adr/**/*.md,docs/decisions/**/*.md"
---

# Artefatos de Spec-Driven Development (SDD)

A skill [sdd-requirements-engineer](../skills/sdd-requirements-engineer/SKILL.md) é dona dos procedimentos de ciclo de vida e geração. Estas instruções são donas do formato dos artefatos em `specs/` e das decisões de apoio. Não crie uma árvore paralela (por exemplo, `.specs/`).

## Contratos de artefatos

Cada funcionalidade aprovada usa `specs/<NNN>-<funcionalidade>/` com estes arquivos:

| Artefato | Responsabilidade |
| --- | --- |
| `spec.md` | Requisitos EARS, linha `origem:`, critérios de aceite, escopo, premissas, dependências, registro de fontes e status de aprovação |
| `plan.md` | Design, decisões, riscos, contratos e diagramas aplicáveis, estratégia de testes e rastreabilidade requisito-componente |
| `tasks.md` | Tarefas de implementação e teste ordenadas por dependência, mapeamento REQ/AC, verificações planejadas, evidências datadas e status de conclusão |
| `docs/adr/` ou `docs/decisions/` | ADRs e decisões de escopo aprovadas por humanos, somente quando necessárias |

Preserve especificações existentes e seus IDs; não as renomeie como parte de uma nova funcionalidade. Um pedido apenas de requisitos não autoriza a criação do pacote completo. Adicione contratos, arquivos de evidência ou análises complementares somente quando o escopo selecionado exigir e referencie-os a partir do artefato dono.

Reutilize a constituição do projeto quando existir (por exemplo, `.specify/memory/constitution.md` do Spec-Kit ou um `CONSTITUTION.md`). Se não existir, registre o fato e use as instruções do repositório; não invente uma constituição nem declare inicialização de CLI que não ocorreu.

## Requisitos e evidências

- Use `REQ-NNN` para requisitos funcionais e `NFR-NNN` para não funcionais, salvo se o repositório já tiver outro esquema (por exemplo, `RF-01`/`RNF-01`). Preserve IDs existentes.
- Classifique o padrão EARS e escreva uma única resposta observável usando `deve` (ou `shall` em projetos em inglês).
- Coloque uma linha `origem:` até 20 linhas após a declaração de cada requisito e antes do próximo. Ela deve citar ao menos uma fonte verificável: `SRC-###` do registro de fontes, caminho de arquivo existente (documento de requisitos, código legado, ata, issue) ou `[GREENFIELD]` com justificativa explícita.
- Dê aos novos critérios de aceite IDs estáveis `AC-<ID>-NN` (por exemplo, `AC-REQ-001-01`) em formato Dado/Quando/Então. Preserve IDs de aceite existentes.
- Mantenha separados os estados de rascunho, aprovação, implementação e verificação. Registre `PENDENTE`, `BLOQUEADO` ou `NÃO APLICÁVEL` com motivo em vez de inventar execução ou aceite.

## Apresentação de diagramas e tarefas

- Aplique o [padrão de documentos SDD e Mermaid](../skills/sdd-requirements-engineer/references/sdd-document-and-mermaid-standard.md) aos diagramas solicitados. Inclua apenas visões que esclareçam uma decisão relevante; não crie diagramas para cumprir cota.
- Em `plan.md`, mapeie requisitos para componentes de design, tarefas, dependências, testes/evidências e estado atual versus alvo.
- Em `tasks.md`, use checkboxes com ID estável de tarefa, metadados de dependência/paralelismo, rastreio de requisito e aceite, superfície de mudança e evidência planejada ou executada. Uma tarefa marcada exige evidência real de aceite no registro de execução datado.
- Mantenha o grafo de tarefas consistente com a lista quando houver grafo. Um ciclo red-green-refactor planejado não prova que os testes rodaram.

## Verificações executáveis

Se o repositório tiver um validador de rastreabilidade (script ou job de CI), execute-o a partir da raiz e anexe o resultado. Se não houver, faça a verificação manual abaixo e reporte o validador como `NÃO EXECUTADO (inexistente)`:

- Todo `REQ-NNN`/`NFR-NNN` ativo tem linha `origem:` válida.
- Todo requisito ativo aparece em `plan.md` e em pelo menos uma tarefa de `tasks.md`.
- Todo teste que verifica um requisito referencia o ID em comentário (ver [tests.instructions.md](tests.instructions.md)).

Validação textual não verifica semântica EARS, aprovações humanas, renderização Mermaid, precisão de âncoras de linha ou equivalência comportamental. Revise esses pontos explicitamente e anexe evidência de execução para verificações de runtime aplicáveis.

## Convenções

- Preserve nomes de arquivo em minúsculas e diretórios de funcionalidade com zero à esquerda (`001-`, `002-`).
- Preserve a rastreabilidade bidirecional: fonte → requisito → design → tarefa → teste → resultado.
- Trate afirmações sobre estado real como evidência datada, não como plano ou saída esperada.
- Oculte credenciais, dados pessoais e saídas sensíveis de comandos nas evidências.

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Mantenha `specs/<NNN>-<funcionalidade>/spec.md`, `plan.md` e `tasks.md` | Gerar um portfólio paralelo em maiúsculas ou uma árvore `.specs/` |
| Use os validadores existentes e declare seus limites | Exigir scripts inexistentes ou declarar validação semântica a partir de busca textual |
| Registre decisões humanas, evidências datadas ou bloqueios explícitos | Marcar trabalho planejado como concluído ou simular aprovação |

## Checklist de PR

- [ ] Os artefatos usam caminhos canônicos e IDs, fontes e critérios de aceite consistentes.
- [ ] Todo requisito ativo mapeia para verificações planejadas ou executadas, com lacunas explícitas.
- [ ] Toda declaração `origem:` é válida e o relatório de referências em testes foi revisado.
- [ ] Significado EARS, aprovação de escopo, renderização de diagramas e evidências de runtime foram revisados separadamente quando aplicável.
- [ ] Validação de artefatos não é reportada como sucesso de implementação.
