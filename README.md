# Teacher Learning App — Part A (Professional Development)

A mobile-first teacher professional development app: **Learn → Think →
Reflect → Understand → Apply → Improve**.

This is **Part A only** — the learning, reflection, and growth journey for
teachers. It intentionally does **not** duplicate Part B (the existing
Classroom Implementation / Evidence Portal). Part A links out to Part B via
an **"Apply in Classroom"** button; the two systems stay fully separate.

---

## 1. Architecture

```
UI (Home + pages/)
   ↓
Components (learning, reflection, progress, ui)
   ↓
Services (supabase_service, r2_service, ai_service, transcription_service)
   ↓
Supabase Postgres · Cloudflare R2 · AI provider · STT provider
```

- **Modules** (`modules/`) hold learning *content* only — sessions, the
  six-part framework, and assessment questions — with no database or UI
  logic, so new modules can be added by writing one content file and
  registering it in `module_registry.py`.
- **Services** are the only code that talks to external systems, and every
  service degrades to a safe **Demo Mode** if its credentials aren't
  configured — the app never crashes because a provider isn't wired up yet.
- **Components** render reusable pieces of UI (learning sessions, the voice
  reflection flow, progress/growth widgets) that the pages compose together.

---

## 2. Project Structure

```
teacher_learning_app/
├── app.py                          # Home dashboard
├── config.py                       # Central configuration + Demo Mode flags
├── pages/
│   ├── 2_Learning.py                # My Modules / Current Module / Assessments / Reflections
│   ├── 3_Growth.py                  # My Growth
│   └── 4_Profile.py                 # My Profile
├── components/
│   ├── learning.py                  # Learning session renderer
│   ├── reflection.py                # Voice reflection flow (record → transcript → edit → feedback)
│   ├── progress.py                  # Final assessment + completion + growth summary
│   └── ui.py                        # Shared styling & widgets
├── services/
│   ├── supabase_service.py          # Persistence (with in-memory Demo Mode fallback)
│   ├── r2_service.py                # Audio storage in Cloudflare R2
│   ├── ai_service.py                # AI extraction + pedagogical coaching
│   └── transcription_service.py     # Speech-to-text
├── modules/
│   ├── module_registry.py           # Catalogue of all 14 modules
│   └── module_1_lesson_planning.py  # Fully implemented Module 1 content
├── database/
│   └── schema.sql                   # Complete, executable Supabase schema
├── .streamlit/
│   └── secrets.toml.example
├── requirements.txt
└── README.md
```

---

## 3. Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Running Locally

```bash
streamlit run app.py
```

The app runs immediately in **Demo Mode** with no configuration at all.

---

## 5. Demo Mode

Demo Mode is not a separate build — it's the automatic fallback state of
every service when its credentials are missing:

| Service        | Without credentials...                                          |
|-----------------|------------------------------------------------------------------|
| Supabase        | Progress/reflections/assessments are kept in-memory for the session |
| Cloudflare R2   | Audio "uploads" are simulated; a realistic object path is generated but no bytes are stored |
| AI provider     | Returns a realistic, clearly-labeled demo extraction and demo coaching feedback |
| STT provider    | Returns a clearly-labeled demo transcript |

This means you (or anyone testing the app) can walk through the entire
teacher journey — modules, sessions, voice reflection, AI feedback, final
assessment, completion, growth — **before connecting any production
credentials.** A blue "🧪 Demo Mode" banner appears wherever it's relevant.

---

## 6. Production Setup

Copy the secrets template and fill in real values:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

### Supabase
1. Create a Supabase project.
2. Open the SQL Editor and run the full contents of `database/schema.sql`.
3. Set `SUPABASE_URL` and `SUPABASE_KEY` in `secrets.toml`.
   - Use a **service-role key**, since this is a trusted server-side
     Streamlit app (never a client-side one). Row Level Security is enabled
     on every table with no permissive policies, so only the service-role
     key can read/write — never use the `anon` key here.

### Cloudflare R2
1. Create an R2 bucket (e.g. `teacher-pd-audio`) — **separate from** any
   bucket/prefix Part B already uses.
2. Create an R2 API token (Access Key ID + Secret Access Key).
3. Set `R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
   `R2_BUCKET_NAME` in `secrets.toml`.
4. Part A audio is written under its own path prefix:
   `pd/module_{module_id}/{teacher_id}/{date}/{uuid}_{filename}` — this
   never touches Part B's evidence path structure.

### AI provider
Set `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL` to any OpenAI-compatible
chat-completions endpoint. The app calls `POST {AI_BASE_URL}/chat/completions`.

### Speech-to-Text provider
Set `STT_API_KEY`, `STT_BASE_URL`, `STT_MODEL` to any OpenAI-compatible
`/audio/transcriptions` endpoint (e.g. Whisper-compatible).

### Part B link
Set `PART_B_URL` to the existing Classroom Implementation / Evidence Portal
URL. The "Apply in Classroom" button simply opens this URL — Part A never
reads or writes Part B data directly.

---

## 7. Deployment

**Streamlit Community Cloud:**
1. Push this repository to GitHub (do **not** commit `secrets.toml`).
2. Create a new app on [share.streamlit.io](https://share.streamlit.io),
   pointing at `app.py`.
3. In the app's "Secrets" settings, paste the contents of your filled-in
   `secrets.toml`.

**Any other Streamlit-compatible host** (Render, Fly.io, a VM, etc.):
1. Install dependencies from `requirements.txt`.
2. Provide the same keys as environment variables (this app reads
   `st.secrets` first, then falls back to `os.environ`), or mount a
   `.streamlit/secrets.toml` file.
3. Run `streamlit run app.py --server.port <port> --server.address 0.0.0.0`.

---

## 8. Part A ↔ Part B — Future Integration

Part A (this app) and Part B (the existing Classroom Implementation /
Evidence Portal) are deliberately kept as two separate systems with two
separate database schemas:

- Part A owns: `teacher_pd_profiles`, `teacher_pd_progress`,
  `teacher_pd_reflections`, `teacher_pd_assessments`.
- Part B owns: `teacher_records` and its own evidence/implementation tables
  and R2 storage structure — **untouched by this project**.

The only connection point today is the **"Apply in Classroom"** link, which
opens `PART_B_URL` in a new context. A future integration could:

- Read teacher identity from Part B's `teacher_records` (read-only) to
  pre-fill the Part A profile, instead of the demo profile used today.
- Pass a `teacher_id` and/or `module_id` as a query parameter to Part B, so
  it can show "learning you've completed" context inside the classroom
  portal.
- Eventually surface a read-only summary of Part A reflections inside Part
  B (or vice versa), without merging the underlying data models.

None of this is required for the current MVP, and no such integration code
has been built yet — the architecture above is simply structured so it can
be added later without reshaping either system.

---

## 9. What This MVP Does Not Do (By Design)

- It does not rebuild any Part B functionality (lesson implementation,
  classroom evidence, student work, phonics evidence, teacher portfolio).
- It does not create a `teacher_submissions` table or any classroom
  evidence tracking.
- It does not implement Modules 2–14 — they appear as "Coming Soon" and the
  architecture is ready for them.
- It does not implement gamification (points, badges, leaderboards) by
  design — this is professional development, not a game.
