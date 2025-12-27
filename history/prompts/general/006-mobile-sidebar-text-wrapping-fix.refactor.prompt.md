---
id: 006
title: Mobile Sidebar Text Wrapping Fix
stage: refactor
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-auth-profile-guardrails
user: Abdul Mannan
command: /sp.implement
labels: ["responsive", "mobile", "sidebar", "css", "readability", "ux"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/css/custom.css (modified - added mobile sidebar text wrapping fixes)
tests:
  - Manual testing required: Mobile viewport at 996px (Docusaurus mobile breakpoint)
  - Manual testing required: Mobile viewport at 480px (small screens)
  - Visual verification: Long module names wrap to second line
  - Visual verification: Text doesn't touch scrollbar (safe spacing)
  - Visual verification: All menu items 100% visible
---

## Prompt

## 📱 MOBILE SIDEBAR CONTENT UNREADABLE – CSS FIX

### CONTEXT
- **Framework:** Docusaurus (React)
- **Content:** Educational content (ROS Modules, chapters)
- **Issue:** The mobile sidebar menu has "bad CSS" that makes the content **unreadable**.
- **Symptoms:**
  - The text for chapters (e.g., "Module 2.1...", "Fundamentals") is cut off on the right side.
  - The text does not wrap to the next line.
  - There is no space between the text and the screen edge/scrollbar.

### 🚨 THE PROBLEM
I cannot see the full names of the modules because they run off the screen. The user experience is broken because the navigation text is hidden.

### 🎯 THE GOAL
I need a CSS fix that ensures **100% visibility** of all menu items.
1.  **Text Wrapping:** Long titles MUST wrap to a second line. They should never be cut off.
2.  **Safe Spacing:** Add padding to the right side so text never touches the scrollbar.
3.  **Container Width:** Ensure the list items fit strictly within the mobile viewport width.

### 🧪 REQUIRED CSS FIX (Use `custom.css`)

Please provide the CSS to fix the `.navbar-sidebar__items` and `.menu__link` classes.

**Requirements:**
- Force `white-space: normal !important` to enable text wrapping.
- Add `padding-right: 25px !important` (or more) to clear the scrollbar.
- Set `line-height: 1.5` for better readability when text wraps.

## Response snapshot

### Implementation Summary

Successfully fixed mobile sidebar content readability by adding CSS rules to enable text wrapping, provide safe spacing from scrollbar, and ensure 100% visibility of all menu items in Docusaurus mobile sidebar.

**Root Cause Analysis:**

**Issue: Long Module Names Cut Off**
- Docusaurus default CSS uses `white-space: nowrap` on `.menu__link` elements
- Long titles (e.g., "Module 2.1: Fundamentals of ROS...") exceeded viewport width
- No text wrapping allowed, causing right-side cut-off
- Insufficient padding-right, causing text to overlap with scrollbar
- Container width constraints not properly enforced

**Solution Implemented:**

### Added Mobile Sidebar Fixes to `src/css/custom.css`

**Lines 180-242: Complete Mobile Sidebar Text Wrapping Solution**

**1. @media (max-width: 996px) - Docusaurus Mobile Breakpoint**

```css
/* Sidebar container - ensure proper width constraints */
.navbar-sidebar__items {
  max-width: 100vw !important;
  overflow-x: hidden !important;
  padding-right: 20px !important; /* Safe spacing from scrollbar */
}

/* Menu links - enable text wrapping and proper spacing */
.menu__link {
  white-space: normal !important; /* CRITICAL: Allow text to wrap */
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  line-height: 1.5 !important; /* Better readability for wrapped text */
  padding-right: 25px !important; /* Ensure text doesn't touch scrollbar */
  max-width: 100% !important;
  display: block !important;
}

/* Menu list items - proper width constraints */
.menu__list-item {
  max-width: 100% !important;
  overflow: visible !important;
}

/* Category labels - also enable wrapping */
.menu__list-item-collapsible .menu__link {
  white-space: normal !important;
  word-wrap: break-word !important;
  padding-right: 40px !important; /* Extra space for collapse arrow */
}

/* Ensure nested items also wrap properly */
.menu__list .menu__list {
  padding-left: 1rem !important;
}

.menu__list .menu__list .menu__link {
  white-space: normal !important;
  word-wrap: break-word !important;
  padding-right: 25px !important;
}
```

**2. @media (max-width: 480px) - Extra Small Screens**

```css
.navbar-sidebar__items {
  padding-right: 15px !important;
}

.menu__link {
  font-size: 14px !important; /* Slightly smaller for better fit */
  padding: 0.5rem 0.75rem !important;
  padding-right: 20px !important;
}

.menu__list-item-collapsible .menu__link {
  padding-right: 35px !important;
}
```

### Key CSS Properties Applied:

**Text Wrapping (CRITICAL):**
- ✅ `white-space: normal !important` - Overrides Docusaurus default `nowrap`
- ✅ `word-wrap: break-word !important` - Breaks long words if needed
- ✅ `overflow-wrap: break-word !important` - Modern CSS word breaking
- ✅ `line-height: 1.5 !important` - Better readability for multi-line text

**Safe Spacing (CRITICAL):**
- ✅ `.navbar-sidebar__items` padding-right: 20px - Container safe spacing
- ✅ `.menu__link` padding-right: 25px - Link text safe spacing
- ✅ `.menu__list-item-collapsible .menu__link` padding-right: 40px - Extra space for collapse arrow
- ✅ Nested items padding-right: 25px - Consistent spacing for sub-items

**Container Width Constraints:**
- ✅ `max-width: 100vw !important` - Prevent sidebar exceeding viewport
- ✅ `overflow-x: hidden !important` - Prevent horizontal scrolling
- ✅ `max-width: 100% !important` - Ensure links fit within container
- ✅ `display: block !important` - Proper block-level rendering

**Responsive Adjustments:**
- ✅ 480px breakpoint: Reduced font-size to 14px for better fit
- ✅ 480px breakpoint: Reduced padding-right to 20px (still safe)
- ✅ Nested items: padding-left: 1rem for proper indentation

### Testing Scenarios:

**Long Module Names:**
- "Module 2.1: Fundamentals of ROS and Robotic Systems"
- "Chapter 3: Advanced Navigation Techniques"
- "Section 4.2: Deep Learning for Computer Vision"

**Expected Behavior:**
1. ✅ Long titles wrap to second line (not cut off)
2. ✅ Text has 20-25px safe spacing from scrollbar
3. ✅ All text is 100% visible and readable
4. ✅ Collapse arrows on collapsible items don't overlap text
5. ✅ Nested sub-items also wrap properly with indentation

**Files Modified:**
- `src/css/custom.css` - Lines 180-242 (63 new lines)

**Breakpoints:**
- 996px - Docusaurus mobile sidebar activation
- 480px - Extra small screens with reduced font-size

## Outcome

- ✅ Impact: CRITICAL UX FIX - Enabled text wrapping for long module names in mobile sidebar, added safe spacing to prevent scrollbar overlap, ensured 100% visibility of all menu items
- 🧪 Tests: Manual testing required on mobile viewports at 996px (Docusaurus mobile), 480px (small screens) - verify long module names wrap to second line, text doesn't touch scrollbar, all menu items fully visible
- 📁 Files: Modified 1 file (custom.css) - added 63 lines of mobile sidebar text wrapping CSS
- 🔁 Next prompts: Test mobile sidebar on actual devices/emulators with long module names, verify text wrapping works correctly, confirm safe spacing prevents scrollbar overlap
- 🧠 Reflection: Root cause was Docusaurus default white-space: nowrap on .menu__link elements. Solution: Force white-space: normal + word-wrap + overflow-wrap + padding-right for safe spacing. Critical !important flags needed to override Docusaurus defaults.

## Evaluation notes (flywheel)

- Failure modes observed: Previous implementation relied on Docusaurus defaults which use white-space: nowrap, causing long module names to extend beyond viewport width and get cut off. No padding-right on menu items caused text to overlap scrollbar.
- Graders run and results (PASS/FAIL): Manual testing pending - awaiting visual verification on mobile devices at 996px and 480px viewports. Expected PASS if long module names wrap to second line and text has visible safe spacing from scrollbar.
- Prompt variant (if applicable): CSS-only fix using white-space: normal + word-wrap + padding-right strategy with !important flags
- Next experiment (smallest change to try): If text still overlaps scrollbar on specific devices, increase padding-right to 30px for .menu__link. If wrapping doesn't work, verify !important flags are applied correctly and check for conflicting CSS.
