# Server-Side Changes Required for Consistent Client Protocol

This document lists server changes needed so client/server interaction stays deterministic and fully aligned with the current client protocol.

## 1) Coordination wait route collision (must fix)

Current issue in `views.py`:
- `if block and block.startswith("coordination"):` is evaluated before `if offer == "coordination":`.
- A wait request with `round=coordination<round>_1` and `offer=coordination` is incorrectly treated as a write operation (trial choice), not a wait read.

### Required fix
Handle coordination wait-read request before the generic coordination write branch.

Recommended protocol:
- Request (client -> server):
  - `id=<participant_id>`
  - `round=coordination<round>_1`
  - `offer=coordination`
- Response (server -> client):
  - `A` or `B` when partner first-trial decision is available
  - empty string while waiting

### Suggested code change shape
Move the `if offer == "coordination":` block above the `if block and block.startswith("coordination"):` block, and keep write logic restricted to offers `A`/`B`.

---

## 2) Optional: make market tie resolution explicit in WaitResults payload

Current `wait/results` response sends:
- `market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>`

If both enter and quiz scores tie, client currently cannot infer who won without making an extra random decision.

### Recommended improvement
Extend market section with explicit self payoff or tie winner:
- Option A: `market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>,<payoff_self>`
- Option B: `market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>,<winner>` where `<winner>` is `self`/`other`

This removes any need for random tie resolution on the client during response processing.

---

## 3) Keep response formats stable

Please keep these response formats stable because client parsing now assumes them directly:
- Login success payload: `<token1>|<token2>|<coord_roles>`
- Wait groups payload: `<id1>_<id2>_...!<groups1>~<groups2>~...`
- Wait results payload:
  - `coordination:<round>,<self1>,<other1>,<self2>,<other2>|market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>|trust:<round>,<sentA>,<sentB>`
