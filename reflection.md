# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The AI assistant installed the dependencies, launched the app through Streamlit, and used Streamlit AppTest to interact with the actual app; these are automated observations, not a claim that I manually played in a browser.
On the initial Normal screen, the app showed the title, difficulty selector, guess input, buttons, and Developer Debug Info, but only 7 attempts left despite allowing 8.
For repeatable observations, the assistant temporarily mocked `random.randint` to return 50 in the test process without changing the game files: game 1 used `60`, `40`, and `50`, then New Game, while game 2 used `9`, `9`, and `50.9` in a fresh session.
These runs and follow-up automated checks exposed reversed hints, inconsistent comparisons, invalid-input and range problems, incorrect attempt counts, and a restart that remained stuck in the won state.
The AI explained that `check_guess()` pairs the `guess > secret` branch with `Go HIGHER!`, so a guess of 60 against 50 incorrectly tells the player to increase the guess; the opposite branch is reversed too.

**Bug Reproduction Logs**

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|------------|-------------------|-----------------|------------------------|-------------------------|
| Open a fresh Normal session without submitting a guess. | All 8 allowed attempts should be available. | The sidebar allows 8 attempts, but the main instruction shows only 7 left; internal attempts is already 1. | No app exception; UI: `Attempts left: 7`. | `app.py`, lines 95-96 initialize attempts to 1; lines 109-111 subtract that value from the limit. |
| Game 1, secret 50: submit `60`, then `40`. | 60 should prompt a lower guess; 40 should prompt a higher guess. | 60 displays `Go HIGHER!`; 40 displays `Go LOWER!`. | No app exception; UI: `Go HIGHER!`, then `Go LOWER!`. | `app.py`, `check_guess()`, lines 32-47: the directional messages are reversed in both comparison paths. |
| Game 1: submit `50` to win, click New Game, then submit `50` again. | New Game should restore the playing state and accept guesses. | Status stays `won`; the app repeats the already-won message and ignores the submission, with attempts remaining 0. | No app exception; UI: `You already won. Start a new game to play again.` | `app.py`, lines 134-138 reset only attempts and secret; lines 140-145 stop execution because status was never reset to `playing`. |
| Game 2, fresh Normal session, secret 50: submit `9` twice. | Both identical guesses should be classified as too low and consistently request a higher guess. | First shows `Go HIGHER!` and score 5; second shows `Go LOWER!` and score 0, although the secret stays 50. | No app exception; UI: `Go HIGHER!`, then `Go LOWER!`. | `app.py`, lines 158-161 convert the secret to a string on even internal attempts; `check_guess()`, lines 41-47, compares strings, making `'9' > '50'` true; `update_score()`, lines 57-63, then scores the inconsistent outcomes. |
| Game 2, secret 50: after `9`, `9`, submit `50.9`. | A non-whole-number guess should be rejected rather than treated as exactly 50. | The app stores 50 in history and declares a win for the entered value 50.9. | No app exception; UI: `You won! The secret was 50. Final score: 50`. | `app.py`, `parse_guess()`, lines 21-25: `int(float(raw))` silently truncates the decimal before comparison. |
| Fresh Normal session: click New Game before winning, then submit `60` against secret 50; toggle Show hint afterward. | The counter should immediately drop from 8 to 7 after the submitted guess; toggling a hint should not change the count. | It still displays 8 immediately after submission even though internal attempts is 1; toggling Show hint finally displays 7. | No app exception; UI: `Attempts left: 8`, then `Attempts left: 7`. | `app.py`, lines 109-111 render the counter before line 148 increments attempts; no rerun refreshes the counter after submission. |
| Fresh Normal session: submit `abc` once, then eight more times, then toggle Show hint or trigger another rerun. | Invalid text should show a validation error without using a valid guess; attempts left should never become negative. | The first invalid entry increments internal attempts from 1 to 2. After nine invalid submissions, internal attempts is 10, status is still `playing`, and the counter shows -1 immediately, then -2 on the next rerun. | No app exception; validation message: `That is not a number.`; refreshed UI: `Attempts left: -2`. | `app.py`, lines 147-154 increment attempts before validation; the loss check at lines 181-187 runs only for valid, non-winning guesses, so invalid entries bypass it. |
| Fresh Normal session, secret 50: submit `0`, then `101`. | Both numbers should be rejected as outside the advertised 1-100 range. | Both are accepted into history, consume attempts, and receive directional hints instead of range errors. | No app exception; UI: `Go LOWER!` for 0 and `Go HIGHER!` for 101. | `app.py`, `parse_guess()`, lines 14-29 checks conversion only; the submit handler at lines 150-163 never checks `low <= guess_int <= high`. |
| Fresh Normal session with secret 50: switch Difficulty to Easy, inspect Developer Debug Info, then click New Game while still playing. | The target and main instructions should match Easy's advertised range of 1-20, including after New Game. | Switching preserves secret 50 while the sidebar says 1-20 and the main instructions still say 1-100. New Game also requests a number from 1-100; in the controlled run it produces 50 again. | No app exception; sidebar: `Range: 1 to 20`; debug secret: 50; recorded random call on New Game: `randint(1, 100)`. | `app.py`, lines 92-93 create a secret only if absent, so difficulty changes keep the old target; line 110 hardcodes 1-100; line 136 also hardcodes 1-100 for New Game. |

