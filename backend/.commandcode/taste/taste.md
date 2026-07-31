# Taste

## Workflow & communication
- Wants the assistant to explain the folder structure and architecture *before* generating code. Confidence: 0.9
- Prefers scaffolding projects with starter files only, explicitly deferring business logic to later stages ("create starter files only", "do not implement business logic yet"). Confidence: 0.9

## Architecture & code quality
- Prefers clean, layered architecture for backend applications (clear separation of API/presentation, core/config, database, models, schemas, services, middleware). Confidence: 0.9
- Wants production-ready code even in scaffolds: pinned dependencies, env-driven config, tests, README, and a runnable/verified result. Confidence: 0.9
