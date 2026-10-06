"""Animated proof that the integral of e^(-x^2) over the real line is sqrt(pi).

    manim -pql main.py FullProof            # preview
    manim -qh --fps 60 main.py FullProof    # 1080p60
    manim -pql main.py Step4                # one step; earlier ones replay silently
"""

import math

import numpy as np
from manim import (
    BOLD,
    DEGREES,
    DL,
    DOWN,
    DR,
    LEFT,
    ORIGIN,
    OUT,
    RIGHT,
    TAU,
    UP,
    AnnularSector,
    Arrow,
    Axes,
    Create,
    DecimalNumber,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    Line,
    MathTex,
    Rectangle,
    ReplacementTransform,
    Square,
    Surface,
    SurroundingRectangle,
    Tex,
    Text,
    ThreeDAxes,
    ThreeDScene,
    Transform,
    TransformFromCopy,
    TransformMatchingTex,
    ValueTracker,
    VGroup,
    VMobject,
    Write,
    always_redraw,
    linear,
    smooth,
)

import math_steps as ms
from theme import load_logo, load_theme


class Timing:
    BEAT = 0.5
    QUICK = 0.8
    NORMAL = 1.3
    SLOW = 2.2
    SWEEP = 3.5
    HOLD = 1.0
    LONG_HOLD = 2.0
    ORBIT = 5.0
    TITLE_WRITE = 1.8


class Layout:
    # algebra on the left, geometry pane on the right
    LEFT_EDGE = -6.75
    LEFT_WIDTH = 7.0
    EQ_Y = 1.75
    SIDEBAR_Y = (0.55, -0.35, -1.25)
    PANE_CENTER = np.array([3.75, 0.45, 0.0])
    HEADER_ANCHOR = np.array([-6.75, 3.5, 0.0])
    PROGRESS_CENTER = np.array([5.85, 3.5, 0.0])
    CAPTION_Y = -3.4
    CAPTION_MAX_WIDTH = 12.4
    FINALE_CENTER = np.array([-3.25, 0.1, 0.0])


class Geometry:
    X_MAX = 3.5  # stands in for infinity on the plots
    BELL_W, BELL_H = 5.6, 3.2
    SMALL_BELL_SCALE = 0.5
    SURFACE_XY, SURFACE_Z = 4.4, 2.4
    SURFACE_HALF = 2.4
    SURFACE_RES = 24
    GRID_HALF = 2.4
    GRID_STEP = 0.6
    N_RINGS = 6
    N_SPOKES = 12
    LINE_SAMPLES = 73
    RECT_W, RECT_H = 5.0, 4.0
    WEDGE_DR = 0.4
    WEDGE_DTHETA = 15 * DEGREES
    WEDGE_START = 38 * DEGREES
    WEDGE_R_MIN, WEDGE_R_MAX = 0.4, 1.9
    TILT_PHI = 62 * DEGREES
    FLAT_THETA = -90 * DEGREES
    ORBIT_RATE = 0.35  # rad/s
    RADIAL_PLOT_MAX = 3.2
    FINALE_SCALE = 1.7


EQ_FONT_SIZE = 44
TITLE_EQ_FONT_SIZE = 84
NUMBER_FONT_SIZE = 34
N_STEPS = 7
NUMBER_DECIMALS = 4

# grid lines are morphed pairwise, so both grids need the same count
assert Geometry.N_RINGS + Geometry.N_SPOKES == 2 * (2 * round(Geometry.GRID_HALF / Geometry.GRID_STEP) + 1)


def gaussian(x):
    return math.exp(-x * x)


def gaussian_area(half_width):
    # closed form of the integral of e^(-x^2) over [-t, t]
    return math.sqrt(math.pi) * math.erf(half_width)


def radial_area(upper):
    # integral of r e^(-r^2) over [0, t]
    return 0.5 * (1 - math.exp(-upper * upper))


