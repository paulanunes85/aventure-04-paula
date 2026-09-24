# Notação EARS

EARS (Easy Approach to Requirements Syntax) restringe requisitos em linguagem natural a uma ordem de cláusulas previsível. Use-a para requisitos normativos funcionais e não funcionais, para que o revisor identifique gatilho, sistema, resposta e alvo de verificação sem inferir comportamento oculto.

## Idioma

EARS foi definida em inglês com a palavra-chave `shall`. Em documentos em português, use as palavras-chave equivalentes abaixo e o verbo `deve` para a obrigação. Mantenha um único idioma por documento.

| Inglês | Português |
| --- | --- |
| `While` | `Enquanto` |
| `When` | `Quando` |
| `Where` | `Onde` (no sentido de "se a funcionalidade estiver presente") |
| `If ... then` | `Se ... então` |
| `shall` | `deve` |

## Sintaxe genérica

A ordem genérica das cláusulas é:

```text
Enquanto <pré-condição opcional>, quando <gatilho opcional>, o <nome do sistema> deve <resposta do sistema>.
```

Nesta skill, mantenha uma única resposta observável por requisito, embora as regras gerais do EARS permitam várias. Requisitos atômicos produzem rastreabilidade, análise de impacto e resultados de teste mais claros.

## Seis padrões

| Padrão | Modelo canônico | Use quando |
| --- | --- | --- |
| Ubíquo | `O <sistema> deve <resposta>.` | O comportamento ou restrição de qualidade está sempre ativo. |
| Orientado a evento | `Quando <gatilho>, o <sistema> deve <resposta>.` | Um evento discreto causa a resposta. |
| Orientado a estado | `Enquanto <estado>, o <sistema> deve <resposta>.` | O comportamento vale durante um estado. |
| Opcional | `Onde <funcionalidade ou configuração estiver presente>, o <sistema> deve <resposta>.` | O comportamento se aplica apenas a uma capacidade incluída. |
| Indesejado | `Se <condição indesejada>, então o <sistema> deve <mitigação>.` | O sistema precisa detectar, rejeitar, recuperar ou degradar com segurança. |
| Complexo | `Enquanto <estado>, quando <gatilho>, o <sistema> deve <resposta>.` | Uma pré-condição e um evento governam a resposta. |

Um requisito indesejado complexo pode combinar cláusulas:

```text
Enquanto <estado>, se <condição indesejada>, então o <sistema> deve <mitigação>.
```

Classifique como complexo apenas quando mais de uma palavra-chave EARS for necessária. Não adicione cláusulas só para parecer detalhado.

## Registro de requisito

```markdown
### REQ-<NNN>: <título curto>
origem: <SRC-NNN, caminho da evidência ou [GREENFIELD] justificativa>

- Padrão: <ubíquo|evento|estado|opcional|indesejado|complexo>
- Prioridade: <P0|P1|P2|P3>
- Status: <proposto|pronto-para-revisão|aprovado|implementado|verificado|aposentado>
- Justificativa: <por que o comportamento é necessário>

> <Declaração EARS canônica.>

**Sinais de aceite**
- AC-REQ-<NNN>-01: Dado <contexto>, Quando <ação>, Então <resultado observável>

**Verificação**
- <teste|inspeção|análise|demonstração|medição>: <evidência planejada>
```

Use `NFR-<NNN>` para requisitos não funcionais (ou o esquema do repositório). Um NFR continua sendo uma declaração EARS, mas seu sinal de aceite também define o envelope de medição.

## Regras de escrita

