#!/usr/bin/env python3
"""Generate Ukrainian lecture graphics for Deep Generative Modeling."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
import numpy as np
import os

OUTPUT_DIR = "6S191_lecture_graphics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Palette matching MIT 6.S191 slides ───────────────────────────────────────
C_ENCODER  = '#5BAD6F'
C_DECODER  = '#9B59B6'
C_LATENT   = '#5B9BD5'
C_MU_SIG   = '#F5A623'
C_DISC     = '#5BAD6F'
C_GEN      = '#9B59B6'
C_REAL_DOT = '#27AE60'
C_FAKE_DOT = '#E8735A'
C_TITLE    = '#1A1A2E'
C_BG       = '#FFFFFF'
C_BORDER   = '#CCCCCC'
C_ACCENT   = '#2980B9'
C_DARK     = '#333333'
C_LIGHT_BG = '#F0F4F8'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13})

W, H, DPI = 13.33, 7.5, 150


def save(name):
    plt.savefig(f"{OUTPUT_DIR}/{name}.png", dpi=DPI, bbox_inches='tight',
                facecolor=C_BG, edgecolor='none')
    plt.close()
    print(f"  saved {name}.png")


def new_fig(title=None, title_size=20):
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    fig.patch.set_facecolor(C_BG)
    if title:
        ax.text(0.5, 0.955, title, ha='center', va='top',
                fontsize=title_size, fontweight='bold', color=C_TITLE)
    return fig, ax


def rbox(ax, cx, cy, w, h, fc, label='', fs=13, tc='white', ec='none', lw=1.5,
         alpha=1.0, bold=True):
    p = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle="round,pad=0.015", facecolor=fc,
                       edgecolor=ec, linewidth=lw, alpha=alpha)
    ax.add_patch(p)
    if label:
        ax.text(cx, cy, label, ha='center', va='center', fontsize=fs,
                color=tc, fontweight='bold' if bold else 'normal', wrap=True,
                multialignment='center')


def trap(ax, cx, cy, w, h, fc, label='', fs=16, wide_side='left'):
    """Trapezoid: wide_side controls which side is wider."""
    pad = h * 0.32
    if wide_side == 'left':
        pts = [[cx-w/2, cy+h/2], [cx+w/2, cy+pad],
               [cx+w/2, cy-pad], [cx-w/2, cy-h/2]]
    else:
        pts = [[cx-w/2, cy+pad], [cx+w/2, cy+h/2],
               [cx+w/2, cy-h/2], [cx-w/2, cy-pad]]
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor='none', alpha=0.88)
    ax.add_patch(poly)
    if label:
        ax.text(cx, cy, label, ha='center', va='center', fontsize=fs,
                color='white', fontweight='bold')


def arr(ax, x0, y0, x1, y1, color='#555', lw=2.0, style='->', head=15):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=f'->', color=color, lw=lw,
                                mutation_scale=head,
                                connectionstyle='arc3,rad=0.0'))


def img_placeholder(ax, cx, cy, sz=0.072, label='', var=''):
    """Simulate a small image with a pixel-art style box."""
    np.random.seed(42)
    for i in range(5):
        for j in range(5):
            g = np.random.uniform(0.15, 0.85)
            r = plt.Rectangle((cx - sz/2 + i*sz/5, cy - sz/2 + j*sz/5),
                               sz/5, sz/5, fc=str(g), ec='none')
            ax.add_patch(r)
    ax.add_patch(plt.Rectangle((cx - sz/2, cy - sz/2), sz, sz,
                                fill=False, ec='#444', lw=1.5))
    if var:
        ax.text(cx, cy - sz/2 - 0.025, var, ha='center', fontsize=14,
                fontstyle='italic', color=C_TITLE)
    if label:
        ax.text(cx, cy + sz/2 + 0.015, label, ha='center', fontsize=11,
                color='#666')


# ══════════════════════════════════════════════════════════════════════════════
# 1. Supervised vs Unsupervised
# ══════════════════════════════════════════════════════════════════════════════
def fig1():
    fig, ax = new_fig("Навчання з учителем vs. Навчання без учителя", 19)
    ax.plot([0.5, 0.5], [0.08, 0.88], color=C_BORDER, lw=2)

    def col(items, x_label, x_val, start_y, color):
        y = start_y
        for k, v in items:
            ax.text(x_label, y, k, ha='left', fontsize=14,
                    fontweight='bold', color=color)
            ax.text(x_val, y, v, ha='left', fontsize=13, color=color,
                    multialignment='left')
            y -= 0.155

    ax.text(0.25, 0.87, "Навчання з учителем", ha='center',
            fontsize=16, fontweight='bold', color=C_ACCENT)
    col([
        ("Дані:", "(x, y)"),
        ("    ", "x — дані,  y — мітка"),
        ("Мета:", "Навчити функцію  x → y"),
        ("Приклади:", "Класифікація, регресія,\nрозпізнавання об'єктів"),
    ], 0.07, 0.19, 0.77, C_DARK)

    ax.text(0.75, 0.87, "Навчання без учителя", ha='center',
            fontsize=16, fontweight='bold', color='#999999')
    col([
        ("Дані:", "x"),
        ("    ", "x — дані, мітки відсутні"),
        ("Мета:", "Виявити приховану\nструктуру даних"),
        ("Приклади:", "Кластеризація,\nзниження вимірності"),
    ], 0.54, 0.66, 0.77, '#999999')

    save("01_supervised_vs_unsupervised")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Generative Modeling Goal
# ══════════════════════════════════════════════════════════════════════════════
def fig2():
    fig, ax = new_fig("Генеративне моделювання", 21)

    # Subtitle
    ax.text(0.5, 0.88,
            "Мета: взяти навчальні зразки з розподілу та навчити модель,\n"
            "яка відтворює цей розподіл",
            ha='center', va='top', fontsize=14, color=C_DARK,
            multialignment='center')

    # Left: density estimation curve
    ax.text(0.22, 0.74, "Оцінка щільності", ha='center',
            fontsize=15, fontweight='bold', color=C_ACCENT)

    xs = np.linspace(0.04, 0.42, 200)
    ys_base = 0.2
    curve_x = (xs - 0.04) / 0.38
    ys = ys_base + 0.42 * np.exp(-((curve_x - 0.5)**2) / (2 * 0.12**2))
    ax.plot(xs, ys, color=C_ACCENT, lw=2.5)
    ax.fill_between(xs, ys_base, ys, alpha=0.18, color=C_ACCENT)
    ax.plot([0.04, 0.42], [ys_base, ys_base], color='#555', lw=1.5)

    # Scatter samples below curve
    np.random.seed(7)
    sx = np.random.normal(0.22, 0.055, 18)
    sx = sx[(sx > 0.07) & (sx < 0.38)]
    ax.scatter(sx, [0.175] * len(sx), s=18, color=C_ACCENT, alpha=0.7, zorder=5)
    ax.text(0.04, 0.155, "зразки", fontsize=11, color='#555')

    ax.text(0.22, 0.12,
            r"$P_{model}(x) \approx P_{data}(x)$",
            ha='center', fontsize=14, color=C_DARK)

    # Divider
    ax.plot([0.5, 0.5], [0.1, 0.77], color=C_BORDER, lw=1.5, ls='--')

    # Right: sample generation
    ax.text(0.75, 0.74, "Генерація зразків", ha='center',
            fontsize=15, fontweight='bold', color='#E67E22')

    ax.text(0.6, 0.62, "Навчальні дані", ha='center', fontsize=11, color='#666')
    ax.text(0.9, 0.62, "Згенеровані дані", ha='center', fontsize=11, color='#666')

    # Mini grids of sample images
    np.random.seed(1)
    for col_idx, cx_g in enumerate([0.6, 0.9]):
        for row in range(2):
            for col2 in range(2):
                cx = cx_g - 0.04 + col2 * 0.045
                cy = 0.52 - row * 0.12
                np.random.seed(col_idx * 100 + row * 10 + col2)
                g_val = np.random.uniform(0.4, 0.8)
                rbox(ax, cx, cy, 0.038, 0.08, fc=str(g_val), label='',
                     tc='white', ec='#aaa', lw=0.5)

    arr(ax, 0.64, 0.46, 0.76, 0.46, color='#E67E22', lw=2, head=18)
    ax.text(0.70, 0.49, r"$G$", ha='center', fontsize=13, color='#E67E22',
            fontweight='bold')

    ax.text(0.6, 0.355, r"$\sim P_{data}(x)$", ha='center', fontsize=12,
            color='#666')
    ax.text(0.9, 0.355, r"$\sim P_{model}(x)$", ha='center', fontsize=12,
            color='#666')

    ax.text(0.5, 0.10,
            r"Як навчити $P_{model}(x)$ подібний до $P_{data}(x)$?",
            ha='center', fontsize=15, color=C_DARK, fontstyle='italic')

    save("02_generative_modeling_goal")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Autoencoder Architecture
# ══════════════════════════════════════════════════════════════════════════════
def fig3():
    fig, ax = new_fig("Автокодувальник (Autoencoder)", 21)

    cx_img_in  = 0.10
    cx_enc     = 0.28
    cx_z       = 0.50
    cx_dec     = 0.72
    cx_img_out = 0.90
    cy         = 0.52

    img_placeholder(ax, cx_img_in, cy, sz=0.10, var='x')
    trap(ax, cx_enc, cy, 0.22, 0.42, C_ENCODER,
         label='Кодувальник\n(Encoder)', wide_side='left')
    rbox(ax, cx_z, cy, 0.07, 0.42, C_LATENT, label='z', fs=22)
    trap(ax, cx_dec, cy, 0.22, 0.42, C_DECODER,
         label='Декодувальник\n(Decoder)', wide_side='right')
    img_placeholder(ax, cx_img_out, cy, sz=0.10, var=r'$\hat{x}$')

    arr(ax, cx_img_in + 0.055, cy, cx_enc - 0.115, cy, color='#555')
    arr(ax, cx_enc + 0.115, cy, cx_z - 0.037, cy, color='#555')
    arr(ax, cx_z + 0.037, cy, cx_dec - 0.115, cy, color='#555')
    arr(ax, cx_dec + 0.115, cy, cx_img_out - 0.055, cy, color='#555')

    # Brace annotations
    ax.annotate('', xy=(cx_z - 0.04, 0.24), xytext=(cx_img_in, 0.24),
                arrowprops=dict(arrowstyle='-', color='#888', lw=1,
                                connectionstyle='bar,fraction=0.1'))
    ax.text((cx_img_in + cx_z)/2 - 0.02, 0.17,
            r"Кодування: $q_\phi(z|x)$",
            ha='center', fontsize=13, color='#555')

    ax.annotate('', xy=(cx_img_out, 0.24), xytext=(cx_z + 0.04, 0.24),
                arrowprops=dict(arrowstyle='-', color='#888', lw=1,
                                connectionstyle='bar,fraction=0.1'))
    ax.text((cx_z + cx_img_out)/2 + 0.02, 0.17,
            r"Декодування: $p_\theta(x|z)$",
            ha='center', fontsize=13, color='#555')

    ax.text(0.5, 0.10,
            r"Функція втрат: мінімізуємо $||x - \hat{x}||^2$  (помилка реконструкції)",
            ha='center', fontsize=14, color=C_DARK)

    ax.text(cx_z, 0.84,
            "Стиснений прихований простір\n(Latent Space)",
            ha='center', fontsize=13, color=C_LATENT, fontweight='bold')
    ax.annotate('', xy=(cx_z, 0.74), xytext=(cx_z, 0.82),
                arrowprops=dict(arrowstyle='->', color=C_LATENT, lw=1.5))

    save("03_autoencoder_architecture")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VAE Architecture
# ══════════════════════════════════════════════════════════════════════════════
def fig4():
    fig, ax = new_fig("Варіаційний автокодувальник (VAE)", 21)

    cx_img_in  = 0.08
    cx_enc     = 0.26
    cx_mu_sig  = 0.46
    cx_z       = 0.56
    cx_dec     = 0.73
    cx_img_out = 0.92
    cy         = 0.52

    img_placeholder(ax, cx_img_in, cy, sz=0.10, var='x')
    trap(ax, cx_enc, cy, 0.22, 0.42, C_ENCODER,
         label='Кодувальник', wide_side='left', fs=14)

    # μ and σ stacked
    rbox(ax, cx_mu_sig, cy + 0.08, 0.065, 0.10, C_MU_SIG, label='μ', fs=18)
    rbox(ax, cx_mu_sig, cy - 0.08, 0.065, 0.10, '#E8735A', label='σ', fs=18)

    # z (sampled)
    rbox(ax, cx_z, cy, 0.065, 0.28, C_LATENT, label='z', fs=20)

    trap(ax, cx_dec, cy, 0.22, 0.42, C_DECODER,
         label='Декодувальник', wide_side='right', fs=14)
    img_placeholder(ax, cx_img_out, cy, sz=0.10, var=r'$\hat{x}$')

    arr(ax, cx_img_in + 0.055, cy, cx_enc - 0.115, cy, color='#555')
    arr(ax, cx_enc + 0.115, cy, cx_mu_sig - 0.035, cy + 0.08, color='#555')
    arr(ax, cx_enc + 0.115, cy, cx_mu_sig - 0.035, cy - 0.08, color='#555')
    arr(ax, cx_mu_sig + 0.035, cy + 0.08, cx_z - 0.034, cy + 0.05, color='#555')
    arr(ax, cx_mu_sig + 0.035, cy - 0.08, cx_z - 0.034, cy - 0.05, color='#555')
    arr(ax, cx_z + 0.034, cy, cx_dec - 0.115, cy, color='#555')
    arr(ax, cx_dec + 0.115, cy, cx_img_out - 0.055, cy, color='#555')

    # Key annotation
    ax.text(cx_mu_sig - 0.01, 0.83,
            "Ключова відмінність від AE:\nкодувальник видає розподіл, а не точку",
            ha='center', fontsize=13, color=C_MU_SIG, fontweight='bold',
            multialignment='center')
    ax.annotate('', xy=(cx_mu_sig, 0.68), xytext=(cx_mu_sig, 0.76),
                arrowprops=dict(arrowstyle='->', color=C_MU_SIG, lw=1.5))

    ax.text(cx_z, 0.17,
            r"$z \sim \mathcal{N}(\mu, \sigma^2)$",
            ha='center', fontsize=14, color=C_LATENT, fontweight='bold')

    save("04_vae_architecture")


# ══════════════════════════════════════════════════════════════════════════════
# 5. VAE Loss / Computation Graph
# ══════════════════════════════════════════════════════════════════════════════
def fig5():
    fig, ax = new_fig("VAE: Обчислювальний граф та функція втрат", 20)

    cx_img_in  = 0.08
    cx_enc     = 0.26
    cx_mu_sig  = 0.46
    cx_z       = 0.56
    cx_dec     = 0.73
    cx_img_out = 0.92
    cy         = 0.58

    img_placeholder(ax, cx_img_in, cy, sz=0.10, var='x')
    trap(ax, cx_enc, cy, 0.22, 0.40, C_ENCODER, label='Кодувальник', wide_side='left', fs=13)
    rbox(ax, cx_mu_sig, cy + 0.075, 0.065, 0.095, C_MU_SIG, label='μ', fs=17)
    rbox(ax, cx_mu_sig, cy - 0.075, 0.065, 0.095, '#E8735A', label='σ', fs=17)
    rbox(ax, cx_z, cy, 0.06, 0.26, C_LATENT, label='z', fs=19)
    trap(ax, cx_dec, cy, 0.22, 0.40, C_DECODER, label='Декодувальник', wide_side='right', fs=13)
    img_placeholder(ax, cx_img_out, cy, sz=0.10, var=r'$\hat{x}$')

    arr(ax, cx_img_in + 0.055, cy, cx_enc - 0.115, cy, color='#555')
    arr(ax, cx_enc + 0.115, cy, cx_mu_sig - 0.035, cy + 0.075, color='#555')
    arr(ax, cx_enc + 0.115, cy, cx_mu_sig - 0.035, cy - 0.075, color='#555')
    arr(ax, cx_mu_sig + 0.035, cy + 0.075, cx_z - 0.032, cy + 0.045, color='#555')
    arr(ax, cx_mu_sig + 0.035, cy - 0.075, cx_z - 0.032, cy - 0.045, color='#555')
    arr(ax, cx_z + 0.032, cy, cx_dec - 0.115, cy, color='#555')
    arr(ax, cx_dec + 0.115, cy, cx_img_out - 0.055, cy, color='#555')

    # Brace labels
    ax.annotate('', xy=(cx_z - 0.035, 0.30), xytext=(cx_img_in, 0.30),
                arrowprops=dict(arrowstyle='-', color='#888', lw=1,
                                connectionstyle='bar,fraction=0.08'))
    ax.text((cx_img_in + cx_z) / 2, 0.245,
            r"Кодувальник: $q_\phi(z|x)$",
            ha='center', fontsize=12, color='#555')

    ax.annotate('', xy=(cx_img_out, 0.30), xytext=(cx_z + 0.035, 0.30),
                arrowprops=dict(arrowstyle='-', color='#888', lw=1,
                                connectionstyle='bar,fraction=0.08'))
    ax.text((cx_z + cx_img_out) / 2, 0.245,
            r"Декодувальник: $p_\theta(x|z)$",
            ha='center', fontsize=12, color='#555')

    # Loss formula
    ax.text(0.5, 0.15,
            r"$\mathcal{L}(\phi,\theta,x)$ = (Реконструктивні втрати) + (Регуляризація)",
            ha='center', fontsize=15, color=C_DARK, fontweight='bold')

    # Breakdown
    rbox(ax, 0.28, 0.07, 0.32, 0.06, fc=C_ENCODER + '33',
         label=r'$||x - \hat{x}||^2$  — точність реконструкції',
         fs=12, tc=C_DARK, ec=C_ENCODER, lw=1.5, bold=False)
    rbox(ax, 0.72, 0.07, 0.32, 0.06, fc=C_DECODER + '33',
         label=r'$D_{KL}(q_\phi(z|x) \| p(z))$  — відповідність апріорному',
         fs=12, tc=C_DARK, ec=C_DECODER, lw=1.5, bold=False)

    save("05_vae_loss_computation_graph")


# ══════════════════════════════════════════════════════════════════════════════
# 6. Reparameterization Trick
# ══════════════════════════════════════════════════════════════════════════════
def fig6():
    fig, ax = new_fig("Трюк репараметризації (Reparameterization Trick)", 20)

    # Left panel: problem
    ax.text(0.22, 0.88, "Проблема", ha='center', fontsize=17,
            fontweight='bold', color='#C0392B')
    rbox(ax, 0.22, 0.73, 0.36, 0.20, '#FDEDEC',
         label=r"$z \sim q_\phi(z|x)$  — стохастичний вузол" + "\n\n"
               "Зворотне поширення через\nвипадкову вибірку неможливе",
         fs=13, tc='#C0392B', ec='#C0392B', lw=1.5, bold=False)

    # Draw broken backprop
    arr(ax, 0.14, 0.52, 0.22, 0.62, color='#888')
    ax.text(0.11, 0.50, 'ϕ', fontsize=18, color='#888', fontstyle='italic')
    rbox(ax, 0.22, 0.47, 0.09, 0.09, C_FAKE_DOT, label='z', fs=17)   # stochastic (circle-like)
    arr(ax, 0.22, 0.52, 0.22, 0.60, color=C_FAKE_DOT)
    arr(ax, 0.22, 0.42, 0.22, 0.38, color='#888', head=14)
    ax.text(0.22, 0.33, 'f', fontsize=18, color='#888', fontstyle='italic',
            ha='center')
    ax.plot([0.30, 0.38], [0.47, 0.47], color='#C0392B', lw=2.5)
    ax.plot([0.30, 0.38], [0.42, 0.52], color='#C0392B', lw=2.5)
    ax.text(0.36, 0.54, "Backprop ✗", fontsize=12, color='#C0392B',
            fontweight='bold')

    # Divider
    ax.plot([0.5, 0.5], [0.08, 0.92], color=C_BORDER, lw=2, ls='--')

    # Right panel: solution
    ax.text(0.75, 0.88, "Рішення", ha='center', fontsize=17,
            fontweight='bold', color='#27AE60')
    rbox(ax, 0.75, 0.73, 0.40, 0.20, '#EAFAF1',
         label=r"$z = \mu + \sigma \odot \varepsilon$,  де  $\varepsilon \sim \mathcal{N}(0, I)$" + "\n\n"
               "Випадковість виноситься за межі\nграфа обчислень",
         fs=13, tc='#27AE60', ec='#27AE60', lw=1.5, bold=False)

    # Draw working backprop
    rbox(ax, 0.63, 0.47, 0.08, 0.08, C_MU_SIG, label='μ', fs=16)
    rbox(ax, 0.63, 0.35, 0.08, 0.08, '#E8735A', label='σ', fs=16)
    rbox(ax, 0.75, 0.35, 0.08, 0.08, '#DDDDDD', label='ε', fs=16, tc='#333')
    ax.text(0.71, 0.47, '⊕', ha='center', fontsize=22, color='#27AE60')
    rbox(ax, 0.80, 0.47, 0.08, 0.08, C_LATENT, label='z', fs=16)
    arr(ax, 0.63, 0.51, 0.63, 0.57, color='#888')
    ax.text(0.60, 0.59, 'ϕ', fontsize=18, color='#888', fontstyle='italic')
    arr(ax, 0.63, 0.43, 0.68, 0.47, color=C_MU_SIG)
    arr(ax, 0.63, 0.39, 0.68, 0.43, color='#E8735A')
    arr(ax, 0.75, 0.39, 0.75, 0.43, color='#999', lw=1.5)
    ax.text(0.775, 0.365, r'$\varepsilon \sim \mathcal{N}(0,I)$',
            fontsize=11, color='#666')
    arr(ax, 0.76, 0.47, 0.84, 0.47, color='#555')
    ax.text(0.80, 0.37, 'f', fontsize=18, color='#888', fontstyle='italic',
            ha='center')
    arr(ax, 0.80, 0.43, 0.80, 0.37, color='#888')
    ax.text(0.82, 0.54, "Backprop ✓", fontsize=12, color='#27AE60',
            fontweight='bold')

    ax.text(0.5, 0.13,
            "Параметри φ (μ, σ) стають диференційованими → навчання через зворотне поширення",
            ha='center', fontsize=14, color=C_DARK)

    save("06_reparameterization_trick")


# ══════════════════════════════════════════════════════════════════════════════
# 7. GAN Training Architecture
# ══════════════════════════════════════════════════════════════════════════════
def fig7():
    fig, ax = new_fig("Навчання GAN: змагальний процес", 21)

    cy = 0.55

    # Noise z
    rbox(ax, 0.08, cy, 0.09, 0.14, C_MU_SIG, label='z\nшум', fs=13)
    ax.text(0.08, cy - 0.12, r'$z \sim \mathcal{N}(0,I)$',
            ha='center', fontsize=12, color='#666')

    arr(ax, 0.13, cy, 0.21, cy, color='#555', lw=2)

    # Generator G
    trap(ax, 0.30, cy, 0.18, 0.38, C_GEN, label='G', fs=22, wide_side='right')
    ax.text(0.30, cy + 0.27,
            "G намагається створити\nзображення, що обманює D",
            ha='center', fontsize=12, color=C_GEN, multialignment='center')

    # X_fake
    arr(ax, 0.39, cy, 0.485, cy + 0.10, color='#555', lw=2)
    img_placeholder(ax, 0.50, cy + 0.14, sz=0.09)
    ax.text(0.50, cy + 0.06, r'$X_{fake}$', ha='center', fontsize=14,
            fontstyle='italic', color=C_DARK)

    # X_real
    img_placeholder(ax, 0.50, cy - 0.14, sz=0.09)
    ax.text(0.50, cy - 0.22, r'$X_{real}$', ha='center', fontsize=14,
            fontstyle='italic', color=C_DARK)

    # Arrows to D
    arr(ax, 0.545, cy + 0.14, 0.60, cy + 0.07, color='#555', lw=2)
    arr(ax, 0.545, cy - 0.14, 0.60, cy - 0.07, color='#555', lw=2)

    # Discriminator D
    trap(ax, 0.68, cy, 0.16, 0.34, C_DISC, label='D', fs=22, wide_side='left')
    ax.text(0.68, cy - 0.26,
            "D намагається відрізнити\nсправжні дані від синтетичних",
            ha='center', fontsize=12, color=C_DISC, multialignment='center')

    # Output y
    arr(ax, 0.76, cy, 0.83, cy, color='#555', lw=2)
    rbox(ax, 0.88, cy, 0.09, 0.14, '#F1C40F', label='y', fs=20, tc=C_DARK)
    ax.text(0.88, cy + 0.13, "Справжнє\nчи синтетичне?",
            ha='center', fontsize=11, color='#666', multialignment='center')

    # Bottom summary
    rbox(ax, 0.5, 0.10, 0.85, 0.09, fc=C_LIGHT_BG,
         label="Навчання: змагальні цілі для D та G  |  Глобальний оптимум: G відтворює справжній розподіл даних",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False)

    save("07_gan_training_architecture")


# ══════════════════════════════════════════════════════════════════════════════
# 8. GAN Loss Functions
# ══════════════════════════════════════════════════════════════════════════════
def fig8():
    fig, ax = new_fig("GAN: функції втрат", 21)

    ax.text(0.5, 0.88,
            "Мінімаксна гра між генератором G та дискримінатором D:",
            ha='center', fontsize=14, color=C_DARK)

    # Minmax objective
    rbox(ax, 0.5, 0.74, 0.85, 0.12, C_LIGHT_BG,
         label=r"$\min_G \max_D V(D,G) = \mathbb{E}_{x \sim p_{data}}[\log D(x)]"
               r"+ \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$",
         fs=15, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=True)

    # Two columns
    ax.plot([0.5, 0.5], [0.12, 0.63], color=C_BORDER, lw=1.5, ls='--')

    # Discriminator loss
    ax.text(0.25, 0.63, "Функція втрат дискримінатора", ha='center',
            fontsize=15, fontweight='bold', color=C_DISC)
    rbox(ax, 0.25, 0.48, 0.42, 0.12, '#EAFAF1',
         label=r"$\max_D \, \mathbb{E}[\log D(x)] + \mathbb{E}[\log(1 - D(G(z)))]$",
         fs=13, tc=C_DARK, ec=C_DISC, lw=1.5, bold=False)
    ax.text(0.25, 0.37,
            "D хоче:\n• D(x) → 1  (справжні дані → 1)\n• D(G(z)) → 0  (синтетичні → 0)",
            ha='center', fontsize=13, color=C_DARK, multialignment='left',
            va='top')
    rbox(ax, 0.25, 0.20, 0.38, 0.08, C_DISC + '22',
         label="D розрізняє справжні та синтетичні дані",
         fs=12, tc=C_DISC, ec=C_DISC, lw=1, bold=False)

    # Generator loss
    ax.text(0.75, 0.63, "Функція втрат генератора", ha='center',
            fontsize=15, fontweight='bold', color=C_GEN)
    rbox(ax, 0.75, 0.48, 0.42, 0.12, '#F5EEF8',
         label=r"$\min_G \, \mathbb{E}[\log(1 - D(G(z)))]$",
         fs=13, tc=C_DARK, ec=C_GEN, lw=1.5, bold=False)
    ax.text(0.75, 0.37,
            "G хоче:\n• D(G(z)) → 1  (змусити D\n  вважати синтетичне справжнім)",
            ha='center', fontsize=13, color=C_DARK, multialignment='left',
            va='top')
    rbox(ax, 0.75, 0.20, 0.38, 0.08, C_GEN + '22',
         label="G обманює дискримінатор",
         fs=12, tc=C_GEN, ec=C_GEN, lw=1, bold=False)

    save("08_gan_loss_functions")


# ══════════════════════════════════════════════════════════════════════════════
# 9. GAN as Distribution Transformer
# ══════════════════════════════════════════════════════════════════════════════
def fig9():
    fig, ax = new_fig("GAN — перетворювач розподілів", 21)

    cy = 0.52

    # Noise z box
    rbox(ax, 0.10, cy, 0.11, 0.26, '#F5CBA7',
         label='z', fs=24, tc=C_DARK, ec='#E59866', lw=2)
    ax.text(0.10, cy - 0.20, r"$z \sim \mathcal{N}(0,1)$",
            ha='center', fontsize=13, color=C_DARK)
    ax.text(0.10, cy + 0.20, "Гауссовий\nшум", ha='center', fontsize=12,
            color='#888', multialignment='center')

    arr(ax, 0.16, cy, 0.25, cy, color='#555', lw=2.5, head=18)

    # Generator trapezoid
    trap(ax, 0.36, cy, 0.22, 0.44, C_GEN, label='G', fs=26, wide_side='right')
    ax.text(0.36, cy - 0.32, "Навчений генератор",
            ha='center', fontsize=12, color=C_GEN)

    arr(ax, 0.47, cy, 0.55, cy, color='#555', lw=2.5, head=18)
    ax.text(0.51, cy + 0.06, '?', ha='center', fontsize=22, color='#888')

    arr(ax, 0.63, cy, 0.71, cy, color='#555', lw=2.5, head=18, style='--')

    # Target distribution blob (freeform shape)
    theta = np.linspace(0, 2*np.pi, 200)
    r = 0.18 + 0.04 * np.cos(3*theta) + 0.03 * np.sin(5*theta)
    blob_x = 0.85 + r * np.cos(theta) * 0.65
    blob_y = cy + r * np.sin(theta) * 0.85
    ax.fill(blob_x, blob_y, color=C_LATENT, alpha=0.25)
    ax.plot(blob_x, blob_y, color=C_LATENT, lw=1.5, ls='--')
    ax.text(0.85, cy, 'X', ha='center', va='center', fontsize=30,
            color=C_LATENT, fontweight='bold')
    ax.text(0.85, cy - 0.32, "Цільовий розподіл\nданих", ha='center',
            fontsize=12, color=C_LATENT, multialignment='center')

    ax.text(0.5, 0.12,
            "Генератор перетворює простий (гауссовий) розподіл\n"
            "на складний розподіл реальних даних",
            ha='center', fontsize=14, color=C_DARK, multialignment='center')

    save("09_gan_distribution_transformer")


# ══════════════════════════════════════════════════════════════════════════════
# 10. VAE vs GAN Summary
# ══════════════════════════════════════════════════════════════════════════════
def fig10():
    fig, ax = new_fig("Підсумок: Автокодувальники та GAN", 21)

    # Left: VAE
    rbox(ax, 0.27, 0.55, 0.46, 0.60, C_LIGHT_BG,
         label='', tc=C_DARK, ec=C_LATENT, lw=2)
    ax.text(0.27, 0.82, "Автокодувальники та VAE",
            ha='center', fontsize=16, fontweight='bold', color=C_LATENT)

    # Mini VAE diagram
    trap(ax, 0.18, 0.60, 0.10, 0.22, C_ENCODER, label='', wide_side='left')
    rbox(ax, 0.27, 0.60, 0.04, 0.22, C_LATENT, label='z', fs=12)
    trap(ax, 0.36, 0.60, 0.10, 0.22, C_DECODER, label='', wide_side='right')
    arr(ax, 0.13, 0.60, 0.175, 0.60, color='#555')
    arr(ax, 0.235, 0.60, 0.255, 0.60, color='#555')
    arr(ax, 0.285, 0.60, 0.305, 0.60, color='#555')
    arr(ax, 0.365, 0.60, 0.40, 0.60, color='#555')

    ax.text(0.27, 0.44,
            "• Навчаються прихований простір\n"
            "  меншої розмірності\n"
            "• Вибірка з p(z) для генерації\n"
            "• Явна функція втрат\n"
            "  (реконструкція + KL)",
            ha='center', fontsize=12, color=C_DARK, va='top',
            multialignment='left')

    # Right: GAN
    rbox(ax, 0.73, 0.55, 0.46, 0.60, C_LIGHT_BG,
         label='', tc=C_DARK, ec=C_GEN, lw=2)
    ax.text(0.73, 0.82, "Генеративно-змагальні мережі (GAN)",
            ha='center', fontsize=16, fontweight='bold', color=C_GEN)

    # Mini GAN diagram
    rbox(ax, 0.61, 0.60, 0.05, 0.10, C_MU_SIG, label='z', fs=12)
    trap(ax, 0.69, 0.60, 0.10, 0.22, C_GEN, label='G', fs=14, wide_side='right')
    trap(ax, 0.79, 0.60, 0.10, 0.22, C_DISC, label='D', fs=14, wide_side='left')
    arr(ax, 0.64, 0.60, 0.655, 0.60, color='#555')
    arr(ax, 0.74, 0.60, 0.755, 0.60, color='#555')
    rbox(ax, 0.87, 0.60, 0.05, 0.10, '#F1C40F', label='y', fs=12, tc=C_DARK)
    arr(ax, 0.84, 0.60, 0.848, 0.60, color='#555')

    ax.text(0.73, 0.44,
            "• Змагальне навчання двох мереж\n"
            "• Генератор та дискримінатор\n"
            "• Неявне моделювання розподілу\n"
            "• Часто дають якісніші зображення,\n"
            "  але складніші у навчанні",
            ha='center', fontsize=12, color=C_DARK, va='top',
            multialignment='left')

    ax.text(0.5, 0.13,
            "Обидва підходи навчаються генерувати нові зразки,\n"
            "що відповідають розподілу навчальних даних",
            ha='center', fontsize=13, color=C_DARK, multialignment='center')

    save("10_vae_vs_gan_summary")


# ══════════════════════════════════════════════════════════════════════════════
# 11. Diffusion Models
# ══════════════════════════════════════════════════════════════════════════════
def fig11():
    fig, ax = new_fig("Дифузійні моделі (Diffusion Models)", 21)

    ax.text(0.5, 0.88,
            "Навчаються поступово прибирати шум — крок за кроком",
            ha='center', fontsize=14, color=C_DARK)

    cy_fwd = 0.66
    cy_rev = 0.36
    steps = ['$x_0$', '$x_1$', '$x_2$', '...', '$x_{T-1}$', '$x_T$']
    xs = [0.10, 0.25, 0.40, 0.52, 0.66, 0.82]

    # ── Forward process (top row) ──
    ax.text(0.03, cy_fwd + 0.04, "Прямий\nпроцес:", fontsize=12,
            color='#C0392B', va='center', multialignment='right')
    ax.annotate('', xy=(0.88, cy_fwd), xytext=(0.08, cy_fwd),
                arrowprops=dict(arrowstyle='->', color='#C0392B', lw=2))
    ax.text(0.5, cy_fwd + 0.08, "Поступове додавання шуму  q(x_t | x_{t-1})",
            ha='center', fontsize=12, color='#C0392B')

    grays_fwd = [0.88, 0.72, 0.56, 0.45, 0.35, 0.22]
    for i, (xp, step, gv) in enumerate(zip(xs, steps, grays_fwd)):
        rbox(ax, xp, cy_fwd, 0.08, 0.16, str(gv), label='',
             tc='white', ec='#888', lw=1)
        ax.text(xp, cy_fwd, step, ha='center', va='center',
                fontsize=12, color='white' if gv < 0.5 else '#333')
    ax.text(xs[0], cy_fwd - 0.12, "Зображення\n$x_0$",
            ha='center', fontsize=10, color='#666', multialignment='center')
    ax.text(xs[-1], cy_fwd - 0.12, "Чистий\nгауссовий шум",
            ha='center', fontsize=10, color='#666', multialignment='center')

    # ── Reverse process (bottom row) ──
    ax.text(0.03, cy_rev + 0.04, "Зворотний\nпроцес:", fontsize=12,
            color='#27AE60', va='center', multialignment='right')
    ax.annotate('', xy=(0.08, cy_rev), xytext=(0.88, cy_rev),
                arrowprops=dict(arrowstyle='->', color='#27AE60', lw=2))
    ax.text(0.5, cy_rev + 0.08,
            "Поступове видалення шуму  $p_\\theta(x_{t-1} | x_t)$",
            ha='center', fontsize=12, color='#27AE60')

    grays_rev = list(reversed(grays_fwd))
    steps_rev = list(reversed(steps))
    for i, (xp, step, gv) in enumerate(zip(xs, steps_rev, grays_rev)):
        rbox(ax, xp, cy_rev, 0.08, 0.16, str(gv), label='',
             tc='white', ec='#888', lw=1)
        ax.text(xp, cy_rev, step, ha='center', va='center',
                fontsize=12, color='white' if gv < 0.5 else '#333')
    ax.text(xs[0], cy_rev - 0.12, "Чистий шум\n$x_T$",
            ha='center', fontsize=10, color='#666', multialignment='center')
    ax.text(xs[-1], cy_rev - 0.12, "Згенеровані\nдані $x_0$",
            ha='center', fontsize=10, color='#666', multialignment='center')

    # Neural net label
    rbox(ax, 0.5, 0.14, 0.65, 0.09, C_LIGHT_BG,
         label="Нейронна мережа навчається передбачати шум "
               r"$\varepsilon_\theta(x_t, t)$ на кожному кроці",
         fs=13, tc=C_DARK, ec=C_BORDER, lw=1.5, bold=False)

    save("11_diffusion_models")


# ══════════════════════════════════════════════════════════════════════════════
# Run all
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating lecture graphics...")
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    fig8()
    fig9()
    fig10()
    fig11()
    print(f"\nAll done → {OUTPUT_DIR}/")
