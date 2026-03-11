"""
Transfer Learning — Lecture 7: CNNs and Transfer Learning
Example: ResNet pretrained on ImageNet → Класифікатор скріншотів гри

Scenes
------
TransferLearningScene  — full step-by-step animation

Render
------
manim -pqm transfer_learning.py TransferLearningScene   # medium, preview
manim -pqh transfer_learning.py TransferLearningScene   # high quality
manim --format gif -ql transfer_learning.py TransferLearningScene
"""

from manim import *

# ── palette ───────────────────────────────────────────────────────────────────
FROZEN_COLOR   = BLUE_D
HEAD_NEW_COLOR = GREEN_D
BG_COLOR       = "#12122a"

# PT Sans was designed by ParaType for Cyrillic — correct kerning for Ukrainian
UA_FONT = "PT Sans"

# ── network geometry ──────────────────────────────────────────────────────────
R   = 0.18    # neuron radius
BUF = 0.09    # gap between adjacent neurons in a layer

# x-positions of each layer column (input, conv1, conv2, fc, output)
XS = [-5.0, -3.1, -1.3, 0.5, 2.8]
# neuron count per column
NS = [4,    6,    5,    4,   7]

# ── class labels ──────────────────────────────────────────────────────────────
# ImageNet representative classes shown on the old head
OLD_LABELS = ["кіт", "собака", "авто", "літак", "квітка", "будинок", "птах"]
# New target task: game screenshot categories
NEW_LABELS = ["Головне меню", "Ігровий процес", "Інвентар", "Карта", "Заставка"]
# Column header labels
COL_NAMES = ["Вхідний\nшар", "Згорт.\nблок 1", "Згорт.\nблок 2", "FC\nшар", "Вихідний\nшар"]

# ── factory helpers ───────────────────────────────────────────────────────────

def neuron(color=WHITE, fill_opacity=0.9):
    return Circle(
        radius=R, fill_color=color, fill_opacity=fill_opacity,
        stroke_color=WHITE, stroke_width=1.5,
    )


def layer_col(n: int, color=WHITE) -> VGroup:
    """Vertical column of n neurons."""
    g = VGroup(*[neuron(color) for _ in range(n)])
    g.arrange(DOWN, buff=BUF)
    return g


def connections(col_a: VGroup, col_b: VGroup,
                color=GREY, opacity=0.40, width=1.1) -> VGroup:
    """All-to-all connections between two neuron columns."""
    return VGroup(*[
        Line(
            a.get_center(), b.get_center(),
            stroke_color=color, stroke_opacity=opacity, stroke_width=width,
        )
        for a in col_a for b in col_b
    ])


def side_labels(col: VGroup, texts: list, color=WHITE, fs=13) -> VGroup:
    """Short text labels to the right of each neuron."""
    g = VGroup()
    for n, t in zip(col, texts):
        lbl = Text(t, font_size=fs, color=color, font=UA_FONT)
        lbl.next_to(n, RIGHT, buff=0.15)
        g.add(lbl)
    return g


def col_caption(col: VGroup, text: str, color=GREY_A) -> Text:
    t = Text(text, font_size=11, color=color, font=UA_FONT)
    t.next_to(col, DOWN, buff=0.18)
    return t


def ph_label(text: str) -> Text:
    """Phase heading at top of screen."""
    lbl = Text(text, font_size=17, color=WHITE, font=UA_FONT)
    lbl.to_edge(UP, buff=0.82)
    return lbl


# ── main scene ────────────────────────────────────────────────────────────────

