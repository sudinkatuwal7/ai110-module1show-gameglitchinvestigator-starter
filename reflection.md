# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I tried the game, the higher/lower hints and the number of attempts left did not seem right.
I pointed out that there were more problems with attempts and invalid guesses, even after the first bugs had been documented.
One result I shared was `Out of attempts! The secret was 44. Score: -25`, because the negative score and confusing hints made me question how the game was working.
Codex helped investigate my observations and used automated playthroughs to find the exact causes, including reversed messages, string comparisons, and counting attempts before validating input.
The reproduction table below records those automated checks, including problems with decimals, difficulty ranges, and starting a new game.

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

For these automated checks, Codex temporarily fixed the secret at 50 in the test process; the live game still chose randomly. Game 1 used 60, 40, and 50, then New Game; game 2 used 9, 9, and 50.9. AppTest produced no app exceptions in the completed runs, although the test harness emitted a `missing ScriptRunContext` warning and initially needed a longer timeout. The code locations in the table refer to the original version, before the functions moved into `logic_utils.py`.

---

## 2. How did you use AI as a teammate?

I used Codex to help investigate the code, but I also kept asking questions and reporting what still seemed wrong in the game.
One correct suggestion was to keep guesses and secrets as integers and move the comparisons into `logic_utils.py`, since comparing strings can incorrectly treat 9 as greater than 44.
Codex verified that change with tests for numeric comparisons and repeated higher/lower hints.
An AI-generated approach we changed instead of keeping was the starter's `int(float(raw))`: turning 50.9 into 50 hides invalid input, so we replaced it with whole-number validation, and a test confirmed that 50.9 no longer wins or uses an attempt.
I also questioned whether documenting the bugs meant the work was finished and came back with the -25 result, which helped move the conversation from describing problems to repairing the game.

---

## 3. Debugging and testing your fixes

The first two repair targets were the confusing hints and the negative score I reported, with attempt counting and input validation checked alongside them.
My observations gave us concrete symptoms to investigate, and Codex connected them to the code, implemented the repairs, and added tests.
For example, one test checks that 60 against a secret of 50 returns `Too High`, while another plays through eight wrong guesses and checks that the game ends with zero attempts left and a score of 0.
The README walkthrough was also tested: 40 and 70 get the correct hints, 50.9 is rejected without using an attempt, and 50 wins for 80 points on the third valid guess.
Codex ran `python -m pytest -q` and got `25 passed in 12.24s`, including the starter tests, and checked that the Streamlit server responded successfully; this is the automated evidence for the repairs.

---

## 4. What did you learn about Streamlit and state?

Streamlit rebuilds the page by running the script again when a user interacts with a widget.
Ordinary variables are recreated during that run, while `st.session_state` keeps values such as the secret, attempts, score, and history for the current session.
The original counter was drawn before the submission handler changed it, so it showed the previous value until another interaction caused a rerun.
The repaired app uses a submit callback to validate and update state before the page renders, and New Game explicitly resets all the values for a fresh round.

---

## 5. Looking ahead: your developer habits

I want to keep asking how things work instead of only asking whether they are done.
For this assignment, I asked which commands cloned the repository and which commands committed and pushed the changes, and I also checked whether changing folders in the assistant changed my own terminal.
Next time, I would record exact bug examples earlier, review each small diff myself, and commit the bug log separately before making repairs.
Seeing more problems after the initial bug report taught me that a progress message is not enough evidence that the game works.
AI helped with the code and testing, while my questions and feedback helped decide what still needed attention.
