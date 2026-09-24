# Padrão de documentos SDD e Mermaid

Use este contrato para pacotes canônicos em `specs/<NNN>-<funcionalidade>/` e decisões de apoio. As [instruções de artefatos](../../../instructions/sdd-artifacts.instructions.md) são donas dos nomes de arquivo e dos limites de validação. Inclua apenas seções e diagramas que esclareçam o escopo aprovado; não gere uma árvore de artefatos paralela.

## Responsabilidades dos artefatos

| Artefato | Responsabilidade obrigatória |
| --- | --- |
| `spec.md` | Requisitos EARS canônicos, `origem:`, aceite, registro de fontes, premissas, escopo, aprovação e decisões em aberto |
| `plan.md` | Design, diagramas aplicáveis, decisões ou links para ADRs, riscos, estratégia de testes e rastreabilidade requisito-componente |
| `tasks.md` | Ordem de dependências, mapa de testes, checkboxes, gate de conclusão, comandos determinísticos e evidências de execução datadas |
| Contratos e decisões de apoio | Arquivos separados apenas quando justificados, vinculados a partir do artefato dono, com aplicabilidade explícita |

## Tema Mermaid universal

Comece todo bloco Mermaid com esta diretiva exata:

```text
%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF","primaryColor":"#FFFFFF","primaryTextColor":"#222222","primaryBorderColor":"#777777","lineColor":"#555555","secondaryColor":"#F2F2F2","tertiaryColor":"#E8E8E8"}}}%%
```

Para `flowchart`, `graph` e `classDiagram`, inclua estas definições exatamente uma vez:

```text
classDef default fill:#FFFFFF,stroke:#777777,color:#222222
classDef zone fill:#F2F2F2,stroke:#999999,color:#222222
classDef external fill:#E8E8E8,stroke:#555555,color:#222222
```

Use `zone` para limites próprios e agrupamentos lógicos, e `external` para atores, sistemas externos, especificações vizinhas ou fontes de evidência fora do limite da funcionalidade. `stateDiagram`, `sequenceDiagram`, `erDiagram` e `gantt` herdam o tema universal e não devem conter `classDef`. Renderizadores atuais de `stateDiagram-v2` tratam `default` como token reservado.

Mantenha os diagramas revisáveis:

- menos de 40 nós por bloco;
- rótulos curtos, com detalhes em tabelas adjacentes;
- rótulos de arestas entre aspas;
- IDs explícitos de subgraph;
- sem cores cromáticas;
- estados atual, parcial, planejado, bloqueado e alvo separados.

## Portfólio de design

Quando relevante para a funcionalidade, `plan.md` inclui:

1. Visão geral da arquitetura
2. Contexto do sistema
3. Mapa de componentes ou serviços
4. Visão de implantação
5. Modelo de estados
6. Sequências críticas
7. Fluxo ou ciclo de vida dos dados
8. Modelo de dados
9. Interfaces e contratos
10. Design de erros, segurança, ameaças e observabilidade
11. Superfície de implementação
12. Visão de entrega e rastreabilidade
13. Riscos e trade-offs
14. Desenvolvimento em fases

Para projetos pequenos (por exemplo, uma CLI ou biblioteca), é aceitável reduzir o portfólio a visão geral, contexto, modelo de dados, erros, superfície de implementação e visão de entrega, declarando as seções omitidas como não aplicáveis.

A visão de entrega mapeia IDs reais de requisitos para componentes de design, itens de plano e tarefas, IDs de dependências ou especificações vizinhas, testes/evidências e estado atual versus alvo. Não invente implementação ou aprovação para completar um diagrama.

## Contrato de tarefas

Use uma entrada de checkbox por tarefa:

```text
- [ ] **T001 [S] [Plano:P1.1] RED** Adicionar teste de contrato que falha. Rastreia REQ-001.
  - Arquivos: `tests/contract.test.ts`.
  - Aceite: TST-C001 falha antes da implementação e passa depois.
```

- `[S]` significa sequencial; `[P]` significa independente em dependências e superfície de mudança.
- O DAG de dependências contém cada tarefa exatamente uma vez.
- O mapa de testes nomeia os requisitos governantes e os testes planejados ou executados.
- `[x]` só é permitido quando a tarefa aparece no registro datado `Marcadas como concluídas pela verificação:` e sua evidência de aceite existe.
- Código parcial existente permanece desmarcado até que o sinal de aceite completo seja demonstrado.

## Validação exigida

Se o repositório tiver validadores (script de rastreabilidade, job de CI, lint de Markdown, renderizador Mermaid), execute-os e registre comando, data e resultado em `tasks.md`. Se não houver, faça a verificação manual das [instruções de artefatos](../../../instructions/sdd-artifacts.instructions.md) e registre os validadores como não executados.

Validadores textuais não provam correção EARS, precisão de linhas de fonte, sintaxe de diagramas, aprovação ou testes de produto passando. Revise esses pontos separadamente. Renderize os diagramas aplicáveis com um renderizador disponível (por exemplo, `npx @mermaid-js/mermaid-cli`) e registre o resultado; se nenhum estiver disponível, reporte a renderização como não executada.

Reporte uma verificação reprovada ou bloqueada como tal. Nunca enfraqueça um gate, adicione baseline ou crie evidência vazia apenas para obter resultado verde.
