# Experiment Frame Guide for Server-Side Implementation

This document describes the experiment frame by frame with emphasis on what the server-side code must provide, store, or respond with. It is intentionally complementary to [SERVER_DATA_FORMATS.md](SERVER_DATA_FORMATS.md) and focuses on control flow, frame purpose, and backend responsibilities rather than exact payload schemas.

## High-Level Flow

The experiment is launched from [experiment.pyw](../experiment.pyw) and follows this order:

1. Login
2. Intro screens
3. Groups selection
4. Coordination game
5. Market entry task
6. Trust game
7. Fire game and tutorials
8. Product choice task, questionnaires, demographics, comments
9. Wait for final results
10. Ending screen

The backend is involved mainly in:
- participant login and session setup
- group matching and role assignment
- multi-player round resolution
- final result aggregation

## Frame-By-Frame Guide

### 1. `Login`

**File:** [Stuff/login.py](login.py)

**Purpose:**
Authenticate the participant and provide session-level data needed before the main experiment starts.

**Server responsibility:**
- Return the selected product codes for payoff-relevant product realization.
- Return coordination role assignments for all coordination blocks.
- The client stores these values in `root.status` and uses them later without further backend lookup.

**Client-side state produced:**
- `root.status["selected_products"]`
- `root.status["co_roles"]`

**Backend notes:**
- This is the first place where the backend must provide experiment-specific identity data.
- The response must remain consistent because later frames assume the stored status is already present.

### 2. `Initial` and `Intro`

**Files:** [Stuff/intros.py](intros.py)

**Purpose:**
Introductory text only.

**Server responsibility:**
None.

**Backend notes:**
- No data exchange.
- These screens are only instructional and do not affect server state.

### 3. `GamesIntro`

**File:** [Stuff/games.py](games.py)

**Purpose:**
Introduces the first decision tasks.

**Server responsibility:**
None directly.

**Backend notes:**
- This frame is a bridge into the first block of tasks.
- It does not send or receive data itself.

### 4. `InstructionsGroups` and `Groups`

**File:** [Stuff/groups.py](groups.py)

**Purpose:**
Participant selects 5 preferred words/groups.

**Server responsibility:**
- Receive the selected groups from the client.
- Store the selection for later use, especially for trust-game partner information.

**Client-side state produced:**
- The selected groups are written locally.
- The server should mirror the selection if the backend uses group matching or partner information.

**Backend notes:**
- This selection is used later by the trust game.
- The server-side implementation must preserve the chosen words in a stable structure because the trust game expects them when the partner-group block begins.

### 5. `IntroCoordination` and `InstructionsCoordination`

**File:** [Stuff/coordination.py](coordination.py)

**Purpose:**
Instruction screens for the coordination task.

**Server responsibility:**
None directly.

**Backend notes:**
- The actual coordination role assignment for each block is already carried in the login response and stored in `root.status["co_roles"]`.
- The server should not rely on the client to invent roles locally.

### 6. `CoordinationGame`

**File:** [Stuff/coordination.py](coordination.py)

**Purpose:**
Participant chooses A or B in a specific coordination round.

**Server responsibility:**
- Accept the round decision for the current block/trial.
- Use the role mapping from login (`root.status["co_roles"]`) when resolving the outcome.
- Store the decision and outcome so the wait/result frames can retrieve them later.

**Client-side state produced:**
- `root.status["co_decisions"]`
- `root.status["co_results"]`

**Backend notes:**
- Prediction is not sent to the server; it is kept locally only.
- The server side must treat the round identifier as the source of truth for which block/trial is being processed.
- The partner decision is resolved later through the wait/resolution step.

### 7. `WaitCoordination`

**File:** [Stuff/coordination.py](coordination.py)

**Purpose:**
Wait for the partner decision and finalize the coordination outcome for the current round.

**Server responsibility:**
- Return the partner's decision for the waiting round.
- The client then computes payoffs and stores the round result locally.

**Backend notes:**
- This frame is the first clear example of a server-mediated interaction step.
- The backend should provide the partner's A/B choice in a deterministic, round-specific way.
- The wait frame should not fabricate outcomes; it should only reflect server resolution.

### 8. `CoordinationRoundResult`

**File:** [Stuff/coordination.py](coordination.py)

**Purpose:**
Display the result of the resolved coordination round.

**Server responsibility:**
None directly.

**Backend notes:**
- This is presentation-only after the wait step.

### 9. `NextRoundInfo`

**File:** [Stuff/coordination.py](coordination.py)

**Purpose:**
Transition screen between coordination partners/rounds.

**Server responsibility:**
None directly.

### 10. `IntroMarketEntry`, `InstructionsMarketEntry`, `MarketEntryQuiz`, `MarketEntryGame`

**File:** [Stuff/marketentry.py](marketentry.py)

**Purpose:**
Market-entry task with quiz and entry decision.

**Server responsibility:**
- Receive quiz data for each round.
- Receive the decision to enter or stay out.
- Store quiz scores and decisions for later payoff resolution.

**Client-side state produced:**
- `root.status["me_quiz_scores"]`
- `root.status["me_decisions"]`
- `root.status["me_results"]` (later, when final outcomes are resolved)

