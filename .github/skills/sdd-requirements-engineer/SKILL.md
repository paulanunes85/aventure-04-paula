---
name: "sdd-requirements-engineer"
description: "Elicita, normaliza, valida e rastreia requisitos em um fluxo completo de Spec-Driven Development usando EARS. Use ao converter notas, PRDs, documentos de requisitos, atas, evidências de sistemas existentes ou insumos de design em FRD/NFRD, spec.md, plan.md, tasks.md, matrizes de rastreabilidade, quality gates ou um handoff SDD pronto para implementação. Gatilhos: EARS, requisitos, especificação, SDD, spec-driven, FRD, NFRD, rastreabilidade, critérios de aceite."
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
| Requisitos | Notas, PRD, issue, entrevistas, documento de requisitos ou evidência de sistema existente | Análise de lacunas mais FRD e NFRD (ou seções equivalentes em `spec.md`) |
| SDD completo | Requisitos brutos ou aprovados | `spec.md`, `plan.md` e `tasks.md` com análise, decisões, gates e rastreabilidade |
| Design-first | Esboço de arquitetura, contrato de API, modelo de dados ou protótipo | Requisitos recuperados, premissas explícitas e depois a cadeia SDD completa |
| Validação | FRD, NFRD, especificação, design ou tarefas existentes | Achados por severidade, declarações EARS corrigidas e decisão de prontidão |
| Handoff | Artefatos SDD revisados | Pacote de implementação delimitado, com gates, dependências e bloqueios não resolvidos |

Selecione o menor modo que atende ao pedido. Não gere o conjunto completo de artefatos para a revisão de um único requisito.

## Contrato do repositório

Leia primeiro as [instruções de artefatos SDD](../../instructions/sdd-artifacts.instructions.md) e o [copilot-instructions.md](../../copilot-instructions.md). Por padrão, `Requisitos` é dono de `specs/<NNN>-<funcionalidade>/spec.md`; `SDD completo` significa o pacote aprovado `spec.md`, `plan.md` e `tasks.md`, não dez arquivos extras. Mantenha fontes e aceite em `spec.md`, design e decisões em `plan.md` ou ADRs vinculados, e mapeamento de testes e evidências de execução em `tasks.md`. Os modelos estendidos abaixo são seções de referência opcionais, não entregáveis obrigatórios.

Use `REQ-NNN`/`NFR-NNN`, `AC-<ID>-NN` e uma linha `origem:` válida, salvo se o repositório já tiver outro esquema. Preserve identificadores e especificações existentes. Não crie `.specs/` nem renomeie artefatos existentes. Só exija verificações executáveis que existam no repositório; validação textual não é evidência de runtime nem de aprovação.

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
   - Use o [modelo de FRD](references/frd-template.md) e o [modelo de NFRD](references/nfrd-template.md) quando esses artefatos estiverem no escopo.
   - Siga o esquema de IDs do repositório. Preserve IDs existentes; IDs genéricos dos modelos não são instrução de migração.
   - Escreva uma resposta observável do sistema por declaração EARS. Divida comportamento composto.
   - Mantenha requisitos funcionais neutros quanto à implementação. Coloque restrições tecnológicas genuínas no NFRD, com justificativa e fonte.
   - Dê a todo requisito prioridade, fonte, justificativa, sinal de aceite, método de verificação e status de ciclo de vida.
   - Expresse NFRs numéricos com contexto de medição: métrica, meta, carga, percentil ou agregação, janela de observação, ambiente e responsável pela evidência. Se algum valor obrigatório for desconhecido, mantenha um bloqueio visível.
   - Transforme exemplos fornecidos pelo negócio em sinais de aceite; exemplos com resultado ambíguo ou em aberto viram perguntas, não requisitos.
   - Adicione um modelo de estados quando o comportamento depender do ciclo de vida de uma entidade.

