# Server Data Formats Documentation

This document describes all data formats sent from the client (experiment application) to the server via HTTP POST requests. All data is URL-encoded and sent to the endpoint configured in `constants.URL`.

## Overview

**Server Communication Pattern:**
- Protocol: HTTP POST
- Encoding: URL-encoded form data (`application/x-www-form-urlencoded`)
- Configuration: Endpoint URL set in `constants.URL` (e.g., `"https://bahnik.pythonanywhere.com/"` or `"http://127.0.0.1:8000/"`)
- Testing Mode: When `constants.URL = "TEST"`, requests are logged to console instead of sent to server
- Implementation: Located in `common.py`, method `ExperimentFrame.sendData(message, pause=0.1, trials=-1)`

**Standard Parameters:**
All server requests follow a standard structure with three required fields:
- `id`: Participant identifier (string)
- `round`: Phase/round identifier (string) - uniquely identifies the game round or phase
- `offer`: Decision/data payload (string) - typically contains the participant's choice or response

## Server Requests by Frame

---

### 1. Login

**Frame:** `login.Login`  
**File:** `Stuff/login.py`  
**Purpose:** Authenticate participant and retrieve selected product codes for payoff-relevant product realization  
**Timing:** Sent repeatedly (every 0.1s) until server responds with start signal

**Request Format:**
```
id: <participant_id>
round: <session_code>
offer: "login"
```

**Example:**
```
id: "P001"
round: "ABC123"
offer: "login"
```

**Server Response (Expected):**
```
<token1>|<token2>|<coord_roles>
```

Required token format:
- `<product_code>_<round>` for non-control products (e.g., `S14_2`, `N11_1`)
- `<control_code>` for control products (e.g., `CONTROL1`)

Constraints:
- Response always contains exactly three tokens separated by `|`
- `<round>` is `1` or `2`

Coordination roles token:
- `<coord_roles>` is an underscore-separated sequence of role numbers for each coordination block
- Format example for 3 rounds: `1_2_1`
- `1` means participant is Player 1 in that block, `2` means participant is Player 2

**Implementation Details:**
- Server response parsed to populate `root.status["selected_products"]`
- Server response parsed to populate `root.status["co_roles"]` (mapped as block -> A/B for game logic)

---

### 2. Groups

**Frame:** `groups.Groups`  
**File:** `Stuff/groups.py`  
**Purpose:** Log participant's selection of 5 preferred words/groups from a list  
**Timing:** Sent once, immediately before advancing to next frame  
**Multi-player:** Yes (groups are shared with trust game partner)

**Request Format:**
```
id: <participant_id>
round: "groups"
offer: <word1>_<word2>_<word3>_<word4>_<word5>
```

**Example:**
```
id: "P001"
round: "groups"
offer: "trust_fairness_honesty_cooperation_integrity"
```

**Notes:**
- Exactly 5 words selected from randomized list in `groups.txt`
- Each word joined with underscore; order matches selection
- Skipped if `constants.URL == "TEST"` (debug mode)

---

### 3. Coordination Game (Multi-player)

**Frame:** `coordination.CoordinationGame`  
**File:** `Stuff/coordination.py`  
**Purpose:** Log coordination game decision (choice A/B). Prediction is not sent to server.  
**Timing:** Sent once per round, immediately after decision confirmed  
**Multi-player:** Yes (players paired randomly each round)  
**Rounds:** `constants.COORDINATION_ROUNDS` (default: 3)

**Request Format:**
```
id: <participant_id>
round: "coordination<block>_<trial>"
offer: <decision>
```

