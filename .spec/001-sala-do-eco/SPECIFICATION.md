# SPECIFICATION: Sala do Eco (Fase 1 - console)

- ID da funcionalidade: 001
- Slug: sala-do-eco
- Status: Rascunho
- Etapa dona: /write-ears-spec
- Versão: 0.1.0 (2026-09-24)
- Fontes: SRC-001, SRC-002, SRC-003 (registro em SOURCE_TRACEABILITY.md)
- Constituição: não existe (`CONSTITUTION.md` ausente em 2026-09-24); governança por `.github/copilot-instructions.md` e `.github/instructions/`
- Aprovação: PENDENTE (aprovadores "A definir" em `requisitos/requisitos.md#L11`; ver Q-016)

## Problema e resultado

Hoje os professores trabalham sequências numéricas em planilha e no quadro, o que consome tempo de aula (`requisitos/requisitos.md#L22`). O resultado desejado para a Fase 1 é que o aluno informe uma sequência na Sala do Eco, uma versão em console, e receba o próximo número ("eco"). Isso torna o aprendizado mais lúdico e reduz o tempo de correção (`requisitos/requisitos.md#L18`, `#L26-L27`, `#L32`).

## Escopo e não objetivos

- **Em escopo (hipótese ASM-002):** Fase 1, versão console chamada Sala do Eco. Inclui REQ-001 a REQ-007 e NFR-001 a NFR-003.
- **Adiados por decisão pendente de fase (Q-012):** RF-09, RF-10, RF-11, RF-20, RNF-10, RNF-14. São itens da versão web Castelo do Eco (`requisitos/requisitos.md#L34-L36`).
- **Adiados por status "Em análise" na fonte:** RF-08, RF-12, RF-16.
- **Bloqueados até resposta do Product Owner (sem requisito atribuído):**
  - memórias e histórico: RF-05, RF-19, RNF-11 (Q-008, Q-009);
  - visão do professor: RF-18 (Q-010);
  - apagar memórias: RF-17 (Q-011);
  - decimais e formatos livres: RF-14 (Q-005);
  - entrada não numérica: exemplo em `#L110` (Q-004).
- **Não normativos até haver envelope de medição ou critério verificável (Q-014, Q-006):** RF-15, RF-21, RNF-02 a RNF-08, RNF-12, RNF-13.
- **Fora do escopo declarado na fonte:** "A definir" (`requisitos/requisitos.md#L38`).

## Atores e dependências

| Ator ou dependência | Papel | Fonte |
| --- | --- | --- |
| Aluno | Informa sequências e recebe ecos | SRC-001 (`#L42`, `#L18`) |
| Professores | Fornecem exemplos e resultados esperados | SRC-001 (`#L99-L110`) |
| Coordenação Pedagógica | Responsável pelo documento de origem | SRC-001 (`#L6-L7`) |
| TI | Define restrições técnicas (RNF-01, RF-13) | SRC-001 (`#L62`, `#L78`) |
| Product Owner / aprovadores | Decide perguntas em aberto e aprova a spec; ainda não identificado | SRC-001 (`#L11`); Q-016 |

## Glossário

| Termo | Definição | Fonte |
| --- | --- | --- |
| Sala do Eco | Versão em console da Fase 1 | SRC-001 (`#L32`) |
| Sequência | Lista ordenada de números informada pelo aluno | SRC-001 (`#L18`, `#L51`) |
| Eco | Resposta da Sala do Eco com o próximo número da sequência | SRC-001 (`#L18`) |
| Sessão | Período entre abrir e encerrar a Sala do Eco; a forma de encerrar está pendente (Q-007) | SRC-001 (`#L56`) |
| Memória | PENDENTE: significado e persistência indefinidos (Q-008) | SRC-001 (`#L55`, `#L68`) |

## Requisitos

