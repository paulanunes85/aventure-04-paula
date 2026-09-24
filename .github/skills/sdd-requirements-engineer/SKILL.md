---
name: "sdd-requirements-engineer"
description: "Elicita, normaliza, valida e rastreia requisitos em um fluxo completo de Spec-Driven Development usando EARS. Use ao converter notas, PRDs, documentos de requisitos, atas, evidências de sistemas existentes ou insumos de design em pacotes .spec/ (SPECIFICATION, SOURCE_TRACEABILITY, FRD, NFRD, ANALYSIS, DESIGN, DECISIONS, TASKS, TESTING, TDD, CHECKLIST, CROSS_ANALYSIS, VERIFICATION, checkpoints, contracts, evidence), quality gates ou um handoff SDD pronto para implementação. Gatilhos: EARS, requisitos, especificação, SDD, spec-driven, FRD, NFRD, rastreabilidade, critérios de aceite."
---

# Engenharia de requisitos SDD com EARS

Transforme intenção de produto incompleta ou evidências de design existentes em requisitos EARS atômicos e em um conjunto coerente de artefatos de Spec-Driven Development. Preserve a proveniência desde a primeira fonte até design, tarefas, verificação e handoff de implementação.

## Quando invocar

- "Transforme estas notas em FRD e NFRD usando EARS."
- "Rode o fluxo SDD completo para esta funcionalidade."
- "Converta este design em requisitos EARS rastreáveis e tarefas."
- "Revise estes requisitos ou artefatos SDD procurando lacunas e trabalho órfão."
- "Prepare um handoff pronto para implementação a partir desta especificação aprovada."

## Modos de operação

| Modo | Ponto de partida | Entregável |
| --- | --- | --- |
| Requisitos | Notas, PRD, issue, entrevistas, documento de requisitos ou evidência de sistema existente | Um pacote por funcionalidade da fonte, com a estrutura completa e `SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md` e `NFRD.md` produzidos; índice `.spec/README.md` e `CONSTITUTION.md`, se ausente |
| SDD completo | Requisitos brutos ou aprovados | Todos os pacotes com os 13 arquivos produzidos, `checkpoints/`, `contracts/`, `evidence/`, `CODEMAP.md` e ADRs necessários |
| Design-first | Esboço de arquitetura, contrato de API, modelo de dados ou protótipo | Requisitos recuperados, premissas explícitas e depois a cadeia SDD completa |
| Validação | FRD, NFRD, especificação, design ou tarefas existentes | Achados por severidade, declarações EARS corrigidas e decisão de prontidão |
| Handoff | Artefatos SDD revisados | Pacote de implementação delimitado, com gates, dependências e bloqueios não resolvidos |

Selecione o menor modo que atende ao pedido. Todo modo que grava artefatos os produz completos; a revisão de um único requisito usa `Validação` e não cria arquivos novos.

## Contrato do repositório

Leia primeiro as [instruções de artefatos SDD](../../instructions/sdd-artifacts.instructions.md) e o [copilot-instructions.md](../../copilot-instructions.md). Elas definem a estrutura obrigatória, a etapa dona de cada arquivo, a decomposição em funcionalidades e a regra de completude. Em resumo:

- Todo pacote `.spec/<NNN>-<funcionalidade>/` tem 13 arquivos em maiúsculas (`SPECIFICATION.md`, `SOURCE_TRACEABILITY.md`, `FRD.md`, `NFRD.md`, `ANALYSIS.md`, `DESIGN.md`, `DECISIONS.md`, `TASKS.md`, `TESTING.md`, `TDD.md`, `CHECKLIST.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md`) e 3 pastas (`checkpoints/`, `contracts/`, `evidence/`), cada pasta com `README.md`.
- Criar as specs a partir de uma fonte significa criar um pacote para cada funcionalidade da fonte e o índice `.spec/README.md`; só `feature=` restringe a um pacote.
- `Requisitos` cria a estrutura inteira, produz os quatro arquivos de requisitos e deixa os demais com `Status: Não iniciado` até a etapa dona.
- Todo arquivo produzido segue o modelo completo desta skill: nenhuma seção é omitida, e seções sem conteúdo ficam `NÃO APLICÁVEL: <motivo>`.
- A declaração EARS, o aceite e a verificação de cada requisito vivem apenas em `SPECIFICATION.md`; `SOURCE_TRACEABILITY.md` é dono das fontes e da cobertura da fonte; os demais arquivos referenciam por ID.

