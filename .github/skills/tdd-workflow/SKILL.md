---
name: "tdd-workflow"
description: "Use ao praticar desenvolvimento orientado a testes, escrever primeiro um teste que falha ou guiar o ciclo red-green-refactor em qualquer linguagem. Gatilhos: TDD, test first, red-green-refactor, teste falhando, escrever um teste, regressão."
---
# Fluxo de TDD

## Quando invocar

- "Vamos implementar esta regra com TDD."
- "Escreva primeiro o teste que falha para este bug."
- "Qual deve ser o próximo teste deste ciclo?"
- "As mudanças continuam quebrando coisas; preciso de uma rede de segurança."

## O ciclo

```text
RED      -> escreva o menor teste que falha e expressa o próximo comportamento
GREEN    -> escreva o mínimo de código que faz o teste passar
REFACTOR -> melhore o design mantendo os testes verdes
```

Faça commit a cada passo verde. Cubra um comportamento por ciclo.

## Regras

1. **Não escreva código de produção sem um teste falhando.** Sem teste, sem mudança.
2. **Mantenha apenas um teste falhando por vez.** Nunca tenha dois testes vermelhos.
3. **Dê o menor passo que falha.** Se o primeiro teste é difícil de escrever, o design está sinalizando um problema.
4. **Nomes de teste descrevem comportamento**, não implementação: `should_apply_discount_when_coupon_is_valid`, não `test_method1`.
5. Use a estrutura **Dado-Quando-Então / Arrange-Act-Assert** no corpo do teste.
6. **Confirme o vermelho pelo motivo certo.** O teste deve falhar pela ausência do comportamento, não por erro de sintaxe, import ou configuração.
7. **A fase de refatoração não é opcional.** É nela que está a maior parte do valor.

## Como escolher o próximo teste

Ordene os testes para guiar o design:

- Comece pelo caso não trivial mais simples (o caso "0->1" ou o caminho feliz com uma entrada).
- Depois adicione uma única variação (um limite, um branch ou um erro).
- Transforme tabelas de exemplos do negócio em testes parametrizados, um exemplo por vez.
- Evite escrever um teste enorme que cubra tudo.

## Dublês de teste

- Use um dublê apenas quando o colaborador real for lento, não determinístico ou ainda não existir.
- Não faça mock de tipos que você não controla. Envolva-os em uma abstração fina primeiro.
- Um teste que faz mock de tudo não testa nada.

## Quando o TDD está difícil, o problema costuma estar no design

- Dificuldade de construir o objeto sob teste: colaboradores demais, violação do princípio de responsabilidade única.
- Impossível fazer uma asserção sem ler três outros objetos: problema de Lei de Demeter ou encapsulamento.
- Precisar de mock do mundo inteiro: acoplamento oculto; introduza uma abstração.

## Antipadrões

- Escrever o código e depois o teste (isso é verificação, não TDD).
- Pular a fase de refatoração.
- Testes que duplicam a implementação (detectores de mudança).
- Fixtures enormes compartilhadas entre arquivos, porque são frágeis.
- Verificar detalhes de implementação (métodos privados ou strings SQL exatas).

## Modelo de saída

Adapte a sintaxe ao framework de testes do projeto. Exemplo em TypeScript:

```ts
// REQ-NNN: <comportamento sob teste>
it('should_return_zero_tax_when_customer_is_tax_exempt', () => {
  // Arrange
  const customer = createCustomer({ status: 'TAX_EXEMPT' });
  // Act
  const tax = calculator.taxFor(customer);
  // Assert
  expect(tax).toBe(0);
});
```

Sequência de commits por comportamento: `test: add failing test for REQ-NNN` -> `feat: make REQ-NNN pass` -> `refactor: <melhoria>`.

## Gate de qualidade

- [ ] Nenhum código de produção foi escrito sem um teste falhando antes.
- [ ] O vermelho foi confirmado pelo motivo certo.
- [ ] Apenas um teste está vermelho por vez, e cada ciclo cobre um comportamento.
- [ ] A refatoração foi feita com os testes verdes.
- [ ] Os nomes dos testes descrevem comportamento e referenciam o REQ-ID em comentário.

## Referências

- [Kent Beck - Test Driven Development: By Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
- [GOOS - Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/)
- [Martin Fowler - Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
