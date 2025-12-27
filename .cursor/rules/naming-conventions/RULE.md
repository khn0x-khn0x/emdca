---
description: "Naming Conventions — Concepts over Layers. No generic filenames."
globs: ["**/*.py"]
alwaysApply: false
---

# Naming Conventions

## The Principle
File names must describe the **Business Concept** or **Specific Role** they contain, not a generic technical pattern. Generic names create "Junk Drawers" where unrelated logic accumulates. Specific names create **Context Boundaries**.

---

## ❌ Anti-Pattern: Layer Naming

Naming files after the "Layer" or "Pattern" obscures the content.

```text
domain/
  └── order/
      ├── model.py    # ❌ Generic. Every file is a model?
      ├── logic.py    # ❌ Generic. What kind of logic?
      ├── utils.py    # ❌ The Junk Drawer.
      ├── helpers.py  # ❌ The other Junk Drawer.
      └── intent.py   # ❌ Generic Pattern Name.
```

---

## ✅ Pattern: Concept Naming

Name files after the **Thing** or the **Process**.

```text
domain/
  └── order/
      ├── order.py         # ✅ The Aggregate Root
      ├── fulfillment.py   # ✅ Specific Workflow
      ├── pricing.py       # ✅ Specific Logic
      └── contract.py      # ✅ Data Contracts (Intents/Results)
```

---

## Allowed Exceptions (Boundary Files)

Some files define the **Boundary itself**, so the technical name is the concept.

| Filename | Role | Allowed? |
| :--- | :--- | :--- |
| `api.py` | Foreign Reality (API Contract) | ✅ |
| `db.py` | Foreign Reality (DB Schema) | ✅ |
| `vendor.py` | Foreign Reality (3rd Party) | ✅ |
| `config.py` | Environment Schema | ✅ |
| `main.py` | Composition Root | ✅ |
| `conftest.py` | Test Fixtures | ✅ |
| `__init__.py` | Package Marker | ✅ |

---

## Constraints

| Required | Forbidden |
|----------|-----------|
| **`domain/context/concept.py`** | `domain/context/model.py` |
| **`domain/context/workflow.py`** | `domain/context/process.py` (Too vague) |
| **`domain/context/contract.py`** | `domain/context/intent.py` |
| **`service/specific_service.py`** | `service/service.py` |
| **`shared/money.py`** | `shared/utils.py` |
| **Rename `helpers.py` to `[concept].py`** | `helpers.py` |
