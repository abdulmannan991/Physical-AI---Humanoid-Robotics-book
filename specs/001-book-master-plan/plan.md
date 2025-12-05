## Phase 1: Environment & Initialization
- Step 1.1: Initialize Docusaurus 3 (TypeScript variant).
- Step 1.2: Clean up default boilerplate (remove blog, generic pages).
- Step 1.3: Configure `docusaurus.config.ts` (Metadata, distinct `url` and `baseUrl`).

## Phase 2: Core Architecture & Theming
- Step 2.1: Implement the "Docs-Only" mode structure.
- Step 2.2: Apply custom "Textbook" styling (CSS/Infima overrides).
- Step 2.3: Set up the Sidebar logic in `sidebars.ts`.

## Phase 3: Content Engine & Features
- Step 3.1: Install and configure `remark-math` and `rehype-katex`.
- Step 3.2: Create a reusable "Chapter" template.
- Step 3.3: Implement the custom Homepage (Dashboard style).

## Phase 4: CI/CD & Deployment
- Step 4.1: Configure GitHub Actions for deployment to GitHub Pages.
- Step 4.2: Verify build process locally.