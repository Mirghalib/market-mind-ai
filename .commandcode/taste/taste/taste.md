# Taste
- Prefers comprehensive, phased, systematic end-to-end audits of the entire project before making any changes — inspect everything, report every issue, then fix. Confidence: 0.8
- Strongly prefers preserving existing architecture and structure: do NOT regenerate the project, do NOT rewrite architecture, do NOT remove working code — only fix broken code. Confidence: 0.9
- Wants every fix explained, then the project re-run/verified after each fix, continuing automatically until the whole app works end-to-end (backend starts, frontend starts, frontend talks to backend, DB/AI/auth/RBAC/uploads/export/history/admin all work, no console/network/runtime errors, no 500s). Confidence: 0.8
- Expects full-stack coverage in a single engagement — frontend, backend, database, DevOps, security, QA, and product/UX all reviewed together (multi-role expert framing). Confidence: 0.7
- Prefers config-driven graceful degradation for external dependencies (e.g. fall back to deterministic mock when an AI provider is rate-limited) so demos never hard-fail. Confidence: 0.6
- Wants a professional final report with a health score per area (project, backend, frontend, security, database, performance, UI/UX, AI pipeline), a list of bugs found, fixes applied, remaining improvements, and a verified-features checklist with PASS/FAIL status. Confidence: 0.8
