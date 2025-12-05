# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This repository primarily contains the Claude Agent SDK and related `speckit` commands.

- **Running `speckit` commands**: The `speckit` commands are located in `.claude/commands/`. You can execute them using the `/speckit.<command-name>` syntax. For example, to run the `analyze` command, you would use `/speckit.analyze`.

## High-level Code Architecture and Structure

This repository is structured around the Claude Agent SDK and a set of PowerShell scripts for managing the specification and planning process.

- **`.claude/commands/`**: This directory contains markdown files that define custom slash commands for `speckit` functionality. Each `.md` file represents a distinct command (e.g., `speckit.analyze.md`, `speckit.plan.md`). These commands are used to automate various stages of the software development lifecycle within Claude Code.

- **`.specify/memory/`**: This directory holds `constitution.md`, which outlines the core principles and guidelines for the project.

- **`.specify/scripts/powershell/`**: This directory contains PowerShell scripts that support the `speckit` commands. These scripts handle tasks like checking prerequisites (`check-prerequisites.ps1`), creating new features (`create-new-feature.ps1`), and updating agent context (`update-agent-context.ps1`).

- **`.specify/templates/`**: This directory stores various markdown templates used by the `speckit` commands, such as `spec-template.md`, `plan-template.md`, and `tasks-template.md`. These templates provide a consistent structure for different project artifacts.