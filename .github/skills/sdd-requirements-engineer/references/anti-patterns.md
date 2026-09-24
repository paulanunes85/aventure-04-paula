# Antipadrões de SDD e EARS

Use este catálogo durante correção e validação. Corrija o defeito subjacente de requisito, evidência ou rastreabilidade, em vez de apenas polir o texto.

## Defeitos de requisitos

| Antipadrão | Por que falha | Ação corretiva |
| --- | --- | --- |
| História de usuário tratada como requisito | Intenção não é uma resposta normativa do sistema. | Preserve a história como contexto e derive um ou mais requisitos EARS. |
| `deveria`, `pode`, `irá` ou `tem que` vago | Obrigação ou momento ficam ambíguos. | Use o padrão EARS adequado com `deve`. |
| Resposta composta unida por "e" | Uma parte pode passar enquanto outra falha. | Divida em requisitos atômicos com IDs separados. |
| Sujeito pronominal como "ele" | O limite do sistema responsável fica obscuro. | Nomeie o sistema ou componente. |
| Gatilho ou estado oculto | Revisores precisam inferir quando o comportamento se aplica. | Adicione cláusulas `quando`, `enquanto`, `onde` ou `se...então`. |
| Tecnologia em requisito funcional | Comportamento e implementação ficam acoplados. | Mova uma escolha obrigatória com fonte para as restrições do NFRD; caso contrário, adie para o design. |
| Qualidade vaga | "Rápido", "seguro", "bonito" e "disponível" não são verificáveis. | Adicione envelope de medição com evidência ou um bloqueio. |
| Absoluto impossível | "Acertar sempre" ignora entradas ambíguas ou fora do domínio. | Defina o domínio válido e o comportamento para entradas ambíguas ou inválidas. |
| Meta numérica inventada | O documento cria política de negócio ou operação sem suporte. | Cite carga medida ou aprovação de um responsável. |
| Comportamento indesejado ausente | O caminho feliz esconde obrigações de erro, timeout e recuperação. | Adicione requisitos EARS indesejados ou complexos. |
| IDs instáveis ou duplicados | Rastreabilidade e histórico de mudanças quebram. | Preserve IDs e registre disposições de divisão, mescla, substituição ou aposentadoria. |
| ID removido sem motivo | Não é possível saber se o comportamento saiu do escopo ou foi esquecido. | Registre a disposição, mesmo com motivo "desconhecido", e crie uma pergunta em aberto. |

## Defeitos de artefatos e fluxo

| Antipadrão | Por que falha | Ação corretiva |
| --- | --- | --- |
| Status `Aprovado` pré-preenchido | O artefato declara uma revisão que não ocorreu. | Comece como `Rascunho` ou `Pronto para revisão`; vincule a evidência de aprovação depois. |
| Design-first sem requisitos recuperados | Escolhas de arquitetura viram a fonte de verdade sem revisão. | Derive e revise requisitos antes do handoff. |
| Constituição local conflita com a governança do repositório | Duas autoridades podem impor regras incompatíveis. | Reutilize a constituição do repositório ou registre uma emenda explícita. |
| Texto completo do requisito copiado em todos os artefatos | Cópias divergem e criam várias fontes normativas. | Mantenha a declaração canônica em `SPECIFICATION.md` e referencie por ID estável nos demais arquivos do pacote. |
| Só o primeiro pacote criado | Funcionalidades inteiras da fonte somem sem disposição. | Crie um pacote por funcionalidade e atribua cada ID da fonte a um pacote no índice. |
| Arquivo ou pasta da estrutura ausente | Revisores e o validador não distinguem etapa pendente de esquecimento. | Crie a estrutura inteira; arquivos de etapas futuras ficam `Não iniciado`. |
| Seção do modelo omitida | O revisor não distingue "não se aplica" de "esquecido". | Mantenha a seção com `NÃO APLICÁVEL: <motivo>`, `PENDENTE` ou `BLOQUEADO`. |
| Seção preenchida para parecer completa | Completude vira ficção e esconde lacunas reais. | Use apenas conteúdo com fonte; o resto fica `NÃO APLICÁVEL` ou bloqueio visível. |
| Especificação fora de `.spec/` | Hooks, prompts e revisores não encontram o pacote. | Mova o pacote para `.spec/<NNN>-<funcionalidade>/`. |
| Requisito sem design, tarefa ou verificação | A especificação não consegue guiar implementação nem evidência. | Adicione mapeamentos ou remova o item do escopo ativo. |
| Tarefa sem requisito | Trabalho entra no escopo sem necessidade aprovada. | Rastreie-a a um requisito ou classifique-a como governança/habilitação com evidência. |
| `[P]` baseado apenas no texto da tarefa | Trabalho paralelo ainda pode conflitar em dependências ou arquivos. | Verifique independência de dependências e de superfície de mudança. |
| Diagrama Mermaid com limites sem rótulo | Revisores não conseguem avaliar responsabilidade ou confiança. | Rotule atores, componentes, armazenamentos de dados, sistemas externos e limites de confiança. |
| NFR repetido entre contextos sem envelope de medição | Uma meta pode significar coisas diferentes em cada ambiente. | Defina carga, ambiente, agregação, janela e instrumentação. |
| Status forte sem evidência | "Implementado" ou "Verificado" vira ficção com cara de sucesso. | Vincule evidência do repositório ou de execução e mantenha um status mais fraco caso contrário. |
| Regra arbitrária de quantidade de P0 | Limites mecânicos escondem risco de entrega ou forçam classificação errada. | Justifique cada P0 e divida o incremento quando o conjunto não for revisável. |
| Link relativo quebrado ou referência a recurso inexistente | A skill ou o agente não consegue carregar a própria orientação. | Use caminhos relativos ao arquivo atual e valide que o destino existe. |

## Perguntas de revisão

1. Existe exatamente uma declaração normativa canônica por ID de requisito ativo?
2. Um revisor consegue encontrar a fonte primária e o responsável de cada requisito?
3. Um testador consegue derivar uma verificação de aprovação/reprovação sem inventar comportamento ausente?
4. Todo artefato derivado preserva escopo e significado?
5. Os bloqueios estão visíveis onde, de outra forma, apareceriam premissas sem suporte?