The completed automated runs produced no app exceptions. AppTest emitted the harness warning `Thread 'MainThread': missing ScriptRunContext!`, which is separate from the gameplay issues above; an initial harness run also hit its default 3-second timeout, and the completed runs used a 30-second timeout. The original browser app used a random secret, so reproducing these observations required checking Developer Debug Info and adjusting guesses accordingly. At the time of these observations, the game used functions in `app.py`, while `logic_utils.py` contained unimplemented placeholders; the later fixes described in section 3 moved the working logic into that module. This table records the original bugs, not the behavior after the fixes.

---

## 2. How did you use AI as a teammate?

I used Codex as an AI coding teammate with access to `app.py`, `logic_utils.py`, and the tests, and I supplied feedback about attempts, invalid guesses, incorrect hints, and the displayed score of -25.
One correct suggestion was to keep guesses and secrets as integers and move comparisons into `logic_utils.py`, because numeric order correctly treats 9 as less than 44; the comparison tests and repeated-hint interaction tests verified that repair.
One AI-generated approach we changed instead of accepting as written was the starter parser's `int(float(raw))`, which silently turned a decimal such as 50.9 into 50 and could award a win for an invalid guess.
The replacement uses integer-only parsing and validates the range before consuming an attempt, and the walkthrough test verifies that 50.9 produces an error while preserving the score, attempt count, and history before a valid 50 wins.
This critique concerns the AI-generated starter code, not a fabricated later suggestion; our work used one ongoing chat, and the assistant reviewed the diffs rather than claiming that I opened separate chats or personally reviewed every change.

---

## 3. Debugging and testing your fixes

The two priority repairs were inconsistent higher/lower hints and negative scores; the plan was to compare integers in `check_guess()`, map outcomes to directions in `app.py`, and make `update_score()` apply consistent penalties with a zero floor.
After I reported the symptoms, the AI assistant implemented those repairs along with input validation, attempt counting, and game resets, moved reusable functions into `logic_utils.py`, and added `FIXME (resolved)` and `FIX` comments identifying the original causes and collaboration.
The scoring rule now awards 100 points for a first-guess win, reduces that award by 10 per additional valid guess to a minimum of 10, and prevents wrong-guess penalties from lowering the score below zero.
The assistant added focused tests in `test/test_game_logic.py` and interaction tests in `tests/test_gameplay.py`, then ran `python -m pytest -q`: `25 passed in 12.24s`, including the three original tests; cases cover 60 against 50 returning `Too High`, repeated hints with secret 44, invalid inputs, immediate counters, a loss after eight Normal guesses at score 0, a last-attempt win, restarts, difficulty ranges, and the README walkthrough's third-guess win for 80 points.
The app was launched with `python -m streamlit run app.py` using headless local-server options, and its health endpoint returned `ok`; these are automated verification results, and a personal browser retest of the fixed version has not been recorded.

---

## 4. What did you learn about Streamlit and state?

Streamlit rebuilds the page by running the script again when a user interacts with a widget.
Ordinary variables are recreated during that run, while `st.session_state` keeps values such as the secret, attempts, score, and history for the current session.
The original counter was drawn before the submission handler changed it, so it showed the previous value until another interaction caused a rerun.
The repaired app uses a submit callback to validate and update state before the page renders, and New Game explicitly resets all the values for a fresh round.

---

## 5. Looking ahead: your developer habits

The habit I want to carry forward is recording the exact input, expected result, actual result, and relevant code before asking AI to change anything.
Next time, I would keep each AI request focused on one bug, review that diff myself, and commit the bug log before the repair instead of combining the initial documentation and fixes in one commit.
Reporting the remaining hint problems and the -25 score showed why an assistant's progress summary should be checked against the actual game.
AI-generated code is a starting point to inspect and test, and passing simple comparison tests alone is not enough to prove that input handling, session state, and the full game work together.
