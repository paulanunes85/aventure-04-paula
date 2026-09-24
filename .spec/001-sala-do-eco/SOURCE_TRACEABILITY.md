# SOURCE_TRACEABILITY: Sala do Eco (Fase 1 - console)

- Funcionalidade: 001-sala-do-eco
- Status: Rascunho
- Etapa dona: /write-ears-spec

## Registro de fontes

| ID | Classe | Local ou decisão | Data | Autoridade | Notas |
| --- | --- | --- | --- | --- | --- |
| SRC-001 | repositório | `requisitos/requisitos.md` (v0.4), seções 1 a 10 e 12 | não datado na fonte ("ver histórico"); lido em 2026-09-24 | Coordenação Pedagógica | Documento em revisão; RF/RNF com status próprio; exemplos dos professores em `#L99-L110` |
| SRC-002 | repositório | `requisitos/requisitos.md#L126-L140` (transcrição da reunião de alinhamento) | não datado; lido em 2026-09-24 | Participantes da reunião | Registra as contradições sobre `2, 4, 8`, login e "acertar sempre" |
| SRC-003 | repositório | `.github/copilot-instructions.md` (tabelas "Projeto" e "Stack e comandos") | lido em 2026-09-24 | Mantenedores do repositório | Node.js 24 LTS, JavaScript ESM, `index.js`, interface em pt-BR |

O refinamento de histórias (US-001 a US-012) feito no chat em 2026-09-24 serviu de contexto. Ele não foi gravado e não é fonte primária.

## Matriz de rastreabilidade

| REQ-ID | Padrão EARS | origem | SRC-ID | ID na fonte | AC-ID | Verificação | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | Evento | `requisitos/requisitos.md#L51-L52, #L95, #L103` | SRC-001 | RF-01, RF-02, RN-01 | AC-REQ-001-01 | teste | Proposto |
| REQ-002 | Evento | `requisitos/requisitos.md#L53, #L104` | SRC-001 | RF-03 | AC-REQ-002-01 | teste | Proposto (bloqueio parcial Q-003) |
| REQ-003 | Evento | `requisitos/requisitos.md#L53, #L105, #L138-L140` | SRC-001, SRC-002 | RF-03 | BLOQUEADO | PENDENTE | Bloqueado (Q-001, Q-003) |
| REQ-004 | Evento | `requisitos/requisitos.md#L53, #L107` | SRC-001 | RF-03 | AC-REQ-004-01 | teste | Proposto (bloqueio parcial Q-003) |
| REQ-005 | Indesejado | `requisitos/requisitos.md#L54, #L62, #L108` | SRC-001 | RF-04, RF-13 | AC-REQ-005-01 | teste | Proposto (bloqueio parcial Q-002, Q-006) |
| REQ-006 | Indesejado | `requisitos/requisitos.md#L54, #L96` | SRC-001 | RN-02, RF-04 | BLOQUEADO | PENDENTE | Bloqueado (Q-003) |
| REQ-007 | Complexo | `requisitos/requisitos.md#L56, #L103-L104, #L108` | SRC-001 | RF-06 | AC-REQ-007-01, AC-REQ-007-02 | teste | Proposto |
| NFR-001 | Ubíquo | `requisitos/requisitos.md#L78`; `.github/copilot-instructions.md` | SRC-001, SRC-003 | RNF-01 | AC-NFR-001-01 | inspeção | Proposto |
| NFR-002 | Ubíquo | `requisitos/requisitos.md#L78` | SRC-001 | RNF-01 | AC-NFR-002-01 | demonstração | Proposto |
| NFR-003 | Ubíquo | `requisitos/requisitos.md#L86`; `.github/copilot-instructions.md` | SRC-001, SRC-003 | RNF-09 | AC-NFR-003-01 | inspeção | Proposto |

## Cobertura da fonte

| ID na fonte | Disposição | IDs nesta spec | Motivo |
| --- | --- | --- | --- |
| RF-01 | derivado | REQ-001 | Núcleo da previsão |
| RF-02 | derivado | REQ-001 | PA com exemplo oficial |
| RF-03 | dividido | REQ-002, REQ-003, REQ-004 | Polinomial, geométrica e Fibonacci ("entre outras"); o restante de "entre outras" está pendente (Q-003) |
| RF-04 | dividido | REQ-005, REQ-006 | Recusa por tamanho e ausência de padrão; entrada não numérica pendente (Q-004) |
| RF-05, RF-19 | bloqueado | nenhum | Q-008, Q-009 |
| RF-06 | derivado | REQ-007 | Várias sequências por sessão |
| RF-07 | aposentado na fonte | nenhum | Removido na reunião 2 por motivo desconhecido (`#L72`); Q-013 |
| RF-08, RF-12, RF-16 | adiado | nenhum | Status "Em análise" na fonte |
| RF-09, RF-10, RF-11, RF-20 | adiado | nenhum | Fase 2 (Q-012) |
| RF-13 | derivado | REQ-005 | Valor do mínimo pendente (Q-002) |
| RF-14 | bloqueado | nenhum | "Do jeito que achar melhor" não é verificável; decimais são uma dúvida em aberto (`#L123`) em conflito com o exemplo `#L109` (Q-005) |
| RF-15 | não normativo | nenhum | "Casos de borda" sem lista (Q-006) |
| RF-17 | bloqueado | nenhum | Administrador indefinido (Q-011) |
| RF-18 | bloqueado | nenhum | Conflito com "sem login" (Q-010) |
| RF-21, RNF-02, RNF-08 | não normativo | nenhum | Sem envelope de medição (Q-014) |
| RN-01 | derivado | REQ-001, REQ-002, REQ-004 | Incorporado como justificativa |
| RN-02 | derivado | REQ-006 | Bloqueado por Q-003 |
| RN-03 | pendente na fonte | nenhum | "A definir com os professores" |
| RNF-01 | dividido | NFR-001, NFR-002 | Runtime e arquivo principal |
| RNF-03, RNF-04, RNF-05, RNF-06, RNF-07, RNF-12, RNF-13 | não normativo | nenhum | Termos vagos sem critério (Q-006, Q-014). RNF-06 e RNF-07 são cobertos pelas convenções do repositório (limites de cobertura em SRC-003), não por requisito de produto |
| RNF-09 | derivado | NFR-003 | Interface em português |
| RNF-10, RNF-14 | adiado | nenhum | "Em análise" e dependentes da Fase 2 |
| RNF-11 | bloqueado | nenhum | "Nunca perdidas" não é verificável (Q-008) |

## Disposições históricas

NÃO APLICÁVEL: nenhum ID desta spec foi transferido, substituído, dividido, mesclado ou aposentado desde a versão 0.1.0.

## Histórico de mudanças

| Versão | Data | Mudança |
| --- | --- | --- |
| 0.1.0 | 2026-09-24 | Seções de fontes, matriz e disposição movidas de `SPECIFICATION.md` sem alterar conteúdo |
