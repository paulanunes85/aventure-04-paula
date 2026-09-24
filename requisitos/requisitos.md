# Documento de Requisitos: Echo Chamber

| Campo | Valor |
|---|---|
| Projeto | Echo Chamber (nome provisório, marketing ainda vai validar) |
| Área solicitante | Coordenação Pedagógica / Clube de Matemática |
| Responsável pelo documento | Renata (Coordenação) |
| Versão | 0.4 (rascunho) |
| Status | Em revisão |
| Data da última atualização | ver histórico |
| Aprovadores | A definir |
| Prazo | "O quanto antes", ideal para o início do semestre |

---

## 1. Contexto

Queremos uma aplicação para ajudar os alunos a aprender sequências numéricas de um jeito lúdico. A ideia é que o aluno "sussurre" uma sequência de números na Sala do Eco e a sala devolva o próximo número, como se fosse um eco mágico.

A diretoria gostou muito da ideia e quer algo moderno, bonito e gamificado. O sistema tem que ser inteligente e entender as sequências sozinho.

Hoje os professores fazem isso em planilha e no quadro, o que toma muito tempo das aulas.

## 2. Objetivo

- Tornar o aprendizado de sequências mais divertido.
- Reduzir o tempo que os professores gastam corrigindo exercícios.
- Ter um produto que possa ser mostrado para outras escolas no futuro.

## 3. Escopo

**Fase 1:** versão no terminal (console), chamada de Sala do Eco.

**Fase 2:** versão web com o tema Castelo do Eco, com gráficos, histórico e site de documentação.

> Observação: a diretoria pediu para ver a versão web já na primeira apresentação. Confirmar se a Fase 2 entra junto com a Fase 1.

**Fora do escopo:** A definir.

## 4. Usuários

- Alunos
- Professores
- Administrador (?)
- Coordenação

## 5. Requisitos Funcionais

| ID | Descrição | Prioridade | Origem | Status |
|---|---|---|---|---|
| RF-01 | O sistema deve prever o próximo número de uma sequência informada pelo usuário. | Alta | Reunião 1 | Aprovado |
| RF-02 | O sistema deve reconhecer progressões aritméticas. Exemplo: [3, 6, 9, 12] deve retornar 15. | Alta | Reunião 1 | Aprovado |
| RF-03 | O sistema deve reconhecer progressões geométricas e sequências polinomiais, entre outras. | Alta | Diretoria | Aprovado |
| RF-04 | Quando a sequência for inválida, o sistema deve avisar o usuário de forma clara. | Alta | Reunião 1 | Aprovado |
| RF-05 | O sistema deve guardar as "memórias" dos ecos anteriores. | Alta | Reunião 1 | Aprovado |
| RF-06 | O usuário deve poder testar várias sequências. | Média | Reunião 1 | Aprovado |
| RF-08 | O sistema deve contar a história da Sala do Eco de forma amigável. | Média | Marketing | Em análise |
| RF-09 | O sistema deve ter uma interface web bonita com o tema Castelo do Eco, parecida com a do app que a diretoria viu na feira. | Alta | Diretoria | Aprovado |
| RF-10 | O sistema deve mostrar gráficos das sequências. | Alta | Diretoria | Aprovado |
| RF-11 | O sistema deve analisar o histórico das sequências ao longo do tempo e gerar insights. | Alta | Diretoria | Em análise |
| RF-12 | O sistema deve explicar como chegou na resposta. | Média | Professores | Em análise |
| RF-13 | A sequência deve ter no mínimo 3 números. | Alta | TI | Aprovado |
| RF-14 | O aluno pode digitar a sequência do jeito que achar melhor. | Média | Professores | Aprovado |
| RF-15 | O sistema deve tratar os casos de borda. | Alta | TI | Aprovado |
| RF-16 | O sistema deve permitir prever mais de um número quando necessário. | Baixa | Professores | Em análise |
| RF-17 | O administrador pode apagar as memórias. | Média | TI | Aprovado |
| RF-18 | O professor deve conseguir ver o que os alunos digitaram. | Alta | Professores | Aprovado |
| RF-19 | O sistema deve guardar o histórico dos ecos. | Alta | Coordenação | Aprovado |
| RF-20 | O sistema deve ter um site de documentação explicando os conceitos matemáticos. | Média | Coordenação | Aprovado |
| RF-21 | O sistema deve ser rápido. | Alta | Diretoria | Aprovado |

