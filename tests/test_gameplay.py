from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def new_game(secret=44):
    with patch("random.randint", return_value=secret):
        app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    return app


def submit(app, guess):
    app.text_input[0].set_value(str(guess))
    app.button[0].click().run()
    assert not app.exception


def test_hints_secret_and_counter_stay_consistent_across_guesses():
    app = new_game()
    assert "Attempts left: 8" in app.info[0].value
    for attempt, (guess, direction) in enumerate(
        [(9, "HIGHER"), (9, "HIGHER"), (60, "LOWER"), (60, "LOWER")], 1
    ):
        submit(app, guess)
        assert direction in app.warning[0].value
        assert app.session_state.secret == 44
        assert app.session_state.attempts == attempt
        assert f"Attempts left: {8 - attempt}" in app.info[0].value
        assert app.session_state.score == 0


@pytest.mark.parametrize("guess", ["", "   ", "abc", "44.9", "0", "101", "-5"])
def test_invalid_guesses_do_not_use_attempts_or_change_score(guess):
    app = new_game()
    submit(app, guess)
    assert app.error
    assert app.session_state.attempts == 0
    assert app.session_state.history == []
    assert app.session_state.score == 0
    assert app.session_state.status == "playing"
    assert "Attempts left: 8" in app.info[0].value


def test_loss_uses_exact_limit_and_new_game_recovers():
    app = new_game()
    for _ in range(8):
        submit(app, 1)
    assert app.session_state.status == "lost"
    assert "Attempts left: 0" in app.info[0].value
    assert "The secret was 44. Score: 0" in app.error[0].value
    assert app.button[0].disabled
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state.status == "playing"
    assert app.session_state.attempts == 0
    assert app.session_state.history == []
    assert app.text_input[0].value == ""
    assert not app.button[0].disabled


def test_win_on_last_attempt_and_restart():
    app = new_game()
    for _ in range(7):
        submit(app, 1)
    submit(app, 44)
    assert app.session_state.status == "won"
    assert app.session_state.score == 30
    assert "Final score: 30" in app.success[0].value
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state.status == "playing"
    assert app.session_state.score == 0
    submit(app, app.session_state.secret)
    assert app.session_state.status == "won"
    assert app.session_state.score == 100


def test_readme_walkthrough_with_invalid_input_and_third_guess_win():
    app = new_game(50)
    submit(app, 40)
    assert "Too low. Go HIGHER!" in app.warning[0].value
    assert "Attempts left: 7" in app.info[0].value
    assert app.session_state.score == 0

    submit(app, 70)
    assert "Too high. Go LOWER!" in app.warning[0].value
    assert "Attempts left: 6" in app.info[0].value
    assert app.session_state.score == 0

    submit(app, "50.9")
    assert "Enter a whole number." in app.error[0].value
    assert "Attempts left: 6" in app.info[0].value
    assert app.session_state.history == [40, 70]
    assert app.session_state.score == 0

    submit(app, 50)
    assert "You won! The secret was 50. Final score: 80" in app.success[0].value
    assert "Attempts left: 5" in app.info[0].value
    assert app.session_state.history == [40, 70, 50]
    assert app.session_state.status == "won"
    assert app.button[0].disabled


@pytest.mark.parametrize("difficulty,high,limit", [("Easy", 20, 6), ("Hard", 50, 5)])
def test_difficulty_changes_and_new_games_use_selected_range(difficulty, high, limit):
    app = new_game(99)
    with patch("random.randint", return_value=high) as draw:
        app.selectbox[0].select(difficulty).run()
        draw.assert_called_once_with(1, high)
    assert not app.exception
    assert app.session_state.secret == high
    assert app.session_state.attempts == 0
    assert f"between 1 and {high}" in app.info[0].value
    assert f"Attempts left: {limit}" in app.info[0].value
    submit(app, high + 1)
    assert app.error
    assert app.session_state.attempts == 0
    with patch("random.randint", return_value=1) as draw:
        app.button[1].click().run()
        draw.assert_called_once_with(1, high)
    assert not app.exception
    assert app.session_state.secret == 1
    assert not app.error
