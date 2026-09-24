---
description: "Use ao criar, revisar ou depurar uma Agent Skill do GitHub Copilot em .github/skills/: frontmatter do SKILL.md, correspondência entre name e diretório, ajuste da description para carregamento automático, divulgação progressiva e recursos empacotados."
applyTo: ".github/skills/**/SKILL.md"
---

# Agent Skills - guia de autoria

Este arquivo é ativado ao criar ou editar um `SKILL.md` em `.github/skills/`. Ele ensina como criar uma skill carregada de forma confiável e com escopo claro: frontmatter válido, igualdade entre `name` e diretório, uso da `description` para carregamento automático, divulgação progressiva e empacotamento de scripts e referências. Ele ensina a estruturar e empacotar uma skill, mas não decide quais skills o projeto precisa nem qual procedimento de domínio cada uma deve conter.

## O que é uma skill

Uma skill é uma pasta autocontida com um `SKILL.md` e recursos opcionais (scripts, referências, templates e assets) que ensina ao Copilot uma capacidade especializada e repetível. Agent Skills é um [padrão aberto](https://agentskills.io/specification) suportado pelo GitHub Copilot no VS Code, no Copilot CLI e no Copilot cloud agent.

| Primitiva | Propósito | Carregamento |
| --- | --- | --- |
| Instruções (`*.instructions.md`) | Regras permanentes para arquivos que casam com `applyTo` | Sempre que um arquivo correspondente está em contexto |
| Skill (`SKILL.md`) | Fluxo ou capacidade sob demanda | Somente quando o pedido casa com a `description` ou via `/nome-da-skill` |
| Agente (`*.agent.md`) | Papel com instruções e ferramentas próprias | Quando selecionado no seletor de agentes ou chamado como subagente |

## Onde as skills ficam

| Local | Escopo |
| --- | --- |
| `.github/skills/<nome-da-skill>/` | Este repositório (também são aceitos `.claude/skills/` e `.agents/skills/`) |
| `~/.copilot/skills/<nome-da-skill>/` | Pessoal; todos os seus repositórios |

Cada skill tem seu próprio diretório e pelo menos um `SKILL.md`. Este arquivo governa `.github/skills/**/SKILL.md`.

## Frontmatter

`name` e `description` são obrigatórios. Use campos opcionais somente quando houver necessidade real.

```yaml
---
name: "gerador-de-diagramas"
description: "Use ao criar, editar ou gerar diagramas draw.io (.drawio, .drawio.svg), fluxogramas, diagramas de sequência ou diagramas ER."
---
```

| Campo | Obrigatório | Regra |
| --- | --- | --- |
| `name` | Sim | Letras minúsculas, dígitos e hífens; no máximo 64 caracteres; sem hífen no início/fim nem `--`; deve ser idêntico ao diretório pai |
| `description` | Sim | Diz o que a skill faz e quando usá-la, com palavras-chave; no máximo 1.024 caracteres |
| `argument-hint` | Não (VS Code) | Texto de ajuda exibido quando a skill é invocada como comando `/` |
| `user-invocable` | Não (VS Code) | `false` esconde a skill do menu `/`, mantendo o carregamento automático |
| `disable-model-invocation` | Não (VS Code) | `true` exige invocação manual via `/` |
| `license`, `compatibility`, `metadata`, `allowed-tools` | Não (padrão aberto) | Definidos na especificação Agent Skills; o suporte varia por cliente, então não dependa deles para comportamento no VS Code |

> [!IMPORTANT]
> `name` deve ser idêntico ao nome da pasta. `.github/skills/gerador-de-diagramas/SKILL.md` deve declarar `name: "gerador-de-diagramas"`. Caracteres inválidos ou divergência impedem o carregamento silenciosamente. Não use prefixos de namespace (`org/skill`, `org:skill`).

## A description controla o carregamento automático

Durante a descoberta, o Copilot lê apenas `name` e `description`. Inclua:

1. O que a skill faz.
2. Quando usá-la, com gatilhos concretos, tipos de arquivo ou frases.
3. Palavras-chave que o usuário provavelmente digitará (inclua sinônimos em português e inglês quando o time usa ambos).

```yaml
# Bom: específico
description: "Use ao criar ou gerar arquivos draw.io, fluxogramas, diagramas de sequência ou diagramas ER."

# Ruim: vago
description: "Ajuda com diagramas"
```

Coloque o valor entre aspas. Use aspas simples quando os gatilhos contiverem aspas duplas.

## Formato recomendado do corpo

Depois do frontmatter, use um título `#` em sentence case e estas seções, nesta ordem:

- `## Quando invocar`: três ou quatro pedidos realistas entre aspas.
- Uma ou mais seções de procedimento com tabelas, checklists ou passos.
- `## Modelo de saída`: um bloco cercado com o artefato exato.
- `## Gate de qualidade`: um checklist `- [ ]`.

Seções como `## Armadilhas`, `## Solução de problemas` e `## Referências` são opcionais quando agregam informação.

## Divulgação progressiva

| Nível | Conteúdo carregado | Quando |
| --- | --- | --- |
| Descoberta | Somente `name` e `description` | Sempre |
| Instruções | Corpo completo do `SKILL.md` | Quando o pedido casa com a descrição ou a skill é invocada via `/` |
| Recursos | Scripts, referências e templates | Quando o corpo os referencia e o Copilot segue o link |

Mantenha o corpo focado. Depois de cerca de 200 linhas, mova detalhes para `references/` e referencie-os. Trate 500 linhas como limite rígido. Mantenha referências a um nível de profundidade a partir do `SKILL.md`.

## Empacotando recursos

| Pasta | Conteúdo | Lido no contexto? |
| --- | --- | --- |
| `scripts/` | Automação executável (`.py`, `.sh`, `.js`, `.ts`) | Somente quando executado |
| `references/` | Documentação que o Copilot usa para decidir | Sim, quando referenciada |
| `templates/` | Estruturas que o Copilot modifica | Sim, quando referenciada |
| `assets/` | Arquivos estáticos emitidos sem alteração | Não |

Use `templates/` quando o Copilot edita o arquivo e `assets/` quando o emite sem alteração. Referencie arquivos por caminhos relativos ao `SKILL.md`, como `[validador](./scripts/validate.py)`.

Prefira scripts a código inline regenerado quando a lógica se repete, exige determinismo ou merece testes. Scripts devem oferecer `--help`, falhar com mensagens claras, não armazenar segredos e usar caminhos relativos.

## Escrevendo skills de alto impacto

- Ensine apenas o que o Copilot provavelmente erraria: convenções internas, padrões não óbvios, particularidades de versão e fluxos de domínio.
- Mantenha descrições curtas e ricas em palavras-chave, pois todas competem pela mesma janela de descoberta.
- Registre armadilhas como "nunca faça X porque Y" quando o Copilot produzir resultado incorreto.
- Prefira orientação flexível para trabalho aberto e reserve passos numerados para sequências obrigatórias, como build, deploy e setup.
- Não amarre a skill a um projeto específico: parametrize caminhos, stacks e IDs, ou leia-os das instruções do repositório.

## Convenções

| Regra | Motivo |
| --- | --- |
| `name` idêntico ao diretório da skill | Divergência impede o carregamento silenciosamente |
| `description` diz quando usar, em até 1.024 caracteres | É o único texto lido na descoberta |
| Campos opcionais só com necessidade real | Evita suposições sobre suporte em cada cliente |
| Corpo segue invocação, procedimento, modelo de saída e gate de qualidade | Padrão previsível para quem revisa |
| Detalhes vão para `references/` após cerca de 200 linhas | Reduz custo de contexto |
| Scripts têm `--help`, tratam erros e não armazenam segredos | Automação empacotada deve ser segura e autoexplicativa |

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Usar o mesmo nome na pasta e em `name` | Renomear apenas um dos dois |
| Escrever uma `description` rica em gatilhos | Usar uma descrição vaga como "helpers" |
| Referenciar arquivos empacotados por caminhos relativos | Fixar caminhos absolutos ou específicos de máquina |
| Dividir skills grandes em `references/` | Deixar um `SKILL.md` passar de 500 linhas |
| Incluir as quatro seções recomendadas | Omitir invocação, modelo de saída ou gate de qualidade |
| Referenciar apenas skills, agentes e arquivos que existem | Apontar para prompts, scripts ou pastas inexistentes |

## Checklist de PR

- [ ] Frontmatter contém `name` e `description` entre aspas; campos opcionais são justificados
- [ ] `name` usa minúsculas e hífens, tem no máximo 64 caracteres e é idêntico ao diretório pai
- [ ] `description` diz o que a skill faz e quando usá-la, em até 1.024 caracteres
- [ ] O corpo tem invocação, pelo menos um procedimento, modelo de saída e gate de qualidade
- [ ] O conteúdo ensina conhecimento não óbvio, não sintaxe básica
- [ ] Scripts, referências, templates e assets usam caminhos relativos e existem
- [ ] O corpo permanece focado, sem emojis nem pragmas de lint inline

## Referências

- [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [Agent Skills specification](https://agentskills.io/specification)
