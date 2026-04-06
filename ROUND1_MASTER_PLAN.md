# OpenEnv Round 1 - 100% Execution + Handoff Plan

Owner today: Balaji  
Owner tomorrow: Yeshwanth  
Deadline: 8 Apr, 11:59 PM

---

## 1) What You Must Deliver (Non-negotiable)

Your submission is valid only if all of these are true:

1. Real-world environment (NOT game/toy)
2. Full OpenEnv interface
   - Typed Pydantic `Observation`, `Action`, `Reward`
   - `step(action) -> (observation, reward, done, info)`
   - `reset() -> observation`
   - `state() -> current_state`
   - `openenv.yaml`
3. Minimum 3 tasks (easy/medium/hard), each with deterministic grader and score in `[0.0, 1.0]`
4. Reward shaping (partial progress), not only binary terminal reward
5. `inference.py` in root using OpenAI client + required env vars
6. Deployable Hugging Face Space (containerized)
7. Working `Dockerfile`
8. `README.md` with all required sections
9. `openenv validate` passes

If any mandatory item is missing, you risk disqualification.

---

## 2) Best Domain Choice (Fast + High Score)

Pick one practical domain that is easy to model deterministically.

Recommended: **Email Triage Assistant**

Why this is strong:
- Real-world utility is obvious
- Easy to define measurable tasks
- Deterministic grading is simple
- Supports rich reward shaping

### Proposed task ladder

1. Easy: classify intent + priority for 1 short email
2. Medium: classify + draft correct response + route to team
3. Hard: handle multi-email inbox with constraints (SLA, conflict, urgency, wrong recipient risk)

---

## 3) Target Project Structure (Create Exactly This)

```text
.
├─ openenv.yaml
├─ inference.py
├─ Dockerfile
├─ requirements.txt
├─ README.md
├─ env/
│  ├─ __init__.py
│  ├─ models.py          # Pydantic models
│  ├─ tasks.py           # task definitions + hidden testcases
│  ├─ graders.py         # deterministic scoring 0..1
│  ├─ reward.py          # partial rewards + penalties
│  └─ email_env.py       # step/reset/state
├─ scripts/
│  ├─ run_local_eval.py
│  └─ precheck.sh
└─ tests/
   ├─ test_env_api.py
   ├─ test_graders.py
   └─ test_rewards.py
```

---

## 4) Environment Design Blueprint

## 4.1 Observation schema (typed)

Include fields like:
- `current_email`
- `inbox_summary`
- `available_actions`
- `step_count`
- `history`
- `task_goal`

## 4.2 Action schema (typed)

Include a constrained action enum + payload:
- `classify`
- `set_priority`
- `assign_team`
- `draft_reply`
- `mark_done`

## 4.3 Reward schema (typed)

Return normalized reward in `[0.0, 1.0]` each step with shaped signal:
- `+0.25` correct classification
- `+0.25` correct priority
- `+0.25` correct routing
- `+0.25` valid response quality
- penalty for invalid action / repeated loop / destructive action

Clamp final per-step reward to `[0.0, 1.0]`.

## 4.4 Episode boundary

`done=true` when:
- all required subtasks solved, OR
- max steps reached, OR
- fatal invalid behavior threshold crossed

---

## 5) Deterministic Graders (Critical)

Each task must have exact rubric and deterministic logic.

Use strict rule scoring:
- Boolean checks mapped to weighted points
- No random judge behavior
- Same trajectory => same score always

Example (Hard task):
- urgency handled correctly: 0.30
- routing/team assignment correct: 0.25
- reply policy-safe + complete: 0.25
- SLA respected in sequence: 0.20

Final score = weighted sum, clipped to `[0.0, 1.0]`.

---

## 6) `inference.py` Requirements (Must Follow Exactly)

Mandatory environment variables:
- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

Also accepted from sample:
- `IMAGE_NAME` (if using local docker image)

Rules:
1. File name must be exactly `inference.py` in root
2. Must use OpenAI client
3. Print logs exactly in format:
   - `[START] ...`
   - `[STEP] ...`
   - `[END] ...`
4. `reward` and `rewards` formatted to 2 decimals
5. `done`/`success` lowercase: `true` or `false`
6. `error` must be raw error text or `null`
7. Every task score in `[0,1]`
8. End-to-end runtime under 20 minutes on 2 vCPU / 8 GB RAM

