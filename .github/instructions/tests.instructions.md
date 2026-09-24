---
description: "Use ao criar ou revisar testes automatizados, estratégia de testes, lacunas de cobertura, testes de regressão e quality gates em qualquer stack."
applyTo: "**/*.test.*,**/*.spec.*,**/test_*.py,**/*_test.*,**/*Test.java,**/*Tests.cs,**/tests/**,**/test/**,**/__tests__/**"
---

# Convenções de testes - estrutura, rastreabilidade e cobertura

Este arquivo é ativado para qualquer arquivo de teste, em backend ou frontend. Ele ensina estrutura e nomenclatura de testes, escolha de ferramentas por stack, rastreabilidade por REQ-ID e metas de cobertura. Testes são escritos **durante** a implementação, nunca depois.

A stack de testes efetiva (framework, comandos e limites de cobertura) é a declarada em [copilot-instructions.md](../copilot-instructions.md) ou na constituição do projeto. As tabelas abaixo são referência quando o projeto ainda não definiu.

## Pirâmide de testes

| Camada | O que prova | Proporção |
| --- | --- | --- |
| Unitário (lógica pura, serviços) | Regras de negócio sem I/O | A maioria |
| Integração (repositórios, APIs, componentes) | Comportamento com dependências reais ou renderização | Menos |
| Ponta a ponta | Fluxo crítico do usuário | Poucos |

## Ferramentas de referência por stack

| Stack | Unitário | Integração | E2E |
| --- | --- | --- | --- |
| JavaScript/TypeScript (Node) | `node:test`, Vitest ou Jest | Supertest, Testcontainers | Playwright |
| Frontend (React/Vue) | Vitest + Testing Library | Testing Library + MSW | Playwright |
| Java | JUnit 5 + AssertJ | Testcontainers | Playwright |
| Python | pytest | pytest + Testcontainers | Playwright |
| .NET | xUnit ou NUnit | Testcontainers | Playwright |

Adote apenas as ferramentas que o projeto já usa ou que foram aprovadas em ADR.

## Estrutura: Arrange-Act-Assert

Cada teste tem três fases visíveis e verifica um comportamento. Faça mock apenas de fronteiras externas (rede, relógio, serviços de terceiros), nunca da classe ou função sob teste.

```ts
import { describe, it, expect } from 'vitest';
import { calculateTotal } from './cart';

describe('calculateTotal', () => {
  it('should_apply_discount_when_coupon_is_valid', () => { // REQ-002
    const items = [{ price: 100 }, { price: 50 }];            // Arrange
    const total = calculateTotal(items, { coupon: 'OFF10' }); // Act
    expect(total).toBe(135);                                  // Assert
  });
});
```

## Nomenclatura

Nomeie testes como `should_<comportamento esperado>_when_<condição>` ou use a mesma intenção em linguagem natural no `it(...)`/`@DisplayName`. Mantenha o idioma consistente dentro do projeto.

```text
should_return_409_when_identifier_already_exists
should_render_empty_state_when_no_items
deve_rejeitar_sequencia_quando_tem_menos_de_tres_numeros
```

## Dependências reais versus dublês

- Quando o comportamento de dados importa (consultas, transações, restrições), use a dependência real em contêiner (Testcontainers ou equivalente) em vez de um substituto em memória com semântica diferente.
- Use dublês apenas para colaboradores lentos, não determinísticos ou inexistentes.
- Não faça mock de tipos que você não controla; envolva-os em uma abstração fina primeiro.

## Frontend

Consulte elementos por papel acessível ou rótulo, nunca por `data-testid` quando existir um papel. Dirija a interação com `user-event`. Evite testes apenas de snapshot.

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ArchiveButton } from './ArchiveButton';

describe('ArchiveButton', () => {
  it('should call onArchive when clicked', async () => { // REQ-032
    const onArchive = vi.fn().mockResolvedValue(undefined);
    render(<ArchiveButton id="1" onArchive={onArchive} />);
    await userEvent.click(screen.getByRole('button', { name: /arquivar/i }));
    expect(onArchive).toHaveBeenCalledWith('1');
  });
});
```

## Rastreabilidade por REQ-ID

Todo teste que verifica um requisito cita o ID em comentário na mesma linha ou logo acima (`// REQ-NNN`, `# REQ-NNN`). Isso alimenta a verificação de rastreabilidade descrita em [sdd-artifacts.instructions.md](sdd-artifacts.instructions.md), que lista requisitos ainda não referenciados por testes.

## Metas de cobertura

Use os limites definidos pelo projeto. Se não houver, proponha limites e registre-os como decisão do time (ponto de partida comum: 80% de linhas e 70% de branches, com meta maior para regras de negócio). Configure os limites na ferramenta de cobertura para que o comando de teste falhe abaixo do mínimo.

> [!NOTE]
> Cobertura é piso, não objetivo. Um branch sem asserção não foi testado, mesmo que a linha conste como "coberta". Verifique comportamento, não apenas a chamada.

## Convenções

| Regra | Motivo |
| --- | --- |
| Arrange-Act-Assert, um comportamento por teste | Legível e isola a falha |
| Mock apenas de fronteiras externas | Dependências reais capturam bugs reais |
| Nomes `should_<comportamento>_when_<condição>` | Intenção clara no relatório |
| Comentário `REQ-NNN` em testes de requisito | Mantém a rastreabilidade spec-teste ativa |
| Escritos durante a implementação | Código sem teste não é integrado |

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Usar a dependência real em contêiner quando dados importam | Substituir o banco por um equivalente em memória com semântica diferente |
| Consultar por papel/rótulo | Consultar por `data-testid` quando existe um papel |
| Verificar comportamento e branches de borda | Depender apenas de snapshots ou cobertura de linhas |
| Escrever o teste junto com o código | Adicionar testes depois que a funcionalidade está "pronta" |
| Pular ou enfraquecer teste somente com issue e justificativa | Pular testes para forçar pipeline verde |

## Checklist de PR

- [ ] Comportamento novo tem testes unitários; persistência tem teste de integração com dependência real quando aplicável
- [ ] Testes seguem Arrange-Act-Assert e a convenção de nomes do projeto
- [ ] Testes orientados a requisito têm comentário `REQ-NNN`
- [ ] Regras de negócio cobrem caminho feliz, falha de validação e, quando houver, falha de autorização
- [ ] Cobertura atende ao mínimo definido pelo projeto
- [ ] Nenhuma fronteira externa ficou sem mock e nenhuma dependência real necessária foi substituída por mock
