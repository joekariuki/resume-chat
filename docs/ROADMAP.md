# ResumeChat — Phase 2 Roadmap (Post‑MVP)

This document outlines the next-phase plan after the MVP described in `PRD.md`. The focus is on shipping an embeddable chat widget that can be dropped into any website with a simple script (and optionally a React component), plus hardening the API, notifications, and basic observability.


## Vision

Make ResumeChat a copy‑paste chat bubble that answers questions about a resume (or any single source document) and escalates to the owner when uncertain — easy to embed, reliable, and safe by default.


## Primary Objectives

- Ship a no‑framework script embed that injects a floating chat bubble and opens a panel rendered in an iframe.
- Reuse existing Next.js chat components inside a dedicated widget route.
- Enrich API with per‑site metadata (`site_key`, `origin`) and basic logging for unanswered questions and leads.
- Provide minimal theming, accessibility, and performance guarantees.


## Deliverables

- Embeddable widget (Script Embed)
  - `web/public/embed.js` that injects a bubble + iframe.
  - Iframe loads `web/app/widget/page.tsx` (compact chat UI).
  - Config via script `data-*` attributes and/or query params.
- React wrapper (optional)
  - Publish a tiny `@resumechat/widget-react` package exposing `<ResumeChatBubble />` that wraps the script embed.
- API enhancements
  - Accept `site_key` and `origin` (headers or query).
  - Include these in notifications/logs; basic rate limiting (per `site_key`).
  - CORS safe defaults for MVP (wildcard) with path to tighten later.
- Notifications
  - Enrich messages with `origin`, `page_title` if provided by the widget.
  - Maintain existing channels: WhatsApp → SMS → Email for `QUESTION_UNANSWERED`, Email + WhatsApp for `LEAD_CAPTURED`.
- Storage & analytics (lightweight)
  - Store per‑message metadata: timestamp, origin, site_key, question, handled flag, confidence.
  - Store leads with origin and site_key.
- Theming & branding
  - Light/dark/auto and accent color via CSS variables or query params.
  - Optional logo/avatar overrides.
- Reliability & performance
  - Lazy load iframe on first open.
  - Keep `embed.js` <10KB gz if possible; no heavy deps.
  - Graceful fallback if API is unreachable.
- Security & privacy
  - No third‑party cookies; use iframe `localStorage` only.
  - Input length limits and basic abuse protection.
  - Content Security Policy guidance for host sites.
- Documentation
  - Copy‑paste HTML snippet.
  - React usage snippet.
  - Configuration reference and troubleshooting.


## Phased Milestones

- M1 — Widget MVP (1–2 days)
  - Create `web/app/widget/page.tsx` that composes `ChatPanel`, `MessageList`, `ChatInput`, etc.
  - Add `public/embed.js` to inject bubble + iframe and pass config.
  - Iframe calls existing API (`/chat`, `/contact`) via `NEXT_PUBLIC_API_URL` or `api` query param.
  - Basic open/close UX, responsive layout, ESC to close.

- M2 — API Enrichment (0.5–1 day)
  - Add support for `site_key` and `origin` headers/params to `/chat` and `/contact`.
  - Log interactions (in-memory or SQLite) with metadata.
  - Include metadata in notifications.

- M3 — Theming, A11y, Docs (0.5–1 day)
  - Theme: light/dark/auto + accent color.
  - ARIA attributes and keyboard navigation polish.
  - Add `README` section and a dedicated `docs/embed.md` with snippets.

- M4 — Packaging & DX (1 day, optional)
  - Publish npm package `@resumechat/widget-react` (wrapper around script embed).
  - Add simple playground page for manual testing.

- M5 — Multi‑tenant Alpha (2–4 days, optional/next)
  - `site_key` issuance and lookup (map to resume content + notify settings).
  - Dynamic CORS and per‑site rate limits.
  - Admin script to generate keys and rotate credentials.


## Technical Design Notes