> RF-07 foi removido na reunião 2 (ninguém lembra o motivo).

## 6. Requisitos Não Funcionais

| ID | Descrição | Prioridade | Status |
|---|---|---|---|
| RNF-01 | Deve ser feito em JavaScript com Node.js, que é o padrão já aprovado pela TI. O arquivo principal deve se chamar `index.js`. | Alta | Aprovado |
| RNF-02 | Deve processar sequências grandes de forma eficiente. | Alta | Aprovado |
| RNF-03 | Deve estar pronto para produção. | Alta | Aprovado |
| RNF-04 | Deve ter tratamento de erros adequado e logs. | Alta | Aprovado |
| RNF-05 | Deve ter uma boa experiência do usuário e ser intuitivo. | Alta | Aprovado |
| RNF-06 | O código deve ter comentários e documentação adequada. | Média | Aprovado |
| RNF-07 | Deve ter testes abrangentes, incluindo casos de borda. | Alta | Aprovado |
| RNF-08 | A resposta deve parecer instantânea para o aluno. | Alta | Aprovado |
| RNF-09 | A interface deve ser em português. | Alta | Aprovado |
| RNF-10 | Deve funcionar no celular. | Média | Em análise |
| RNF-11 | As memórias nunca podem ser perdidas. | Alta | Aprovado |
| RNF-12 | Deve ser acessível. | Média | Em análise |
| RNF-13 | Deve ser seguro. | Alta | Aprovado |
| RNF-14 | O sistema deve permitir exportar o histórico para Excel. | Baixa | Em análise |

## 7. Regras de Negócio

- RN-01: O próximo número sempre segue o padrão identificado.
- RN-02: Se a sequência não seguir nenhum padrão, o sistema deve informar.
- RN-03: A definir com os professores de matemática.

## 8. Exemplos Fornecidos pelos Professores

| Sequência | Resultado esperado | Observação |
|---|---|---|
| 3, 6, 9, 12 | 15 | Exemplo oficial |
| 1, 4, 9, 16 | 25 | |
| 2, 4, 8 | 16 | |
| 2, 4 | 6 | Caso simples, tem que funcionar |
| 1, 1, 2, 3, 5 | 8 | Os alunos adoram Fibonacci |
| 5 | Erro | |
| 1,5; 3; 4,5 | 6 | Alguns alunos usam vírgula como decimal |
| 10, 20, 30, abc | ? | Ver com TI |

## 9. Premissas

- Os alunos já sabem o que é uma progressão.
- Não vamos precisar de servidor por enquanto.
- Não precisa de login.

## 10. Dúvidas em Aberto

- Quem vai ser o administrador?
- Vai ter versão em inglês? Uma escola parceira é do Chile.
- Quanto é uma "sequência grande"? Na reunião falaram em milhares, talvez milhões no futuro.
- Precisa aceitar números decimais? (seria legal)
- Os gráficos são por sequência ou do histórico todo?

## 11. Anexo: Trechos da Reunião de Alinhamento (transcrição)

> **Diretor:** "O castelo é a versão web e a sala é o console, certo? Ou é tudo a mesma coisa?"
>
> **TI:** "Se for web, alguém vai ter que hospedar. A gente não tem servidor ainda."
>
> **Professora Carla:** "O mais importante para mim é ver o que cada aluno digitou e onde errou."
>
> **Renata:** "Mas combinamos que não teria login, né?"
>
> **Diretor:** "Não quero nada complicado. Tem que ficar pronto rápido e tem que impressionar."
>
> **Professor Marcos:** "Se o aluno digitar 2, 4, 8, o sistema pode dizer 16 ou 14, depende de como você olha. Isso vai gerar discussão em sala."
>
> **Diretor:** "O sistema tem que acertar sempre."

## 12. Histórico de Versões

| Versão | Autor | Alteração |
|---|---|---|
| 0.1 | Renata | Primeira versão, após reunião 1 |
| 0.2 | TI | Inclusão de requisitos técnicos |
| 0.3 | Renata | Ajustes pós reunião 2 (removido RF-07) |
| 0.4 | Renata | Inclusão dos pedidos da diretoria e dos exemplos dos professores |