<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0 (MAJOR: Initial creation/significant update of the Constitution file based on provided project context)
Modified principles: All (from template placeholders to specific project rules)
Added sections: N/A (sections are filled from template, but content is new)
Removed sections: Generic [SECTION_2_NAME]/[SECTION_2_CONTENT] and [SECTION_3_NAME]/[SECTION_3_CONTENT] (not specified by user)
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending (review for alignment with new principles)
- .specify/templates/spec-template.md: ⚠ pending (review for alignment with new principles)
- .specify/templates/tasks-template.md: ⚠ pending (review for alignment with new principles)
- .claude/commands/speckit.constitution.md: ✅ updated (this file's guidance is aligned)
Follow-up TODOs: N/A
-->
# Project Constitution: Physical AI & Humanoid Robotics Course

## 1. Project Vision

- **Goal:** Create a comprehensive, interactive digital book on Physical AI & Humanoid Robotics.
- **Platform:** Docusaurus 3 (TypeScript) deployed to GitHub Pages.
- **Structure:** "Docs-Only Mode" (Book structure). The landing page (`/`) must redirect immediately to Chapter 1. No blog.

## 2. The "Context7" Golden Rule (CRITICAL)

- **Rule:** The AI must NEVER rely on its internal training data for Docusaurus syntax, as it may be outdated (v2 vs v3).
- **Mandate:** For ANY task involving frontend code, `docusaurus.config.ts`, swizzling, or CSS customization, you MUST first use the `context7` MCP server to fetch the latest official documentation.
- **Verification:** Before implementing a UI feature, cite the Docusaurus docs URL you retrieved via Context7.

## 3. Spec-Kit Workflow Enforcement

- We strictly follow the 5-step cycle:
  1. **Constitution** (This file - The Laws)
  2. **Specification** (Detailed requirements gathering)
  3. **Planning** (Architecture and logic mapping)
  4. **Tasks** (Atomic, step-by-step checklists)
  5. **Implementation** (Coding - only after steps 1-4 are approved)
- **Anti-Pattern:** "Vibe Coding" (jumping to code without a plan) is strictly forbidden.

## 4. Code Quality & Standards

- **Strict TypeScript:** Use `.ts` and `.tsx` for all config and page files. No `.js` allowed.
- **Content:** All educational content must be written in Markdown/MDX with interactive components (Mermaid diagrams, Tabs).
- **Structure:** Maintain a clean folder structure suitable for a textbook (e.g., `/docs/01-module/`, `/docs/02-module/`).

## 5. Governance

- This constitution supersedes all other practices.
- Amendments require formal documentation in the `history/` folder.
- All code generation tasks must explicitly verify compliance with these principles before execution.

**Version**: 1.0.0 | **Ratified**: 2025-12-04 | **Last Amended**: 2025-12-04