- Web (Next.js)
  - New route: `web/app/widget/page.tsx` renders the chat UI optimized for iframe (compact header, scrollable message list, fixed input).
  - Use existing components in `web/components/chat/` like `ChatPanel`, `MessageList`, `MessageItem`, `ChatInput`, `ChatHeader`.
  - Accept config via query string (e.g., `?api=...&site_key=...&theme=dark&title=...`).

- Embed script (`web/public/embed.js`)
  - On load, create a bubble `<button>` and a hidden `<iframe>` container.
  - When clicked, lazy‑set iframe `src` to `/widget` with serialized config.
  - `postMessage` can pass dynamic info (page title/URL) if needed.
  - Minimal CSS injected for bubble; inner UI styling isolated in iframe.

- API (FastAPI)
  - `/chat` and `/contact` accept `X-ResumeChat-SiteKey`, `X-Host-Origin`, or query params.
  - Store message and lead logs with metadata and confidence score.
  - Continue using `BackgroundTasks` for notifications.
  - CORS: wildcard for MVP; plan for origin allowlist per `site_key` later.

- Data model additions (SQLite option)
  - `sites(site_key, owner_email, created_at, ...)` [optional for multi‑tenant].
  - `conversations(id, site_key, origin, started_at, ...)`.
  - `messages(id, conversation_id, role, content, handled, confidence, created_at)`.
  - `leads(id, site_key, origin, name, email, phone, created_at)`.

- Config schema (embed)
  - `api`: string (API base URL; default `NEXT_PUBLIC_API_URL`).
  - `site_key`: string (optional for single‑owner MVP; required for multi‑tenant).
  - `title`: string (UI header title).
  - `theme`: `light` | `dark` | `auto`.
  - `position`: `bottom-right` | `bottom-left`.
  - `accent`: string (CSS color or token; optional).

- Observability
  - Simple server logs for messages and leads.
  - Optional `/metrics` or log export later.


## Acceptance Criteria

- A public demo page shows the widget opening and functioning against the existing API.
- A copy‑paste HTML snippet embeds the widget on any external site.
- API logs contain `origin` and `site_key` for messages and leads.
- Notifications include referrer origin information.
- Theming works (light/dark/auto) and basic accessibility checks pass.


## Security & Privacy Checklist

- No third‑party cookies; store only in iframe storage.
- Sanitize and bound user inputs (max length, rate limits per IP/site_key).
- Avoid leaking host page DOM/JS to the iframe and vice‑versa.
- Document CSP requirements (allow `your-vercel-web-app.vercel.app` for script and iframe domains).


## Risks and Mitigations

- CSS/JS conflicts on host pages → Use iframe isolation and minimal outer DOM.
- CSP blocks script or iframe → Document and provide troubleshooting.
- API latency from third‑party embeds → Add retries + timeouts; show skeleton/loading states.
- Abuse/spam → Add rate limiting, captcha toggle (later), simple blocklist.


## Documentation To Produce

- `docs/embed.md` or a new section in `web/README.md` with:
  - HTML snippet usage
  - React usage
  - Config options
  - CSP and CORS notes
  - Troubleshooting (API URL, mixed content, CORS, CSP)


## Backlog Ideas (Nice‑to‑Have)

- Inline file support: upload CV variants or portfolio PDFs by site.
- Brand customization: custom avatar, welcome message per site.
- Pre‑chat lead capture mode or delayed contact prompt.
- Analytics dashboard (charts for sessions, questions, unanswered rate).
- Export logs to CSV or webhook destinations.
- Rate limit tuning and abuse detection heuristics.
- Fine‑tuned system prompt per site.


## Next Steps

- Decide scope for v1 of the embed:
  - Single‑owner MVP vs. multi‑tenant alpha.
  - Theming options to include now.
- Implement M1 (Widget MVP) and wire to current API.
- Validate with 2–3 real external sites; iterate based on feedback.