5. Construa a cadeia de artefatos SDD.
   - Leia os [modelos de artefatos SDD](references/spec-templates.md) e o [padrão de documentos SDD e Mermaid](references/sdd-document-and-mermaid-standard.md).
   - Reutilize a constituição do repositório quando existir. Não crie uma constituição local conflitante.
   - Para SDD completo, crie ou atualize especificação, análise, design, tarefas, checklist, análise cruzada, verificação, decisões e rastreabilidade de fontes dentro dos artefatos donos; adicione planos ou manifestos opcionais apenas quando o risco justificar.
   - Use o portfólio de design, o tema Mermaid claro universal, as classes canônicas de grafo e uma visão de entrega que conecte requisitos, componentes, tarefas, dependências, evidências e estado atual versus alvo.
   - Escreva checkboxes de tarefas ordenadas por dependência com metadados de sequência/plano/requisito/mudança/evidência, um DAG completo, mapa de testes, gate de conclusão e registro; marque apenas tarefas com evidência completa e use `[P]` apenas quando forem realmente independentes.
   - Use pastas sequenciais como `001-nome-da-funcionalidade` apenas ao iniciar ou seguir essa convenção do repositório.

6. Garanta rastreabilidade ponta a ponta.
   - Dê a todo requisito ativo um mapeamento explícito de fonte em `spec.md` e mantenha sua linha `origem:`.
   - Mapeie cada requisito ativo para componentes de design em `plan.md` e para tarefas, critérios de aceite e verificação planejada ou executada em `tasks.md`. Arquivos de rastreabilidade separados são opcionais.
   - Rejeite requisitos, elementos de design, tarefas e testes órfãos.
   - Registre IDs transferidos, substituídos, divididos, mesclados ou aposentados em uma tabela de disposição. Nunca renumere silenciosamente requisitos estáveis.
   - Preserve o mesmo significado normativo em FRD/NFRD, especificação, design, tarefas e testes. Referencie por ID em vez de copiar texto que pode divergir.

7. Valide e entregue.
   - Aplique todas as verificações aplicáveis dos [quality gates unificados](references/quality-gates.md).
   - Use o [catálogo de antipadrões](references/anti-patterns.md) para corrigir defeitos antes da entrega.
   - Mantenha artefatos como `Rascunho` ou `Pronto para revisão` até um revisor responsável aprová-los.
   - Use `Implementado` ou `Verificado` apenas quando houver evidência no repositório ou de execução.
   - Se o repositório tiver um validador de rastreabilidade, execute-o para as especificações alteradas e reporte o resultado. Caso contrário, faça a verificação manual descrita nas instruções de artefatos e reporte o validador como não executado. Revise significado EARS, aprovações e renderização de diagramas separadamente.
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
- Não force todos os artefatos opcionais em mudanças pequenas quando um conjunto mais leve e rastreável for suficiente.

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
- [Modelos de artefatos SDD](references/spec-templates.md): responsabilidades completas dos artefatos e modelos concisos.
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
- [ ] O conteúdo de FRD e NFRD está completo para toda categoria aplicável.
- [ ] Os artefatos SDD são internamente consistentes e proporcionais ao escopo.
- [ ] Todo diagrama Mermaid usa o tema claro universal e todo diagrama tipo grafo carrega as classes neutras canônicas.
- [ ] `plan.md` mapeia requisitos por componentes, tarefas, dependências, testes/evidências e estado atual versus alvo.
- [ ] Checkboxes de `tasks.md`, DAG aplicável, mapa de testes e registro de verificação concordam; implementação parcial não é marcada como concluída.
- [ ] Todo requisito ativo é rastreável da fonte ao design, tarefas, aceite e verificação.
- [ ] Mudanças de ciclo de vida preservam IDs ou incluem disposições explícitas.
- [ ] Nenhuma métrica, aprovação, afirmação de compatibilidade ou fato atual de plataforma foi fabricado.
- [ ] Toda verificação detalhada aplicável dos [quality gates unificados](references/quality-gates.md) passa ou é reportada como bloqueio.
- [ ] A resposta segue exatamente o `## Modelo de saída`.
- [ ] Todo recurso empacotado referenciado por esta skill existe.
- [ ] O validador automático, se existir, passou; avisos e lacunas de validação manual ou de runtime estão reportados explicitamente.