Use `REQ-NNN`/`NFR-NNN`, `AC-<ID>-NN` e uma linha `origem:` válida, salvo se o repositório já tiver outro esquema. Preserve identificadores e especificações existentes. Toda especificação fica em `.spec/`; não crie `specs/`, `.specs/` nem arquivos em minúsculas (`spec.md`, `plan.md`, `tasks.md`), e não renomeie IDs existentes. Só exija verificações executáveis que existam no repositório; validação textual não é evidência de runtime nem de aprovação.

## Política de fontes e evidências

Use esta ordem de precedência:

1. Objetivos, restrições e decisões aprovados pelo usuário.
2. Evidências do repositório, como especificações, documentos de requisitos, código, testes, schemas, ADRs, issues e configuração operacional existentes.
3. Documentação oficial datada para comportamento de plataformas externas que precisa estar atual.
4. Premissas explícitas com responsável, impacto e estado de confirmação.

Atribua a cada fonte um identificador estável `SRC-###`. Um artefato derivado não é a fonte primária de um requisito quando a fonte original (usuário, repositório ou documentação oficial) está disponível. Nunca invente meta, cota, preço, benchmark, obrigação de conformidade ou estado de aprovação.

## Procedimento

1. Estabeleça escopo e ação.
   - Inspecione instruções, modelos, especificações e convenções de nomes do repositório antes de criar arquivos.
   - Identifique se o pedido é requirements-first, design-first, apenas validação ou apenas handoff.
   - Registre os caminhos de saída solicitados e se o usuário já autorizou a criação de arquivos. Se a criação não foi pedida, devolva rascunhos ou achados de revisão sem gravar.
   - Inventárie todos os IDs da fonte e decomponha a fonte em funcionalidades (fase, capacidade, ator ou superfície de entrega). Crie um pacote por funcionalidade e atribua cada ID da fonte a exatamente um pacote; registre o mapa no índice `.spec/README.md`.

2. Classifique o contexto do projeto.

   | Contexto | Ênfase obrigatória |
   | --- | --- |
   | Greenfield | Resultados, sinais de sucesso, não objetivos, premissas |
   | Brownfield | Comportamento atual, escopo do delta, compatibilidade, limites de regressão |
   | Modernização ou migração | Paridade com a fonte, correção dos dados, cutover, rollback, descomissionamento |
   | API ou plataforma | Consumidores, contratos, versionamento, limites de taxa, compatibilidade |
   | Mobile ou edge | Estados de conectividade, plataformas suportadas, sincronização, recuperação |
   | Dados ou IA | Qualidade e linhagem de dados, evolução de modelo ou schema, avaliação, fallback |
   | SaaS ou multi-tenant | Isolamento, onboarding, direitos de uso, controle de vizinhos ruidosos |
   | Ferramenta interna ou CLI | Contexto de identidade, distribuição, instalação, suporte |
   | Educacional ou público vulnerável | Faixa etária, privacidade de menores, linguagem, acessibilidade, supervisão |
   | Infraestrutura | Modelo de acesso, ambientes, confiabilidade, observabilidade, rollback |

3. Rode o gate de ambiguidade e lacunas.
   - Classifique cada lacuna como `PRESENTE`, `BLOQUEIO`, `PREMISSA DE ALTO RISCO` ou `NÃO APLICÁVEL`.
   - Trate como bloqueio a ausência de atores e permissões, resultado principal, limite de escopo e fonte autoritativa.
   - Faça no máximo três perguntas focadas sobre bloqueios, uma por vez. Não pergunte o que a evidência do repositório já responde.
   - Registre itens de alto risco não resolvidos em vez de substituí-los por padrões silenciosos.
   - Detecte contradições entre fontes (por exemplo, duas decisões incompatíveis de escopo ou de acesso) e registre-as como bloqueio com as interpretações possíveis.

