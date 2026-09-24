# Padrão de documentos SDD e Mermaid

Use este contrato para o pacote canônico de artefatos e decisões de apoio. As [instruções de artefatos](../../../instructions/sdd-artifacts.instructions.md) são donas dos nomes de arquivo, da etapa dona de cada arquivo, da regra de completude e dos limites de validação. Todo arquivo contém todas as seções do seu modelo; não gere uma árvore de artefatos paralela.

## Responsabilidades dos artefatos

| Artefato | Responsabilidade obrigatória |
| --- | --- |
| `CONSTITUTION.md` | Princípios `CON-NNN` com fonte, governança e emenda; reutilize a constituição existente quando houver |
| `.spec/README.md` | Índice de funcionalidades, critério de corte, IDs da fonte por pacote e dependências |
| `SPECIFICATION.md` | Requisitos EARS canônicos, `origem:`, aceite, premissas, escopo, validação e aprovação |
| `SOURCE_TRACEABILITY.md` | Registro `SRC-###`, matriz, cobertura da fonte e disposições históricas |
| `FRD.md` | Escopo funcional, atores, domínio e ciclo de vida, requisitos por domínio (por ID), interações externas, incrementos e revisão |
| `NFRD.md` | Aplicabilidade de categorias, contextos e envelopes de medição, segurança, conformidade, restrições tecnológicas e revisão |
| `ANALYSIS.md` | Evidências, lacunas, opções e riscos |
| `DESIGN.md` | Portfólio de design completo e rastreabilidade requisito-componente |
| `DECISIONS.md` | Decisões `DEC-NNN` e ADRs vinculados |
| `TASKS.md` | Ordem de dependências, checkboxes, grafo, gate de conclusão e registro de execução |
| `TESTING.md` | Estratégia, ambientes, catálogo, mapa e cobertura de testes |
| `TDD.md` | Ciclo RED/GREEN/REFACTOR por critério de aceite |
| `CHECKLIST.md` | Gates de revisão, implementação, verificação e release |
| `CROSS_ANALYSIS.md` | Consistência entre todos os arquivos e análise de órfãos |
| `VERIFICATION.md` | Verificações planejadas, execuções de validadores e resultados |
| `checkpoints/`, `contracts/`, `evidence/` | Mapas legíveis por máquina, contratos de interface com `manifest.yaml` e evidências datadas, cada pasta com `README.md` |
| `CODEMAP.md` | Módulos, fluxo de dados, integrações e cobertura de REQ-IDs |
| ADRs | Decisão estrutural ou nova dependência que exige aprovação humana |

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

`DESIGN.md` sempre cobre, nesta ordem:

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

Mantenha as 14 visões em qualquer porte de projeto, usando todas as seções do modelo `DESIGN` dos [modelos de artefatos](spec-templates.md). Em projetos pequenos (por exemplo, uma CLI ou biblioteca), escreva `NÃO APLICÁVEL: <motivo>` sob o título das seções sem conteúdo, em vez de removê-las. As visões 2, 4, 5, 6 e 7 levam diagrama Mermaid quando aplicáveis; nenhum diagrama descreve comportamento ou estrutura sem fonte.

A visão de entrega mapeia IDs reais de requisitos para componentes de design, itens de plano e tarefas, IDs de dependências ou especificações vizinhas, testes/evidências e estado atual versus alvo. Não invente implementação ou aprovação para completar um diagrama.

## Contrato de tarefas

Use uma entrada de checkbox por tarefa:

```text
- [ ] **T001 [S] [Plano:P1.1] RED** Adicionar teste de contrato que falha. Rastreia REQ-001.
  - Arquivos: `tests/contract.test.ts`.
  - Aceite: TST-C001 falha antes da implementação e passa depois.
```

- `[S]` significa sequencial; `[P]` significa independente em dependências e superfície de mudança.
- O DAG de dependências em `TASKS.md` e `checkpoints/plan-to-tasks.yaml` contêm cada tarefa exatamente uma vez.
- O mapa de testes em `TESTING.md` nomeia os requisitos governantes e os testes planejados ou executados.
- `[x]` só é permitido quando a tarefa aparece no registro datado `Marcadas como concluídas pela verificação:` e sua evidência de aceite existe em `evidence/`.
- Código parcial existente permanece desmarcado até que o sinal de aceite completo seja demonstrado.

## Validação exigida

Execute os validadores da seção `Verificações executáveis` das [instruções de artefatos](../../../instructions/sdd-artifacts.instructions.md) (`.github/scripts/validate-sdd.py` e `.github/scripts/validate-design-diagrams.py`) e registre comando, data e resultado em `VERIFICATION.md` (ou na seção `Validação` de `SPECIFICATION.md` antes da etapa de tarefas), com a saída salva em `evidence/`. Sem ferramenta de execução, faça a verificação manual descrita ali e registre os validadores como não executados.

Validadores textuais não provam correção EARS, precisão de linhas de fonte, sintaxe de diagramas, aprovação ou testes de produto passando. Revise esses pontos separadamente. Renderize os diagramas aplicáveis com um renderizador disponível (por exemplo, `npx @mermaid-js/mermaid-cli`) e registre o resultado; se nenhum estiver disponível, reporte a renderização como não executada.

Reporte uma verificação reprovada ou bloqueada como tal. Nunca enfraqueça um gate, adicione baseline ou crie evidência vazia apenas para obter resultado verde.
