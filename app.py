import random

import streamlit as st

from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score


ATTEMPT_LIMITS = {"Easy": 6, "Normal": 8, "Hard": 5}


def start_game():
    # FIX: AI-assisted reset clears the whole round and uses the selected range.
    low, high = get_range_for_difficulty(st.session_state.difficulty)
    st.session_state.update(
        secret=random.randint(low, high),
        attempts=0,
        score=0,
        status="playing",
        history=[],
        outcome=None,
        input_error=None,
        guess_input="",
        active_difficulty=st.session_state.difficulty,
    )


def submit_guess():
    # FIX: The AI moved updates into a callback so the next render has fresh counts.
    if st.session_state.status != "playing":
        return

    ok, guess, error = parse_guess(st.session_state.guess_input)
    low, high = get_range_for_difficulty(st.session_state.difficulty)
    if ok and not low <= guess <= high:
        error = f"Enter a whole number between {low} and {high}."
    st.session_state.input_error = error
    # FIX: Following the user's invalid-input report, validate before using an attempt.
    if error:
        return

    st.session_state.attempts += 1
    st.session_state.history.append(guess)
    outcome = check_guess(guess, st.session_state.secret)
    st.session_state.outcome = outcome
    st.session_state.score = update_score(
        st.session_state.score, outcome, st.session_state.attempts
    )
    if outcome == "Win":
        st.session_state.status = "won"
    elif st.session_state.attempts >= ATTEMPT_LIMITS[st.session_state.difficulty]:
        st.session_state.status = "lost"


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")
st.title("🎮 Game Glitch Investigator")
st.caption("Find the secret number using the hints.")
st.sidebar.header("Settings")
difficulty = st.sidebar.selectbox(
    "Difficulty", ["Easy", "Normal", "Hard"], index=1, key="difficulty"
)

if st.session_state.get("active_difficulty") != difficulty:
    start_game()

low, high = get_range_for_difficulty(difficulty)
attempt_limit = ATTEMPT_LIMITS[difficulty]
st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

st.subheader("Make a guess")
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)
st.metric("Score", st.session_state.score)
st.caption(
    "Win on your first guess for 100 points. Each additional valid guess "
    "reduces the win award by 10 points, down to 10. Wrong guesses deduct "
    "5 points, but your score never goes below 0. New Game resets your score."
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

finished = st.session_state.status != "playing"
st.text_input("Enter your guess:", key="guess_input", disabled=finished)
col1, col2, col3 = st.columns(3)
with col1:
    submitted = st.button("Submit Guess 🚀", on_click=submit_guess, disabled=finished)
with col2:
    st.button("New Game 🔁", on_click=start_game)
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if st.session_state.input_error:
    st.error(st.session_state.input_error)
elif st.session_state.status == "won":
    if submitted:
        st.balloons()
    st.success(
        f"You won! The secret was {st.session_state.secret}. "
        f"Final score: {st.session_state.score}"
    )
elif st.session_state.status == "lost":
    st.error(
        f"Out of attempts! The secret was {st.session_state.secret}. "
        f"Score: {st.session_state.score}"
    )
elif show_hint and st.session_state.outcome:
    # FIX: AI-assisted review paired Too High with LOWER and Too Low with HIGHER.
    hints = {
        "Too High": "📉 Too high. Go LOWER!",
        "Too Low": "📈 Too low. Go HIGHER!",
    }
    st.warning(hints[st.session_state.outcome])

st.divider()
st.caption("Game Glitch Investigator")