4. Escreva ou normalize requisitos.
   - Leia a [referência de notação EARS](references/ears-notation.md) antes de escrever requisitos normativos.
   - Grave `FRD.md` com o [modelo de FRD](references/frd-template.md) e `NFRD.md` com o [modelo de NFRD](references/nfrd-template.md), completos, referenciando os IDs canônicos de `SPECIFICATION.md`.
   - Siga o esquema de IDs do repositório. Preserve IDs existentes; IDs genéricos dos modelos não são instrução de migração.
   - Escreva uma resposta observável do sistema por declaração EARS. Divida comportamento composto.
   - Mantenha requisitos funcionais neutros quanto à implementação. Coloque restrições tecnológicas genuínas no NFRD, com justificativa e fonte.
   - Dê a todo requisito prioridade, fonte, justificativa, sinal de aceite, método de verificação e status de ciclo de vida.
   - Expresse NFRs numéricos com contexto de medição: métrica, meta, carga, percentil ou agregação, janela de observação, ambiente e responsável pela evidência. Se algum valor obrigatório for desconhecido, mantenha um bloqueio visível.
   - Transforme exemplos fornecidos pelo negócio em sinais de aceite; exemplos com resultado ambíguo ou em aberto viram perguntas, não requisitos.
   - Adicione um modelo de estados quando o comportamento depender do ciclo de vida de uma entidade.

5. Construa a cadeia de artefatos SDD.
   - Leia os [modelos de artefatos SDD](references/spec-templates.md) e o [padrão de documentos SDD e Mermaid](references/sdd-document-and-mermaid-standard.md).
   - Reutilize a constituição do repositório quando existir. Se não existir, crie `CONSTITUTION.md` como `Rascunho` com princípios derivados de fontes verificáveis. Não crie uma constituição local conflitante.
   - Para SDD completo, produza todos os 13 arquivos de cada pacote, os checkpoints, o manifesto de contratos e os índices das pastas, na ordem das etapas.
   - Use todas as seções do modelo `DESIGN`, cobrindo as 14 visões do portfólio (declarando `NÃO APLICÁVEL` com motivo quando for o caso), o tema Mermaid claro universal, as classes canônicas de grafo e uma visão de entrega que conecte requisitos, componentes, tarefas, dependências, evidências e estado atual versus alvo.
   - Escreva em `TASKS.md` checkboxes ordenadas por dependência com metadados de sequência/plano/requisito/mudança/evidência, um DAG completo, gate de conclusão e registro; em `TESTING.md` o catálogo e o mapa de testes; em `TDD.md` um ciclo por critério de aceite. Marque apenas tarefas com evidência em `evidence/` e use `[P]` apenas quando forem realmente independentes.
   - Use pastas sequenciais `001-nome-da-funcionalidade`, preservando a numeração existente.

6. Garanta rastreabilidade ponta a ponta.
   - Dê a todo requisito ativo sua linha `origem:` em `SPECIFICATION.md` e uma linha na matriz de `SOURCE_TRACEABILITY.md`.
   - Mapeie cada requisito ativo em `DESIGN.md`, `TASKS.md`, `TESTING.md`, `CROSS_ANALYSIS.md`, `VERIFICATION.md` e nos checkpoints, e cada critério de aceite em `TDD.md`.
   - Rejeite requisitos, elementos de design, tarefas e testes órfãos.
   - Registre IDs transferidos, substituídos, divididos, mesclados ou aposentados em uma tabela de disposição. Nunca renumere silenciosamente requisitos estáveis.
   - Preserve o mesmo significado normativo em todos os arquivos. Referencie por ID em vez de copiar texto que pode divergir; resumos e contagens concordam com `SPECIFICATION.md`.

