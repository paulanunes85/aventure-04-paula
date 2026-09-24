---
description: "Use ao implementar ou revisar o contrato de plataforma frontend: framework, TypeScript estrito, fronteira servidor/cliente, estilização, design system, linha de base de acessibilidade e testes de componentes."
applyTo: "**/*.{tsx,jsx,vue,svelte},**/{frontend,web,client}/**/*.{ts,js,mjs}"
---

# Contrato de plataforma frontend

Este arquivo é ativado ao trabalhar com componentes, rotas ou código de interface. Ele define o contrato de plataforma: framework declarado, TypeScript estrito, fronteira servidor/cliente, estilização, linha de base de acessibilidade e integração de testes. Ele governa framework, tipagem, estilo e fronteiras; [frontend.instructions.md](frontend.instructions.md) governa construção de componentes, interação, estado, implementação de acessibilidade e fluxos do usuário.

## Perfil de stack do projeto

A stack efetiva é a declarada em [copilot-instructions.md](../copilot-instructions.md) ou em ADR. Se não estiver declarada, pergunte antes de criar a estrutura do frontend. Perfis comuns:

| Perfil | Framework | Renderização | Estilo | Testes |
| --- | --- | --- | --- | --- |
| SPA | React ou Vue + Vite | Cliente | Tailwind CSS ou CSS Modules | Vitest + Testing Library |
| Full-stack React | Next.js (App Router) | Server Components + Client Components | Tailwind CSS + shadcn/ui | Vitest + Testing Library |
| Full-stack Vue | Nuxt | SSR + componentes cliente | Tailwind CSS | Vitest + Vue Testing Library |
| Site estático/docs | Astro, VitePress ou similar | Estático | Tema do gerador | Verificação de links e build |

Não misture perfis nem adicione um segundo sistema de estilização sem ADR.

## Fronteira servidor/cliente

Aplique quando o framework renderiza no servidor (Next.js, Nuxt, Remix, SvelteKit):

- Componentes são de servidor por padrão; marque como cliente (`'use client'` no Next.js) apenas o menor componente que precisa de interatividade.
- A busca de dados fica no servidor; o componente interativo recebe dados por props.
- Mutações passam por uma fronteira de servidor (Server Actions, rotas de API ou handlers do framework) com validação antes de chamar o backend.
- **Nunca** exponha segredos no cliente: chaves de API, tokens e URLs internas ficam no servidor. Variáveis públicas (`NEXT_PUBLIC_`, `VITE_`, `NUXT_PUBLIC_`) são visíveis no navegador.

Em uma SPA sem servidor, trate toda configuração do bundle como pública e mantenha segredos fora do frontend.

```tsx
// Next.js: página de servidor busca dados; só o filtro é componente cliente
export default async function ItemsPage() {
  const response = await fetch(`${process.env.API_URL}/api/v1/items`);
  if (!response.ok) throw new Error('Falha ao carregar os itens');
  const items: ItemDto[] = await response.json();
  return <ItemList items={items} />;
}
```

## Convenções TypeScript

- **`strict: true`** no `tsconfig.json`: sem exceções e sem `// @ts-ignore`.
- **Sem `any`**: use `unknown` e refine com type guards.
- **Exports nomeados em componentes reutilizáveis**: `export function ItemCard()`. Arquivos de rota podem usar o `export default` exigido pelo framework.
- **`interface` para formatos extensíveis**; use `Pick`, `Omit` e `Partial` em vez de duplicar tipos.
- **Valide dados externos na fronteira** (resposta de API, entrada de formulário, `localStorage`) antes de tratá-los como tipados.

```tsx
// Correto: export nomeado e props tipadas
export function ItemCard({ item }: { item: ItemDto }) {
  return <div>{item.label}</div>;
}

// Errado: export default e any
export default function ItemCard({ item }: { item: any }) { /* ... */ }
```

## Estilização e design system

- Use a abordagem de estilo declarada pelo projeto (por exemplo, utilitários Tailwind) e os componentes do design system adotado (por exemplo, shadcn/ui) para elementos padrão.
- Use tokens do design system para cores, espaçamento e tipografia; não fixe valores soltos no código.
- Responsivo por padrão: mobile-first.
- Use SVG para ícones, favicons e ilustrações.

## Linha de base de acessibilidade

Toda página e componente DEVE atender a estes mínimos:

- Toda imagem informativa tem `alt`; imagens decorativas têm `alt=""`
- Todo campo de formulário tem `<label>` associado
- Elementos interativos são operáveis por teclado
- Cor não é o único meio de transmitir informação
- A página tem um único `<h1>` e os títulos seguem ordem lógica
- O atributo `lang` do documento corresponde ao idioma da interface

## Testes de componentes

Siga [tests.instructions.md](tests.instructions.md). Exemplo mínimo:

```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ItemCard } from './ItemCard';

describe('ItemCard', () => {
  it('displays the item label when an item is provided', () => { // REQ-NNN
    render(<ItemCard item={{ label: 'Exemplo' }} />);
    expect(screen.getByText('Exemplo')).toBeInTheDocument();
  });
});
```

## Convenções

| Regra | Motivo |
| --- | --- |
| Framework e perfil declarados antes do scaffold | Evita stacks ad hoc e retrabalho |
| Servidor por padrão quando o framework suporta | Reduz JavaScript no cliente e mantém acesso a dados no servidor |
| `strict: true`, sem `any` e sem `// @ts-ignore` | Erros de tipo aparecem antes da execução |
| Exports nomeados em componentes reutilizáveis | Imports consistentes; rotas mantêm os defaults exigidos |
| Mutações por fronteira de servidor | Formulários passam por validação no servidor |
| Um único sistema de estilo e design system | Componentes consistentes |

## Faça / Não faça

| Faça | Não faça |
| --- | --- |
| Usar exports nomeados em componentes | Usar `export default` em componentes reutilizáveis |
| Usar `unknown` com type guards | Usar `any` ou suprimir o TypeScript estrito |
| Usar `async`/`await` em fluxos assíncronos | Encadear `.then()` |
| Estilizar com a abordagem declarada | Adicionar CSS Modules, styled-components ou outro sistema sem ADR |
| Manter segredos no servidor | Colocar segredos em componentes cliente ou variáveis públicas |

## Checklist de PR

- [ ] `tsconfig.json` continua estrito; nenhum `any` ou `// @ts-ignore` foi adicionado
- [ ] Componentes de servidor continuam padrão quando aplicável, e o código cliente aparece só onde há interação
- [ ] Mutações passam por fronteira de servidor e validam dados antes de chamar o backend
- [ ] Componentes reutilizáveis usam exports nomeados
- [ ] A estilização usa a abordagem declarada, sem nova dependência de estilo
- [ ] A linha de base de acessibilidade está coberta: rótulos, teclado, ordem de títulos e sinais além da cor
- [ ] Testes de componente cobrem o comportamento alterado com a convenção de nomes do projeto
