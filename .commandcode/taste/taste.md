# Taste
See [taste/taste.md](taste/taste.md)

- When a bug persists after a previous fix, expects the engineer to treat prior work as suspect and re-verify the live runtime behavior (inspect the actual network request, the real browser DOM, localStorage, and the on-disk uploads) before concluding — a "save succeeds" UI message is not proof the data was sent; the root cause can hide in infrastructure glue (e.g. the axios client forcing `Content-Type: application/json` on FormData so FastAPI silently drops the file field). Confidence: 0.9
- Prefers runtime/browser-level verification of bug fixes over static code reading alone: use headless-browser automation against the running app to reproduce the exact reported flow (upload → save → check navbar/sidebar/profile) and confirm the fix, including persistence after refresh and logout/login. Confidence: 0.8
