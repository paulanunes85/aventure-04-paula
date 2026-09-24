# Modelo de Documento de Requisitos Funcionais (FRD)

Grave este modelo completo em `.spec/<NNN>-<funcionalidade>/frd.md` após a análise de lacunas. Todas as seções são obrigatórias; seções sem conteúdo ficam `NÃO APLICÁVEL: <motivo>`. A declaração EARS, o aceite e a verificação de cada requisito vivem apenas em [spec.md](./spec-templates.md#specification-specmd); o FRD referencia os IDs e acrescenta domínio, atores, justificativa, dependências e falha e recuperação. Mantenha o documento como `Rascunho` ou `Pronto para revisão` até um revisor responsável registrar a aprovação.

```markdown
---
title: "Documento de Requisitos Funcionais: <Projeto ou Funcionalidade>"
description: "Escopo funcional e comportamento observável, neutros quanto à implementação."
date: "<AAAA-MM-DD>"
version: "0.1.0"
status: "Rascunho"
project_context: "<greenfield|brownfield|modernização|migração|api|mobile|dados|saas|ferramenta-interna|cli|educacional|infraestrutura>"
companion_nfrd: "nfrd.md"
spec: "spec.md"
---

# Documento de Requisitos Funcionais: <Projeto ou Funcionalidade>

## 1. Controle do documento

| Campo | Valor |
| --- | --- |
| Responsável | <responsável> |
| Revisores | <papéis ou nomes> |
| Status | Rascunho |
| Fontes governantes | <SRC-IDs> |
| Última revisão | <AAAA-MM-DD ou não-revisado> |

## 2. Problema e resultados

### 2.1 Problema
<Problema observado e atores afetados.>

### 2.2 Resultados desejados
| ID | Resultado observável | Fonte |
| --- | --- | --- |
| OUT-001 | <resultado de negócio ou do usuário> | SRC-001 |

### 2.3 Sinais de sucesso
| Sinal | Medida | Meta ou bloqueio | Responsável pela evidência |
| --- | --- | --- | --- |
| <sinal> | <como é observado> | <meta aprovada ou BLOQUEADO> | <responsável> |

## 3. Escopo

### 3.1 Dentro do escopo
- <capacidade delimitada>

### 3.2 Fora do escopo
- <exclusão explícita e justificativa>

### 3.3 Premissas e bloqueios
| ID | Tipo | Declaração | Impacto se errada | Responsável | Estado |
| --- | --- | --- | --- | --- | --- |
| ASM-001 | premissa | <declaração> | <impacto> | <responsável> | aberta |
| BLK-001 | bloqueio | <decisão ausente> | <trabalho bloqueado> | <responsável> | aberto |

## 4. Atores e permissões

| Ator | Objetivo | Ações permitidas | Ações proibidas | Fonte |
| --- | --- | --- | --- | --- |
| <papel> | <objetivo> | <ações> | <limites> | SRC-001 |

## 5. Modelo de domínio e ciclo de vida

| Termo de domínio | Definição | Fonte |
| --- | --- | --- |
| <termo> | <definição sem ambiguidade> | SRC-001 |

<Adicione um diagrama de estados Mermaid quando uma entidade tiver ciclo de vida. Caso contrário, declare "Nenhuma entidade dependente de ciclo de vida identificada.">

## 6. Requisitos funcionais por domínio

A declaração EARS canônica, o aceite e a verificação de cada ID estão em [spec.md](spec.md). Não copie nem reescreva a declaração aqui.

### Domínio: <nome do domínio>

| ID | Título | Justificativa | Dependências | Falha e recuperação | Atores |
| --- | --- | --- | --- | --- | --- |
| REQ-001 | <título curto> | <por que o comportamento é necessário> | <IDs ou nenhuma> | <IDs de requisitos indesejados vinculados ou NÃO APLICÁVEL> | <papéis> |

<Repita por domínio. Não organize requisitos por tela de interface nem por camada de implementação.>

## 7. Interações externas

| Interação | Direção | Contrato ou evento | Comportamento em falha | IDs de requisitos |
| --- | --- | --- | --- | --- |
| <sistema> | entrada/saída | <contrato> | <resposta observável> | REQ-... |

## 8. Resumo dos requisitos

| ID | Domínio | Padrão | Prioridade | Fonte | Status |
| --- | --- | --- | --- | --- | --- |
| REQ-001 | <domínio> | <padrão> | P0 | SRC-001 | Proposto |

## 9. Disposição de IDs históricos

| ID histórico | Disposição | IDs substitutos | Decisão | Data |
| --- | --- | --- | --- | --- |
| <ID> | transferido/substituído/dividido/mesclado/aposentado | <IDs ou nenhum> | <decisão ou motivo desconhecido> | <data> |

## 10. Incrementos de entrega

| Incremento | Objetivo | IDs de requisitos | Dependências | Sinal de saída |
| --- | --- | --- | --- | --- |
| 1 | <resultado revisável> | REQ-... | <IDs ou nenhuma> | <sinal observável> |

## 11. Perguntas em aberto

| ID | Pergunta | Bloqueia | Responsável | Prazo |
| --- | --- | --- | --- | --- |
| Q-001 | <pergunta> | <requisito ou artefato> | <responsável> | <data ou A DEFINIR> |

## 12. Registro de revisão

| Revisor | Decisão | Data | Evidência ou comentários |
| --- | --- | --- | --- |
| <revisor> | pendente | <data> | <notas> |
```

## Verificações do modelo

- Todo ator é referenciado por pelo menos um requisito ou declarado explicitamente como informativo.
- Todo requisito P0 tem justificativa de impacto na entrega.
- Comportamento de erro e recuperação está explícito para cada ação principal.
- Requisitos permanecem neutros quanto à implementação e atômicos.
- As linhas do resumo correspondem exatamente aos registros normativos de `spec.md` (IDs, padrão, prioridade, fonte e status).
- Todo `REQ-NNN` ativo de `spec.md` aparece na seção 6 e no resumo, e nenhuma declaração EARS foi copiada.
- Toda seção está presente; seções sem conteúdo declaram `NÃO APLICÁVEL` com motivo.
- IDs removidos têm disposição registrada, mesmo que o motivo seja "desconhecido".
- O status de aprovação não vem preenchido.