### REQ-001: Ecoar o próximo termo de uma progressão aritmética
origem: SRC-001 (requisitos/requisitos.md#L51-L52, #L95, #L103)

- IDs da fonte: RF-01, RF-02, RN-01
- Padrão: orientado a evento
- Prioridade: P0. RF-01 e RF-02 são "Alta" e "Aprovado" (ASM-001). Sem este comportamento, a Fase 1 não entrega o eco.
- Status: Proposto
- Justificativa: é o comportamento central da Sala do Eco e o "exemplo oficial" dos professores.

> Quando o aluno informar uma sequência que forma uma progressão aritmética, a Sala do Eco deve responder com o próximo termo dessa progressão.

**Sinais de aceite**
- AC-REQ-001-01: Dado a sequência `3, 6, 9, 12`, Quando o aluno a informa, Então a Sala do Eco responde `15`.

**Verificação**
- teste: `deve_ecoar_15_quando_sequencia_e_3_6_9_12` com a entrada `[3, 6, 9, 12]`. Falha antes da implementação porque ainda não existe comportamento de previsão. Passa quando o eco é `15`.
- Nota: o comprimento mínimo da PA depende de Q-002. Não há critério para `2, 4` enquanto a pergunta estiver aberta.

### REQ-002: Ecoar o próximo termo de uma sequência polinomial
origem: SRC-001 (requisitos/requisitos.md#L53, #L104)

- IDs da fonte: RF-03, RN-01
- Padrão: orientado a evento
- Prioridade: P0. RF-03 é "Alta" e "Aprovado" (ASM-001).
- Status: Proposto. **Bloqueio parcial:** o grau máximo e a precedência entre padrões dependem de Q-003.
- Justificativa: RF-03 pede sequências polinomiais, e os professores fornecem o exemplo dos quadrados.

> Quando o aluno informar uma sequência polinomial de grau até o limite aprovado, a Sala do Eco deve responder com o próximo termo dessa sequência.

**Sinais de aceite**
- AC-REQ-002-01: Dado a sequência `1, 4, 9, 16`, Quando o aluno a informa, Então a Sala do Eco responde `25`.

**Verificação**
- teste: `deve_ecoar_25_quando_sequencia_e_1_4_9_16` com a entrada `[1, 4, 9, 16]`. Falha antes da implementação porque só progressões aritméticas são reconhecidas (REQ-001). Passa quando o eco é `25`.
- Nota: `1, 4, 9, 16` dá `25` em qualquer grau a partir de 2. Não há critério para o limite de grau enquanto Q-003 estiver aberta.

### REQ-003: Ecoar o próximo termo de uma progressão geométrica
origem: SRC-001 (requisitos/requisitos.md#L53, #L105); SRC-002 (requisitos/requisitos.md#L138-L140)

- IDs da fonte: RF-03
- Padrão: orientado a evento
- Prioridade: P0. RF-03 é "Alta" e "Aprovado" (ASM-001).
- Status: Proposto. **BLOQUEADO** por Q-001 e Q-003.
- Justificativa: RF-03 pede explicitamente progressões geométricas.

> Quando o aluno informar uma sequência que forma uma progressão geométrica, a Sala do Eco deve responder com o próximo termo dessa progressão.

**Sinais de aceite**
- BLOQUEADO. O único exemplo da fonte, `2, 4, 8`, tem dois resultados esperados: `16` em `#L105` e `14` em `#L138`. Enquanto polinômios sem limite de grau forem aceitos (Q-003), toda PG também se ajusta a um polinômio com outro próximo termo. Os professores precisam fornecer um exemplo sem ambiguidade.

**Verificação**
- teste: PENDENTE. O ciclo TDD é NÃO APLICÁVEL até existir um exemplo aprovado.

### REQ-004: Ecoar o próximo termo de uma sequência de Fibonacci
origem: SRC-001 (requisitos/requisitos.md#L53, #L107)

- IDs da fonte: RF-03 ("entre outras"); exemplo dos professores
- Padrão: orientado a evento
- Prioridade: P0, herdada de RF-03 "Alta" (ASM-001). Confirmar se Fibonacci faz parte de "entre outras" (Q-003).
- Status: Proposto. **Bloqueio parcial:** a precedência sobre o ajuste polinomial depende de Q-003.
- Justificativa: exemplo explícito dos professores ("Os alunos adoram Fibonacci").

> Quando o aluno informar uma sequência em que cada termo, a partir do terceiro, é a soma dos dois anteriores, a Sala do Eco deve responder com a soma dos dois últimos termos.

**Sinais de aceite**
- AC-REQ-004-01: Dado a sequência `1, 1, 2, 3, 5`, Quando o aluno a informa, Então a Sala do Eco responde `8`.

**Verificação**
- teste: `deve_ecoar_8_quando_sequencia_e_1_1_2_3_5` com a entrada `[1, 1, 2, 3, 5]`. Falha antes da implementação porque o padrão não é reconhecido. Passa quando o eco é `8`.
- Nota: um polinômio de grau 4 ajusta os mesmos termos com próximo termo `11`. O critério vale somente se Q-003 der precedência a Fibonacci ou limitar o grau.

### REQ-005: Recusar sequência com menos números que o mínimo
origem: SRC-001 (requisitos/requisitos.md#L54, #L62, #L108)

- IDs da fonte: RF-04, RF-13
- Padrão: indesejado
- Prioridade: P0. RF-04 e RF-13 são "Alta" e "Aprovado" (ASM-001). Sem este comportamento, o aluno recebe um eco sem base.
- Status: Proposto. **Bloqueio parcial:** o valor do mínimo depende de Q-002, e o critério de mensagem "clara" depende de Q-006.
- Justificativa: RF-13 exige um mínimo de números, e os professores esperam "Erro" para uma entrada com um único número.

> Se o aluno informar uma sequência com menos números que o mínimo aprovado, então a Sala do Eco deve responder com um aviso de sequência inválida em vez de um próximo número.

**Sinais de aceite**
- AC-REQ-005-01: Dado a entrada `5`, Quando o aluno a informa, Então a Sala do Eco exibe um aviso de sequência inválida e não exibe nenhum próximo número.

**Verificação**
- teste: `deve_avisar_sequencia_invalida_quando_ha_um_unico_numero` com a entrada `[5]`. Falha antes da implementação porque não existe validação de tamanho. Passa quando o resultado é um aviso de sequência inválida, sem número.
- Nota: `1 < 2 ≤ 3`, então `5` é inválido nas duas interpretações de Q-002. Não há critério para `2, 4` enquanto a pergunta estiver aberta.

### REQ-006: Informar quando nenhum padrão é reconhecido
origem: SRC-001 (requisitos/requisitos.md#L54, #L96)

- IDs da fonte: RN-02, RF-04
- Padrão: indesejado
- Prioridade: P0. RF-04 é "Alta" e "Aprovado" (ASM-001); RN-02 não tem prioridade na fonte.
- Status: Proposto. **BLOQUEADO** por Q-003.
- Justificativa: RN-02 exige que o sistema informe quando a sequência não segue nenhum padrão.

> Se a sequência informada não corresponder a nenhum padrão reconhecido, então a Sala do Eco deve informar ao aluno que nenhum padrão foi encontrado.

**Sinais de aceite**
- BLOQUEADO. A fonte não traz exemplo, e sem limite de grau polinomial toda sequência de n números tem ajuste, o que torna esta condição inalcançável (Q-003).

**Verificação**
- teste: PENDENTE. O ciclo TDD é NÃO APLICÁVEL até Q-003 ser resolvida e existir um exemplo aprovado.

### REQ-007: Aceitar nova sequência na mesma sessão
origem: SRC-001 (requisitos/requisitos.md#L56, #L103-L104, #L108)

- IDs da fonte: RF-06
- Padrão: complexo
- Prioridade: P1. RF-06 é "Média" e "Aprovado" (ASM-001). Existe um contorno (reabrir a sessão), mas ele reduz a prática contínua.
- Status: Proposto
- Justificativa: RF-06 pede que o usuário possa testar várias sequências.

> Enquanto a sessão da Sala do Eco estiver aberta, quando o aluno receber a resposta a uma sequência, a Sala do Eco deve aceitar uma nova sequência sem reiniciar a sessão.

**Sinais de aceite**
- AC-REQ-007-01: Dado que a Sala do Eco respondeu `15` para `3, 6, 9, 12`, Quando o aluno informa `1, 4, 9, 16` na mesma sessão, Então a Sala do Eco responde `25`.
- AC-REQ-007-02: Dado que a Sala do Eco recusou a entrada `5`, Quando o aluno informa `3, 6, 9, 12` na mesma sessão, Então a Sala do Eco responde `15`.

**Verificação**
- teste: `deve_ecoar_segunda_sequencia_quando_sessao_continua_aberta`, com duas entradas consecutivas na mesma sessão. Falha antes da implementação porque a sessão termina após o primeiro eco. Passa quando os ecos são `15` e depois `25`.
- teste: `deve_aceitar_nova_sequencia_quando_anterior_foi_recusada`, com as entradas `[5]` e `[3, 6, 9, 12]`. Passa quando o resultado é um aviso e depois `15`.
- Nota: a forma de encerrar a sessão está pendente (Q-007).

### NFR-001: Executar em JavaScript sobre Node.js
origem: SRC-001 (requisitos/requisitos.md#L78); SRC-003 (.github/copilot-instructions.md, tabela "Stack e comandos")

- IDs da fonte: RNF-01 (primeira parte)
- Categoria: restrição tecnológica
- Padrão: ubíquo
- Prioridade: P0. RNF-01 é "Alta" e "Aprovado", e a fonte o declara como padrão já aprovado pela TI.
- Status: Proposto
- Justificativa: padrão tecnológico aprovado pela TI. Gatilho de revisão: mudança do padrão da TI ou decisão sobre a Fase 2.

> A Sala do Eco deve ser implementada em JavaScript e executada em Node.js 24 LTS.

**Sinais de aceite**
- AC-NFR-001-01: Dado o repositório da Sala do Eco, Quando o código-fonte é inspecionado, Então todo código de produto está em JavaScript e é executado com Node.js 24 LTS.

**Verificação**
- inspeção: revisão do código e da versão de runtime declarada. O ciclo TDD é NÃO APLICÁVEL porque se trata de uma restrição de plataforma, não de comportamento.

### NFR-002: Ponto de entrada `index.js`
origem: SRC-001 (requisitos/requisitos.md#L78)

- IDs da fonte: RNF-01 (segunda parte)
- Categoria: restrição tecnológica
- Padrão: ubíquo
- Prioridade: P0. RNF-01 é "Alta" e "Aprovado".
- Status: Proposto
- Justificativa: a fonte exige que o arquivo principal se chame `index.js`.

> A Sala do Eco deve ter como arquivo principal um arquivo chamado `index.js`.

**Sinais de aceite**
- AC-NFR-002-01: Dado o repositório da Sala do Eco, Quando o comando `node index.js` é executado na raiz, Então a sessão da Sala do Eco é iniciada.

**Verificação**
- demonstração: executar `node index.js` e observar o início da sessão. O ciclo TDD é NÃO APLICÁVEL. Um teste de fumaça que inicie o processo é opcional e cabe à fase de tarefas.

### NFR-003: Mensagens em português
origem: SRC-001 (requisitos/requisitos.md#L86); SRC-003 (.github/copilot-instructions.md, tabela "Projeto")

- IDs da fonte: RNF-09
- Categoria: localização
- Padrão: ubíquo
- Prioridade: P0. RNF-09 é "Alta" e "Aprovado".
- Status: Proposto
- Justificativa: o público da Fase 1 é de alunos que usam o português. Uma versão em outro idioma está em aberto (Q-015).

> A Sala do Eco deve apresentar todas as mensagens ao aluno em português do Brasil.

**Sinais de aceite**
- AC-NFR-003-01: Dado as respostas da Sala do Eco (ecos, avisos e instruções), Quando elas são inspecionadas, Então todo texto exibido ao aluno está em português do Brasil.

**Verificação**
- inspeção: revisão do catálogo de mensagens. O ciclo TDD é NÃO APLICÁVEL porque a qualidade linguística não é verificável por asserção automática.

## Premissas, bloqueios e perguntas em aberto

| ID | Tipo | Declaração | Evidência | Interpretações possíveis | Impacto | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ASM-001 | premissa | As prioridades da fonte são mapeadas como Alta → P0, Média → P1, Baixa → P2 | `requisitos/requisitos.md#L49-L70` | A) manter o mapeamento / B) repriorizar por impacto no incremento | Prioridade de todos os REQ/NFR | Product Owner | Aberta |
| ASM-002 | premissa | Esta spec cobre só a Fase 1 (console) | `requisitos/requisitos.md#L32-L36`; `.github/copilot-instructions.md` | Ver Q-012 | Escopo inteiro | Product Owner | Aberta |
| ASM-003 | premissa (da fonte) | Os alunos já sabem o que é uma progressão | `requisitos/requisitos.md#L114` | n/a | Texto das mensagens | Coordenação Pedagógica | Não confirmada |
| ASM-004 | premissa (da fonte) | Não haverá servidor por enquanto | `requisitos/requisitos.md#L115`, `#L130` | n/a | Fase 2 e persistência | TI | Não confirmada |
| ASM-005 | premissa (da fonte) | Não haverá login | `requisitos/requisitos.md#L116`, `#L134` | n/a | RF-17, RF-18 | Product Owner | Não confirmada |
| Q-001 | bloqueio | Qual é o eco de `2, 4, 8`, dado que o diretor pede "acertar sempre"? | `requisitos/requisitos.md#L105`, `#L138-L140` | A) PG → 16 / B) diferenças → 14 / C) avisar que há ambiguidade | REQ-003; "acertar sempre" não é verificável | Product Owner + professores | Aberta |
| Q-002 | bloqueio | O mínimo é 3 números (RF-13) ou `2, 4 → 6` precisa funcionar? | `requisitos/requisitos.md#L62`, `#L106` | A) mínimo 3 e `2, 4` é erro / B) mínimo 2 | REQ-001, REQ-005 | Product Owner + TI | Aberta |
| Q-003 | bloqueio | Quais padrões entram em "entre outras", qual é o grau polinomial máximo e qual padrão vence quando dois servem? `1, 1, 2, 3, 5` dá 8 (Fibonacci) ou 11 (grau 4) | `requisitos/requisitos.md#L53`, `#L95-L97`, `#L107` | A) lista fechada com precedência / B) polinômio sem limite, e aí RN-02 nunca dispara | REQ-002, REQ-003, REQ-004, REQ-006 | Product Owner + professores de matemática | Aberta |
| Q-004 | pergunta | Qual é o resultado de `10, 20, 30, abc`? | `requisitos/requisitos.md#L110` | A) recusar com aviso / B) ignorar o token e ecoar 40 | Entrada não numérica sem requisito | Product Owner + TI | Aberta |
| Q-005 | pergunta | Quais formatos de entrada são aceitos? Decimais com vírgula são obrigatórios? Negativos entram? | `requisitos/requisitos.md#L63`, `#L109`, `#L123` | A) lista fechada de formatos / B) entrada livre | RF-14 sem requisito | Product Owner + professores | Aberta |
| Q-006 | pergunta | Que critério verificável define aviso "claro" (RF-04) e quais são os "casos de borda" (RF-15)? | `requisitos/requisitos.md#L54`, `#L64` | A) lista enumerada de casos e mensagens / B) critério de linguagem por faixa etária | REQ-005, REQ-006 | Product Owner | Aberta |
| Q-007 | pergunta | Como o aluno encerra a sessão? | `requisitos/requisitos.md#L56` | A) comando de saída / B) só com o encerramento do terminal | REQ-007 | Product Owner | Aberta |
| Q-008 | pergunta | RF-05 e RF-19 são o mesmo requisito? As memórias persistem entre execuções? Entram na Fase 1 ou na 2? Como medir "nunca perdidas"? | `requisitos/requisitos.md#L34`, `#L55`, `#L68`, `#L88` | A) só durante a sessão / B) persistência local / C) só na Fase 2 | RF-05, RF-17, RF-19, RNF-11 | Product Owner + TI | Aberta |
| Q-009 | pergunta | Qual é a faixa etária dos alunos? Que dados deles podem ser guardados e por quanto tempo? A LGPD se aplica? | `requisitos/requisitos.md#L42`, `#L55`, `#L67`, `#L132` | A) guardar sem identificação / B) guardar com identificação e consentimento | RF-05, RF-18, RF-19 | Product Owner + Coordenação Pedagógica | Aberta |
| Q-010 | pergunta | Como o professor vê "cada aluno" se não há login? | `requisitos/requisitos.md#L67`, `#L116`, `#L132-L134` | A) o aluno digita o próprio nome / B) adotar login / C) visão só agregada | RF-18 | Product Owner | Aberta |
| Q-011 | pergunta | Quem é o administrador e como ele é identificado? Apagar é total ou por aluno? | `requisitos/requisitos.md#L44`, `#L66`, `#L120` | A) coordenação / B) TI / C) papel removido | RF-17 | Product Owner | Aberta |
| Q-012 | pergunta | A Fase 2 entra junto com a Fase 1? Sala e Castelo são o mesmo produto? | `requisitos/requisitos.md#L32-L38`, `#L128-L130` | A) só Fase 1 / B) as duas fases, o que exige hospedagem | Escopo inteiro (ASM-002) | Product Owner + Diretoria | Aberta |
| Q-013 | pergunta | Qual é a disposição de RF-07, removido sem motivo registrado? | `requisitos/requisitos.md#L72` | A) aposentado / B) substituído | Rastreabilidade | Product Owner | Aberta |
| Q-014 | pergunta | Que métricas definem "rápido", "instantânea" e "sequência grande"? | `requisitos/requisitos.md#L70`, `#L79`, `#L85`, `#L122` | A) tamanho máximo e tempo-alvo definidos / B) bloqueado até haver medição | NFRs de desempenho não normativos | Product Owner + TI | Aberta |
| Q-015 | pergunta | Haverá versão em outro idioma para a escola parceira do Chile? | `requisitos/requisitos.md#L86`, `#L121` | A) só pt-BR na Fase 1 / B) multilíngue | NFR-003 | Product Owner | Aberta |
| Q-016 | pergunta | Quem é o Product Owner e quem aprova esta spec? | `requisitos/requisitos.md#L11` | n/a | Aprovação de todos os requisitos | Coordenação Pedagógica | Aberta |

