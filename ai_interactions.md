# AI Interactions Log

This log records the agent workflow and AI-generated tests actually used in this project. It does not claim linting or a comparison between models.

## Agent Workflow (SF8)

**What task did you give the agent?**

I supplied the assignment instructions and asked for help running, investigating, and repairing the game. As I worked through it, I pointed out problems with attempts and invalid guesses, then shared the concrete output: `Out of attempts! The secret was 44. Score: -25`. I also asked how cloning, changing directories, committing, and pushing worked because I wanted to understand the commands being used.

**What did the agent do?**

Codex inspected `app.py` and `logic_utils.py`, installed the required libraries, started Streamlit, and reproduced bugs using Streamlit AppTest. It documented nine reproduction cases in `reflection.md`, moved reusable logic into `logic_utils.py`, and repaired comparisons, hint directions, validation, attempt counting, score handling, and resets. It added focused tests in `test/test_game_logic.py` and interaction tests in `tests/test_gameplay.py`, while retaining the original `tests/test_game_logic.py`. It completed the README walkthrough and reflection, reviewed diffs, and used Git in PowerShell to commit and push the authorized changes.

**What did you have to verify or fix manually?**

I noticed that the game still had attempt, hint, and scoring problems after the initial documentation stage, and I brought those problems back to the assistant instead of assuming the work was finished. My report of the -25 score gave us a specific result to investigate. Codex made the code changes and ran the automated checks; my contribution was trying the game, questioning the results, and directing attention to the remaining problems. We worked through those questions in one ongoing chat.

## Test Generation (SF7)

The prompts below quote requests or reports supplied in this conversation. The assistant designed the specific cases from that context; they were not all separately typed prompts.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Numbers with different digit lengths and repeated hints | “Ask your AI coding assistant to generate a pytest case in test/test_game_logic.py that specifically targets the bug you just fixed.” | Check 9 against 44 as Too Low and 100 against 44 as Too High; repeat guesses in the app to verify consistent hints. | Yes. | A string comparison can give the wrong order even if ordinary two-digit examples pass. |
| Invalid decimal followed by a valid winning guess | “Ask your AI coding assistant to generate a pytest case in test/test_game_logic.py that specifically targets the bug you just fixed.” | Reject 50.9 without changing attempts, score, or history, then accept 50 and win on the third valid guess for 80 points. | Yes. | A parser must not silently change a rejected guess into the secret, and the next valid submission must still work. |
| Negative score and exhausted attempts | “Out of attempts! The secret was 44. Score: -25” | Submit eight wrong guesses with secret 44; assert zero attempts left, score 0, a loss message, and successful restart. | Yes. | This reproduces the reported failure through actual widget interactions and checks the complete round. |
| Winning on the final allowed guess | “Confirm that your new test passes along with the existing starter tests.” | Make seven wrong Normal guesses, then guess the secret; assert a win and score 30. | Yes. | Reaching the attempt limit must not override a correct final guess. |

Final full-suite command: `python -m pytest -q`.

```text
.........................                                                [100%]
25 passed in 12.24s
```

The suite also covers blanks, whitespace, letters, negative and out-of-range numbers, score floors, and difficulty changes. A controlled secret is supplied only by test mocks; the live app still chooses randomly.
