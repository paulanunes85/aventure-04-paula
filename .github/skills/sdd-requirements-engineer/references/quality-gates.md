# Quality gates unificados de SDD com EARS

Aplique toda verificação relevante. Marque cada uma como `APROVADO`, `REPROVADO`, `BLOQUEADO` ou `NÃO APLICÁVEL` e cite o artefato, ID de requisito, ID de fonte ou evidência usada. Um pacote só passa quando nenhuma verificação aplicável está reprovada ou bloqueada.

Os nomes em maiúsculas (`SPECIFICATION.md`, `DESIGN.md`, `TASKS.md` etc.) identificam responsabilidades descritas nos [modelos de artefatos](spec-templates.md). No layout padrão elas vivem dentro de `spec.md`, `plan.md` e `tasks.md`.

## G1. Escopo e evidência

- [ ] G1.01 O modo de operação e os entregáveis solicitados estão explícitos.
- [ ] G1.02 O contexto do projeto e o limite do sistema estão identificados.
- [ ] G1.03 Atores principais, permissões e ações proibidas são conhecidos.
- [ ] G1.04 O resultado principal e o limite de escopo são conhecidos.
- [ ] G1.05 Artefatos e convenções existentes do repositório foram inspecionados.
- [ ] G1.06 Toda fonte tem ID estável `SRC-###` e classe de fonte.
- [ ] G1.07 Premissas têm impacto, responsável e estado de confirmação.
- [ ] G1.08 Metas, políticas ou aprovações sem suporte permanecem como bloqueios visíveis.
- [ ] G1.09 A criação de arquivos ocorreu apenas quando solicitada ou explicitamente autorizada.
- [ ] G1.10 Contradições entre fontes estão registradas com as interpretações possíveis e um responsável pela decisão.

## G2. Requisitos EARS

- [ ] G2.01 Todo requisito normativo tem ID único e estável.
- [ ] G2.02 Todo requisito normativo registra exatamente uma classificação EARS.
- [ ] G2.03 A ordem das cláusulas corresponde ao padrão EARS selecionado.
- [ ] G2.04 A declaração usa `deve` (ou `shall`) e nomeia o sistema ou componente responsável.
- [ ] G2.05 A declaração tem uma resposta observável e nenhum comportamento composto oculto.
- [ ] G2.06 Pré-condições, gatilhos, opcionalidade e condições indesejadas estão explícitos quando aplicável.
- [ ] G2.07 Requisitos funcionais declaram comportamento, não implementação.
- [ ] G2.08 Todo requisito tem fonte (`origem:`), justificativa, prioridade, sinal de aceite, método de verificação e status.
- [ ] G2.09 Toda prioridade tem justificativa baseada em impacto.
- [ ] G2.10 Caminhos de erro, entrada inválida, timeout, falha de dependência e recuperação estão cobertos quando aplicável.
- [ ] G2.11 Comportamento dependente de ciclo de vida tem modelo de estados e requisitos orientados a estado.
- [ ] G2.12 Termos, formatos de entrada e unidades estão definidos de forma consistente.

## G3. Prontidão do FRD

- [ ] G3.01 Problema, resultados desejados, sinais de sucesso, itens em escopo e não objetivos estão explícitos.
- [ ] G3.02 Todo ator participa de um requisito ou é explicitamente informativo.
- [ ] G3.03 Requisitos estão agrupados por domínio e preservam IDs estáveis.
- [ ] G3.04 Interações externas incluem contratos e comportamento em falha.
- [ ] G3.05 As linhas do resumo correspondem exatamente aos registros normativos.
- [ ] G3.06 Incrementos de entrega estão ordenados por dependência e são revisáveis.
- [ ] G3.07 Todo requisito P0 está justificado como essencial ao incremento nomeado.
- [ ] G3.08 Perguntas em aberto identificam responsável e escopo afetado.

## G4. Prontidão do NFRD

- [ ] G4.01 Toda categoria de qualidade tem decisão de aplicabilidade.
- [ ] G4.02 Toda categoria aplicável tem requisitos ou um bloqueio explícito.
- [ ] G4.03 Toda métrica define meta, agregação, janela, carga, ambiente, instrumentação e responsável.
- [ ] G4.04 Toda meta numérica cita evidência ou aprovação de um responsável.
- [ ] G4.05 Todo contexto de implantação tem cobertura ou um bloqueio visível.
- [ ] G4.06 Autenticação, autorização, proteção de dados e comportamento de abuso ou falha estão cobertos quando aplicável.
- [ ] G4.07 Requisitos de confiabilidade definem detecção, degradação, recuperação, RTO ou RPO somente quando aplicáveis e com fonte.
- [ ] G4.08 Conformidade está aplicável, não aplicável ou bloqueada, com responsável.
- [ ] G4.09 Escopo de acessibilidade e localização está explícito para superfícies voltadas ao usuário.
- [ ] G4.10 Qualidade, linhagem, migração, retenção e exclusão de dados estão cobertas quando aplicável.
- [ ] G4.11 Restrições tecnológicas têm fonte, justificativa e gatilho de revisão.

