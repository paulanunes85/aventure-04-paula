# Modelo de Documento de Requisitos Não Funcionais (NFRD)

Use este modelo para restrições de qualidade mensuráveis. Declarações normativas seguem a [notação EARS](./ears-notation.md). Nunca preencha uma meta com um padrão "de mercado" quando evidência de carga, política ou um responsável não a forneceu.

```markdown
---
title: "Documento de Requisitos Não Funcionais: <Projeto ou Funcionalidade>"
description: "Restrições de qualidade mensuráveis e envelopes de verificação."
date: "<AAAA-MM-DD>"
version: "0.1.0"
status: "Rascunho"
companion_frd: "<caminho relativo ou não-criado>"
---

# Documento de Requisitos Não Funcionais: <Projeto ou Funcionalidade>

## 1. Controle do documento

| Campo | Valor |
| --- | --- |
| Responsável | <responsável> |
| Revisores | <papéis ou nomes> |
| Status | Rascunho |
| Fontes governantes | <SRC-IDs> |
| Última revisão | <AAAA-MM-DD ou não-revisado> |

## 2. Aplicabilidade

| Categoria | Aplica | Justificativa | Responsável |
| --- | --- | --- | --- |
| Desempenho e capacidade | sim/não/desconhecido | <motivo> | <responsável> |
| Segurança e identidade | sim/não/desconhecido | <motivo> | <responsável> |
| Confiabilidade e recuperação | sim/não/desconhecido | <motivo> | <responsável> |
| Privacidade e conformidade (por exemplo, LGPD) | sim/não/desconhecido | <motivo> | <responsável> |
| Observabilidade e suporte | sim/não/desconhecido | <motivo> | <responsável> |
| Acessibilidade e localização | sim/não/desconhecido | <motivo> | <responsável> |
| Testabilidade e manutenibilidade | sim/não/desconhecido | <motivo> | <responsável> |
| Entrega e operabilidade | sim/não/desconhecido | <motivo> | <responsável> |
| Qualidade, retenção e migração de dados | sim/não/desconhecido | <motivo> | <responsável> |
| Custo e eficiência de recursos | sim/não/desconhecido | <motivo> | <responsável> |

## 3. Contextos de implantação e medição

| Contexto | Carga e formato dos dados | Região ou topologia | Dependências | Ferramenta de medição | Responsável |
| --- | --- | --- | --- | --- | --- |
| <contexto> | <usuários, taxa, payload, volume> | <escopo> | <serviços> | <ferramenta ou BLOQUEADO> | <responsável> |

## 4. Requisitos de qualidade

### NFR-001: <Título curto>
origem: <SRC-### ou [GREENFIELD] justificativa>

- Categoria: <categoria>
- Padrão: <padrão EARS>
- Prioridade: <P0|P1|P2|P3>
- Status: Proposto
- Justificativa: <por que a restrição é necessária>
- Aplica-se a: <contextos>
- Responsável: <responsável>

> <Declaração EARS canônica com restrição mensurável aprovada, ou declaração cuja meta não resolvida está explicitamente bloqueada.>

**Envelope de medição**

| Campo | Valor |
| --- | --- |
| Métrica | <métrica> |
| Meta | <meta aprovada ou BLOQUEADO> |
| Agregação | <p95, máximo, taxa, contagem, percentual ou outra> |
| Janela de observação | <duração ou BLOQUEADO> |
| Carga | <carga e formato dos dados ou BLOQUEADO> |
| Ambiente | <contexto ou BLOQUEADO> |
| Instrumentação | <fonte da evidência ou BLOQUEADO> |

**Sinais de aceite**
- AC-NFR-001-01: <resultado observável de aprovação/reprovação sob o envelope de medição>

**Verificação**
- <teste|inspeção|análise|demonstração|medição>: <evidência planejada>

<Repita para toda categoria de qualidade aplicável.>

## 5. Decisões de segurança e conformidade

| Decisão | IDs de requisitos | Fonte ou política | Responsável | Estado |
| --- | --- | --- | --- | --- |
| Método de autenticação (ou ausência justificada) | NFR-... | SRC-... | <responsável> | decidido/bloqueado |
| Modelo de autorização | NFR-... | SRC-... | <responsável> | decidido/bloqueado |
| Classificação e proteção de dados | NFR-... | SRC-... | <responsável> | decidido/bloqueado |
| Aplicabilidade de conformidade | NFR-... | SRC-... | <responsável> | aplicável/não-aplicável/bloqueado |

## 6. Restrições tecnológicas

| Restrição | Justificativa | Fonte | IDs de requisitos | Gatilho de revisão |
| --- | --- | --- | --- | --- |
| <restrição de tecnologia ou plataforma> | <por que é obrigatória> | SRC-... | NFR-... | <condição> |

<Se nenhuma tecnologia for obrigatória, declare "Nenhuma restrição tecnológica aprovada." Não promova preferências a requisitos.>

## 7. Resumo dos requisitos

| ID | Categoria | Prioridade | Contextos | Estado da meta | Fonte | Status |
| --- | --- | --- | --- | --- | --- | --- |
| NFR-001 | <categoria> | P0 | <contextos> | definida/bloqueada | SRC-001 | Proposto |

## 8. Bloqueios e perguntas em aberto

| ID | Fato ou decisão ausente | IDs afetados | Responsável | Evidência de resolução |
| --- | --- | --- | --- | --- |
| BLK-001 | <meta ou política desconhecida> | NFR-... | <responsável> | <evidência esperada> |

## 9. Registro de revisão

| Revisor | Decisão | Data | Evidência ou comentários |
| --- | --- | --- | --- |
| <revisor> | pendente | <data> | <notas> |
```

## Verificações do modelo

- Toda categoria aplicável tem pelo menos um requisito ou uma justificativa explícita para não ter.
- Toda meta numérica tem fonte, responsável, carga, ambiente e método de observação.
- Todo contexto de implantação é coberto por requisitos mensuráveis ou por um bloqueio visível.
- Segurança identifica autenticação, autorização, proteção e comportamento em falha quando aplicável.
- Conformidade é explicitamente aplicável, não aplicável ou bloqueada; nunca é suposta em silêncio.
- Restrições tecnológicas têm evidência e gatilho de revisão.
- Termos vagos ("rápido", "seguro", "pronto para produção", "intuitivo") foram convertidos em envelopes de medição ou bloqueios.
- O status de aprovação não vem preenchido.
