---
title: Email Triage OpenEnv
emoji: 📚
colorFrom: red
colorTo: red
sdk: docker
pinned: false
---

# Email Triage OpenEnv (Round 1)

A real-world OpenEnv environment for training/evaluating AI agents on customer email triage operations.

## Why this environment

Teams handling support inboxes need consistent triage for urgency, ownership, and response quality. This environment simulates that exact workflow with deterministic scoring and progressive task complexity.

## Real-world task coverage

This environment models a realistic process:
- classify incoming request intent
- set urgency/priority
- assign to the correct internal team
- draft a policy-safe response
- complete inbox handling while respecting urgency ordering

## API contract

Implemented OpenEnv-style API:
- `reset(task_id=None)` -> initial observation
- `step(action)` -> observation, reward, done, info
- `state()` -> current state snapshot

Server endpoints:
- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /tasks`
- `GET /health`

## Typed models

Pydantic typed models are implemented in `env/models.py`:
- `EmailTriageAction`
- `EmailTriageObservation`
- `EmailTriageReward`
- `EmailTriageState`
- `StepResult`

## Action space

Allowed actions:
- `classify`
- `set_priority`
- `assign_team`
- `draft_reply`
- `mark_done`

Action payload supports fields:
- `email_id`
- `classification`
- `priority`
- `assigned_team`
- `draft_reply`

## Observation space

Observation fields include:
- `task_id`, `task_goal`
- `step_count`, `max_steps`
- `inbox_remaining`
- `current_email`
- `available_actions`
- `history`
- `last_action_error`

## Reward design (0.0 to 1.0)

Partial progress shaping:
- +0.20 classification correct
- +0.20 priority correct
- +0.20 team routing correct
- +0.25 reply quality (keywords/rubric)
- +0.10 mark email complete
- -0.30 invalid action
- -0.10 repeated no-op action

Final task score from deterministic grader is in `[0, 1]`.

## Task set (3 tasks)

1. `email_easy` (easy)
- single billing email, full triage completion

2. `email_medium` (medium)
- dual inbox with technical + sales intents

3. `email_hard` (hard)
- outage + compliance + low-priority request with outage-first ordering pressure

## Deterministic graders

Grader logic in `env/graders.py`:
- structure score: classification + priority + team correctness
- reply score: required keyword coverage
- ordering score: outage-first requirement for hard task
- weighted final score clipped to `[0,1]`

## Inference script requirements compliance

Root file: `inference.py`

Mandatory env vars:
- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

The script:
- uses OpenAI client
- emits strict stdout logs only in these forms:
  - `[START] task=... env=... model=...`
  - `[STEP] step=... action=... reward=... done=... error=...`
  - `[END] success=... steps=... score=... rewards=...`
- formats reward values to 2 decimals
- ensures task scores are normalized to `[0,1]`

## Setup (local)

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## Run tests

```bash
pytest -q
```

## Run inference

```bash
python inference.py
```

## Run API server

```bash
uvicorn env.app:app --host 0.0.0.0 --port 7860
```

## Docker

```bash
docker build -t email-triage-openenv .
docker run --rm -p 7860:7860 email-triage-openenv
```

## OpenEnv validation

```bash
openenv validate
```

## Final submission runbook (single pass)

Run these checks in this exact order before website submission:

```bash
# 1) tests
pytest -q

# 2) baseline logs for all tasks
python inference.py

# 3) OpenEnv contract
openenv validate

# 4) container build
docker build .

# 5) live Space health and contract checks
bash scripts/precheck.sh https://<your-space-url>
```

Windows PowerShell equivalent for step 5:

```powershell
./scripts/precheck.ps1 -SpaceUrl https://<your-space-url>
```

Expected result:
- tests pass
- inference prints `[START]`, `[STEP]`, `[END]` lines for all three tasks
- `openenv validate` passes
- docker build succeeds
- Space `POST /reset` returns HTTP 200

Common failures and quick fixes:
- missing env vars for inference: set `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`
- Space reset endpoint failing: verify Space is fully running and URL is correct
- Docker build slow/large: ensure `.dockerignore` is present

## Hugging Face Space deployment

Recommended flow:
1. Create a Space repo
2. Push this project with Dockerfile
3. Ensure port 7860 and API endpoints are reachable
4. Tag repo with `openenv`

## Baseline reproducibility

Use `python inference.py` for baseline trajectory logs and scores.

Example expected score profile with rule-consistent policy:
- `email_easy`: near 1.00
- `email_medium`: near 1.00
- `email_hard`: high score if outage is completed first

## Resource fit

Designed for constraints:
- runtime under 20 minutes
- 2 vCPU, 8GB memory

## Files to review before submission

- `openenv.yaml`
- `inference.py`
- `Dockerfile`
- `README.md`
- `env/` package
- `scripts/precheck.sh`

## Team handoff

If transferring by zip, update:
- `ROUND1_MASTER_PLAN.md` status section
- `HANDOFF_NOTES.md`
