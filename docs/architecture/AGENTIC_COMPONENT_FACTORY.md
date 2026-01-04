# 🏭 Agentic Component Factory (Experimental)
*AI-Driven "Liquid Glass" Generator Specification*

**Status**: EXPERIMENTAL
**Owner**: Solution Architect (SA-1)
**Issue**: #55

---

## 1. The Concept
Instead of manually coding every A2UI component, we will build a **Factory Workflow** that uses an LLM to generate them on-demand.
This ensures the UI remains "Liquid" and can adapt to new Plugin capabilities instantly.

## 2. The Workflow
The Factory operates in 3 stages:

### Stage 1: The Blueprint (Input)
*   **Input**: A human-readable description (e.g., "A dark-mode Kanban board with drag-and-drop cards for Deal Flow").
*   **Context**: The `A2UI_SCHEMA.md` and `Custom Component Registry`.

### Stage 2: The Fabrication (Generation)
The Agent (Factory Worker) generates three files:
1.  **Schema Definition**: The JSON structure extending `AppShell`.
2.  **Frontend Wrapper**: A React/Vue component that maps the JSON to UI.
3.  **Backend Mock**: A Python Plugin capability that serves sample data for this component.

### Stage 3: The Assembly (Integration)
*   **Auto-Register**: The new component is added to `component_registry.json`.
*   **Hot-Reload**: The Frontend picks up the new mapping.

## 3. The Prompt Strategy
We will use a specialized "System Prompt" for the Factory Agent.

**System Prompt Template**:
```text
You are the A2UI CONFIGURATOR.
Your goal is to convert a user request into a valid A2UI JSON Component.

RULES:
1. Use ONLY the types defined in A2UI_SCHEMA.md (card, pane, app_shell).
2. For advanced features, use 'custom:type' from the Registry.
3. Return ONLY valid JSON.

EXAMPLE INPUT: "A list of emails"
EXAMPLE OUTPUT:
{
  "type": "pane",
  "cards": [
     { "type": "card", "title": "Email 1", "summary": "..." }
  ]
}
```

## 4. Implementation Plan
1.  Create `tools/component_factory.py`: A CLI tool to run the generation.
2.  Create `templates/`: Jinja2 templates for the code generation.
3.  **MVP Goal**: Generate a "Deals Funnel" component (Issue #40) using this Factory.