## Validação (2026-09-24)

| Gate | Resultado | Evidência ou motivo |
| --- | --- | --- |
| G1.01-G1.05 Escopo, atores, convenções | PASS | Modo Requisitos; Fase 1 (ASM-002); atores listados; o repositório não tinha `specs/` nem constituição |
| G1.03 Permissões e ações proibidas | BLOQUEADO | Administrador e professor indefinidos (Q-010, Q-011); fora dos requisitos ativos |
| G1.06-G1.08 Fontes e premissas | PASS | SRC-001 a SRC-003; premissas com responsável; nenhuma meta inventada |
| G1.10 Contradições | PASS | Q-001, Q-002, Q-003, Q-005 e Q-010 registradas com interpretações |
| G2.01-G2.07 Forma EARS | PASS | 10 declarações com um padrão, `deve`, sujeito "Sala do Eco" e uma resposta; nenhum requisito funcional nomeia tecnologia |
| G2.08 Metadados completos | FAIL | REQ-003 e REQ-006 não têm sinal de aceite (BLOQUEADO por Q-001 e Q-003) |
| G2.09 Prioridade justificada | BLOQUEADO | Depende da confirmação de ASM-001 |
| G2.10 Caminhos de erro | BLOQUEADO | Entrada não numérica (Q-004) e "casos de borda" (Q-006) sem requisito |
| G2.11 Ciclo de vida | NÃO APLICÁVEL | Só existe a sessão; o encerramento está pendente (Q-007) |
| G4.03-G4.04 NFR mensuráveis | NÃO APLICÁVEL | Os NFRs ativos são restrições verificadas por inspeção; os de desempenho continuam não normativos (Q-014) |
| G4.06 Segurança e proteção de dados | BLOQUEADO | Q-009; sem persistência nos requisitos ativos |
| G6.01 `origem:` em todo requisito ativo | PASS | 10/10, verificado manualmente |
| G6.02 Design, tarefas e verificação | NÃO APLICÁVEL | `plan.md` e `tasks.md` não foram solicitados neste passo |
| G6.05 Verificação ↔ aceite | PASS | Todo AC tem verificação planejada; REQ-003 e REQ-006 estão PENDENTES |
| G6.08 Disposições | PASS | Todos os IDs da fonte estão na tabela de disposição, inclusive RF-07 |
| Validador automático | NÃO EXECUTADO (inexistente) | Não há script nem job de rastreabilidade no repositório |

**Decisão:** a spec permanece em `Rascunho`. Os P0 REQ-003 e REQ-006 estão bloqueados, e ASM-001 e Q-016 seguem abertos.

## Histórico de mudanças

| Versão | Data | Mudança |
| --- | --- | --- |
| 0.1.0 | 2026-09-24 | Rascunho inicial derivado de `requisitos/requisitos.md` v0.4 |