## G5. Integridade dos artefatos SDD

- [ ] G5.01 A constituição do repositório é reutilizada ou existe um artefato governante justificado.
- [ ] G5.02 A especificação contém os requisitos ativos canônicos.
- [ ] G5.03 A análise registra evidências, lacunas, riscos e alternativas.
- [ ] G5.04 O design cobre arquitetura, dados, interfaces, segurança, falhas e trade-offs exigidos pelo escopo.
- [ ] G5.05 Diagramas Mermaid estão presentes e válidos quando arquitetura, contexto, implantação, estado, sequência, fluxo de dados ou ciclo de vida forem relevantes.
- [ ] G5.06 As tarefas estão ordenadas por dependência e toda tarefa tem resultado de evidência esperado.
- [ ] G5.07 Toda tarefa `[P]` é independente em dependências e em superfície de mudança.
- [ ] G5.08 O checklist contém gates de revisão, implementação, verificação e release aplicáveis ao escopo.
- [ ] G5.09 As decisões registram escolhas relevantes, alternativas, consequências, evidências e gatilhos de revisão.
- [ ] G5.10 Artefatos opcionais existem somente quando convenções do repositório ou risco os justificam.
- [ ] G5.11 Todo tipo de Mermaid usa o tema claro universal; diagramas tipo grafo carregam as classes canônicas default/zone/external e tipos não estilizáveis não contêm `classDef`.
- [ ] G5.12 O design inclui uma visão de entrega que mapeia requisitos por componentes, tarefas/plano, dependências, testes/evidências e estado atual versus alvo.
- [ ] G5.13 Toda tarefa tem checkbox, marcador de sequência, mapeamento de plano, rastreio de requisito e superfície de mudança; o DAG cobre todas as tarefas e as tarefas marcadas correspondem ao registro de verificação.

## G6. Rastreabilidade e ciclo de vida

- [ ] G6.01 Todo requisito ativo tem exatamente uma linha explícita de fonte primária.
- [ ] G6.02 Todo requisito ativo mapeia para design, tarefas, aceite e verificação.
- [ ] G6.03 Todo elemento de design mapeia para um ou mais requisitos governantes.
- [ ] G6.04 Toda tarefa de implementação mapeia para um ou mais requisitos ou para uma obrigação de governança com fonte.
- [ ] G6.05 Todo item de verificação mapeia para um requisito e um sinal de aceite.
- [ ] G6.06 Nenhum requisito, elemento de design, tarefa ou item de verificação ativo está órfão.
- [ ] G6.07 Resumos copiados não redefinem nem contradizem declarações normativas canônicas.
- [ ] G6.08 IDs divididos, mesclados, transferidos, substituídos e aposentados têm disposições explícitas.
- [ ] G6.09 IDs históricos estáveis não foram renomeados em massa silenciosamente.
- [ ] G6.10 Contagens e valores de status entre artefatos concordam.

## G7. Prontidão e handoff

- [ ] G7.01 Os status dos artefatos não excedem a evidência de aprovação ou execução disponível.
- [ ] G7.02 Verificações reprovadas e bloqueadas incluem responsável e ação corretiva.
- [ ] G7.03 O escopo aprovado para implementação é um conjunto explícito de IDs de requisitos.
- [ ] G7.04 Dependências e ordenação estão claras para um agente de implementação.
- [ ] G7.05 A evidência de validação exigida e as condições de parada estão explícitas.
- [ ] G7.06 Comportamento atual de plataformas externas cita evidência oficial datada.
- [ ] G7.07 O handoff exclui bloqueios não resolvidos.
- [ ] G7.08 O relatório de entrega segue o modelo de saída da skill.

## Regra de decisão

- `APROVADO`: todas as verificações aplicáveis passam.
- `PRONTO PARA REVISÃO`: nenhum bloqueio permanece, mas a aprovação do responsável está pendente.
- `BLOQUEADO`: pelo menos um fato, decisão, fonte ou mapeamento obrigatório está ausente.
- `REPROVADO`: um artefato ou requisito aplicável viola uma verificação que pode ser corrigida com a evidência disponível.

Não transforme `BLOQUEADO` ou `REPROVADO` em redação com cara de sucesso.
