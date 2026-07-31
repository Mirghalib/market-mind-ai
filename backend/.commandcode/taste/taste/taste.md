# Taste
- Wants the assistant to explain the folder structure and architecture *before* generating code. Confidence: 0.95
- Prefers scaffolding projects with starter files only, explicitly deferring business logic to later stages ("create starter files only", "do not implement business logic yet"). Confidence: 0.95
- Prefers clean, layered architecture for backend applications (clear separation of API/presentation, core/config, database, models, schemas, services, middleware). Confidence: 0.9
- Wants production-ready code even in scaffolds: pinned dependencies, env-driven config, tests, README, and a runnable/verified result. Confidence: 0.9
- Explicitly requires deliverables to be reusable and easy to extend (lists these as hard requirements, with documented extension points like overridable templates/hooks). Confidence: 0.95
- Wants code to be well documented — module/class docstrings covering usage examples, input/output contracts, and how to extend. Confidence: 0.9
- Prefers pure, self-contained components with no side effects where the task allows (e.g., prompt building explicitly must make no API calls, keeping it decoupled from LLM provider I/O). Confidence: 0.7
