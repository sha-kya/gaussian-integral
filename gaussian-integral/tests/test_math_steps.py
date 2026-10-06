from itertools import pairwise

import math_steps as ms

EQUATION_CHAIN = [
    ms.INTEGRAL,
    ms.SQUARED,
    ms.ITERATED,
    ms.OVER_PLANE,
    ms.OVER_PLANE_RADIAL,
    ms.POLAR_MEASURE,
    ms.POLAR_LIMITS,
    ms.SEPARATED,
    ms.ANGLE_EVALUATED,
    ms.BOTH_EVALUATED,
    ms.EQUALS_PI,
    ms.ROOT_BOTH_SIDES,
    ms.ANSWER,
]


def test_disambiguate_only_changes_repeats():
    assert ms.disambiguate(["a", "b", "a", "a"]) == ["a", "b", "a\\relax", "a\\relax\\relax"]


def test_every_equation_has_unique_parts_after_disambiguation():
    for parts in EQUATION_CHAIN:
        assert len(set(ms.disambiguate(parts))) == len(parts)


def test_neighbouring_equations_share_a_part_to_morph_from():
    for before, after in pairwise(EQUATION_CHAIN):
        assert set(before) & set(after), (before, after)


def test_jacobian_index_points_at_r():
    assert ms.POLAR_MEASURE[ms.JACOBIAN_INDEX] == ms.R


def test_radial_slice_matches_the_radial_integral():
    assert ms.ANGLE_EVALUATED[ms.RADIAL_SLICE] == ms.RADIAL


def test_each_step_has_a_title_and_caption():
    assert sorted(ms.STEP_TITLES) == sorted(ms.CAPTIONS) == list(range(1, 8))
