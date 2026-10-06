"""LaTeX for every equation state, plus the on-screen text.

An equation is a list of parts. TransformMatchingTex pairs parts whose strings
are identical, so a part that should stay put between two equations has to be
spelled the same way in both. Each part is typeset on its own, which is why
the brackets are \\Big( and \\Big) rather than \\left ... \\right split over
parts.
"""

I_PLAIN = "I"
I_SQUARED = "I^2"
EQ = "="
INF_INT = r"\int_{-\infty}^{\infty}"
OPEN = r"\Big("
CLOSE = r"\Big)"
E_X = "e^{-x^2}"
E_Y = "e^{-y^2}"
E_XY = "e^{-(x^2+y^2)}"
E_R = "e^{-r^2}"
E_U = "e^{-u}"
DX = r"\,dx"
DY = r"\,dy"
DXDY = r"\,dx\,dy"
R = "r"  # separate from dr so the Jacobian factor can be boxed
DR = r"\,dr"
DU = r"\,du"
D_THETA = r"\,d\theta"
INT_THETA = r"\int_{0}^{2\pi}"
INT_R = r"\int_{0}^{\infty}"
IINT_PLANE = r"\iint_{\mathbb{R}^2}"
TWO_PI = r"2\pi"
PI = r"\pi"
SQRT_PI = r"\sqrt{\pi}"
SQRT_I_SQUARED = r"\sqrt{I^2}"
HALF = r"\tfrac{1}{2}"

RESULT_PARTS = frozenset({TWO_PI, PI, SQRT_PI, HALF})
INTEGRAND_PARTS = frozenset({E_X, E_Y, E_XY, E_R, E_U})


def disambiguate(parts):
    """Give repeated parts distinct strings that typeset identically.

    A string that occurs once in the old equation and twice in the new one
    breaks TransformMatchingTex's one-to-one pairing. Appending \\relax (which
    draws nothing) to the second and later copies keeps them apart.
    """
    seen = {}
    unique = []
    for part in parts:
        copies = seen.get(part, 0)
        seen[part] = copies + 1
        unique.append(part + r"\relax" * copies)
    return unique


INTEGRAL = [I_PLAIN, EQ, INF_INT, E_X, DX]
SQUARED = [I_SQUARED, EQ, OPEN, INF_INT, E_X, DX, CLOSE, OPEN, INF_INT, E_Y, DY, CLOSE]
ITERATED = [I_SQUARED, EQ, INF_INT, INF_INT, E_X, E_Y, DX, DY]
OVER_PLANE = [I_SQUARED, EQ, IINT_PLANE, E_XY, DXDY]
OVER_PLANE_RADIAL = [I_SQUARED, EQ, IINT_PLANE, E_R, DXDY]
POLAR_MEASURE = [I_SQUARED, EQ, IINT_PLANE, E_R, R, DR, D_THETA]
POLAR_LIMITS = [I_SQUARED, EQ, INT_THETA, INT_R, E_R, R, DR, D_THETA]
SEPARATED = [I_SQUARED, EQ, OPEN, INT_THETA, D_THETA, CLOSE, OPEN, INT_R, E_R, R, DR, CLOSE]
ANGLE_EVALUATED = [I_SQUARED, EQ, TWO_PI, OPEN, INT_R, E_R, R, DR, CLOSE]
BOTH_EVALUATED = [I_SQUARED, EQ, TWO_PI, r"\cdot", HALF]
EQUALS_PI = [I_SQUARED, EQ, PI]
ROOT_BOTH_SIDES = [SQRT_I_SQUARED, EQ, SQRT_PI]
ANSWER = [I_PLAIN, EQ, SQRT_PI]

# where the radial integral and the r in dx dy -> r dr dtheta sit in their lists
RADIAL_SLICE = slice(4, 8)
JACOBIAN_INDEX = 4

POLAR_SUBSTITUTIONS = [
    [r"x = r\cos\theta", r",\quad", r"y = r\sin\theta"],
    [r"x^2+y^2 = r^2"],
    [r"dx\,dy \;\to\; r\,dr\,d\theta"],
]

U_RULE = [r"u = r^2", r",\quad", r"du = 2r\,dr", r",\quad", r"r\,dr = \tfrac{1}{2}\,du"]
RADIAL = [INT_R, E_R, R, DR]
RADIAL_IN_U = [HALF, INT_R, E_U, DU]
RADIAL_ANTIDERIVATIVE = [HALF, r"\Big[-e^{-u}\Big]_{0}^{\infty}"]
RADIAL_AT_LIMITS = [HALF, r"\cdot", "1"]
RADIAL_VALUE = [HALF]

TITLE_CARD = "The Gaussian Integral"
TITLE_SUBTITLE = "a proof in seven moves"

STEP_TITLES = {
    1: "1 · The area under the bell",
    2: "2 · The trick: square it",
    3: "3 · Merge into one double integral",
    4: "4 · Switch to polar coordinates",
    5: "5 · The integral separates",
    6: "6 · Evaluate each piece",
    7: "7 · Combine and take the root",
}

CAPTIONS = {
    1: "We want the total area under e^(−x²) from −∞ to ∞.",
    2: "No antiderivative exists, so square it and use two copies.",
    3: "Two one-dimensional integrals become one over the whole plane.",
    4: "x² + y² is just r², so the surface is rotationally symmetric.",
    5: "The domain is now a rectangle, so the integral splits in two.",
    6: "The angle gives 2π; the substitution u = r² gives ½.",
    7: "I² = π, so the area is √π ≈ 1.7725.",
}

LABEL_AREA_WANTED = "the area we want"
LABEL_AREA_RESULT = r"area $=\sqrt{\pi}$"