7. Valide e entregue.
   - Aplique todas as verificações aplicáveis dos [quality gates unificados](references/quality-gates.md).
   - Use o [catálogo de antipadrões](references/anti-patterns.md) para corrigir defeitos antes da entrega.
   - Mantenha artefatos como `Rascunho` ou `Pronto para revisão` até um revisor responsável aprová-los.
   - Use `Implementado` ou `Verificado` apenas quando houver evidência no repositório ou de execução.
   - Execute `python3 -B .github/scripts/validate-sdd.py` (e `--require-full --strict` antes do handoff) e `python3 -B .github/scripts/validate-design-diagrams.py`, e reporte comando, código de saída e achados. Sem ferramenta de execução, reporte-os como não executados e faça a verificação manual das instruções de artefatos. Revise significado EARS, aprovações e renderização de diagramas separadamente.
   - Entregue apenas o escopo aprovado, os caminhos dos artefatos, a ordem de dependências, os resultados dos gates e os bloqueios não resolvidos. Não inicie a implementação como parte desta skill.

## Contrato de requisito EARS

Todo registro de requisito normativo contém:

| Campo | Regra |
| --- | --- |
| ID | Estável e único; segue o esquema de IDs do repositório |
| Padrão | Exatamente um entre ubíquo, orientado a evento, orientado a estado, opcional, indesejado ou complexo |
| Declaração | Ordem canônica das cláusulas EARS com `deve` (ou `shall`) e uma resposta observável |
| Prioridade | P0, P1, P2 ou P3 com justificativa de impacto na entrega |
| Fonte | Linha `origem:` com evidência primária; referências `SRC-###` complementam |
| Justificativa | Por que o comportamento ou a restrição de qualidade é necessário |
| Aceite | Pelo menos um sinal de aprovação/reprovação |
| Verificação | Teste, inspeção, análise, demonstração ou medição planejados |
| Status | Proposto, pronto para revisão, aprovado, implementado, verificado ou aposentado |

Priorize pelo impacto evidenciado na entrega: P0 bloqueia o incremento nomeado; P1 perde valor ou redução de risco relevante, mas tem contorno aprovado; P2 é adiável sem violar o objetivo do incremento; P3 não tem impacto relevante na entrega. Divida o incremento quando o conjunto P0 não for revisável.

## Limites

- Não implemente código de produto, altere infraestrutura nem faça deploy de recursos.
- Não declare aprovação de stakeholders, conformidade, desempenho ou verificação sem evidência.
- Não sobrescreva uma constituição, esquema de IDs ou convenção de artefatos existente sem decisão explícita de compatibilidade.
- Não use a rota design-first para contornar requisitos, sinais de aceite ou rastreabilidade de fontes.
- Não omita arquivos nem seções do pacote em mudanças pequenas; declare `NÃO APLICÁVEL` com motivo. Completude não autoriza inventar conteúdo.

## Armadilhas

- Histórias de usuário expressam intenção, mas não são requisitos normativos; sinais de aceite concordam com os requisitos sem redefini-los.
- `deve`/`shall` pertence às declarações EARS; tecnologias nomeadas são restrições com fonte ou preferências de design não resolvidas, não requisitos funcionais automáticos.
- Uma redação de desempenho não é mensurável a menos que a carga e o método de observação também estejam definidos.
- "O sistema tem que acertar sempre" diante de entradas com mais de uma interpretação válida é uma contradição a expor, não um requisito a aceitar.

## Divulgação progressiva e recursos empacotados

Carregue apenas os recursos exigidos pelo modo selecionado:

- [Notação EARS](references/ears-notation.md): sintaxe, classificação, exemplos, defeitos e referências acadêmicas.
- [Modelo de FRD](references/frd-template.md): escopo funcional, atores, requisitos por domínio, aceite e entrega em fases.
- [Modelo de NFRD](references/nfrd-template.md): restrições de qualidade mensuráveis e envelopes de medição.
- [Modelos de artefatos SDD](references/spec-templates.md): estrutura do pacote e modelo de cada arquivo, checkpoint, contrato e índice.
- [Padrão de documentos SDD e Mermaid](references/sdd-document-and-mermaid-standard.md): contratos canônicos de artefatos, tema claro universal de diagramas, contrato de checklist/registro de tarefas e gates executáveis.
- [Quality gates unificados](references/quality-gates.md): verificações detalhadas de prontidão, EARS, rastreabilidade e handoff.
- [Catálogo de antipadrões](references/anti-patterns.md): defeitos de requisitos e SDD com ação corretiva.

