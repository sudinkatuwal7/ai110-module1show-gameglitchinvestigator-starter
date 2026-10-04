def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    return {"Easy": (1, 20), "Normal": (1, 100), "Hard": (1, 50)}.get(
        difficulty, (1, 100)
    )


def parse_guess(raw: str):
    """Return (ok, integer guess, error); reject blanks and non-integers."""
    # FIX: AI-assisted review replaced decimal truncation with integer validation.
    if raw is None or not raw.strip():
        return False, None, "Enter a guess."
    try:
        return True, int(raw.strip()), None
    except ValueError:
        return False, None, "Enter a whole number."


def check_guess(guess: int, secret: int):
    """Compare integer values and return Win, Too High, or Too Low."""
    # FIXME (resolved): Comparing strings made 9 greater than 44 on some turns.
    # FIX: Refactored with the AI; compare integers and leave hint text to the UI.
    if guess == secret:
        return "Win"
    return "Too High" if guess > secret else "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Award earlier wins more points; wrong guesses never make scores negative."""
    # FIXME (resolved): Wrong guesses could add points or produce negative scores.
    # FIX: After the user's -25 report, the AI made penalties consistent and bounded.
    current_score = max(0, current_score)
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number - 1))
    if outcome in ("Too High", "Too Low"):
        return max(0, current_score - 5)
    return current_score