def cartesian_grid(center, color):
    half, step = Geometry.GRID_HALF, Geometry.GRID_STEP
    n = round(half / step)
    ticks = [k * step for k in range(-n, n + 1)]
    sweep = np.linspace(-half, half, Geometry.LINE_SAMPLES)
    grid = VGroup()
    for x in ticks:
        grid.add(VMobject().set_points_as_corners([center + np.array([x, s, 0]) for s in sweep]))
    for y in ticks:
        grid.add(VMobject().set_points_as_corners([center + np.array([s, y, 0]) for s in sweep]))
    return grid.set_stroke(color, width=2, opacity=0.55)


def polar_blend_grid(blend, center, color):
    """Rings and spokes, drawn as a polar disc at blend=1 and as a (theta, r)
    rectangle at blend=0. The rectangle is the domain of the polar integral."""
    radius = Geometry.GRID_HALF

    def place(theta, r):
        rectangle = np.array([(theta / TAU - 0.5) * Geometry.RECT_W, (r / radius - 0.5) * Geometry.RECT_H, 0])
        disc = np.array([r * math.cos(theta), r * math.sin(theta), 0])
        return center + (1 - blend) * rectangle + blend * disc

    thetas = np.linspace(0, TAU, Geometry.LINE_SAMPLES)
    radii = np.linspace(0, radius, Geometry.LINE_SAMPLES)
    grid = VGroup()
    for k in range(1, Geometry.N_RINGS + 1):
        r = radius * k / Geometry.N_RINGS
        grid.add(VMobject().set_points_as_corners([place(t, r) for t in thetas]))
    for j in range(Geometry.N_SPOKES):
        theta = TAU * j / Geometry.N_SPOKES
        grid.add(VMobject().set_points_as_corners([place(theta, r) for r in radii]))
    return grid.set_stroke(color, width=2)


def axis_style(theme):
    return {"color": theme.muted, "stroke_width": 2, "include_ticks": False}


class MorphTex(TransformMatchingTex):
    """TransformMatchingTex whose key_map can pair parts with different glyph
    counts. The stock key_map goes through FadeTransformPieces, which raises
    for pairs like I -> I^2; here a mapped part just takes its partner's key,
    so it is paired by an ordinary Transform."""

    def __init__(self, source, target, key_map=None, **kwargs):
        aliases = key_map or {}
        for part in self.get_mobject_parts(source):
            if part.tex_string in aliases:
                part.morph_key = aliases[part.tex_string]
        super().__init__(source, target, **kwargs)

    @staticmethod
    def get_mobject_key(part):
        return getattr(part, "morph_key", part.tex_string)


class BellPlot(VGroup):
    def __init__(self, theme, variable, width, height):
        super().__init__()
        x_max = Geometry.X_MAX
        self.axes = Axes(
            x_range=[-x_max, x_max, 1],
            y_range=[0, 1.15, 0.5],
            x_length=width,
            y_length=height,
            tips=False,
            axis_config=axis_style(theme),
        )
        self.graph = self.axes.plot(gaussian, x_range=[-x_max, x_max], color=theme.integrand, stroke_width=5)
        self.variable_label = self.axes.get_x_axis_label(MathTex(variable, color=theme.text))
        self.infinity_labels = VGroup(
            *[
                MathTex(text, color=theme.muted).scale(0.6).next_to(self.axes.c2p(x, 0), DOWN, buff=0.2)
                for text, x in ((r"-\infty", -x_max), (r"\infty", x_max))
            ]
        )
        self.add(self.axes, self.graph, self.variable_label, self.infinity_labels)

    def area_between(self, low, high, color, opacity=0.4):
        return self.axes.get_area(self.graph, x_range=(low, high), color=[color, color], opacity=opacity)

    def add_full_area(self, color, opacity=0.4):
        area = self.area_between(-Geometry.X_MAX, Geometry.X_MAX, color, opacity)
        self.add(area)
        return area