class TransferLearningScene(Scene):
    """
    Step-by-step transfer learning animation.
    Source:  ResNet на ImageNet (1000 класів)
    Target:  Класифікатор скріншотів гри (5 класів)
    """

    # ── construct ────────────────────────────────────────────────────────────

    def construct(self):
        self.camera.background_color = BG_COLOR

        # Build all network objects once (not yet shown)
        self.cols = []       # neuron columns
        self.conns = []      # connection VGroups between adjacent columns
        self.captions = []   # column caption texts

        for i, (x, n, name) in enumerate(zip(XS, NS, COL_NAMES)):
            col = layer_col(n)
            col.move_to([x, 0, 0])
            self.cols.append(col)
            self.captions.append(col_caption(col, name))

        for a, b in zip(self.cols[:-1], self.cols[1:]):
            self.conns.append(connections(a, b))

        # ImageNet head labels (shown in phase 1, removed in phase 3)
        self.imagenet_lbls = side_labels(self.cols[-1], OLD_LABELS, GREY_A, 12)
        self.extra_lbl = Text("⋯ ще 993 класи", font_size=10, color=GREY_B, font=UA_FONT)
        self.extra_lbl.next_to(self.cols[-1][-1], DOWN + RIGHT * 0.3, buff=0.08)

        # Run phases sequentially
        self._title()
        self._phase1_pretrained()
        self._phase2_freeze()
        self._phase3_replace_head()
        self._phase4_finetune()
        self._phase5_summary()

    # ── phases ────────────────────────────────────────────────────────────────

    def _title(self):
        title = Text("Трансферне навчання", font_size=44, color=WHITE, weight=BOLD, font=UA_FONT)
        sub = Text(
            "від ImageNet до класифікатора скріншотів гри",
            font_size=20, color=GREY_A, font=UA_FONT,
        )
        sub.next_to(title, DOWN, buff=0.22)

        self.play(Write(title), run_time=1.3)
        self.play(FadeIn(sub))
        self.wait(0.8)
        self.play(VGroup(title, sub).animate.scale(0.42).to_corner(UL))

    # ─────────────────────────────────────────────────────────────────────────
    def _phase1_pretrained(self):
        """Show the full pretrained network with ImageNet output classes."""
        ph = ph_label("Крок 1: Попередньо навчена модель (ResNet, ImageNet, 1000 класів)")
        self.play(FadeIn(ph, shift=DOWN * 0.12))

        # Small image thumbnail on the left of the input column
        img = Rectangle(
            width=0.70, height=0.70,
            fill_color=GREY_D, fill_opacity=1.0,
            stroke_color=WHITE, stroke_width=1.5,
        )
        px_colors = [RED_D, GREEN_D, BLUE_D, ORANGE, TEAL_D, PURPLE_D, YELLOW_D, PINK]
        pixels = VGroup(*[
            Square(side_length=0.155, fill_opacity=0.92, stroke_width=0, fill_color=c)
            for c in px_colors
        ]).arrange_in_grid(rows=2, cols=4, buff=0.01)
        pixels.move_to(img)
        img_grp = VGroup(img, pixels)
        img_grp.next_to(self.cols[0], LEFT, buff=0.30)
        img_cap = Text("Вхідне\nзображення", font_size=11, color=GREY_A, font=UA_FONT)
        img_cap.next_to(img_grp, DOWN, buff=0.1)
        self.img_grp = img_grp  # keep reference

        # Connections appear first (behind neurons)
        self.play(
            LaggedStart(*[Create(c) for c in self.conns], lag_ratio=0.14),
            run_time=1.5,
        )
        # Neurons and image
        self.play(
            FadeIn(img_grp), FadeIn(img_cap),
            LaggedStart(
                *[LaggedStart(*[GrowFromCenter(n) for n in col], lag_ratio=0.06)
                  for col in self.cols],
                lag_ratio=0.12,
            ),
            run_time=2.0,
        )
        # Column captions
        self.play(
            LaggedStart(*[FadeIn(cap) for cap in self.captions], lag_ratio=0.1),
            run_time=0.8,
        )
        # ImageNet output labels + "…993 more"
        src_banner = Text(
            "Джерело: ImageNet — 1.2 млн фотографій реальних об'єктів",
            font_size=13, color=YELLOW_D, font=UA_FONT,
        ).to_edge(DOWN, buff=0.32)

        self.play(
            LaggedStart(*[Write(l) for l in self.imagenet_lbls], lag_ratio=0.10),
            FadeIn(self.extra_lbl),
            FadeIn(src_banner),
            run_time=1.4,
        )
        self.wait(1.2)
        self.play(FadeOut(ph), FadeOut(src_banner))

    # ─────────────────────────────────────────────────────────────────────────
    def _phase2_freeze(self):
        """Colour frozen columns blue; show brace + lock annotations."""
        ph = ph_label("Крок 2: Заморожуємо базові шари — ваги не зміняться під час навчання")
        self.play(FadeIn(ph, shift=DOWN * 0.12))

        frozen_cols  = self.cols[1:4]   # conv1, conv2, fc
        frozen_conns = self.conns[0:3]  # input→conv1, conv1→conv2, conv2→fc

        # Colour neurons blue
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(*[n.animate.set_fill(FROZEN_COLOR, opacity=0.92) for n in col])
                    for col in frozen_cols
                ],
                lag_ratio=0.25,
            ),
            AnimationGroup(*[c.animate.set_stroke(color=BLUE_E, opacity=0.20) for c in frozen_conns]),
            run_time=1.3,
        )

        # Horizontal brace spanning all three frozen columns
        frozen_grp = VGroup(*frozen_cols)
        brace = Brace(frozen_grp, UP, color=FROZEN_COLOR)
        brace_txt = Text(
            "Заморожені шари — витяг загальних ознак (ребра, текстури, форми)",
            font_size=12, color=FROZEN_COLOR, font=UA_FONT,
        )
        brace_txt.next_to(brace, UP, buff=0.10)

        # Small "[≠]" lock badges under each frozen column
        locks = VGroup(*[
            Text("[frozen]", font_size=9, color=FROZEN_COLOR, font=UA_FONT).next_to(col, DOWN, buff=0.10)
            for col in frozen_cols
        ])

        self.play(GrowFromCenter(brace), Write(brace_txt))
        self.play(LaggedStart(*[FadeIn(lk) for lk in locks], lag_ratio=0.18))
        self.wait(1.0)

        self.play(FadeOut(ph), FadeOut(brace), FadeOut(brace_txt), FadeOut(locks))

    # ─────────────────────────────────────────────────────────────────────────
    def _phase3_replace_head(self):
        """Dramatic cut + replace of the output column (1000 → 5 classes)."""
        ph = ph_label("Крок 3: Відрізаємо стару «голову» — замінюємо 1000 класів на 5")
        self.play(FadeIn(ph, shift=DOWN * 0.12))

        l_old = self.cols[-1]
        c_old = self.conns[-1]
        x_cut = (XS[-2] + XS[-1]) / 2   # midpoint between fc and output

        # Dashed cut line + label
        cut_line = DashedLine(
            [x_cut, 3.3, 0], [x_cut, -3.3, 0],
            color=RED, stroke_width=2.5, dash_length=0.17,
        )
        cut_lbl = Text("cut", font_size=21, color=RED, weight=BOLD, font=UA_FONT)
        cut_lbl.move_to([x_cut, 3.55, 0])

        self.play(Create(cut_line), Write(cut_lbl), run_time=0.75)
        self.wait(0.3)

        # Flash old head red to emphasise removal
        self.play(
            AnimationGroup(*[n.animate.set_fill(RED_D, opacity=0.9) for n in l_old]),
            run_time=0.4,
        )

        # Fade out old head + its connections + labels
        self.play(
            FadeOut(l_old), FadeOut(c_old),
            FadeOut(self.imagenet_lbls), FadeOut(self.extra_lbl),
            FadeOut(cut_line), FadeOut(cut_lbl),
            FadeOut(self.captions[-1]),
            run_time=0.7,
        )

        # ── Build new head (5 neurons) ────────────────────────────────────────
        self.new_col = layer_col(len(NEW_LABELS), HEAD_NEW_COLOR)
        self.new_col.move_to([XS[-1], 0, 0])

        self.new_conns = connections(
            self.cols[-2], self.new_col, color=GREEN_E, opacity=0.22, width=0.65,
        )
        self.game_lbls = side_labels(self.new_col, NEW_LABELS, HEAD_NEW_COLOR, 13)

        new_cap = col_caption(self.new_col, "Нова\nголова", color=HEAD_NEW_COLOR)

        # Target task banner
        tgt_banner = Text(
            "Ціль: класифікація скріншотів гри — 5 класів",
            font_size=13, color=HEAD_NEW_COLOR,
            font=UA_FONT,
        ).to_edge(DOWN, buff=0.32)

        self.play(
            Create(self.new_conns),
            LaggedStart(*[GrowFromCenter(n) for n in self.new_col], lag_ratio=0.10),
            FadeIn(new_cap),
            FadeIn(tgt_banner),
            run_time=1.2,
        )
        self.play(
            LaggedStart(*[Write(l) for l in self.game_lbls], lag_ratio=0.12),
            run_time=1.0,
        )
        self.wait(1.0)
        self.play(FadeOut(ph), FadeOut(tgt_banner))

    # ─────────────────────────────────────────────────────────────────────────
    def _phase4_finetune(self):
        """Show fine-tuning: gradient flows only through the new head."""
        ph = ph_label("Крок 4: Дообучення — лише нова голова оновлює ваги")
        self.play(FadeIn(ph, shift=DOWN * 0.12))

        frozen_cols = self.cols[1:4]

        small_data = Text(
            "Новий датасет: ~500 скріншотів гри",
            font_size=13, color=HEAD_NEW_COLOR,
            font=UA_FONT
        ).to_edge(DOWN, buff=0.32)
        self.play(FadeIn(small_data))

        # 3 forward + backward passes
        for _ in range(3):
            # Forward pass: subtle white shimmer across ALL neurons left→right
            self.play(
                LaggedStart(
                    *[Indicate(n, color=WHITE, scale_factor=1.04)
                      for col in (self.cols[0], *frozen_cols) for n in col],
                    lag_ratio=0.015,
                ),
                run_time=0.55,
            )
            # Gradient update: bright pulse on new head only
            self.play(
                LaggedStart(
                    *[Indicate(n, color=HEAD_NEW_COLOR, scale_factor=1.15)
                      for n in self.new_col],
                    lag_ratio=0.10,
                ),
                run_time=0.55,
            )
            # Frozen layers stay still — brief blue flash to emphasise "no update"
            self.play(
                AnimationGroup(
                    *[Indicate(n, color=BLUE_E, scale_factor=1.03)
                      for col in frozen_cols for n in col],
                ),
                run_time=0.35,
            )

        self.wait(0.4)
        self.play(FadeOut(ph), FadeOut(small_data))

    # ─────────────────────────────────────────────────────────────────────────
    def _phase5_summary(self):
        """Final state with annotations and advantages box."""
        ph = ph_label("Результат: модель адаптована для нової задачі")
        self.play(FadeIn(ph, shift=DOWN * 0.12))

        # Brace above frozen columns
        frozen_grp = VGroup(*self.cols[1:4])
        brace_frz = Brace(frozen_grp, UP, color=FROZEN_COLOR)
        t_frz = Text(
            "Базова мережа — загальні ознаки",
            font_size=12, color=FROZEN_COLOR,
            font=UA_FONT
        )
        t_frz.next_to(brace_frz, UP, buff=0.10)

        # Brace below new head
        brace_new = Brace(self.new_col, DOWN, color=HEAD_NEW_COLOR)
        t_new = Text("Нова голова (5 ігрових класів)",
                     font_size=12,
                     color=HEAD_NEW_COLOR,
                     font=UA_FONT
        )
        t_new.next_to(brace_new, DOWN, buff=0.10)

        # Advantages box — bottom centre
        adv_txt = Text(
            "Переваги трансферного навчання:\n"
            "  + ~500 прикладів замість 1.2 млн\n"
            "  + Хвилини навчання замість тижнів\n"
            "  + Вища точність на малому датасеті",
            font_size=11,
            color=WHITE,
            line_spacing=1.35,
            font=UA_FONT
        )
        adv_bg = SurroundingRectangle(
            adv_txt, color=GOLD, fill_color=GREY_E,
            fill_opacity=0.92, buff=0.20, corner_radius=0.12,
        )
        adv = VGroup(adv_bg, adv_txt)
        adv.to_edge(DOWN, buff=0.28)

        self.play(
            GrowFromCenter(brace_frz), Write(t_frz),
            GrowFromCenter(brace_new), Write(t_new),
        )
        self.play(FadeIn(adv, shift=UP * 0.18))
        self.wait(4.0)
