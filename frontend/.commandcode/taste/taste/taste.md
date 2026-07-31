# Taste
- Prefers a clean, feature-based folder structure: components grouped by concern (common/landing/dashboard/forms/ui), a separate layouts/ folder, one folder per route under pages/, plus services/, hooks/, utils/, constants/, context/, routes/, styles/, animations/. Confidence: 0.9
- Prefers starter/scaffold files only — no business logic, no backend, no unnecessary files; wants minimal clean architecture over premature implementation. Confidence: 0.85
- Prefers a modern, dark, minimal SaaS UI aesthetic similar to Linear, Vercel, Stripe, and Notion. Confidence: 0.8
- Prefers a Vite + React + Tailwind CSS + React Router + Axios + Framer Motion + Lucide React frontend stack. Confidence: 0.8
- Prefers reusable components that compose from the shared design system — built on existing primitives (ui/ components, cn utility) and driven by centralized constants (e.g., NAV_LINKS) rather than hard-coded one-off markup. Confidence: 0.8
- Wants the folder structure and architecture explained before code is generated, including where each file belongs. Confidence: 0.95
- Prefers to build the landing page incrementally, one section at a time — each request delivers a single reusable section component (Navbar, then Hero, etc.) with precise specs, wired into the page rather than written as one giant file. Confidence: 0.75
- Wants complete, ready-to-use React code output for every request (explicitly asks for "Output complete React code") — full components, not partial snippets or stubs. Confidence: 0.8
- Wants premium visual depth in landing sections: animated gradient-blur background blobs, scroll-triggered stat counters, and a floating mock-UI/illustration placeholder with motion effects. Confidence: 0.8
