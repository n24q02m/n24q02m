# Docs Site Standard

**Decision (locked 2026-04-18)**: Mọi docs site dùng **Astro Starlight** (`@astrojs/starlight`). KHÔNG đề xuất VitePress / Docusaurus / Nextra / Mintlify nữa (trừ khi user explicit yêu cầu).

## Khi nào dùng

- Bất kỳ repo public/private nào cần docs site (skret, claude-plugins unified MCP docs, future projects).
- Migration từ VitePress / Docusaurus / Nextra sang chuẩn mới.

## Tại sao Astro Starlight

1. **Pagefind built-in** — client-side static search, chunked lazy-load, scale 1000+ pages, initial bundle <50KB. Vs VitePress minisearch ~500KB+ toàn bộ index.
2. **Content Collections API** mature cho multi-project (multiple MCP docs trong cùng 1 site).
3. **Industry leader 2025-2026**: Cloudflare docs (chính thức), Zed editor, Svelte/SvelteKit, Drizzle ORM, Biome, Arktype, Astro itself.
4. **Static output only** — compat CF Pages free tier, KHÔNG cần Workers (paid).
5. **SEO tốt hơn** — Astro SSG = pure HTML, không hydration overhead cho content pages.
6. **Accessibility** WCAG AA tested built-in.
7. **i18n** built-in nếu cần.
8. **1 framework cho mọi docs site** → giảm context switch, tooling chung.

## Constraint deployment

- Static-only deployment trên CF Pages free (KHÔNG dùng Workers, KHÔNG dùng dynamic SSR).
- Build command: `pnpm astro build`. Output dir: `docs/dist/`.
- Public assets: `docs/public/` (served từ root URL, conv trùng VitePress).
- Logo SVG đặt tại `docs/src/assets/` (import relative — không serve từ `public/`).

## Setup mới (greenfield)

```bash
cd ~/projects/<repo>
pnpm create astro@latest docs --template starlight --no-install --skip-houston --typescript strict
cd docs
pnpm install
pnpm add @astrojs/sitemap
```

## Config template

`docs/astro.config.mjs`:

```javascript
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://<project>.<your-domain>',
  integrations: [
    starlight({
      title: '<project>',
      description: '<short description>',
      logo: {
        light: './src/assets/logo.svg',
        dark: './src/assets/logo-dark.svg',
        alt: '<project> logo',
      },
      favicon: '/favicon.svg',
      head: [
        { tag: 'link', attrs: { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }},
        { tag: 'link', attrs: { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }},
        { tag: 'meta', attrs: { property: 'og:type', content: 'website' }},
        { tag: 'meta', attrs: { property: 'og:image', content: 'https://<project>.<your-domain>/og-image.png' }},
        { tag: 'meta', attrs: { name: 'twitter:card', content: 'summary_large_image' }},
        { tag: 'meta', attrs: { name: 'twitter:image', content: 'https://<project>.<your-domain>/og-image.png' }},
      ],
      social: { github: 'https://github.com/<owner>/<repo>' },
      editLink: { baseUrl: 'https://github.com/<owner>/<repo>/edit/main/docs/' },
      sidebar: [
        { label: 'Guide', autogenerate: { directory: 'guide' }},
        { label: 'Reference', autogenerate: { directory: 'reference' }},
        // ... etc
      ],
    }),
    sitemap(),
  ],
});
```

## Migration từ VitePress

1. Backup: `mv docs docs-old; cp -r docs-old/public docs/public`.
2. Scaffold Starlight (xem trên).
3. Move pages: `cp -r docs-old/<dir>/*.md docs/src/content/docs/<dir>/`.
4. Update frontmatter: VitePress `--- title: X --- # X` → Starlight `--- title: X description: ... ---`. Remove `layout: home`, `hero:` blocks (Starlight dùng components `<Card>`, `<Hero>`, `<LinkCard>`).
5. Move logo SVG: `cp docs/public/logo.svg docs/src/assets/`.
6. Update CI/CD: `pnpm build` (VitePress) → `pnpm astro build` (Starlight). Output dir `docs/dist/` giống VitePress.
7. Effort: ~2-3h cho ~10-15 pages.

## Verify

```bash
cd docs
pnpm astro build
ls dist/_pagefind/pagefind.js  # Pagefind tự sinh post-build
ls dist/sitemap-index.xml      # @astrojs/sitemap tự sinh
pnpm astro preview              # http://localhost:4321 → test search box
du -sh dist/_pagefind/          # < 200KB cho ~10-15 pages
```

## Multi-project unified docs (vd claude-plugins)

Pattern: Content Collections, mỗi MCP = 1 collection trong `src/content/docs/<mcp-name>/`. Sidebar autogenerate per collection:

```javascript
sidebar: [
  { label: 'wet-mcp', autogenerate: { directory: 'wet-mcp' }},
  { label: 'mnemo-mcp', autogenerate: { directory: 'mnemo-mcp' }},
  { label: 'better-notion-mcp', autogenerate: { directory: 'better-notion-mcp' }},
  // ... 7-8 MCPs
]
```

Pagefind tự index toàn bộ → search across multiple MCPs.

## Khi nào KHÔNG dùng Starlight

- User explicit yêu cầu framework khác.
- Docs cực đơn giản < 5 pages → chỉ cần README.md + GitHub render (không build site).
- Cần dynamic SSR features (rare — user thường ruled out static-only).

## References

- Starlight: https://starlight.astro.build
- Pagefind: https://pagefind.app
- Astro: https://astro.build
- CF Pages docs: https://developers.cloudflare.com/pages/ (Starlight-powered, ironic confirmation)