## Modelo de saída

Devolva exatamente esta estrutura:

```markdown
## Resultado SDD EARS

**Status:** concluído | pronto-para-revisão | bloqueado
**Modo:** requisitos | sdd-completo | design-first | validação | handoff
**Contexto do projeto:** <classificação>
**Resumo:** <resultado em uma frase>

### Artefatos
| Artefato | Caminho ou resultado | Status |
| --- | --- | --- |
| <nome> | <caminho, rascunho ou não solicitado> | <rascunho|pronto-para-revisão|bloqueado> |

### Requisitos e lacunas
- Requisitos funcionais: <quantidade>
- Requisitos não funcionais: <quantidade>
- Bloqueios: <IDs e motivo, ou nenhum>
- Premissas de alto risco: <IDs e responsável, ou nenhuma>
- Contradições entre fontes: <IDs e interpretações, ou nenhuma>

### Evidências de EARS e rastreabilidade
- Validação EARS: <aprovados>/<aplicáveis>
- Cobertura de fontes: <requisitos cobertos>/<requisitos ativos>
- Cobertura entre artefatos: <requisitos cobertos>/<requisitos ativos>
- Órfãos ou disposições de ciclo de vida: <nenhum ou resumo>

### Quality gates
- Resultado: <aprovado|reprovado>
- Verificações reprovadas: <IDs dos gates e correções, ou nenhuma>
- Validador automático: <executado com resultado | não executado (motivo)>
- Estado de aprovação: <rascunho|pronto-para-revisão|aprovado com evidência>

### Handoff
- Pronto para implementação: <sim|não>
- Escopo aprovado: <IDs de requisitos ou nenhum>
- Dependências: <resumo ordenado>
- Perguntas em aberto: <perguntas ou nenhuma>
```

## Gate de qualidade

- [ ] O modo de operação selecionado é o menor que atende ao pedido.
- [ ] Precedência de fontes, premissas, bloqueios e autorização de gravação estão explícitos.
- [ ] Todo requisito normativo atende ao contrato de requisito EARS.
- [ ] Toda funcionalidade da fonte tem pacote, todo ID da fonte tem disposição e todo pacote está no índice `.spec/README.md`.
- [ ] Todo pacote tem os 13 arquivos e as 3 pastas; arquivos produzidos têm todas as seções do modelo e os de etapas futuras estão `Não iniciado`.
- [ ] `FRD.md` e `NFRD.md` cobrem toda categoria aplicável e referenciam os IDs de `SPECIFICATION.md` sem redefini-los.
- [ ] Todo diagrama Mermaid usa o tema claro universal e todo diagrama tipo grafo carrega as classes neutras canônicas.
- [ ] `DESIGN.md` mapeia requisitos por componentes, tarefas, dependências, testes/evidências e estado atual versus alvo.
- [ ] `TASKS.md`, `TESTING.md`, `TDD.md`, `VERIFICATION.md` e os checkpoints concordam; implementação parcial não é marcada como concluída.
- [ ] Todo requisito ativo é rastreável da fonte ao design, tarefas, aceite e verificação.
- [ ] Mudanças de ciclo de vida preservam IDs ou incluem disposições explícitas.
- [ ] Nenhuma métrica, aprovação, afirmação de compatibilidade ou fato atual de plataforma foi fabricado.
- [ ] Toda verificação detalhada aplicável dos [quality gates unificados](references/quality-gates.md) passa ou é reportada como bloqueio.
- [ ] A resposta segue exatamente o `## Modelo de saída`.
- [ ] Todo recurso empacotado referenciado por esta skill existe.
- [ ] O validador automático, se existir, passou; avisos e lacunas de validação manual ou de runtime estão reportados explicitamente.