Where:
- `block`: Round number (1, 2, 3, ...)
- `trial`: Trial within block (1 or 2)
- `decision`: "A" or "B" (participant's choice)

**Example (Round 1, Trial 1, chose A):**
```
id: "P001"
round: "coordination1_1"
offer: "A"
```

**Context:**
- Each block represents a new pairing with a different opponent
- Each pairing plays 2 trials (trial 1 and trial 2)
- Participant role in each block is taken from login response (`root.status["co_roles"]`)
- Payoff determined by match: both A → both get coordination bonus + preference bonus, both B → Player2 gets bonus, mismatch → base payoff only

---

### 4. Market Entry Quiz (Multi-player prep)

**Frame:** `marketentry.MarketEntryQuiz`  
**File:** `Stuff/marketentry.py`  
**Purpose:** Log quiz performance scores, which determine market entry payoffs  
**Timing:** Sent once per quiz round, immediately after the local confidence rating is completed  
**Multi-player:** Yes (quiz score used in payoff competition)  
**Rounds:** `constants.MARKET_ROUNDS` (default: 3)

**Request Format:**
```
id: <participant_id>
round: "market_entry_quiz<block>"
offer: <score>
```

Where:
- `block`: Quiz round number (1, 2, 3, ...)
- `score`: Integer 0-5 (number of questions answered within ±10% of correct answer)

**Example (Round 1, confidence recorded locally as 3):**
```
id: "P001"
round: "market_entry_quiz1"
offer: "4"
```

**Quiz Structure:**
- 5 estimation questions per block
- Scoring: answer within ±10% of true value = 1 point
- Confidence: participant selects 0-5 rating locally; it is not sent to the server

---

### 5. Market Entry Game (Multi-player decision)

**Frame:** `marketentry.MarketEntryGame`  
**File:** `Stuff/marketentry.py`  
**Purpose:** Log market entry decision and determine payoff based on quiz score  
**Timing:** Sent once per market round, immediately after decision confirmed  
**Multi-player:** Yes (payoff depends on partner's decision and quiz scores)  
**Rounds:** `constants.MARKET_ROUNDS` (default: 3)

**Request Format:**
```
id: <participant_id>
round: "market_entry<block>"
offer: <decision>_<quiz_score>
```

Where:
- `block`: Market round number (1, 2, 3, ...)
- `decision`: "enter" or "stayout"
- `quiz_score`: Score from the matching market-entry quiz round (0-5)

**Example (Round 2, decided to stay out):**
```
id: "P001"
round: "market_entry2"
offer: "stayout_4"
```

**Payoff Rules:**
- Both stay out: each gets 20 Kč (market endowment)
- One enters, one stays out: entrant gets 50 Kč, stayer gets 20 Kč
- Both enter: higher quiz score gets 50 Kč (market win), lower gets 0 Kč (market loss). Ties broken randomly.

---

### 6. Trust Game (Multi-player sequential decisions)

**Frame:** `trustgame.Trust`  
**File:** `Stuff/trustgame.py`  
**Purpose:** Log trust game decisions for both roles. Prediction is NOT sent to server.  
**Timing:** Sent twice per block (one message for role A decision, one message for role B contingency decisions), immediately after all decisions confirmed  
**Multi-player:** Yes (sequential: Player A sends to B, B responds)  
**Rounds:** `constants.TRUST_ROUNDS` (default: 3)

**Request Format (Role A message):**
```
id: <participant_id>
round: "trustA<block>"
offer: <sentA>
```

Where:
- `block`: Trust block/round number (1, 2, 3, ...)
- `sentA`: Amount sent by Player A (0, 8, 16, 24, 32, 40 Kč)

**Request Format (Role B message):**
```
id: <participant_id>
round: "trustB<block>"
offer: <b0>_<b1>_<b2>_<b3>_<b4>_<b5>
```

Where:
- `b0..b5`: Amount Player B would send back for each possible amount sent by A, in order for A sending `0, 8, 16, 24, 32, 40` Kč
- **Prediction value is not included in server payload.**

**Example (Block 1):**
```
id: "P001"
round: "trustA1"
offer: "16"

id: "P001"
round: "trustB1"
offer: "5_10_15_20_25_30"
```

**Context:**
- Participant makes decisions for BOTH roles (decision-theoretic approach)
- Responses stored in `root.status["trust_groups"]` and `root.status["trust_groups_order"]`
- Partner-group information for each trust round is retrieved in `WaitGroups`

---

### 7. Products (Consumer Choice Task)

**Frame:** `products.Choices`  
**File:** `Stuff/products.py`  
**Purpose:** At the end of the second products presentation, report participant choices for the two products selected at login.  
**Timing:** Sent once, after products presentation 2 is finished. The selected-product payload is always sent, even if both selected products were not bought.  
**Multi-player:** No (individual choice, though may affect payoff redistribution)  
**Blocks:** 2 (initial product choices + post-questionnaire product choices)

**Request Format:**
```
id: <participant_id>
round: "products_selected"
offer: <code1>:<choice1>|<code2>:<choice2>
```

Where:
- `codeX`: Product ID selected by backend/login response
- `choiceX`: `yes`, `no`, or `NA` if the selected code/presentation did not match observed choices

**Example:**
```
id: "P001"
round: "products_selected"
offer: "L01:yes|S04:no"
```

**Notes:**
- Selected products are stored in `root.status["selected_products"]` from login response
- Matching uses product ID and, when metadata is `1` or `2`, the corresponding products presentation round
- The request is always sent after the second products presentation; unmatched selections use `NA`

---

## Implementation: Common.py

**Method:** `ExperimentFrame.sendData(message, pause=0.1, trials=-1)`

**Parameters:**
- `message`: Dictionary with keys 'id', 'round', 'offer'
- `pause`: Delay (seconds) between retry attempts on failure (default 0.1)
- `trials`: Number of retry attempts (-1 = infinite, used in login loop)

**Behavior:**
1. Converts dict to URL-encoded string via `urllib.parse.urlencode()`
2. Encodes to ASCII bytes
3. If `constants.URL == "TEST"`: prints to console instead of sending
4. If `constants.URL == "http://127.0.0.1:8000/"`: debug mode, prints request and response
5. Sends POST request via `urllib.request.urlopen()`
6. Retries on network error until response == "ok" or trials exhausted
7. Returns on successful response

**Error Handling:**
- Network exceptions trigger retry loop (non-blocking)
- Invalid responses stored; participant continues (async-friendly)
- Debug output logged to `log.txt` when run via double-click

---

## Testing and Configuration

**Debug Modes:**

1. **Testing Mode** (`constants.URL = "TEST"`):
   - All requests logged to console
   - No network calls made
  - Login loads product IDs from `products.tsv` and simulates backend product selection
  - Simulated response format: `<token1>|<token2>|<coord_roles>`
  - Simulated `<coord_roles>` has one role value (`1`/`2`) for each coordination round

2. **Local Development** (`constants.URL = "http://127.0.0.1:8000/"`):
   - Sends to localhost server
   - Request and response printed to console
   - Requires local server running on port 8000

3. **Production** (`constants.URL = "https://bahnik.pythonanywhere.com/"`):
   - Sends to live server
   - Responses used to update session state
   - Network failures trigger retries

**Constants Affecting Data:**
- `COORDINATION_ROUNDS`: Number of coordination game rounds (default 3)
- `MARKET_ROUNDS`: Number of market entry rounds (default 3)
- `TRUST_ROUNDS`: Number of trust game rounds (default 3)
- `TRUST_ENDOWMENT`: Initial endowment for trust game (default 40 Kč)
- `MARKET_ENDOWMENT`: Market entry starting amount (default 20 Kč)

---

## Data Format Summary Table

| Frame | Round ID Format | Offer Format | Multi-player | Example |
|-------|-----------------|--------------|--------------|---------|
| Login | Session code | "login" | N/A | ABC123 → login |
| Groups | "groups" | word1_word2_... (5 words) | Yes | groups → trust_honesty_fairness... |
| Coordination | "coordination<block>_<trial>" | "A" or "B" | Yes | coordination1_1 → A |
| Market Quiz | "market_entry_quiz<block>" | "4" (score only) | Yes | market_entry_quiz1 → 4 |
| Market Game | "market_entry<block>" | "enter_4" or "stayout_4" | Yes | market_entry2 → enter_4 |
| Trust (Role A) | "trustA<block>" | "<sentA>" | Yes | trustA1 → 16 |
| Trust (Role B) | "trustB<block>" | 6 underscore-separated amounts | Yes | trustB1 → 5_10_15_20_25_30 |
| Products | "products_selected" | "code1:choice1\|code2:choice2" | No | products_selected → L01:yes\|S04:no |

---

## Participant Data Flow

```
Login 
  ↓ (receives selected product codes + coordination roles)
Groups (selected 5 words sent to server)
  ↓
Coordination (3 rounds, each 2 trials)
  ↓
Market Entry (3 rounds: quiz → decision)
  ↓
Trust Game (3 blocks, both roles)
  ↓
Fire Game (tutorial + 2 experimental rounds) [no server communication]
  ↓
Products Block 1 (product choices)
  ↓
Questionnaires (demographics, personality) [local logging only]
  ↓
Products Block 2 (post-questionnaire choices)
  ↓
Results (final payoff shown)
```

---

## Notes for Server Implementation

1. **Idempotency:** Client may retry requests on network failure; server should handle duplicate requests gracefully (same id + round + offer = already processed)

2. **Timing:** Requests are not queued; if server is slow, client waits before retry. Use `pause` parameter to adjust retry frequency.

3. **Responses:** Server should respond with "ok" on success. Any other response triggers retry.

4. **Login Special:** Login loop runs continuously until server returns a non-empty response in exact format `<token1>|<token2>|<coord_roles>`.

5. **UTF-8 Handling:** All text (id, round, offer) should be UTF-8 encoded; URL encoding handles special characters automatically.

6. **Testing:** Set `constants.URL = "TEST"` to run study locally without server dependency.
