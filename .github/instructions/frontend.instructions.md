---
description: "Use ao criar componentes de UI, páginas, interações do cliente, estado de componentes, acessibilidade e fluxos voltados ao usuário."
applyTo: "**/*.{tsx,jsx,vue,svelte}"
---

# Convenções de frontend - construção de componentes e interação

Este arquivo é ativado quando você cria interface. Ele foca em construção de componentes, interação do cliente, estado, implementação de acessibilidade e fluxos do usuário. O contrato de plataforma (framework, TypeScript estrito, estilização, fronteira servidor/cliente) pertence a [frontend-spec.instructions.md](frontend-spec.instructions.md); siga aquele arquivo para esses temas e não os repita aqui.

Os exemplos usam React + TypeScript. Em Vue ou Svelte, aplique os mesmos princípios com a sintaxe equivalente (`ref`/`defineProps`, stores locais, etc.).

## Construção de componentes

Crie componentes pequenos, com responsabilidade única, exports nomeados e props tipadas. Prefira composição a uma lista crescente de props e mantenha componentes de apresentação livres de busca de dados.

```tsx
import type { ItemDto } from '@/types/item';

export function ItemCard({ item }: { item: ItemDto }) {
  return (
    <article className="rounded-lg border p-4">
      <h3 className="font-semibold">{item.label}</h3>
      <p className="text-muted-foreground">{formatCurrency(item.amount, 'pt-BR', 'BRL')}</p>
    </article>
  );
}
```

Mantenha a superfície interativa (cliente) a menor possível: um componente de servidor ou contêiner busca os dados e os repassa a um componente pequeno que trata a interação.

## Estado de componentes

Use estado local por padrão. Suba o estado para o ancestral comum mais próximo quando irmãos precisarem compartilhá-lo. Use Context (ou `provide`/`inject` no Vue) **apenas** para estado de cliente realmente compartilhado, e adicione biblioteca de estado somente com ADR justificando a dependência.

```tsx
import { useState } from 'react';

export function ItemFilter({ onFilter }: { onFilter: (term: string) => void }) {
  const [term, setTerm] = useState('');
  return (
    <label className="flex flex-col gap-1">
      <span>Filtrar itens</span>
      <input
        value={term}
        onChange={(event) => { setTerm(event.target.value); onFilter(event.target.value); }}
      />
    </label>
  );
}
```

Campos são controlados (`value` + `onChange` ou `v-model`). Derive valores durante a renderização em vez de espelhar props no estado.

## Interação do cliente e fluxos assíncronos

Mutações seguem a fronteira definida em [frontend-spec.instructions.md](frontend-spec.instructions.md). Controle o estado pendente para desabilitar a ação e reflita-o com `aria-busy`.

```tsx
import { useTransition } from 'react';

export function ArchiveButton({ id, onArchive }: { id: string; onArchive: (id: string) => Promise<void> }) {
  const [isPending, startTransition] = useTransition();
  return (
    <button
      type="button"
      disabled={isPending}
      aria-busy={isPending}
      onClick={() => startTransition(() => onArchive(id))}
    >
      {isPending ? 'Arquivando…' : 'Arquivar'}
    </button>
  );
}
```

## Fluxos voltados ao usuário

Toda tela assíncrona renderiza três estados explícitos, **carregando**, **vazio** e **erro**, nunca uma tela em branco. Confirme ações destrutivas e formate valores e datas com locale explícito para que a saída seja determinística.

```tsx
if (isLoading) return <Spinner aria-label="Carregando itens" />;
if (error) return <ErrorState onRetry={refetch} />;
if (items.length === 0) return <EmptyState message="Nenhum item ainda" />;
```

Avalie o erro antes do estado vazio para que uma falha não seja exibida como "nenhum item".

## Acessibilidade (WCAG 2.2 AA)

| Requisito | Como atender |
| --- | --- |
| Rótulos | Todo campo tem `<label htmlFor>` ou `aria-label` |
| Teclado | Todo elemento interativo é alcançável e operável com Tab/Enter/Espaço |
| Foco | Mova o foco para o diálogo ao abrir e devolva-o ao gatilho ao fechar; o foco nunca fica encoberto |
| Contraste | Texto ≥ 4.5:1; texto grande e componentes de interface ≥ 3:1 |
| Alvos | Alvos de toque/clique com pelo menos 24 × 24 px CSS |
| Estrutura | Um `<h1>` por página, ordem lógica de títulos e landmarks |
| Anúncios | Erros e mudanças de estado anunciados via região `aria-live` ou foco |
| Cor | Nunca o único sinal; combine com texto ou ícone |

Use elementos semânticos (`<button>`, `<nav>`, `<table>`) antes de recorrer a ARIA; adicione ARIA apenas quando a semântica nativa faltar.

## Convenções

| Regra | Motivo |
| --- | --- |
| Exports nomeados em componentes | Imports consistentes e compatíveis com tree shaking |
| Props tipadas, sem `any` | Falhas aparecem em tempo de compilação |
| Estado local; Context só quando compartilhado | Grafo de estado mínimo e previsível |
| Teste colocalizado com o componente | Comportamento e cobertura ficam juntos |
| Estados explícitos de carregando/vazio/erro | Nenhum beco sem saída na interface |

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Empurrar a interatividade para a menor folha | Marcar a página inteira como componente cliente |
| Mutar através da fronteira de servidor definida | Espalhar `fetch` de mutação pelos componentes |
| Rotular todo controle | Usar placeholder como rótulo |
| Formatar valores/datas com locale | Exibir números crus ou strings ISO para o usuário |

## Checklist de PR

- [ ] Componentes usam exports nomeados e props totalmente tipadas
- [ ] A superfície cliente está restrita ao menor componente interativo
- [ ] Estado compartilhado usa Context apenas quando justificado; nenhuma biblioteca de estado não aprovada
- [ ] Telas assíncronas renderizam estados de carregando, vazio e erro
- [ ] Campos têm rótulos, funcionam com teclado e atendem ao contraste AA
- [ ] Um teste colocalizado cobre a interação (ver [tests.instructions.md](tests.instructions.md))
