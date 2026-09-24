---
description: "Use ao criar, revisar ou depurar hooks de agente (GitHub Copilot CLI, cloud agent, VS Code Local): descritores em .github/hooks/*.json, scripts de hook, política, eventos, payloads, decisões e segurança."
applyTo: ".github/hooks/**"
---

# Hooks de agente - guia de autoria

Este arquivo é ativado ao editar qualquer coisa em `.github/hooks/`. Ele define como criar hooks portáveis, seguros e testáveis. O funcionamento do kit existente está explicado no [guia didático](../hooks/README.md); política, formatos de saída e verificação estão na [referência técnica](../hooks/REFERENCIA.md). Não repita esse conteúdo aqui.

## Antes de criar um hook

1. Identifique o harness de destino (Session Target): Copilot (CLI, Agent Host, cloud agent) ou Local. Eventos, payloads e decisões diferem.
2. Confirme que o comportamento precisa ser **determinístico**. Se for orientação ao modelo, use instruções, skills ou agentes em vez de hook.
3. Decida o papel: observar, injetar contexto, modificar ou bloquear. Só `preToolUse`, `permissionRequest`, `agentStop` e `subagentStop` tomam decisões.

## Regras de formato

| Regra | Motivo |
| --- | --- |
| Descritores usam `version: 1`, eventos em camelCase, `bash` + `powershell`, `cwd: "."` e `timeoutSec` | Formato nativo do Copilot, convertido pelo parser Local |
| Um único script de entrada com subcomando por evento | Normalização e política compartilhadas, sem scripts divergentes |
| Nenhum `*.json` que não seja descritor na raiz de `.github/hooks/` | Todo JSON ali é carregado como hook; configuração vai para `config/` |
| Scripts somente com biblioteca padrão da linguagem escolhida | Funciona em qualquer projeto sem instalar dependências |
| Caminhos relativos à raiz do repositório | O harness executa com `cwd` na raiz |

## Regras de comportamento

- **Normalize os dois payloads:** `toolName`/`toolArgs`/`sessionId` (Copilot) e `tool_name`/`tool_input`/`session_id` (Local). `toolArgs` pode chegar como string JSON.
- **Responda nos dois formatos:** campos de topo (`permissionDecision`, `additionalContext`, `decision`) e `hookSpecificOutput` com `hookEventName`.
- **Emita um único objeto JSON** no stdout. Dois objetos concatenados viram JSON inválido e são ignorados.
- **Nunca devolva `allow` automático** em `preToolUse`; sem achado, não emita decisão para manter as confirmações normais.
- **Bloqueio = JSON de `deny` + mensagem em stderr + código 2.** Isso bloqueia no Copilot e no Local.
- **`preToolUse` é fail-closed:** JSON inválido ou exceção interna resultam em `deny`. Os demais eventos são fail-open, com mensagem em stderr.
- **Termine bem antes do `timeoutSec`.** Timeout é fail-open no Copilot; um hook lento não protege nada.
- **Limite continuações** em `agentStop`/`Stop`: conte bloqueios e libere após um máximo; cada continuação consome créditos.
- **Execute comandos como lista de argv**, sem shell, e valide entradas antes de usá-las.
- **Mensagens de bloqueio são acionáveis:** diga qual regra disparou e onde ajustar a política.

## Segurança e privacidade

- Não registre prompts, respostas, argumentos brutos, conteúdo de arquivos nem segredos. Audite apenas metadados (evento, ferramenta, resultado, regra).
- Não coloque credenciais em descritores, política, saída ou contexto injetado.
- Proteja `.github/hooks/**` contra escrita silenciosa pelo agente.
- Regex de comando é alarme, não fronteira: combine com `tools:` restritos, aprovação de terminal e revisão humana.
- Não leia o transcript do chat como API estável; o formato muda entre versões e harnesses.

## Testes obrigatórios

Toda mudança em script ou política vem com teste em `scripts/test_*.py` que cubra, no mínimo: passagem sem decisão, `deny`, `ask`, os dois formatos de payload, JSON inválido e o caminho de erro. Rode:

```bash
python3 -B -m unittest discover -s .github/hooks/scripts -v
```

Depois valide em uma sessão real do harness de destino (Chat: Configure Hooks e canal de saída de hooks no VS Code; reinício da CLI no Copilot CLI).

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Centralizar a política em `config/policy.json` | Espalhar regras em vários scripts |
| Testar cada regra nova com um caso que falha sem ela | Confiar só na leitura do código |
| Documentar diferenças entre harnesses no README | Supor que um evento existe em todos os harnesses |
| Usar hooks por agente (`hooks:` no `.agent.md`) apenas no Local, cientes do Preview | Esperar que hooks por agente funcionem no Copilot CLI |

## Checklist de PR

- [ ] O evento existe no harness de destino e o schema de entrada/saída foi conferido na referência oficial
- [ ] O descritor usa o formato padrão e aponta para o script de entrada único
- [ ] `preToolUse` continua fail-closed e sem `allow` automático
- [ ] Nenhum dado sensível é registrado ou injetado
- [ ] O tempo de execução fica bem abaixo de `timeoutSec`
- [ ] Testes cobrem a mudança e passam; `policy.json` e os padrões do script estão alinhados
- [ ] O README foi atualizado quando o comportamento visível mudou

## Referências

- [Configure agent hooks in VS Code](https://code.visualstudio.com/docs/agent-customization/hooks)
- [Local hooks reference (VS Code)](https://code.visualstudio.com/docs/agents/reference/hooks-reference)
- [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)
