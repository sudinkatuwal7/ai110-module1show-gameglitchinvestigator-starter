# Game Glitch Investigator

A Streamlit number-guessing game repaired through AI-assisted debugging. Choose a difficulty, enter whole-number guesses, and use the higher/lower hints to find a secret number before your attempts run out.

## Setup

From the cloned repository folder, run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address printed by Streamlit, usually http://localhost:8501.

| Difficulty | Number range | Valid guesses allowed |
|------------|--------------|-----------------------|
| Easy | 1–20 | 6 |
| Normal | 1–100 | 8 |
| Hard | 1–50 | 5 |

The secret stays the same during a round. New Game and difficulty changes start a fresh round and reset the score, attempts, and history. Blank, non-integer, and out-of-range inputs show an error without using an attempt.

## Document Your Experience

The purpose of the game is to practice debugging AI-generated code by connecting visible symptoms to their causes and verifying repairs.

The original game reversed its hints, compared numbers as strings on alternating attempts, started with one attempt already used, and rendered stale counters. Invalid text consumed attempts, decimals were silently truncated, and numbers outside the selected range were accepted. New Game failed to clear a completed game's status, and difficulty changes could leave the secret outside the displayed range. During play, I reported the message `Out of attempts! The secret was 44. Score: -25`; this provided a concrete example of the negative-score problem.

With Codex, the reusable functions were moved into `logic_utils.py`, leaving the Streamlit interface and session state in `app.py`. Guesses and secrets now stay numeric, hints match the comparison, validation happens before counting an attempt, and callbacks update state before the page renders. Complete resets keep the target within the selected difficulty. Scores are bounded at zero, and regression tests cover both the pure logic and real Streamlit widget interactions.

The original reproduction logs, AI critique, and verification evidence are in [reflection.md](reflection.md). The original starter tests remain in `tests/test_game_logic.py`; focused repair tests are in `test/test_game_logic.py`, and interaction tests are in `tests/test_gameplay.py`.

## Demo Walkthrough

This verified sample uses Normal difficulty with a secret of **50**. The automated walkthrough temporarily fixes the secret to 50; the live game chooses randomly, so use Developer Debug Info to see your actual secret and adjust the guesses.

1. Start a new Normal game. The range is 1–100, there are **8 attempts left**, and the score is **0**.
2. Enter **40** and click Submit Guess. The game displays **“Too low. Go HIGHER!”**, with **7 attempts left** and score **0**.
3. Enter **70** and submit. The game displays **“Too high. Go LOWER!”**, with **6 attempts left** and score **0**.
4. Enter **50.9** and submit. The game displays **“Enter a whole number.”** There are still **6 attempts left**, the score stays **0**, and the rejected value is not added to guess history.
5. Enter **50** and submit. The game displays **“You won! The secret was 50. Final score: 80”**. This was the third valid guess, so **5 attempts remain**, and further submissions are disabled.
6. Click **New Game** to choose a new secret, restore all 8 attempts, clear the input and history, and reset the score to 0.

A win earns `max(10, 100 - 10 * (valid_attempts - 1))` points: 100 on the first guess, 90 on the second, and 80 on the third. Wrong guesses deduct 5 points with a zero floor. Because each round starts at zero and ends on a win, the displayed score remains zero until a successful guess. A loss occurs after the allowed number of valid wrong guesses and reveals the secret.

## Test Results

Run all test folders from the repository root:

```powershell
python -m pytest -q
```

Actual terminal output from the final verification:

```text
.........................                                                [100%]
25 passed in 12.24s
```

The advanced edge-case coverage includes blank and whitespace input, letters, decimals, negative values, out-of-range guesses, comparisons with different digit lengths, zero-floor scoring, winning on the final attempt, restarting after a win or loss, and changing difficulty. A dedicated test verifies the exact walkthrough above. These are automated checks; the Streamlit server also returned `ok` from its health endpoint.

## Project Progress

The project has separate commits for the gameplay repairs and initial bug documentation, the verified demo regression test, and the final README and reflection. The original bug log and repairs were committed together; the history was not rewritten to imply a separate earlier bug-log commit.

No enhanced-UI challenge is claimed.
