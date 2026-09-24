---
name: "user-story-refine"
description: "Use ao refinar itens de backlog, dividir épicos, escrever histórias de usuário com critérios de aceite ou validar critérios INVEST. Gatilhos: refinar história, dividir épico, user story, critérios de aceite, INVEST, backlog."
---
# Refinamento de histórias de usuário

## Quando invocar

- "Esta história está grande demais. Me ajude a dividi-la."
- "Transforme esta descrição de funcionalidade em histórias com critérios de aceite."
- "Verifique se estas histórias atendem ao INVEST."

## Entradas necessárias

- Descrição da funcionalidade ou épico
- Persona ou tipo de usuário
- Objetivo de negócio atendido pela funcionalidade
- Restrições conhecidas (regulatórias, técnicas ou de UX)

Se alguma entrada faltar, registre-a como pergunta em aberto em vez de supor.

## Passos de refinamento

1. **Confirme o resultado.** Cada história deve responder: qual persona, qual resultado e por que importa.
2. **Aplique o INVEST** (independente, negociável, valiosa, estimável, pequena e testável) a cada rascunho.
3. **Divida verticalmente**, nunca horizontalmente. Prefira dividir por etapa do fluxo, variação de dados, operação CRUD, caminho feliz versus borda, regra de negócio ou critério de aceite.
4. **Escreva critérios de aceite em Dado/Quando/Então.** Inclua um caminho feliz, um caso de borda e um caminho de erro.
5. **Rastreie a um requisito.** Toda história deve apontar para pelo menos um ID de requisito (`REQ-NNN` ou o esquema do projeto).

## Padrões de divisão

Use estes padrões quando uma história for grande demais para uma iteração:

| Padrão | Divida por... | Exemplo |
| --- | --- | --- |
| Etapas do fluxo | Cada etapa de um fluxo com vários passos | Enviar versus revisar versus aprovar |
| Regra de negócio | Uma regra por história | Taxa padrão versus taxa de isenção |
| Variação de dados | Cada tipo ou formato de entrada | Endereço nacional versus internacional |
| Operação CRUD | Criar, ler, atualizar e excluir separadamente | Registrar antes de editar |
| Caminho feliz versus borda | Caminho feliz primeiro, depois as bordas | Entrada válida antes de entrada rejeitada |
| Interface | Mesmo núcleo, canais diferentes | CLI antes de web |
| Spike | Separar a incerteza em pesquisa com prazo | Prototipar a integração primeiro |

## Antipadrões

- Histórias escritas como tarefas ("Adicionar um botão").
- Critérios de aceite que descrevem a interface em vez do comportamento.
- Divisões horizontais ("história de backend" + "história de UI" para a mesma funcionalidade).
- Termos vagos sem critério verificável ("bonito", "rápido", "intuitivo").
- Falta de vínculo com um ID de requisito.

## Modelo de saída

```markdown
### US-NNN: <título curto>
**Como** <persona>
**Eu quero** <capacidade>
**Para que** <resultado de negócio>

**Critérios de aceite**
- Dado <contexto>, Quando <ação>, Então <resultado>
- Dado <caso de borda>, Quando <ação>, Então <resultado>
- Dado <condição de erro>, Quando <ação>, Então <resultado>

**Rastreia para**: REQ-001, REQ-042
**Esforço**: P / M / G
**Dependências**: US-NNN (se houver)
**Perguntas em aberto**: <lista ou nenhuma>
```

## Gate de qualidade

- [ ] A história atende a todos os critérios INVEST.
- [ ] Os critérios de aceite usam Dado/Quando/Então e cobrem caminho feliz, caso de borda e caminho de erro.
- [ ] A história está dividida verticalmente, não por camada de arquitetura.
- [ ] A história rastreia para pelo menos um ID de requisito, e cada requisito vinculado tem linha `origem:` (ver [sdd-artifacts.instructions.md](../../instructions/sdd-artifacts.instructions.md)).
- [ ] Entradas ausentes estão registradas como perguntas em aberto.