1. Nomeie um sistema ou componente concreto como sujeito. Evite pronomes como "ele".
2. Use `deve` na resposta normativa. Evite `deveria`, `pode`, `poderia`, `poderá` e futuros preditivos como `irá`.
3. Escreva uma resposta por requisito. Divida conjunções ocultas como "validar e notificar".
4. Torne a resposta observável externamente ou objetivamente inspecionável.
5. Mantenha escolhas de implementação fora dos requisitos funcionais.
6. Declare pré-condições e gatilhos explicitamente e na ordem canônica.
7. Defina termos de forma consistente. Ligue termos de domínio ambíguos a um glossário ou definição de dados.
8. Dê a todo requisito ID estável, fonte, justificativa, prioridade, sinal de aceite, método de verificação e status.
9. Use meta numérica apenas quando evidência ou um responsável a fornecer.
10. Registre comportamento de erro, timeout, entrada inválida, falha de dependência e recuperação com padrões indesejado ou complexo quando aplicável.

## Método de classificação

1. Se o comportamento está sempre ativo, use ubíquo.
2. Se um evento discreto inicia o comportamento, use orientado a evento.
3. Se o comportamento vale enquanto um estado é verdadeiro, use orientado a estado.
4. Se o comportamento existe apenas com uma funcionalidade ou configuração selecionada, use opcional.
5. Se a condição é indesejada e exige mitigação, use indesejado.
6. Se duas cláusulas necessárias governam o comportamento, use complexo.

Registre exatamente uma classificação por requisito, incluindo variantes complexas.

## Exemplos

- Ubíquo: `O serviço de auditoria deve registrar ator, ação, alvo, resultado e data/hora de cada operação privilegiada.`
- Orientado a evento: `Quando um usuário enviar credenciais válidas, o serviço de identidade deve criar uma sessão autenticada.`
- Orientado a estado: `Enquanto um pedido aguardar confirmação de pagamento, o serviço de pedidos deve impedir a criação de remessa.`
- Opcional: `Onde o login único estiver habilitado, o serviço de identidade deve redirecionar usuários não autenticados ao provedor de identidade configurado.`
- Indesejado: `Se um arquivo enviado exceder o limite de tamanho aprovado, então o serviço de upload deve rejeitar o arquivo e identificar o limite violado.`
- Complexo: `Enquanto uma conta estiver bloqueada, quando ocorrer uma tentativa de login, o serviço de identidade deve negar a autenticação sem validar a senha enviada.`

## Defeitos comuns

| Defeito | Exemplo ruim | Correção |
| --- | --- | --- |
| Qualidade vaga | "O sistema deve ser rápido." | Defina métrica com fonte e envelope de medição, ou mantenha um bloqueio explícito. |
| Resposta composta | "O sistema deve validar o pedido e enviar e-mail ao usuário." | Divida validação e notificação em requisitos separados. |
| Comportamento passivo | "A autenticação deve ser suportada." | Nomeie o sistema e a resposta de autenticação observável. |
| Condição oculta | "O sistema deve mostrar um erro." | Declare o evento ou a condição indesejada que causa o erro. |
| Vazamento de implementação | "O sistema deve guardar sessões no Redis." | Declare o comportamento de sessão exigido; mova uma restrição tecnológica com fonte para o NFRD. |
| Limiar sem dono | "A API deve responder em 500 ms." | Cite evidência de carga ou um SLO aprovado por um responsável. |
| Absoluto inverificável | "O sistema deve acertar sempre." | Defina o domínio de entradas válidas e o comportamento para entradas ambíguas ou fora do domínio. |
| Declaração sem rastreio | Frase correta sem ID nem fonte | Adicione os metadados do registro e o mapeamento de fonte. |

## Referências

- Alistair Mavin, [EARS overview and pattern definitions](https://alistairmavin.com/ears/), revisado em 2026-08-25.
- A. Mavin, P. Wilkinson, A. Harwood e M. Novak, "Easy Approach to Requirements Syntax (EARS)," *17th IEEE International Requirements Engineering Conference*, 2009, pp. 317-322, [doi:10.1109/RE.2009.9](https://doi.org/10.1109/RE.2009.9).
- University of Manchester Research Explorer, [registro bibliográfico de "Easy Approach to Requirements Syntax (EARS)"](https://research.manchester.ac.uk/en/publications/easy-approach-to-requirements-syntax-ears/), revisado em 2026-08-25.