**Backend notes:**
- The server must keep the quiz score and entry decision together by round.
- A later wait/result phase uses these values to determine final payoffs.
- The client may send multiple market-related messages; the backend should treat the round identifier as the link.

### 11. `WaitGroups`

**File:** [Stuff/trustgame.py](trustgame.py)

**Purpose:**
Wait for partner-group information used in the trust game.

**Server responsibility:**
- Return the group words or group sets for each trust round.
- The client stores them in `root.status["trust_groups"]` and `root.status["trust_groups_order"]`.

**Backend notes:**
- This is the server-side source of the partner information shown during trust decisions.
- The client uses the returned mapping to display the correct round-specific partner group.

### 12. `IntroTrust`, `InstructionsTrust`, `Trust`

**File:** [Stuff/trustgame.py](trustgame.py)

**Purpose:**
Trust-game decision screen where the participant makes decisions for both roles.

**Server responsibility:**
- Receive the role-A decision.
- Receive the role-B contingency decisions.
- Prediction is not sent to the server.

**Client-side state produced:**
- `root.status["trust_decisions"]`

**Backend notes:**
- The client sends two trust payloads per block: one for role A and one for role B.
- The backend should keep these separate and key them by block.
- Role assignment itself is not negotiated here; it comes from prior backend session setup.

### 13. Fire-game tutorial frames

**Files:** [Stuff/fires.py](fires.py), [Stuff/Tutorial_fire.py](Tutorial_fire.py), [Stuff/Tutorial_sprinkler.py](Tutorial_sprinkler.py), [Stuff/Tutorial_layout.py](Tutorial_layout.py), [Stuff/experiment_game.py](experiment_game.py)

**Purpose:**
Tutorials and the main fire-game mechanics.

**Server responsibility:**
Mostly none during the tutorial frames.

**Backend notes:**
- The fire game is primarily client-side in this codebase.
- If the backend stores results, it should expect local logging from the client rather than intermediate server calls.
- The fire-game logging is tabular and meant for later extraction.

### 14. `FiresUnderstanding`, `FiresRoundIntro`, `ExperimentGame`, `ResultGame`, `FiresQuestionnaire`

**File:** [Stuff/fires.py](fires.py), [Stuff/experiment_game.py](experiment_game.py)

**Purpose:**
Main fire-game rounds and result screens.

**Server responsibility:**
Typically none during round play.

**Backend notes:**
- The experiment game writes its own local records.
- If a backend integration is later added for fire-game outcomes, it should preserve the existing round structure and local file format assumptions.

### 15. Product task block 1

**Files:** [Stuff/products.py](products.py)

**Frames:** `ProductsIntro1`, `ProductsIntro2`, `ProductsIntroUnderstanding`, `ProductsIntro4`, `Choices`

**Purpose:**
First presentation of the product-choice task.

**Server responsibility:**
- No final payoff send yet.
- The backend-selected two products are already stored from login in `root.status["selected_products"]`.

**Backend notes:**
- The client records choices for all shown products locally.
- The final payoff-relevant send happens only after the second presentation.

### 16. Intermission frames

**Files:** [Stuff/questionnaire.py](questionnaire.py), [Stuff/intros.py](intros.py)

**Frames:** `QuestInstructions`, `Numeracy`, `Narcissism`, `SalesProneness`, `TransactionValue`, `Demographics`, `Comments`

**Purpose:**
Questionnaires and demographic data.

**Server responsibility:**
Usually none in the current implementation.

**Backend notes:**
- These are local or file-based captures.
- The server-side code does not need to resolve outcomes here.

### 17. Product task block 2

**Files:** [Stuff/products.py](products.py)

**Frames:** `ProductsIntro5`, `Choices`, `ProductsEnd1`

**Purpose:**
Second presentation of the product-choice task and final realization of the two selected products.

**Server responsibility:**
- The final product outcome send must use the two products chosen by the backend at login.
- The client sends only code + choice for each selected product.

**Backend notes:**
- This is the payoff-relevant products send.
- The server should match the selected product codes from login with the participant's recorded choice in the relevant presentation.
- The resulting data should be stored for final payoff calculation or export.

### 18. `WaitResults`

**File:** [Stuff/games.py](games.py)

**Purpose:**
Wait for backend resolution of the participant's final results.

**Server responsibility:**
- Return or signal the final computed outcome set.
- The client then constructs the final reward message and local result text.

**Backend notes:**
- This is the final aggregation step.
- The backend should combine the information from coordination, market entry, trust, and products as needed.
- The wait frame expects the server to have enough stored state to resolve the final reward cleanly.

### 19. `Ending`

**File:** [Stuff/intros.py](intros.py)

**Purpose:**
Closing screen.

**Server responsibility:**
None.

## Practical Backend Checklist

When implementing the server, the minimum state you need to preserve is:

- participant session identity
- selected product codes from login
- coordination roles from login
- groups selection for trust pairing
- coordination round decisions and partner decisions
- market quiz scores and market-entry decisions
- trust decisions for role A and role B
- final selected-product choices from the second products block
- final aggregated result data

## Relationship to `SERVER_DATA_FORMATS.md`

Use [SERVER_DATA_FORMATS.md](SERVER_DATA_FORMATS.md) when you need exact payload shapes.
Use this guide when you need to understand which frame is responsible for which backend state and where the server must respond versus only store data.
