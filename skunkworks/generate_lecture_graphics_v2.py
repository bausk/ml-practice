#!/usr/bin/env python3
"""Generate Ukrainian lecture graphics v2 – improved quality."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch, Circle
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
import os

OUTPUT_DIR = "6S191_lecture_graphics_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Refined palette ──────────────────────────────────────────────────────────
C_ENCODER  = '#4CAF7D'   # slightly warmer green
C_DECODER  = '#8E6CB8'   # richer purple
C_LATENT   = '#4A90D9'   # vivid blue
C_MU       = '#F0A030'   # warm amber
C_SIGMA    = '#E06850'   # warm coral
C_DISC     = '#4CAF7D'
C_GEN      = '#8E6CB8'
C_TITLE    = '#1C2331'   # near-black navy
C_BG       = '#FFFFFF'
C_BORDER   = '#D0D5DD'
C_ACCENT   = '#2B6CB0'   # deeper blue accent
C_DARK     = '#2D3748'
C_LIGHT_BG = '#EDF2F7'
C_WARM     = '#FFF8F0'   # warm card bg
C_RED      = '#C53030'
C_GREEN    = '#276749'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 14,
    'mathtext.fontset': 'dejavusans',
})

W, H, DPI = 13.33, 7.5, 200


def save(name):
    plt.savefig(f"{OUTPUT_DIR}/{name}.png", dpi=DPI, bbox_inches='tight',
                facecolor=C_BG, edgecolor='none', pad_inches=0.2)
    plt.close()
    print(f"  ✓ {name}.png")


def new_fig(title=None, subtitle=None, title_size=22):
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    fig.patch.set_facecolor(C_BG)
    y = 0.96
    if title:
        ax.text(0.5, y, title, ha='center', va='top',
                fontsize=title_size, fontweight='bold', color=C_TITLE)
        y -= 0.06
    if subtitle:
        ax.text(0.5, y, subtitle, ha='center', va='top',
                fontsize=14, color='#4A5568', multialignment='center')
    return fig, ax


# ── Drawing primitives ───────────────────────────────────────────────────────

def rbox(ax, cx, cy, w, h, fc, label='', fs=13, tc='white', ec='none', lw=1.5,
         alpha=1.0, bold=True, shadow=False, pad=0.012):
    if shadow:
        sh = FancyBboxPatch((cx - w/2 + 0.003, cy - h/2 - 0.004), w, h,
                            boxstyle=f"round,pad={pad}", facecolor='#00000011',
                            edgecolor='none')
        ax.add_patch(sh)
    p = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle=f"round,pad={pad}", facecolor=fc,
                       edgecolor=ec, linewidth=lw, alpha=alpha)
    ax.add_patch(p)
    if label:
        ax.text(cx, cy, label, ha='center', va='center', fontsize=fs,
                color=tc, fontweight='bold' if bold else 'normal',
                multialignment='center')


def trap(ax, cx, cy, w, h, fc, label='', fs=17, wide_side='left', shadow=False):
    """Trapezoid with optional shadow."""
    pad = h * 0.30
    if wide_side == 'left':
        pts = [[cx-w/2, cy+h/2], [cx+w/2, cy+pad],
               [cx+w/2, cy-pad], [cx-w/2, cy-h/2]]
    else:
        pts = [[cx-w/2, cy+pad], [cx+w/2, cy+h/2],
               [cx+w/2, cy-h/2], [cx-w/2, cy-pad]]
    if shadow:
        sp = [[x+0.004, y-0.005] for x, y in pts]
        ax.add_patch(Polygon(sp, closed=True, fc='#00000011', ec='none'))
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor='none', alpha=0.90)
    ax.add_patch(poly)
    if label:
        ax.text(cx, cy, label, ha='center', va='center', fontsize=fs,
                color='white', fontweight='bold', multialignment='center')


def arr(ax, x0, y0, x1, y1, color='#718096', lw=2.0, head=16, dashed=False):
    style = '->' if not dashed else '->'
    ls = '--' if dashed else '-'
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                mutation_scale=head, linestyle=ls,
                                connectionstyle='arc3,rad=0.0'))


def digit_placeholder(ax, cx, cy, sz=0.08, var='', reconstruct=False):
    """Draw a stylized handwritten digit '2' as an image placeholder."""
    # Background square
    ax.add_patch(FancyBboxPatch(
        (cx - sz/2, cy - sz/2), sz, sz,
        boxstyle="round,pad=0.005", facecolor='#1A1A2E' if not reconstruct else '#3A3A4E',
        edgecolor='#555', linewidth=1.2))
    # Stylized "2" path (in relative coords)
    t = np.linspace(0, 1, 50)
    # Top arc of "2"
    arc_x = cx - sz*0.18 + sz*0.36 * np.cos(np.pi * (1 - t[:25]))
    arc_y = cy + sz*0.05 + sz*0.22 * np.sin(np.pi * (1 - t[:25]))
    # Diagonal stroke
    diag_x = np.linspace(cx + sz*0.18, cx - sz*0.22, 15)
    diag_y = np.linspace(cy + sz*0.05, cy - sz*0.28, 15)
    # Bottom line
    bot_x = np.linspace(cx - sz*0.22, cx + sz*0.22, 10)
    bot_y = np.full(10, cy - sz*0.28)
    xs = np.concatenate([arc_x, diag_x, bot_x])
    ys = np.concatenate([arc_y, diag_y, bot_y])
    c = '#DDDDDD' if not reconstruct else '#AAAACC'
    ax.plot(xs, ys, color=c, lw=2.5, solid_capstyle='round')
    if var:
        ax.text(cx, cy - sz/2 - 0.032, var, ha='center', fontsize=15,
                fontstyle='italic', color=C_DARK)


def section_divider(ax, x=0.5, y0=0.08, y1=0.88):
    ax.plot([x, x], [y0, y1], color=C_BORDER, lw=1.5, ls='--', alpha=0.7)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Supervised vs Unsupervised Learning
# ══════════════════════════════════════════════════════════════════════════════
def fig1():
    fig, ax = new_fig("Навчання з учителем vs. Навчання без учителя")
    section_divider(ax, 0.5, 0.06, 0.87)

    # ── Left column ──
    ax.text(0.25, 0.86, "Навчання з учителем", ha='center',
            fontsize=18, fontweight='bold', color=C_ACCENT)

    entries_l = [
        ("Дані:", r"$(x, y)$ — де $x$ дані, $y$ мітка"),
        ("Мета:", r"Навчити функцію $x \rightarrow y$"),
        ("Приклади:", "Класифікація, регресія,\nрозпізнавання об'єктів"),
    ]
    y = 0.74
    for k, v in entries_l:
        ax.text(0.06, y, k, fontsize=14, fontweight='bold', color=C_DARK)
        ax.text(0.06, y - 0.05, v, fontsize=13, color='#4A5568',
                multialignment='left')
        y -= 0.185

    # x→y arrow diagram
    rbox(ax, 0.15, 0.18, 0.08, 0.06, C_ACCENT+'22', label='x', fs=15,
         tc=C_ACCENT, ec=C_ACCENT, lw=1.2)
    arr(ax, 0.20, 0.18, 0.28, 0.18, color=C_ACCENT, lw=2)
    ax.text(0.24, 0.21, 'f', fontsize=14, fontstyle='italic', color=C_ACCENT)
    rbox(ax, 0.33, 0.18, 0.08, 0.06, C_ACCENT, label='y', fs=15, shadow=True)

    # ── Right column ──
    ax.text(0.75, 0.86, "Навчання без учителя", ha='center',
            fontsize=18, fontweight='bold', color='#A0AEC0')

    entries_r = [
        ("Дані:", r"$x$ — мітки відсутні"),
        ("Мета:", "Виявити приховану\nструктуру даних"),
        ("Приклади:", "Кластеризація,\nзниження вимірності"),
    ]
    y = 0.74
    for k, v in entries_r:
        ax.text(0.56, y, k, fontsize=14, fontweight='bold', color='#A0AEC0')
        ax.text(0.56, y - 0.05, v, fontsize=13, color='#A0AEC0',
                multialignment='left')
        y -= 0.185

    # Cluster diagram
    np.random.seed(42)
    for cx_c, cy_c, color in [(0.67, 0.22, '#63B3ED'), (0.77, 0.17, '#FC8181'), (0.72, 0.12, '#68D391')]:
        pts_x = np.random.normal(cx_c, 0.015, 6)
        pts_y = np.random.normal(cy_c, 0.012, 6)
        ax.scatter(pts_x, pts_y, s=22, color=color, alpha=0.7, zorder=5)

    save("01_supervised_vs_unsupervised")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Generative Modeling Goal
# ══════════════════════════════════════════════════════════════════════════════
def fig2():
    fig, ax = new_fig("Генеративне моделювання",
                      subtitle="Мета: навчити модель, яка відтворює розподіл навчальних даних")

    section_divider(ax, 0.5, 0.08, 0.82)

    # ── Left: density estimation ──
    ax.text(0.25, 0.80, "Оцінка щільності", ha='center',
            fontsize=17, fontweight='bold', color=C_ACCENT)

    xs = np.linspace(0.05, 0.45, 300)
    norm = (xs - 0.05) / 0.4
    ys = 0.22 + 0.45 * np.exp(-((norm - 0.5)**2) / (2 * 0.13**2))
    ax.fill_between(xs, 0.22, ys, alpha=0.12, color=C_ACCENT)
    ax.plot(xs, ys, color=C_ACCENT, lw=2.8)
    ax.plot([0.05, 0.45], [0.22, 0.22], color='#A0AEC0', lw=1.5)

    # Data points
    np.random.seed(7)
    sx = np.random.normal(0.25, 0.06, 20)
    sx = sx[(sx > 0.08) & (sx < 0.42)]
    ax.scatter(sx, [0.195]*len(sx), s=22, color=C_ACCENT, alpha=0.65, zorder=5)
    ax.text(0.05, 0.175, "зразки", fontsize=11, color='#718096')
    ax.text(0.38, 0.62, r"$P(x)$", fontsize=16, color=C_ACCENT, fontweight='bold')

    ax.text(0.25, 0.12,
            r"Як навчити $P_{model}(x) \approx P_{data}(x)$?",
            ha='center', fontsize=14, color=C_DARK, fontstyle='italic')

    # ── Right: sample generation ──
    ax.text(0.75, 0.80, "Генерація зразків", ha='center',
            fontsize=17, fontweight='bold', color='#DD6B20')

    # Training samples grid (3×2)
    ax.text(0.60, 0.68, "Навчальні", ha='center', fontsize=11, color='#718096')
    for r in range(2):
        for c in range(3):
            np.random.seed(r * 3 + c + 100)
            g = np.random.uniform(0.3, 0.7)
            rbox(ax, 0.555 + c*0.033, 0.58 - r*0.10, 0.028, 0.068,
                 str(g), ec='#CBD5E0', lw=0.6)

    arr(ax, 0.66, 0.53, 0.73, 0.53, color='#DD6B20', lw=2.5, head=18)
    ax.text(0.695, 0.56, r"$G$", fontsize=16, color='#DD6B20', fontweight='bold')

    ax.text(0.82, 0.68, "Згенеровані", ha='center', fontsize=11, color='#718096')
    for r in range(2):
        for c in range(3):
            np.random.seed(r * 3 + c + 200)
            g = np.random.uniform(0.3, 0.7)
            rbox(ax, 0.775 + c*0.033, 0.58 - r*0.10, 0.028, 0.068,
                 str(g), ec='#CBD5E0', lw=0.6)

    ax.text(0.60, 0.38, r"$\sim P_{data}(x)$", ha='center', fontsize=13, color='#718096')
    ax.text(0.82, 0.38, r"$\sim P_{model}(x)$", ha='center', fontsize=13, color='#718096')

    # Bottom distribution matching
    rbox(ax, 0.75, 0.18, 0.42, 0.12, C_LIGHT_BG,
         label="Генеративна модель вчиться\nстворювати нові реалістичні зразки",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1, bold=False)

    save("02_generative_modeling_goal")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Autoencoder Architecture
# ══════════════════════════════════════════════════════════════════════════════
def fig3():
    fig, ax = new_fig("Автокодувальник (Autoencoder)")

    cx_in  = 0.09;  cx_enc = 0.28;  cx_z = 0.50
    cx_dec = 0.72;  cx_out = 0.91;  cy   = 0.54

    # Components
    digit_placeholder(ax, cx_in, cy, sz=0.11, var='x')
    trap(ax, cx_enc, cy, 0.24, 0.44, C_ENCODER,
         label='Кодувальник\n(Encoder)', fs=14, wide_side='left', shadow=True)
    rbox(ax, cx_z, cy, 0.065, 0.44, C_LATENT, label='z', fs=24, shadow=True)
    trap(ax, cx_dec, cy, 0.24, 0.44, C_DECODER,
         label='Декодувальник\n(Decoder)', fs=14, wide_side='right', shadow=True)
    digit_placeholder(ax, cx_out, cy, sz=0.11, var=r'$\hat{x}$', reconstruct=True)

    # Arrows
    arr(ax, cx_in + 0.06, cy, cx_enc - 0.125, cy)
    arr(ax, cx_enc + 0.125, cy, cx_z - 0.035, cy)
    arr(ax, cx_z + 0.035, cy, cx_dec - 0.125, cy)
    arr(ax, cx_dec + 0.125, cy, cx_out - 0.06, cy)

    # Latent space callout
    ax.text(cx_z, 0.85, "Прихований простір (Latent Space)",
            ha='center', fontsize=14, fontweight='bold', color=C_LATENT)
    ax.text(cx_z, 0.80, "Стиснене представлення вхідних даних",
            ha='center', fontsize=12, color='#718096')
    arr(ax, cx_z, 0.78, cx_z, 0.77, color=C_LATENT, lw=1.5)

    # Brace underlines
    ax.plot([cx_in - 0.02, cx_z - 0.04], [0.26, 0.26], color=C_ENCODER, lw=2)
    ax.text((cx_in + cx_z)/2 - 0.02, 0.22,
            r"Кодування: $q_\phi(z|x)$",
            ha='center', fontsize=13, color=C_ENCODER, fontweight='bold')

    ax.plot([cx_z + 0.04, cx_out + 0.02], [0.26, 0.26], color=C_DECODER, lw=2)
    ax.text((cx_z + cx_out)/2 + 0.02, 0.22,
            r"Декодування: $p_\theta(x|z)$",
            ha='center', fontsize=13, color=C_DECODER, fontweight='bold')

    # Loss
    rbox(ax, 0.5, 0.10, 0.70, 0.08, C_LIGHT_BG,
         label=r"Функція втрат: $\mathcal{L} = ||x - \hat{x}||^2$ (помилка реконструкції)",
         fs=14, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False)

    save("03_autoencoder_architecture")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VAE Architecture
# ══════════════════════════════════════════════════════════════════════════════
def fig4():
    fig, ax = new_fig("Варіаційний автокодувальник (VAE)")

    cx_in  = 0.07;  cx_enc = 0.24;  cx_ms = 0.44
    cx_z   = 0.56;  cx_dec = 0.73;  cx_out = 0.93
    cy     = 0.52

    digit_placeholder(ax, cx_in, cy, sz=0.10, var='x')
    trap(ax, cx_enc, cy, 0.22, 0.42, C_ENCODER,
         label='Кодувальник', fs=13, wide_side='left', shadow=True)

    # μ and σ boxes
    rbox(ax, cx_ms, cy + 0.085, 0.075, 0.11, C_MU, label='μ', fs=20, shadow=True)
    rbox(ax, cx_ms, cy - 0.085, 0.075, 0.11, C_SIGMA, label='σ', fs=20, shadow=True)

    # z sampled
    rbox(ax, cx_z, cy, 0.075, 0.30, C_LATENT, label='z', fs=22, shadow=True)

    trap(ax, cx_dec, cy, 0.22, 0.42, C_DECODER,
         label='Декодувальник', fs=13, wide_side='right', shadow=True)
    digit_placeholder(ax, cx_out, cy, sz=0.10, var=r'$\hat{x}$', reconstruct=True)

    # Arrows
    arr(ax, cx_in + 0.055, cy, cx_enc - 0.115, cy)
    arr(ax, cx_enc + 0.115, cy, cx_ms - 0.04, cy + 0.085)
    arr(ax, cx_enc + 0.115, cy, cx_ms - 0.04, cy - 0.085)
    arr(ax, cx_ms + 0.04, cy + 0.085, cx_z - 0.04, cy + 0.05)
    arr(ax, cx_ms + 0.04, cy - 0.085, cx_z - 0.04, cy - 0.05)
    arr(ax, cx_z + 0.04, cy, cx_dec - 0.115, cy)
    arr(ax, cx_dec + 0.115, cy, cx_out - 0.055, cy)

    # Key difference callout
    rbox(ax, 0.44, 0.89, 0.55, 0.08, C_MU + '18',
         label="Ключова відмінність: кодувальник видає розподіл (μ, σ), а не одну точку",
         fs=13, tc=C_MU, ec=C_MU, lw=1.5, bold=True)

    # Sampling annotation
    ax.text(cx_z, 0.15,
            r"$z \sim \mathcal{N}(\mu, \sigma^2)$  — вибірка з прихованого розподілу",
            ha='center', fontsize=14, color=C_LATENT, fontweight='bold')

    save("04_vae_architecture")


# ══════════════════════════════════════════════════════════════════════════════
# 5. VAE Loss / Computation Graph
# ══════════════════════════════════════════════════════════════════════════════
def fig5():
    fig, ax = new_fig("VAE: функція втрат",
                      subtitle="Обчислювальний граф з двома компонентами оптимізації")

    cx_in  = 0.07;  cx_enc = 0.24;  cx_ms = 0.43
    cx_z   = 0.55;  cx_dec = 0.72;  cx_out = 0.93
    cy     = 0.58

    digit_placeholder(ax, cx_in, cy, sz=0.095, var='x')
    trap(ax, cx_enc, cy, 0.20, 0.38, C_ENCODER, label='', fs=12, wide_side='left')
    rbox(ax, cx_ms, cy + 0.07, 0.06, 0.09, C_MU, label='μ', fs=16)
    rbox(ax, cx_ms, cy - 0.07, 0.06, 0.09, C_SIGMA, label='σ', fs=16)
    rbox(ax, cx_z, cy, 0.06, 0.24, C_LATENT, label='z', fs=18)
    trap(ax, cx_dec, cy, 0.20, 0.38, C_DECODER, label='', fs=12, wide_side='right')
    digit_placeholder(ax, cx_out, cy, sz=0.095, var=r'$\hat{x}$', reconstruct=True)

    arr(ax, cx_in + 0.052, cy, cx_enc - 0.105, cy)
    arr(ax, cx_enc + 0.105, cy, cx_ms - 0.033, cy + 0.07)
    arr(ax, cx_enc + 0.105, cy, cx_ms - 0.033, cy - 0.07)
    arr(ax, cx_ms + 0.033, cy + 0.07, cx_z - 0.033, cy + 0.04)
    arr(ax, cx_ms + 0.033, cy - 0.07, cx_z - 0.033, cy - 0.04)
    arr(ax, cx_z + 0.033, cy, cx_dec - 0.105, cy)
    arr(ax, cx_dec + 0.105, cy, cx_out - 0.052, cy)

    # Brace zones
    ax.plot([cx_in - 0.01, cx_z - 0.04], [0.33, 0.33], color=C_ENCODER, lw=2.5)
    ax.text((cx_in + cx_z)/2 - 0.02, 0.29,
            r"Кодувальник: $q_\phi(z|x)$",
            ha='center', fontsize=12, color=C_ENCODER, fontweight='bold')

    ax.plot([cx_z + 0.04, cx_out + 0.01], [0.33, 0.33], color=C_DECODER, lw=2.5)
    ax.text((cx_z + cx_out)/2 + 0.02, 0.29,
            r"Декодувальник: $p_\theta(x|z)$",
            ha='center', fontsize=12, color=C_DECODER, fontweight='bold')

    # Loss formula
    ax.text(0.5, 0.20,
            r"$\mathcal{L}(\phi, \theta, x)$  =  Реконструктивні втрати  +  Регуляризація",
            ha='center', fontsize=16, color=C_DARK, fontweight='bold')

    # Two loss components
    rbox(ax, 0.28, 0.09, 0.40, 0.10, C_ENCODER + '15',
         label=r"$||x - \hat{x}||^2$" + "\nточність реконструкції",
         fs=12, tc=C_ENCODER, ec=C_ENCODER, lw=1.5, bold=False)

    ax.text(0.50, 0.09, "+", fontsize=22, ha='center', va='center',
            color=C_DARK, fontweight='bold')

    rbox(ax, 0.72, 0.09, 0.40, 0.10, C_DECODER + '15',
         label=r"$D_{KL}(q_\phi(z|x)\,\|\,p(z))$" + "\nвідповідність апріорному N(0,I)",
         fs=12, tc=C_DECODER, ec=C_DECODER, lw=1.5, bold=False)

    save("05_vae_loss_computation_graph")


# ══════════════════════════════════════════════════════════════════════════════
# 6. Reparameterization Trick
# ══════════════════════════════════════════════════════════════════════════════
def fig6():
    fig, ax = new_fig("Трюк репараметризації (Reparameterization Trick)")

    section_divider(ax, 0.5, 0.06, 0.88)

    # ═══════ LEFT: Problem ═══════
    ax.text(0.25, 0.87, "Проблема", ha='center', fontsize=19,
            fontweight='bold', color=C_RED)

    # Computation graph: phi -> z -> f
    #   z is stochastic — backprop cannot flow through
    cy_g = 0.58
    # phi node
    rbox(ax, 0.14, cy_g + 0.14, 0.07, 0.06, '#CBD5E0',
         label='ϕ', fs=16, tc=C_DARK, ec='#A0AEC0', lw=1.2, shadow=True)
    # z node (stochastic - circle/round)
    ax.add_patch(Circle((0.25, cy_g), 0.04, fc=C_SIGMA, ec='none', alpha=0.9, zorder=5))
    ax.text(0.25, cy_g, 'z', ha='center', va='center', fontsize=16,
            color='white', fontweight='bold', zorder=6)
    ax.text(0.33, cy_g, r'$z \sim q_\phi(z|x)$', fontsize=12, color='#718096',
            va='center')
    # f node
    rbox(ax, 0.25, cy_g - 0.14, 0.07, 0.06, C_ACCENT + '33',
         label='f', fs=16, tc=C_ACCENT, ec=C_ACCENT, lw=1.2)

    arr(ax, 0.14, cy_g + 0.10, 0.22, cy_g + 0.04, color='#A0AEC0')
    arr(ax, 0.25, cy_g - 0.04, 0.25, cy_g - 0.10, color='#A0AEC0')

    # Backprop X mark
    arr(ax, 0.25, cy_g + 0.12, 0.25, cy_g + 0.06, color=C_RED, lw=2.5)
    ax.plot([0.28, 0.32], [cy_g + 0.07, cy_g + 0.11], color=C_RED, lw=3)
    ax.plot([0.28, 0.32], [cy_g + 0.11, cy_g + 0.07], color=C_RED, lw=3)
    ax.text(0.36, cy_g + 0.09, "Backprop ✗", fontsize=12, color=C_RED,
            fontweight='bold')

    # Explanation
    rbox(ax, 0.25, 0.28, 0.40, 0.16, '#FFF5F5',
         label="Стохастичний вузол: зворотне\nпоширення градієнтів\nчерез вибірку неможливе",
         fs=12, tc=C_RED, ec=C_RED, lw=1.5, bold=False)

    # ═══════ RIGHT: Solution ═══════
    ax.text(0.75, 0.87, "Рішення", ha='center', fontsize=19,
            fontweight='bold', color=C_GREEN)

    cy_g = 0.60

    # mu node
    rbox(ax, 0.62, cy_g + 0.08, 0.065, 0.065, C_MU,
         label='μ', fs=17, shadow=True)
    # sigma node
    rbox(ax, 0.62, cy_g - 0.08, 0.065, 0.065, C_SIGMA,
         label='σ', fs=17, shadow=True)
    # epsilon node (external randomness)
    rbox(ax, 0.74, cy_g - 0.08, 0.065, 0.065, '#E2E8F0',
         label='ε', fs=17, tc=C_DARK, shadow=True)
    ax.text(0.74, cy_g - 0.13, r'$\sim \mathcal{N}(0,I)$',
            ha='center', fontsize=10, color='#718096')

    # + node
    ax.add_patch(Circle((0.74, cy_g + 0.08), 0.025, fc='#F0FFF4', ec=C_GREEN,
                         lw=1.5, zorder=5))
    ax.text(0.74, cy_g + 0.08, '+', ha='center', va='center', fontsize=16,
            color=C_GREEN, fontweight='bold', zorder=6)

    # z result
    rbox(ax, 0.86, cy_g, 0.07, 0.08, C_LATENT,
         label='z', fs=18, shadow=True)

    # Arrows: mu → +, sigma → ×(epsilon) → +, + → z
    arr(ax, 0.655, cy_g + 0.08, 0.715, cy_g + 0.08, color=C_MU, lw=1.8)
    arr(ax, 0.655, cy_g - 0.08, 0.705, cy_g - 0.08, color=C_SIGMA, lw=1.8)
    # sigma*epsilon → plus
    arr(ax, 0.74, cy_g - 0.05, 0.74, cy_g + 0.05, color='#718096', lw=1.5)
    ax.text(0.78, cy_g - 0.02, '⊙', fontsize=14, color='#718096')
    arr(ax, 0.765, cy_g + 0.08, 0.823, cy_g + 0.01, color=C_GREEN, lw=1.8)

    # Backprop checkmark
    arr(ax, 0.86, cy_g + 0.12, 0.86, cy_g + 0.06, color=C_GREEN, lw=2)
    ax.text(0.86, cy_g + 0.15, "Backprop ✓", ha='center', fontsize=12,
            color=C_GREEN, fontweight='bold')

    # Formula box
    rbox(ax, 0.75, 0.36, 0.42, 0.10, '#F0FFF4',
         label=r"$z = \mu + \sigma \odot \varepsilon$," +
               r"  де  $\varepsilon \sim \mathcal{N}(0, I)$",
         fs=14, tc=C_GREEN, ec=C_GREEN, lw=1.5, bold=True)

    # Explanation
    rbox(ax, 0.75, 0.22, 0.40, 0.12, '#F0FFF4',
         label="Випадковість ε виноситься\nза межі графа обчислень → \nпараметри φ диференційовані",
         fs=12, tc=C_GREEN, ec=C_GREEN, lw=1.5, bold=False)

    save("06_reparameterization_trick")


# ══════════════════════════════════════════════════════════════════════════════
# 7. GAN Training Architecture
# ══════════════════════════════════════════════════════════════════════════════
def fig7():
    fig, ax = new_fig("Навчання GAN: змагальний процес")

    cy = 0.54

    # Noise z
    rbox(ax, 0.07, cy - 0.10, 0.08, 0.12, C_MU + '55',
         label='z', fs=18, tc=C_DARK, ec=C_MU, lw=1.5, shadow=True)
    ax.text(0.07, cy - 0.22, "шум\n" + r"$z \sim \mathcal{N}(0,I)$",
            ha='center', fontsize=11, color='#718096', multialignment='center')

    arr(ax, 0.115, cy - 0.10, 0.17, cy - 0.10, color='#718096', lw=2)

    # Generator G
    trap(ax, 0.27, cy - 0.10, 0.20, 0.38, C_GEN,
         label='G', fs=24, wide_side='right', shadow=True)

    # X_fake
    arr(ax, 0.37, cy - 0.10, 0.43, cy + 0.04, color='#718096', lw=2)
    rbox(ax, 0.46, cy + 0.08, 0.065, 0.065, C_SIGMA + '44',
         label=r'$X_{fake}$', fs=11, tc=C_DARK, ec=C_SIGMA, lw=1)

    # X_real
    rbox(ax, 0.46, cy - 0.18, 0.065, 0.065, C_ENCODER + '44',
         label=r'$X_{real}$', fs=11, tc=C_DARK, ec=C_ENCODER, lw=1)

    # Arrows to D
    arr(ax, 0.495, cy + 0.08, 0.56, cy + 0.02, color='#718096', lw=2)
    arr(ax, 0.495, cy - 0.18, 0.56, cy - 0.12, color='#718096', lw=2)

    # Discriminator D
    trap(ax, 0.66, cy - 0.05, 0.20, 0.38, C_DISC,
         label='D', fs=24, wide_side='left', shadow=True)

    # Output y
    arr(ax, 0.76, cy - 0.05, 0.83, cy - 0.05, color='#718096', lw=2)
    rbox(ax, 0.88, cy - 0.05, 0.08, 0.10, '#F6E05E',
         label='y', fs=20, tc=C_DARK, shadow=True)

    # Annotations
    ax.text(0.27, cy + 0.22,
            "G створює синтетичні\nзображення, щоб обманути D",
            ha='center', fontsize=12, color=C_GEN, fontweight='bold',
            multialignment='center')

    ax.text(0.66, cy + 0.22,
            "D відрізняє справжні\nдані від синтетичних",
            ha='center', fontsize=12, color=C_DISC, fontweight='bold',
            multialignment='center')

    ax.text(0.88, cy + 0.08, "Справжнє /\nсинтетичне?",
            ha='center', fontsize=10, color='#718096', multialignment='center')

    # Bottom
    rbox(ax, 0.5, 0.08, 0.90, 0.10, C_LIGHT_BG,
         label="Навчання: змагальні цілі для D та G   |   "
               "Глобальний оптимум: G відтворює справжній розподіл даних",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False, shadow=True)

    save("07_gan_training_architecture")


# ══════════════════════════════════════════════════════════════════════════════
# 8. GAN Loss Functions
# ══════════════════════════════════════════════════════════════════════════════
def fig8():
    fig, ax = new_fig("GAN: функції втрат",
                      subtitle="Мінімаксна гра між генератором G та дискримінатором D")

    # Main objective
    rbox(ax, 0.5, 0.75, 0.90, 0.10, C_LIGHT_BG,
         label=r"$\min_G \max_D \; V(D,G) = "
               r"\mathbb{E}_{x \sim p_{data}}[\log D(x)] + "
               r"\mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$",
         fs=14, tc=C_DARK, ec=C_BORDER, lw=2, bold=True, shadow=True)

    section_divider(ax, 0.5, 0.08, 0.66)

    # ── Discriminator loss ──
    ax.text(0.25, 0.64, "Функція втрат D", ha='center',
            fontsize=17, fontweight='bold', color=C_DISC)

    rbox(ax, 0.25, 0.52, 0.44, 0.09, C_DISC + '12',
         label=r"$\max_D \; \mathbb{E}[\log D(x)] + \mathbb{E}[\log(1 - D(G(z)))]$",
         fs=12, tc=C_DARK, ec=C_DISC, lw=1.5, bold=False)

    ax.text(0.25, 0.43,
            "D хоче:",
            ha='center', fontsize=13, color=C_DARK, fontweight='bold', va='top')
    ax.text(0.25, 0.38,
            r"• $D(x) \rightarrow 1$  (справжні → 1)" + "\n"
            r"• $D(G(z)) \rightarrow 0$  (синтетичні → 0)",
            ha='center', fontsize=13, color='#4A5568', va='top',
            multialignment='left')

    rbox(ax, 0.25, 0.16, 0.40, 0.08, C_DISC + '15',
         label="Дискримінатор розрізняє\nсправжнє від синтетичного",
         fs=12, tc=C_DISC, ec=C_DISC, lw=1.2, bold=False)

    # ── Generator loss ──
    ax.text(0.75, 0.64, "Функція втрат G", ha='center',
            fontsize=17, fontweight='bold', color=C_GEN)

    rbox(ax, 0.75, 0.52, 0.44, 0.09, C_GEN + '12',
         label=r"$\min_G \; \mathbb{E}[\log(1 - D(G(z)))]$",
         fs=12, tc=C_DARK, ec=C_GEN, lw=1.5, bold=False)

    ax.text(0.75, 0.43,
            "G хоче:",
            ha='center', fontsize=13, color=C_DARK, fontweight='bold', va='top')
    ax.text(0.75, 0.38,
            r"• $D(G(z)) \rightarrow 1$" + "\n"
            "  (змусити D вважати\n  синтетичне справжнім)",
            ha='center', fontsize=13, color='#4A5568', va='top',
            multialignment='left')

    rbox(ax, 0.75, 0.16, 0.40, 0.08, C_GEN + '15',
         label="Генератор вчиться\nобманювати дискримінатор",
         fs=12, tc=C_GEN, ec=C_GEN, lw=1.2, bold=False)

    save("08_gan_loss_functions")


# ══════════════════════════════════════════════════════════════════════════════
# 9. GAN as Distribution Transformer
# ══════════════════════════════════════════════════════════════════════════════
def fig9():
    fig, ax = new_fig("GAN — перетворювач розподілів")

    cy = 0.52

    # Gaussian bell on left
    xs_g = np.linspace(-3, 3, 200)
    ys_g = np.exp(-xs_g**2 / 2)
    gx = 0.04 + (xs_g + 3) / 6 * 0.14
    gy = cy - 0.12 + ys_g * 0.12
    ax.fill_between(gx, cy - 0.12, gy, alpha=0.20, color=C_MU)
    ax.plot(gx, gy, color=C_MU, lw=2)

    rbox(ax, 0.11, cy + 0.06, 0.10, 0.14, C_MU + '35',
         label='z', fs=26, tc=C_DARK, ec=C_MU, lw=2, shadow=True)
    ax.text(0.11, cy + 0.20, "Гауссовий шум",
            ha='center', fontsize=13, color='#718096')
    ax.text(0.11, cy - 0.22, r"$z \sim \mathcal{N}(0,1)$",
            ha='center', fontsize=13, color=C_DARK)

    arr(ax, 0.17, cy + 0.02, 0.26, cy + 0.02, color='#718096', lw=2.5, head=20)

    # Generator
    trap(ax, 0.38, cy, 0.24, 0.48, C_GEN, label='G', fs=28,
         wide_side='right', shadow=True)
    ax.text(0.38, cy - 0.32, "Навчений генератор",
            ha='center', fontsize=13, color=C_GEN, fontweight='bold')

    arr(ax, 0.50, cy, 0.59, cy, color='#718096', lw=2.5, head=20)
    ax.text(0.545, cy + 0.05, '?', ha='center', fontsize=26, color='#CBD5E0',
            fontweight='bold')

    arr(ax, 0.67, cy, 0.75, cy, color='#718096', lw=2.5, head=20, dashed=True)

    # Target distribution blob
    theta = np.linspace(0, 2*np.pi, 300)
    r = 0.16 + 0.035 * np.cos(3*theta) + 0.025 * np.sin(5*theta) + 0.015 * np.cos(7*theta)
    blob_x = 0.87 + r * np.cos(theta) * 0.60
    blob_y = cy + r * np.sin(theta) * 0.90
    ax.fill(blob_x, blob_y, color=C_LATENT, alpha=0.18)
    ax.plot(blob_x, blob_y, color=C_LATENT, lw=2, ls='--')
    ax.text(0.87, cy, 'X', ha='center', va='center', fontsize=32,
            color=C_LATENT, fontweight='bold')
    ax.text(0.87, cy - 0.28, "Цільовий розподіл\nданих",
            ha='center', fontsize=13, color=C_LATENT, fontweight='bold',
            multialignment='center')

    # Bottom
    rbox(ax, 0.5, 0.08, 0.80, 0.08, C_LIGHT_BG,
         label="Генератор перетворює простий гауссовий розподіл на складний розподіл реальних даних",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False)

    save("09_gan_distribution_transformer")


# ══════════════════════════════════════════════════════════════════════════════
# 10. VAE vs GAN Summary
# ══════════════════════════════════════════════════════════════════════════════
def fig10():
    fig, ax = new_fig("Підсумок: генеративні моделі")

    # ── Left card: VAE ──
    rbox(ax, 0.27, 0.50, 0.46, 0.65, C_BG,
         ec=C_LATENT, lw=2.5, shadow=True)
    ax.text(0.27, 0.80, "Автокодувальники та VAE",
            ha='center', fontsize=17, fontweight='bold', color=C_LATENT)

    # Mini VAE
    trap(ax, 0.17, 0.63, 0.10, 0.20, C_ENCODER, wide_side='left')
    rbox(ax, 0.27, 0.63, 0.04, 0.20, C_LATENT, label='z', fs=11)
    trap(ax, 0.37, 0.63, 0.10, 0.20, C_DECODER, wide_side='right')
    arr(ax, 0.12, 0.63, 0.155, 0.63, color='#718096', lw=1.5)
    arr(ax, 0.225, 0.63, 0.253, 0.63, color='#718096', lw=1.5)
    arr(ax, 0.287, 0.63, 0.315, 0.63, color='#718096', lw=1.5)
    arr(ax, 0.375, 0.63, 0.41, 0.63, color='#718096', lw=1.5)

    ax.text(0.27, 0.47,
            "• Прихований простір меншої\n  розмірності\n"
            "• Вибірка з p(z) для генерації\n"
            "• Явна функція втрат\n"
            "  (реконструкція + KL)\n"
            "• Стабільне навчання",
            ha='center', fontsize=12, color=C_DARK, va='top',
            multialignment='left')

    # ── Right card: GAN ──
    rbox(ax, 0.73, 0.50, 0.46, 0.65, C_BG,
         ec=C_GEN, lw=2.5, shadow=True)
    ax.text(0.73, 0.80, "Генеративно-змагальні\nмережі (GAN)",
            ha='center', fontsize=17, fontweight='bold', color=C_GEN,
            multialignment='center')

    # Mini GAN
    rbox(ax, 0.61, 0.63, 0.045, 0.10, C_MU, label='z', fs=10, shadow=True)
    trap(ax, 0.69, 0.63, 0.10, 0.20, C_GEN, label='G', fs=12, wide_side='right')
    trap(ax, 0.79, 0.63, 0.10, 0.20, C_DISC, label='D', fs=12, wide_side='left')
    rbox(ax, 0.87, 0.63, 0.045, 0.10, '#F6E05E', label='y', fs=10, tc=C_DARK, shadow=True)
    arr(ax, 0.635, 0.63, 0.652, 0.63, color='#718096', lw=1.5)
    arr(ax, 0.74, 0.63, 0.755, 0.63, color='#718096', lw=1.5)
    arr(ax, 0.84, 0.63, 0.85, 0.63, color='#718096', lw=1.5)

    ax.text(0.73, 0.47,
            "• Змагальне навчання\n  двох мереж\n"
            "• Неявне моделювання\n  розподілу\n"
            "• Часто якісніші зображення\n"
            "• Складніше навчання\n  (mode collapse)",
            ha='center', fontsize=12, color=C_DARK, va='top',
            multialignment='left')

    # Bottom shared message
    rbox(ax, 0.5, 0.08, 0.88, 0.08, C_LIGHT_BG,
         label="Обидва підходи вчаться генерувати нові зразки, "
               "що відповідають розподілу навчальних даних",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False, shadow=True)

    save("10_vae_vs_gan_summary")


# ══════════════════════════════════════════════════════════════════════════════
# 11. Diffusion Models
# ══════════════════════════════════════════════════════════════════════════════
def fig11():
    fig, ax = new_fig("Дифузійні моделі (Diffusion Models)",
                      subtitle="Навчаються поступово видаляти шум — крок за кроком")

    cy_fwd = 0.67;  cy_rev = 0.37
    xs = [0.10, 0.24, 0.38, 0.50, 0.64, 0.82]
    steps = [r'$x_0$', r'$x_1$', r'$x_2$', '...', r'$x_{T\!-\!1}$', r'$x_T$']
    grays_fwd = [0.90, 0.74, 0.58, 0.47, 0.35, 0.20]

    # ── Forward Process ──
    ax.text(0.04, cy_fwd, "Прямий\nпроцес", fontsize=12, fontweight='bold',
            color=C_RED, va='center', ha='right', multialignment='right')
    ax.annotate('', xy=(0.88, cy_fwd), xytext=(0.08, cy_fwd),
                arrowprops=dict(arrowstyle='->', color=C_RED + '66', lw=2.5))
    ax.text(0.50, cy_fwd + 0.085,
            r"Додавання шуму:  $q(x_t | x_{t-1})$",
            ha='center', fontsize=12, color=C_RED, fontweight='bold')

    for xp, step, gv in zip(xs, steps, grays_fwd):
        # Draw noise-textured box
        np.random.seed(int(gv * 1000))
        for ni in range(8):
            for nj in range(8):
                noise_g = max(0, min(1, gv + np.random.uniform(-0.15, 0.15)))
                sz = 0.075
                r = plt.Rectangle((xp - sz/2 + ni*sz/8, cy_fwd - sz/2 + nj*sz/8),
                                   sz/8, sz/8, fc=str(noise_g), ec='none')
                ax.add_patch(r)
        ax.add_patch(plt.Rectangle((xp - 0.075/2, cy_fwd - 0.075/2), 0.075, 0.075,
                                    fill=False, ec='#A0AEC0', lw=1))
        tc = 'white' if gv < 0.5 else '#1A1A2E'
        ax.text(xp, cy_fwd - 0.06, step, ha='center', fontsize=11, color='#4A5568')

    ax.text(xs[0], cy_fwd + 0.06, "Чисте\nзображення", ha='center',
            fontsize=10, color=C_GREEN, multialignment='center', fontweight='bold')
    ax.text(xs[-1], cy_fwd + 0.06, "Чистий\nшум", ha='center',
            fontsize=10, color=C_RED, multialignment='center', fontweight='bold')

    # ── Reverse Process ──
    ax.text(0.04, cy_rev, "Зворотній\nпроцес", fontsize=12, fontweight='bold',
            color=C_GREEN, va='center', ha='right', multialignment='right')
    ax.annotate('', xy=(0.08, cy_rev), xytext=(0.88, cy_rev),
                arrowprops=dict(arrowstyle='->', color=C_GREEN + '66', lw=2.5))
    ax.text(0.50, cy_rev + 0.085,
            r"Видалення шуму:  $p_\theta(x_{t-1} | x_t)$",
            ha='center', fontsize=12, color=C_GREEN, fontweight='bold')

    grays_rev = list(reversed(grays_fwd))
    steps_rev = list(reversed(steps))
    for xp, step, gv in zip(xs, steps_rev, grays_rev):
        np.random.seed(int(gv * 1000) + 500)
        for ni in range(8):
            for nj in range(8):
                noise_g = max(0, min(1, gv + np.random.uniform(-0.15, 0.15)))
                sz = 0.075
                r = plt.Rectangle((xp - sz/2 + ni*sz/8, cy_rev - sz/2 + nj*sz/8),
                                   sz/8, sz/8, fc=str(noise_g), ec='none')
                ax.add_patch(r)
        ax.add_patch(plt.Rectangle((xp - 0.075/2, cy_rev - 0.075/2), 0.075, 0.075,
                                    fill=False, ec='#A0AEC0', lw=1))
        ax.text(xp, cy_rev - 0.06, step, ha='center', fontsize=11, color='#4A5568')

    ax.text(xs[0], cy_rev + 0.06, "Чистий\nшум", ha='center',
            fontsize=10, color=C_RED, multialignment='center', fontweight='bold')
    ax.text(xs[-1], cy_rev + 0.06, "Згенеровані\nдані", ha='center',
            fontsize=10, color=C_GREEN, multialignment='center', fontweight='bold')

    # Bottom
    rbox(ax, 0.5, 0.12, 0.80, 0.10, C_LIGHT_BG,
         label=r"Нейромережа навчається передбачати шум $\varepsilon_\theta(x_t, t)$"
               "\nна кожному кроці зворотного процесу",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False, shadow=True)

    save("11_diffusion_models")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating v2 lecture graphics...")
    fig1();  fig2();  fig3();  fig4();  fig5()
    fig6();  fig7();  fig8();  fig9();  fig10();  fig11()
    print(f"\nAll done → {OUTPUT_DIR}/")