---

## 7) `openenv.yaml` Must Include

At minimum ensure:
- benchmark/environment metadata
- task list (3+)
- entrypoint/module reference
- action/observation model mapping
- evaluator references
- tags/info needed by OpenEnv validator

Run `openenv validate` until clean.

---

## 8) Docker + HF Space Requirements

- Working `Dockerfile` in root (or `server/` if you intentionally use that layout)
- Build succeeds via `docker build`
- Space responds to reset endpoint / API contract
- Space tagged with `openenv`

Use slim image, pin package versions, avoid heavy dependencies.

---

## 9) README Checklist (Scoring + Compliance)

Must include:
1. Environment description + real-world motivation
2. Action space definition
3. Observation space definition
4. Reward design explanation
5. Task descriptions (easy/medium/hard)
6. Grader logic summary
7. Setup (local + docker + HF)
8. How to run inference
9. Baseline reproducible scores
10. Limitations + future improvements (short)

---

## 10) Today/Tomorrow Split (for Team Handoff)

## Day 1 (Balaji - Today)

Goal: Core environment and 2 tasks done.

1. Initialize repo structure
2. Implement typed models
3. Implement `reset`, `state`, `step` with clean transitions
4. Implement reward shaping function
5. Implement easy + medium tasks and graders
6. Create initial `README.md`
7. Commit and zip handoff

Definition of done today:
- environment runs locally
- at least 2 tasks fully functional
- tests for API basics pass

## Day 2 (Yeshwanth - Tomorrow)

Goal: Finalize hard task, inference, deployment, validation.

1. Implement hard task + grader
2. Create final `inference.py` with exact log format
3. Add/update `openenv.yaml`
4. Finalize Dockerfile
5. Run pre-validation script and fix issues
6. Deploy to HF Space
7. Record baseline scores in README
8. Final submission by team lead

Definition of done tomorrow:
- all 3 tasks validated
- `openenv validate` passes
- Docker builds
- HF endpoint healthy
- inference reproducible

---

## 11) Handoff Protocol (ZIP-friendly)

Before zipping at end of Day 1:

1. Update this file status section (below)
2. Ensure all code pushed/committed locally
3. Include `.env.example` with required variable names only
4. Add `HANDOFF_NOTES.md` summarizing:
   - what works
   - what is pending
   - known bugs
   - exact commands to run
5. Zip full project and send

---

## 12) Commands to Run Locally

```bash
# create venv
python -m venv .venv

# activate (windows powershell)
.\.venv\Scripts\Activate.ps1

# install deps
pip install -r requirements.txt

# run tests (if using pytest)
pytest -q

# validate openenv
openenv validate

# docker build
docker build .
```

---

## 13) Required `.env.example`

```env
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
HF_TOKEN=your_token_here
IMAGE_NAME=optional_local_image_name
```

---

## 14) Risk List (Avoid Disqualification)

1. Non-deterministic graders -> FAIL risk
2. Missing `inference.py` in root -> FAIL risk
3. Wrong stdout format -> scoring breaks
4. Score outside `[0,1]` -> invalid
5. Dockerfile broken -> auto fail
6. openenv spec mismatch -> auto fail
7. HF space not responding -> auto fail

---

## 15) Status Tracker (Update This Before Handoff)

Use this section as live checklist.

- [x] Project structure created
- [x] Typed models implemented
- [x] `reset()` implemented
- [x] `state()` implemented
- [x] `step()` implemented
- [x] Reward shaping implemented
- [x] Easy task + grader
- [x] Medium task + grader
- [x] Hard task + grader
- [x] `inference.py` root-ready
- [x] `openenv.yaml` valid
- [x] Docker build passes
- [ ] HF Space deployed + healthy
- [x] README complete with baseline scores
- [ ] Final precheck script passes

---

## 16) Minimal Daily Sync Message Template

Use this in chat when handing off:

```text
Update:
- Completed: <items>
- In progress: <items>
- Blockers: <items>
- Next for you: <items>

Run this first:
1) pip install -r requirements.txt
2) openenv validate
3) python inference.py
4) docker build .
```

---

This document is your single source of truth for team execution.
If you follow it exactly, you cover both compliance and scoring quality.
