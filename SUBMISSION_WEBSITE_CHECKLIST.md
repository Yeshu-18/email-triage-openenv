# Round 1 Website Double-Check Guide (Balaji + Yeshwanth)

This file is a strict operator checklist for final validation and website submission.

## 1) Goal

Pass all Round 1 gates in one pass:
- Environment deploys and responds
- OpenEnv validation passes
- Docker build passes
- Baseline inference runs with strict logs
- 3 tasks with deterministic graders and scores in [0,1]

## 2) Current Completion Snapshot

Already completed locally:
- Real-world environment implemented (Email Triage)
- step/reset/state API implemented
- Typed models implemented
- 3 tasks (easy/medium/hard) implemented
- Deterministic graders implemented
- Reward shaping implemented
- inference.py implemented in root
- openenv validate passed locally
- docker build passed locally
- tests passed locally

Pending final external checks:
- Hugging Face Space live deploy
- Space endpoint check: POST /reset returns 200
- Website submission action by team lead

## 3) Team Execution Split

Balaji (today):
- Ensure latest code is zipped and shared
- Share this checklist and handoff files

Yeshwanth (tomorrow):
- Deploy to HF Space
- Run precheck scripts
- Re-run inference
- Submit on website from team lead account

## 4) Mandatory Environment Variables

Set these before running inference:
- API_BASE_URL
- MODEL_NAME
- HF_TOKEN
- IMAGE_NAME (optional)

## 5) Local Re-Validation (Windows PowerShell)

From repository root:
1. python -m pip install -r requirements.txt
2. python -m pytest -q
3. python inference.py
4. openenv validate
5. docker build .

Expected outcomes:
- Tests should pass
- Inference should print [START], [STEP], [END] lines for all tasks
- openenv validate should return ready/ok
- Docker build should succeed

## 6) Strict Inference Log Format Check

Your stdout must contain only these line types per episode:
- [START] task=... env=... model=...
- [STEP] step=... action=... reward=... done=... error=...
- [END] success=... steps=... score=... rewards=...

Rules to verify:
- reward has 2 decimals
- done/success are lowercase true or false
- score is clamped to [0,1]
- each task finishes with [END]

## 7) Hugging Face Space Deployment Checklist

1. Create or open target HF Space repository
2. Upload/push full repo contents
3. Confirm Docker runtime is enabled
4. Confirm container starts without crash
5. Confirm endpoints are reachable:
   - GET /
   - GET /health
   - POST /reset
   - POST /step
   - GET /state

Manual endpoint test example for reset body:
- { "task_id": "email_easy" }

## 8) Pre-Submission Scripts

For Linux/macOS shell:
- scripts/precheck.sh <SPACE_URL>

For Windows PowerShell:
- scripts/precheck.ps1 -SpaceUrl <SPACE_URL>

Both scripts check:
- Space reset endpoint (if URL provided)
- Docker build
- openenv validate

## 9) Website Submission Double-Check

Before clicking submit:
- inference.py exists in repo root
- openenv.yaml exists and is valid
- Dockerfile exists and builds
- 3 tasks are discoverable and graded
- README includes motivation, spaces, setup, baseline scores
- Team lead account is the one submitting

## 10) Fast Failure Recovery

If Space reset check fails:
- verify Space is running (not building)
- verify URL is correct
- verify POST /reset accepts JSON body
- verify app listens on expected port and starts uvicorn successfully

If openenv validate fails:
- run it locally and fix the exact missing file/entry
- ensure pyproject.toml, uv.lock, server entrypoint exist

If inference fails:
- ensure env vars are set
- rerun python inference.py
- verify logs still follow exact required line format

## 11) Final Submit Sequence (Do Not Change Order)

1. Run tests
2. Run inference
3. Run openenv validate
4. Run docker build
5. Run precheck script with Space URL
6. Submit on website

## 12) Evidence to Keep (for confidence)

Save screenshots or terminal logs for:
- pytest passed
- openenv validate passed
- docker build success
- inference output with three tasks
- Space reset returning HTTP 200

This file is your final execution checklist for a clean Round 1 submission.
