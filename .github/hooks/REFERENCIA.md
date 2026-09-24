# Hooks do GitHub Copilot: referência do kit

Referência técnica do kit de hooks desta pasta: estrutura, compatibilidade, configuração, verificação e limites. Para entender os conceitos com analogias e exemplos, leia primeiro o [guia didático](README.md). Regras para criar ou alterar hooks estão em [hooks.instructions.md](../instructions/hooks.instructions.md).

## Estrutura

```text
.github/hooks/
  README.md                 guia didático
  REFERENCIA.md             esta referência
  10-guardrails.json        preToolUse
  20-session-context.json   sessionStart
  30-audit.json             postToolUse, postToolUseFailure, sessionEnd
  40-quality-gate.json      agentStop (inativo até ser configurado)
  config/policy.json        política revisável do projeto
  scripts/hook.py           ponto de entrada único (Python 3.9+, só biblioteca padrão)
  scripts/test_hook.py      testes automatizados
  .gitignore                ignora .logs/ e __pycache__/
```

> [!IMPORTANT]
> Todo `*.json` na raiz de `.github/hooks/` é lido como descritor de hooks. Por isso a política fica em `config/`, fora do padrão de descoberta.

## Compatibilidade

| Harness | Carrega este kit? | Observações |
| --- | --- | --- |
| Copilot CLI e Copilot no Agent Host | Sim | Formato nativo do kit (`version: 1`, eventos em camelCase) |
| Copilot cloud agent | Sim | Linux e não interativo: `ask` vira `deny`; só `bash` é usado; logs são efêmeros |
| Local (VS Code) | Sim | Converte o formato Copilot; `sessionEnd` e `postToolUseFailure` não existem no Local; `agentStop` corresponde a `Stop` |
| Claude e Codex | Não por este caminho | Usam formatos próprios |

## Descritores e eventos

| Descritor | Evento | Subcomando | Timeout | Papel |
| --- | --- | --- | ---: | --- |
| `10-guardrails.json` | `preToolUse` | `pre-tool-use` | 10 s | Bloqueia, pede confirmação ou não emite decisão |
| `20-session-context.json` | `sessionStart` | `session-start` | 10 s | Injeta contexto curto do projeto |
| `30-audit.json` | `postToolUse`, `postToolUseFailure`, `sessionEnd` | `post-tool-use`, `post-tool-use-failure`, `session-end` | 10 s | Auditoria e contagem de escritas |
| `40-quality-gate.json` | `agentStop` | `agent-stop` | 300 s | Quality gate opcional antes do encerramento |

Saídas por decisão:

| Decisão | stdout | Código de saída |
| --- | --- | --- |
| `deny` | `permissionDecision` no topo e em `hookSpecificOutput`; motivo também em stderr | `2` |
| `ask` | `permissionDecision: "ask"` no topo e em `hookSpecificOutput` | `0` |
| Sem achado | vazio | `0` |
| Contexto (`sessionStart`) | `additionalContext` no topo e em `hookSpecificOutput` | `0` |
| Bloqueio de encerramento (`agentStop`) | `decision: "block"` e `reason` no topo e em `hookSpecificOutput` | `0` |

JSON de entrada inválido ou exceção interna em `pre-tool-use` resultam em `deny`. Nos demais eventos, o erro vai para stderr com código `1` e a sessão continua.

## Configuração

Edite [config/policy.json](config/policy.json). Cada seção substitui a seção padrão do script. O teste `test_should_ship_policy_equal_to_script_defaults` falha se o arquivo divergir dos padrões, lembrando de atualizar os dois juntos.

| Chave | Efeito |
| --- | --- |
| `protected_paths.deny` / `.ask` | Globs relativos à raiz para escrita bloqueada ou com confirmação |
| `secret_paths.patterns` / `.exceptions` | Arquivos sensíveis; padrões sem `/` casam com o nome do arquivo em qualquer pasta |
| `outside_workspace_write` | `deny`, `ask` ou `off` para escrita fora do repositório |
| `shell.deny` / `.ask` | Expressões regulares Python aplicadas ao comando |
| `audit.enabled` / `.max_bytes` | Liga a auditoria e define o tamanho de rotação |
| `session_context.enabled` / `.extra` | Liga o contexto inicial e define os lembretes |
| `quality_gate.*` | `enabled`, `commands` (lista de argv, sem shell), `timeout_sec` (menor que os 300 s do descritor) e `max_blocks` |

Leitura de arquivo sensível resulta em `deny`; escrita nele ou comando de shell que o menciona resultam em `ask`. Quando há mais de um achado, vale o mais restritivo.

### Quality gate

Para ligar, use o comando de testes do projeto:

```json
"quality_gate": { "enabled": true, "commands": [["npm", "test", "--silent"]], "timeout_sec": 240, "max_blocks": 2 }
```

Outros exemplos: `[["python3", "-m", "pytest", "-q"]]` ou `[["./mvnw", "-q", "verify"]]`.

- O gate só roda quando a sessão escreveu arquivos (contagem feita pelo `postToolUse` em `.logs/state/`).
- Cada bloqueio no `Stop` gera uma nova rodada do agente e consome créditos; após `max_blocks` bloqueios seguidos, o gate libera o encerramento e emite um aviso.
- Os comandos rodam com as permissões do usuário. Trate `policy.json` como código revisado e prefira comandos rápidos e determinísticos.

## Auditoria

Cada linha de `.github/hooks/.logs/audit.jsonl` contém apenas `ts`, `event`, `session`, `tool`, `outcome` e, em decisões, `rule`. Argumentos, conteúdo, caminhos, prompts e respostas nunca são registrados. O arquivo é renomeado para `audit.jsonl.1` ao passar de `audit.max_bytes`.

## Verificação

```bash
# testes do kit
python3 -B -m unittest discover -s .github/hooks/scripts -v

# simula uma decisão de preToolUse (deve sair com código 2)
echo '{"toolName":"edit","toolArgs":{"path":".git/config"}}' \
  | python3 -B .github/hooks/scripts/hook.py pre-tool-use; echo "exit=$?"
```

Em uma sessão real:

- **VS Code (Local):** rode **Chat: Configure Hooks** para ver os arquivos descobertos e use o canal **GitHub Copilot Chat Hooks** no painel Output ou os agent debug logs para inspecionar entrada e saída.
- **Copilot CLI:** confirme que a pasta é confiável, que `disableAllHooks` não está ativo e reinicie a CLI após alterar descritores.
- Peça ao agente para ler um `.env`, confirme o bloqueio e procure a linha correspondente em `.logs/audit.jsonl`.

## Limites conhecidos

- Timeout é fail-open no harness Copilot, inclusive em `preToolUse`; o orçamento do descritor é de 10 s.
- Regex de shell é um alarme, não uma fronteira de segurança. Combine com `tools:` restritos nos agentes, aprovação de terminal e revisão humana.
- Nomes de ferramentas variam por harness. O script classifica ferramentas por nome (shell, escrita, leitura) e extrai caminhos de chaves comuns (`path`, `filePath`, `file_path`) e de cabeçalhos de patch. Ferramentas com esquemas novos podem passar despercebidas; use a auditoria para descobri-las.
- No cloud agent, `ask` equivale a `deny`.
- Hooks por agente (`hooks:` no `.agent.md`) existem apenas no harness Local e estão em Preview.

## Referências

- [Configure agent hooks in Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/hooks)
- [Local hooks reference (VS Code)](https://code.visualstudio.com/docs/agents/reference/hooks-reference)
- [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)
- [Using hooks with GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks)