class ProofScene(ThreeDScene):
    def setup(self):
        super().setup()
        self.theme = load_theme()
        self.camera.background_color = self.theme.background
        widest = MathTex(*ms.SQUARED, font_size=EQ_FONT_SIZE).width
        self.eq_scale = min(1.0, Layout.LEFT_WIDTH / widest)
        self.eq = self.header = self.caption = self.progress = None
        self.pane = []
        self.surface_group = None
        self.pinned = []
        self.tilted = False

    def styled_text(self, content, size, color, **kwargs):
        return Text(content, font=self.theme.font_family, font_size=size, color=color, **kwargs)

    def color_parts(self, mob, parts):
        assert len(mob.submobjects) == len(parts), "MathTex split differently from its parts"
        for part, piece in zip(parts, mob.submobjects, strict=True):
            if part in ms.INTEGRAND_PARTS:
                piece.set_color(self.theme.integrand)
            elif part in ms.RESULT_PARTS:
                piece.set_color(self.theme.result)
        return mob

    def typeset(self, parts, scale, y):
        mob = MathTex(*ms.disambiguate(parts), font_size=EQ_FONT_SIZE, color=self.theme.text)
        mob.scale(scale)
        self.color_parts(mob, parts)
        return mob.move_to([Layout.LEFT_EDGE, y, 0], aligned_edge=LEFT).set_y(y)

    def equation(self, parts):
        return self.typeset(parts, self.eq_scale, Layout.EQ_Y)

    def sidebar(self, parts, row, scale=0.8):
        return self.typeset(parts, self.eq_scale * scale, Layout.SIDEBAR_Y[row])

    def live_number(self, prefix, value_of, color):
        label = MathTex(prefix, font_size=NUMBER_FONT_SIZE, color=self.theme.text)
        number = DecimalNumber(0, num_decimal_places=NUMBER_DECIMALS, font_size=NUMBER_FONT_SIZE, color=color)
        number.next_to(label, RIGHT, buff=0.2)
        number.add_updater(lambda m: m.set_value(value_of()).next_to(label, RIGHT, buff=0.2))
        return VGroup(label, number)

    def callout(self, plot, label, arrow_color):
        label.next_to(plot.axes, UP, buff=0.25)
        return Arrow(
            label.get_bottom(),
            plot.axes.c2p(0.45, 0.4),
            buff=0.08,
            color=arrow_color,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.2,
        )

    def change_step_labels(self, step):
        theme = self.theme
        header = self.styled_text(ms.STEP_TITLES[step], theme.title_size, theme.text)
        header.move_to(Layout.HEADER_ANCHOR, aligned_edge=LEFT)
        caption = self.styled_text(ms.CAPTIONS[step], theme.caption_size, theme.muted)
        caption.scale_to_fit_width(min(caption.width, Layout.CAPTION_MAX_WIDTH))
        caption.move_to([0, Layout.CAPTION_Y, 0])
        dots = VGroup(
            *[Dot(radius=0.07, color=theme.result if i == step else theme.grid) for i in range(1, N_STEPS + 1)]
        )
        dots.arrange(RIGHT, buff=0.16).move_to(Layout.PROGRESS_CENTER)

        rise = UP * 0.15
        if self.header is None:
            animations = [FadeIn(header, shift=rise), FadeIn(caption, shift=rise), FadeIn(dots)]
            self.progress = dots
        else:
            animations = [
                FadeOut(self.header, shift=rise),
                FadeIn(header, shift=rise),
                FadeOut(self.caption, shift=rise),
                FadeIn(caption, shift=rise),
                Transform(self.progress, dots),
            ]
        self.header, self.caption = header, caption
        return animations

    def clear_pane(self):
        fades = [FadeOut(m) for m in self.pane]
        self.pane = []
        return fades

    def gaussian_surface(self):
        theme = self.theme
        axes = ThreeDAxes(
            x_range=[-2.8, 2.8, 1],
            y_range=[-2.8, 2.8, 1],
            z_range=[0, 1.4, 1],
            x_length=Geometry.SURFACE_XY,
            y_length=Geometry.SURFACE_XY,
            z_length=Geometry.SURFACE_Z,
            tips=False,
            axis_config=axis_style(theme),
        )
        half = Geometry.SURFACE_HALF
        surface = Surface(
            lambda u, v: axes.c2p(u, v, math.exp(-(u * u + v * v))),
            u_range=[-half, half],
            v_range=[-half, half],
            resolution=(Geometry.SURFACE_RES, Geometry.SURFACE_RES),
            fill_opacity=0.95,
            stroke_width=0.5,
            stroke_color=theme.text,
        )
        surface.set_fill_by_value(axes=axes, colorscale=[(theme.surface_low, 0), (theme.surface_high, 1)], axis=2)
        group = VGroup(axes, surface)
        group.shift(np.array([Layout.PANE_CENTER[0], 0, 0]) - axes.c2p(0, 0, 0))
        return group, np.array(axes.c2p(0, 0, 0))

    def flatten_camera(self):
        if not self.tilted:
            return
        self.surface_group.clear_updaters()
        self.move_camera(phi=0, theta=Geometry.FLAT_THETA, run_time=Timing.NORMAL)
        self.remove_fixed_in_frame_mobjects(*self.pinned)
        self.pinned = []
        self.tilted = False

    def run_steps(self, first=1, last=N_STEPS):
        for n in range(1, last + 1):
            self.next_section(f"step_{n}", skip_animations=n < first)
            getattr(self, f"step_{n}")()
        self.wait(Timing.HOLD)

    def step_1(self):
        theme = self.theme
        title = self.styled_text(ms.TITLE_CARD, 64, theme.text, weight=BOLD)
        subtitle = self.styled_text(ms.TITLE_SUBTITLE, 30, theme.muted)
        big_integral = self.color_parts(
            MathTex(*ms.INTEGRAL, font_size=TITLE_EQ_FONT_SIZE, color=theme.text), ms.INTEGRAL
        )
        card = VGroup(title, subtitle, big_integral).arrange(DOWN, buff=theme.gutter).move_to(ORIGIN)
        fading = VGroup(title, subtitle)
        logo = load_logo()
        if logo is not None:
            fading.add(logo.scale_to_fit_height(1.1).next_to(card, UP, buff=0.4))

        self.play(FadeIn(fading, shift=UP * 0.3), run_time=Timing.QUICK)
        self.play(Write(big_integral), run_time=Timing.TITLE_WRITE)
        self.wait(Timing.HOLD)

        self.eq = self.equation(ms.INTEGRAL)
        self.play(
            FadeOut(fading),
            MorphTex(big_integral, self.eq),
            *self.change_step_labels(1),
            run_time=Timing.NORMAL,
        )

        bell = BellPlot(theme, "x", Geometry.BELL_W, Geometry.BELL_H)
        bell.move_to(Layout.PANE_CENTER + UP * 0.25)
        self.play(
            Create(bell.axes), FadeIn(bell.infinity_labels), FadeIn(bell.variable_label), run_time=Timing.QUICK
        )
        self.play(Create(bell.graph), run_time=Timing.NORMAL)

        reach = ValueTracker(0)

        def shaded():
            t = max(reach.get_value(), 0.02)
            return bell.area_between(-t, t, theme.integrand)

        area = always_redraw(shaded)
        readout = self.live_number(r"\text{area}\approx", lambda: gaussian_area(reach.get_value()), theme.integrand)
        readout.next_to(bell.axes, DOWN, buff=0.75)
        note = self.styled_text(ms.LABEL_AREA_WANTED, 26, theme.integrand)
        pointer = self.callout(bell, note, theme.muted)
        self.add(area)
        self.play(FadeIn(note), GrowArrow(pointer), FadeIn(readout), run_time=Timing.QUICK)
        self.play(reach.animate.set_value(Geometry.X_MAX), run_time=Timing.SWEEP, rate_func=smooth)

        # swap the live area for a static one and re-add the plot as one group
        self.remove(area)
        bell.add_full_area(theme.integrand)
        self.remove(*bell.submobjects)
        self.add(bell)
        self.wait(Timing.HOLD)
        self.play(FadeOut(note), FadeOut(pointer), FadeOut(readout), run_time=Timing.QUICK)
        self.pane = [bell]
        self.bell = bell

    def step_2(self):
        theme = self.theme
        squared = self.equation(ms.SQUARED)
        bell_x = self.bell
        bell_y = BellPlot(theme, "y", Geometry.BELL_W, Geometry.BELL_H)
        bell_y.add_full_area(theme.integrand)
        bell_y.scale(Geometry.SMALL_BELL_SCALE).move_to(Layout.PANE_CENTER + DOWN * 1.2)
        times = MathTex(r"\times", font_size=48, color=theme.muted).move_to(Layout.PANE_CENTER + UP * 0.1)

        self.play(
            *self.change_step_labels(2),
            MorphTex(self.eq, squared, key_map={ms.I_PLAIN: ms.I_SQUARED}),
            bell_x.animate.scale(Geometry.SMALL_BELL_SCALE).move_to(Layout.PANE_CENTER + UP * 1.45),
            TransformFromCopy(bell_x, bell_y),
            run_time=Timing.SLOW,
        )
        self.eq = squared
        self.play(FadeIn(times, scale=0.6), run_time=Timing.QUICK)
        self.wait(Timing.LONG_HOLD)
        self.pane = [bell_x, bell_y, times]

    def step_3(self):
        theme = self.theme
        iterated, over_plane = self.equation(ms.ITERATED), self.equation(ms.OVER_PLANE)

        self.play(
            *self.change_step_labels(3),
            MorphTex(self.eq, iterated),
            *self.clear_pane(),
            run_time=Timing.NORMAL,
        )
        self.eq = iterated

        self.surface_group, pivot = self.gaussian_surface()
        formula = MathTex(r"z = e^{-(x^2+y^2)}", font_size=36, color=theme.text)
        formula.move_to([Layout.PANE_CENTER[0], -2.45, 0])
        self.play(
            MorphTex(self.eq, over_plane),
            FadeIn(self.surface_group),
            FadeIn(formula),
            run_time=Timing.SLOW,
        )
        self.eq = over_plane
        self.wait(Timing.BEAT)

        # while the camera tilts, the text has to stay flat on screen
        self.pinned = [self.eq, self.header, self.caption, self.progress, formula]
        self.add_fixed_in_frame_mobjects(*self.pinned)
        self.tilted = True
        self.move_camera(phi=Geometry.TILT_PHI, theta=Geometry.FLAT_THETA, run_time=Timing.SLOW)
        # the surface is symmetric about its axis, so spinning it reads as an orbiting camera
        self.surface_group.add_updater(
            lambda m, dt: m.rotate(Geometry.ORBIT_RATE * dt, axis=OUT, about_point=pivot)
        )
        self.wait(Timing.ORBIT)
        self.pane = [self.surface_group, formula]

    def step_4(self):
        theme = self.theme
        center = Layout.PANE_CENTER
        self.flatten_camera()

        cartesian = cartesian_grid(center, theme.muted)
        polar = polar_blend_grid(1, center, theme.geometry)
        cell = Square(
            side_length=Geometry.GRID_STEP, stroke_width=0, fill_color=theme.result, fill_opacity=0.7
        ).move_to(center + np.array([0.9, 0.9, 0]))
        cell_area = MathTex(r"\text{area}=", r"dx\,dy", font_size=36, color=theme.text)
        cell_area.move_to(center + DOWN * 2.75)

        self.play(
            *self.change_step_labels(4),
            *self.clear_pane(),
            Create(cartesian, lag_ratio=0.03),
            run_time=Timing.NORMAL,
        )
        self.play(FadeIn(cell, scale=0.5), FadeIn(cell_area), run_time=Timing.QUICK)
        self.wait(Timing.BEAT)

        coordinates = self.sidebar(ms.POLAR_SUBSTITUTIONS[0], 0)
        self.play(
            FadeIn(coordinates, shift=RIGHT * 0.3),
            FadeOut(cell),
            ReplacementTransform(cartesian, polar),
            run_time=Timing.SLOW,
        )

        radius_rule = self.sidebar(ms.POLAR_SUBSTITUTIONS[1], 1)
        radial = self.equation(ms.OVER_PLANE_RADIAL)
        self.play(FadeIn(radius_rule, shift=RIGHT * 0.3), MorphTex(self.eq, radial), run_time=Timing.NORMAL)
        self.eq = radial
        self.wait(Timing.BEAT)

        measure_rule = self.sidebar(ms.POLAR_SUBSTITUTIONS[2], 2)
        r_now = ValueTracker(Geometry.WEDGE_R_MIN)
        wedge = always_redraw(
            lambda: AnnularSector(
                inner_radius=r_now.get_value(),
                outer_radius=r_now.get_value() + Geometry.WEDGE_DR,
                angle=Geometry.WEDGE_DTHETA,
                start_angle=Geometry.WEDGE_START,
                arc_center=center,
                color=theme.result,
                fill_opacity=0.85,
                stroke_width=0,
            )
        )
        wedge_area = MathTex(r"\text{area}=", r"r", r"\,dr", r"\,d\theta", font_size=36, color=theme.text)
        wedge_area.move_to(cell_area)
        polar_measure = self.equation(ms.POLAR_MEASURE)
        self.add(wedge)
        self.play(
            FadeIn(measure_rule, shift=RIGHT * 0.3),
            MorphTex(self.eq, polar_measure),
            MorphTex(cell_area, wedge_area),
            run_time=Timing.NORMAL,
        )
        self.eq = polar_measure
        box = SurroundingRectangle(
            self.eq[ms.JACOBIAN_INDEX], color=theme.result, buff=0.1, corner_radius=theme.box_radius
        )
        self.play(Create(box), run_time=Timing.QUICK)
        self.play(r_now.animate.set_value(Geometry.WEDGE_R_MAX), run_time=Timing.SWEEP, rate_func=linear)
        self.wait(Timing.BEAT)

        limits = self.equation(ms.POLAR_LIMITS)
        self.play(
            MorphTex(self.eq, limits),
            *[FadeOut(m) for m in (box, coordinates, radius_rule, measure_rule, wedge, wedge_area)],
            run_time=Timing.NORMAL,
        )
        self.remove(wedge)
        self.eq = limits
        self.polar = polar
        self.pane = [polar]

    def step_5(self):
        theme = self.theme
        center = Layout.PANE_CENTER
        blend = ValueTracker(1)
        grid = always_redraw(lambda: polar_blend_grid(blend.get_value(), center, theme.geometry))
        self.remove(self.polar)  # same picture as the blended grid at blend=1
        self.add(grid)

        separated = self.equation(ms.SEPARATED)
        self.play(*self.change_step_labels(5), MorphTex(self.eq, separated), run_time=Timing.NORMAL)
        self.eq = separated
        self.play(blend.animate.set_value(0), run_time=Timing.SWEEP, rate_func=smooth)
        self.remove(grid)
        flat = polar_blend_grid(0, center, theme.geometry)
        self.add(flat)

        self.frame = Rectangle(
            width=Geometry.RECT_W, height=Geometry.RECT_H, color=theme.muted, stroke_width=2
        ).move_to(center)
        self.theta_label = MathTex(r"\theta:\ 0 \to 2\pi", font_size=34, color=theme.text)
        self.theta_label.next_to(self.frame, DOWN, buff=0.25)
        self.r_label = MathTex(r"r:\ 0 \to \infty", font_size=34, color=theme.text)
        self.r_label.rotate(90 * DEGREES).next_to(self.frame, LEFT, buff=0.25)
        self.play(Create(self.frame), FadeIn(self.theta_label), FadeIn(self.r_label), run_time=Timing.NORMAL)
        self.wait(Timing.LONG_HOLD)
        self.pane = [flat, self.frame, self.theta_label, self.r_label]

    def step_6(self):
        theme = self.theme
        center = Layout.PANE_CENTER

        angle_done = self.equation(ms.ANGLE_EVALUATED)
        bottom_edge = Line(
            self.frame.get_corner(DL), self.frame.get_corner(DR), color=theme.result, stroke_width=8
        )
        theta_total = MathTex(r"\int_0^{2\pi}d\theta = 2\pi", font_size=34, color=theme.result)
        theta_total.next_to(self.frame, DOWN, buff=0.45)
        self.play(
            *self.change_step_labels(6),
            MorphTex(self.eq, angle_done, key_map={ms.INT_THETA: ms.TWO_PI}),
            Create(bottom_edge),
            ReplacementTransform(self.theta_label, theta_total),
            run_time=Timing.SLOW,
        )
        self.eq = angle_done
        self.wait(Timing.HOLD)

        plot = Axes(
            x_range=[0, Geometry.RADIAL_PLOT_MAX, 1],
            y_range=[0, 0.5, 0.25],
            x_length=5.4,
            y_length=3.0,
            tips=False,
            axis_config=axis_style(theme),
        ).move_to(center + UP * 0.2)
        curve = plot.plot(
            lambda r: r * math.exp(-r * r),
            x_range=[0, Geometry.RADIAL_PLOT_MAX],
            color=theme.integrand,
            stroke_width=5,
        )
        curve_label = MathTex(r"r\,e^{-r^2}", font_size=36, color=theme.integrand).move_to(plot.c2p(2.2, 0.36))
        r_axis_label = plot.get_x_axis_label(MathTex("r", color=theme.text))
        upper = ValueTracker(0)
        area = always_redraw(
            lambda: plot.get_area(
                curve,
                x_range=(0, max(upper.get_value(), 0.02)),
                color=[theme.integrand, theme.integrand],
                opacity=0.4,
            )
        )
        readout = self.live_number(r"\text{area}=", lambda: radial_area(upper.get_value()), theme.result)
        readout.next_to(plot, DOWN, buff=0.6)

        rule = self.sidebar(ms.U_RULE, 0)
        chain = self.sidebar(ms.RADIAL, 2, scale=0.95)
        rectangle_pieces = (self.frame, self.r_label, theta_total, bottom_edge, self.pane[0])
        self.play(
            *[FadeOut(m) for m in rectangle_pieces],
            Create(plot),
            FadeIn(r_axis_label),
            run_time=Timing.NORMAL,
        )
        self.add(area)
        self.play(
            Create(curve),
            FadeIn(curve_label),
            FadeIn(rule, shift=RIGHT * 0.3),
            TransformFromCopy(VGroup(*self.eq[ms.RADIAL_SLICE]), chain),
            FadeIn(readout),
            run_time=Timing.SLOW,
        )
        self.play(upper.animate.set_value(Geometry.RADIAL_PLOT_MAX), run_time=Timing.SWEEP, rate_func=smooth)

        substitution = (
            (ms.RADIAL_IN_U, {ms.E_R: ms.E_U, ms.DR: ms.DU}),
            (ms.RADIAL_ANTIDERIVATIVE, {}),
            (ms.RADIAL_AT_LIMITS, {}),
            (ms.RADIAL_VALUE, {}),
        )
        for parts, key_map in substitution:
            next_chain = self.sidebar(parts, 2, scale=0.95)
            self.play(MorphTex(chain, next_chain, key_map=key_map), run_time=Timing.NORMAL)
            chain = next_chain
            self.wait(Timing.BEAT)

        self.pane = [plot, curve, curve_label, r_axis_label, area, readout]
        self.rule, self.chain = rule, chain

    def step_7(self):
        theme = self.theme
        both_evaluated, equals_pi = self.equation(ms.BOTH_EVALUATED), self.equation(ms.EQUALS_PI)
        root_both_sides, answer = self.equation(ms.ROOT_BOTH_SIDES), self.equation(ms.ANSWER)

        self.play(
            *self.change_step_labels(7),
            MorphTex(self.eq, both_evaluated),
            FadeOut(self.chain),
            FadeOut(self.rule),
            *self.clear_pane(),
            run_time=Timing.SLOW,
        )
        self.eq = both_evaluated
        self.wait(Timing.BEAT)

        bell = BellPlot(theme, "x", Geometry.BELL_W, Geometry.BELL_H)
        bell.move_to(Layout.PANE_CENTER + UP * 0.25)
        area = bell.add_full_area(theme.result, opacity=0.6)
        self.play(FadeIn(bell, shift=UP * 0.2), run_time=Timing.NORMAL)

        self.play(MorphTex(self.eq, equals_pi, key_map={ms.TWO_PI: ms.PI}), run_time=Timing.NORMAL)
        self.eq = equals_pi
        self.wait(Timing.BEAT)

        root_keys = {ms.I_SQUARED: ms.SQRT_I_SQUARED, ms.PI: ms.SQRT_PI}
        self.play(MorphTex(self.eq, root_both_sides, key_map=root_keys), run_time=Timing.NORMAL)
        self.eq = root_both_sides
        self.play(MorphTex(self.eq, answer, key_map={ms.SQRT_I_SQUARED: ms.I_PLAIN}), run_time=Timing.NORMAL)
        self.eq = answer

        label = Tex(ms.LABEL_AREA_RESULT, font_size=40, color=theme.result)
        pointer = self.callout(bell, label, theme.result)
        approx = MathTex(r"\approx 1.7725", font_size=NUMBER_FONT_SIZE, color=theme.text)
        approx.next_to(bell.axes, DOWN, buff=0.75)
        box = SurroundingRectangle(self.eq, color=theme.result, buff=0.2, corner_radius=theme.box_radius)
        self.play(Create(box), FadeIn(label), GrowArrow(pointer), FadeIn(approx), run_time=Timing.NORMAL)
        self.play(
            VGroup(self.eq, box).animate.scale(Geometry.FINALE_SCALE).move_to(Layout.FINALE_CENTER),
            run_time=Timing.SLOW,
        )
        self.play(
            Indicate(self.eq[2], color=theme.result, scale_factor=1.25),
            Indicate(area, color=theme.result, scale_factor=1.04),
            run_time=Timing.SLOW,
        )
        self.wait(Timing.LONG_HOLD)
        self.pane = [bell, label, pointer, approx, box]


class FullProof(ProofScene):
    def construct(self):
        self.run_steps()


class Step1(ProofScene):
    def construct(self):
        self.run_steps(1, 1)


class Step2(ProofScene):
    def construct(self):
        self.run_steps(2, 2)


class Step3(ProofScene):
    def construct(self):
        self.run_steps(3, 3)


class Step4(ProofScene):
    def construct(self):
        self.run_steps(4, 4)


class Step5(ProofScene):
    def construct(self):
        self.run_steps(5, 5)


class Step6(ProofScene):
    def construct(self):
        self.run_steps(6, 6)


class Step7(ProofScene):
    def construct(self):
        self.run_steps(7, 7)
