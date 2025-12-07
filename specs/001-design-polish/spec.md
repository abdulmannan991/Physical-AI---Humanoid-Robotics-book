# Feature Specification: Design Polish

**Feature Branch**: `001-design-polish`
**Created**: 2025-12-06
**Status**: Draft
**Input**: User description: "We are starting a new feature branch: 002-design-polish.\n\nGoal: Upgrade the visual design of the textbook.\n\nRequirements:\n\nCSS Refactor: Update src/css/custom.css to use a professional 'Textbook Theme' (Serif fonts for body, Sans-Serif for headers, Deep Blue primary color).\n\nNavbar Fix: Ensure the title in docusaurus.config.ts navbar config is empty (so only the logo shows).\n\nVisuals: Add Mermaid diagrams and placeholder images to Module 1 and Module 2 chapters."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enhance Textbook Readability (Priority: P1)

As a reader, I want the textbook to have a professional and easy-to-read visual theme so that I can focus on the content without visual distraction.

**Why this priority**: This directly addresses the core goal of upgrading the visual design and improving the user experience for all readers.

**Independent Test**: The visual theme can be fully tested by navigating through different pages of the textbook and observing the typography, color scheme, and hero section. It delivers a more engaging and professional reading experience.

**Acceptance Scenarios**:

1.  **Given** I am viewing any page of the textbook, **When** the page loads, **Then** headings use a professional Sans-Serif font and body text uses a clean Serif font.
2.  **Given** I am viewing any page of the textbook, **When** the page loads, **Then** the primary color scheme is a Deep Robotic Blue.
3.  **Given** I am on the homepage, **When** the page loads, **Then** the hero section has a distinct appearance (e.g., a dark gradient background).

---

### User Story 2 - Clear Navigation Branding (Priority: P2)

As a reader, I want the navigation bar to display only the logo, without a text title, to maintain a clean and professional brand presentation.

**Why this priority**: This refines the branding and aesthetic consistency of the textbook.

**Independent Test**: This can be tested by navigating to any page and verifying that the title text is absent from the navbar, leaving only the logo visible.

**Acceptance Scenarios**:

1.  **Given** I am viewing any page of the textbook, **When** the page loads, **Then** the navigation bar only displays the logo, and no text title is present.

---

### User Story 3 - Enriched Content Understanding (Priority: P1)

As a reader, I want to see relevant diagrams and illustrative images within Module 1 and Module 2 chapters so that I can better understand complex concepts and visualize the content.

**Why this priority**: This significantly enhances the learning experience by providing visual aids where concepts are explained.

**Independent Test**: This can be tested by navigating through Module 1 and Module 2 chapters and verifying the presence of Mermaid.js diagrams for conceptual explanations and placeholder images at the top of intro chapters.

**Acceptance Scenarios**:

1.  **Given** I am reading a chapter in Module 1 or Module 2 that explains a concept (e.g., 'Perception-Action Loop'), **When** I reach that section, **Then** a Mermaid.js diagram is rendered to illustrate the concept.
2.  **Given** I am reading an intro chapter in Module 1 or Module 2, **When** I reach the top of the chapter, **Then** a markdown image placeholder using Unsplash Source is present for context.

---

### Edge Cases

-   What happens if a required font fails to load? (Fallback to system default)
-   How does the system handle images if Unsplash Source is unavailable? (Placeholder text or broken image icon)

## Requirements *(mandatory)*

### Functional Requirements

-   **FR-001**: System MUST apply a Sans-Serif font for all headings.
-   **FR-002**: System MUST apply a Serif font for all body text.
-   **FR-003**: System MUST use a Deep Robotic Blue (e.g., #25c2a0 or #3366cc) as the primary color.
-   **FR-004**: System MUST update the homepage banner to have a distinct visual style (e.g., dark gradient).
-   **FR-005**: System MUST ensure the navbar title is empty in `docusaurus.config.ts`.
-   **FR-006**: System MUST render Mermaid.js diagrams for concepts in Module 1 chapters (e.g., 'Perception-Action Loop').
-   **FR-007**: System MUST render Mermaid.js diagrams for concepts in Module 2 chapters (e.g., 'ROS Graph').
-   **FR-008**: System MUST include markdown image placeholders (using Unsplash Source) at the top of intro chapters in Module 1.
-   **FR-009**: System MUST include markdown image placeholders (using Unsplash Source) at the top of intro chapters in Module 2.

### Key Entities

-   **Textbook Styles**: Represents the visual properties of the textbook, including typography, color palette, and component-specific styling (e.g., hero section).
-   **Navigation Bar Configuration**: Represents the settings for the website's navigation bar, specifically the title and logo display.
-   **Module Content**: Represents the textual and visual elements within Module 1 and Module 2 chapters, including conceptual explanations and illustrative media.

## Success Criteria *(mandatory)*

### Measurable Outcomes

-   **SC-001**: 100% of headings and body text render with the specified font types (Sans-Serif and Serif, respectively) across all textbook pages.
-   **SC-002**: The primary color of the textbook user interface is consistently the Deep Robotic Blue across all pages.
-   **SC-003**: The homepage hero section visually differentiates itself from other page sections through its distinct styling.
-   **SC-004**: The navigation bar title is empty, and only the logo is displayed on all pages.
-   **SC-005**: All specified concepts in Module 1 and Module 2 chapters have a correctly rendered Mermaid.js diagram.
-   **SC-006**: All intro chapters in Module 1 and Module 2 display a visible image placeholder from Unsplash Source.
-   **SC-007**: The textbook successfully builds without errors after applying all styling and content visual changes.
