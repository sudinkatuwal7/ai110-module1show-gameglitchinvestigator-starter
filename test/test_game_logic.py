import pytest

from logic_utils import check_guess, parse_guess, update_score


@pytest.mark.parametrize(
    "guess,secret,expected",
    [(60, 50, "Too High"), (40, 50, "Too Low"), (50, 50, "Win"),
     (9, 44, "Too Low"), (100, 44, "Too High")],
)
def test_guess_outcome_uses_numeric_order(guess, secret, expected):
    assert check_guess(guess, secret) == expected


def test_parsing_preserves_whole_numbers():
    assert parse_guess(" 44 ") == (True, 44, None)
    assert not parse_guess(None)[0]
    assert not parse_guess("44.9")[0]


@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
def test_wrong_guess_penalties_are_consistent_and_cannot_make_score_negative(outcome):
    for attempt in (1, 2, 3, 4):
        assert update_score(0, outcome, attempt) == 0
        assert update_score(3, outcome, attempt) == 0
        assert update_score(20, outcome, attempt) == 15


def test_win_award_rewards_earlier_guesses_with_a_minimum():
    assert update_score(0, "Win", 1) == 100
    assert update_score(0, "Win", 2) == 90
    assert update_score(0, "Win", 20) == 10
