# Taste
- Wants the assistant to explain the folder structure and architecture *before* generating code. Confidence: 0.9
- Prefers scaffolding projects with starter files only, explicitly deferring business logic to later stages ("create starter files only", "do not implement business logic yet"). Confidence: 0.9
- Prefers clean, layered architecture for backend applications (clear separation of API/presentation, core/config, database, models, schemas, services, middleware). Confidence: 0.9
- Wants production-ready code even in scaffolds: pinned dependencies, env-driven config, tests, README, and a runnable/verified result. Confidence: 0.9
- Prefers database schemas built on normalized relational tables with UUID primary keys, `created_at`/`updated_at` timestamps, and soft-delete support (nullable `deleted_at`). Confidence: 0.8
- Prefers each schema design task to include per-table explanations alongside the generated models. Confidence: 0.7
- Frames build requests as role assignments ("You are a Senior Backend Engineer", "You are a Senior Database Architect") and expects the assistant to respond in that expert capacity. Confidence: 0.7
- Prefers task prompts with explicit, enumerated requirement checklists (endpoints, password hashing, JWT validation, Pydantic schemas, error handling, Swagger docs, etc.) that should each be delivered. Confidence: 0.7
