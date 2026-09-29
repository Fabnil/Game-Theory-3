"""Rebuild the additional SVG explanations paired with photographed board drawings.

Run from any directory with Python, NumPy and Matplotlib installed:
    python3 generate_board_explanations.py

Text and equations remain editable in this source. The exported SVGs outline
glyphs so math labels render consistently in Markdown preview and browsers.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon


OUT = Path(__file__).resolve().parents[1]
BG = "#f8fafc"
NAVY = "#14243c"
MUTED = "#475569"
BLUE = "#2563eb"
BLUE_BG = "#dbeafe"
GREEN = "#15803d"
GREEN_BG = "#dcfce7"
RED = "#dc2626"
RED_BG = "#fee2e2"
AMBER = "#b45309"
AMBER_BG = "#fef3c7"
PURPLE = "#7c3aed"
PURPLE_BG = "#ede9fe"
BORDER = "#cbd5e1"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "svg.fonttype": "path",
})


def canvas(title, subtitle=""):
    fig = plt.figure(figsize=(12, 6.8), dpi=100, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1200), ylim=(680, 0))
    ax.set_aspect("equal")
    ax.axis("off")
    title_size = 23 if len(title) > 55 else 26
    txt(ax, 55, 54, title, title_size, NAVY, "bold")
    if subtitle:
        txt(ax, 55, 100, subtitle, 16, MUTED)
    return fig, ax


def txt(ax, x, y, value, size=20, color=NAVY, weight="normal", align="left"):
    return ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                   ha=align, va="center")


def rect(ax, x, y, w, h, fill="white", edge=BORDER, radius=15, line=1.6):
    shape = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0,rounding_size={radius}",
                           facecolor=fill, edgecolor=edge, linewidth=line)
    ax.add_patch(shape)
    return shape


def arr(ax, start, end, color=MUTED, width=2.4, curve=None):
    kw = {"arrowstyle": "-|>", "mutation_scale": 20, "linewidth": width,
          "color": color}
    if curve:
        kw["connectionstyle"] = curve
    arrow = FancyArrowPatch(start, end, **kw)
    ax.add_patch(arrow)
    return arrow


def dot(ax, x, y, r=8, color=BLUE, edge="white"):
    shape = Circle((x, y), r, facecolor=color, edgecolor=edge, linewidth=1.5)
    ax.add_patch(shape)
    return shape


def save(fig, name):
    path = OUT / name
    fig.savefig(path, format="svg", facecolor=BG, edgecolor="none",
                bbox_inches=None, pad_inches=0)
    plt.close(fig)
    path.write_text("\n".join(line.rstrip() for line in
                              path.read_text().splitlines()) + "\n")
    print(path.name)


def fully_labeled_pair():
    fig, ax = canvas("Полная размеченность в модельной игре",
                     "Все пять меток должны встретиться в паре точек")
    rect(ax, 55, 148, 515, 392)
    rect(ax, 630, 148, 515, 392)
    txt(ax, 85, 185, "График Боба", 21, BLUE, "bold")
    txt(ax, 85, 230, r"$\sigma^*=(1/3,\,2/3)$", 23)
    ax.plot([115, 495], [350, 350], color=MUTED, linewidth=2)
    for x, label in [(115, "0"), (242, r"$1/3$"), (305, r"$1/2$"), (495, "1")]:
        ax.plot([x, x], [343, 357], color=MUTED, linewidth=2)
        txt(ax, x, 379, label, 17, MUTED, align="center")
    dot(ax, 242, 350, 10, BLUE)
    txt(ax, 85, 430, "При $x=1/3$ лучшие ответы Боба:", 18)
    txt(ax, 85, 470, "$M$ и $R$  →  метки {$M,R$}", 21, BLUE, "bold")

    txt(ax, 660, 185, "Смесь Боба", 21, GREEN, "bold")
    txt(ax, 660, 230, r"$\tau^*=(0,\,2/5,\,3/5)$", 23)
    L, M, R = (710, 480), (1050, 480), (880, 268)
    ax.add_patch(Polygon([L, M, R], closed=True, facecolor="#f0fdf4",
                         edgecolor=GREEN, linewidth=2.4))
    ax.plot([M[0], R[0]], [M[1], R[1]], color=GREEN, linewidth=6)
    q = (0.4 * M[0] + 0.6 * R[0], 0.4 * M[1] + 0.6 * R[1])
    dot(ax, *q, r=10, color=GREEN)
    for point, label, dx in [(L, "$L$", -19), (M, "$M$", 19),
                             (R, "$R$", 20)]:
        txt(ax, point[0] + dx, point[1], label, 20, NAVY, align="center")
    txt(ax, 952, 317, r"$\ell=0$", 17, GREEN)
    txt(ax, 660, 518, "Метки: $L$ — нуль, $U,D$ — лучшие ответы", 15)

    rect(ax, 55, 568, 1090, 77, BLUE_BG, BLUE)
    txt(ax, 600, 606, r"$\{M,R\}\cup\{L,U,D\}=\{L,M,R,U,D\}$",
        25, NAVY, "bold", "center")
    save(fig, "01_fully-labeled-pair.svg")


def lemke_pivot():
    fig, ax = canvas("Путь Лемке — Хоусона: что значит «снять метку»",
                     "Повороты чередуются между двумя многогранниками")
    cards = [
        (55, "Начало", "$(0,0)$", "все метки", BLUE_BG, BLUE),
        (340, "Убрать $k$", "поворот по ребру", "$k$ отсутствует", AMBER_BG, AMBER),
        (625, r"Повтор $\ell$", "другой полиэдр", r"снять повтор $\ell$", PURPLE_BG, PURPLE),
        (910, "Вернулась $k$", "все метки", "ненулевая пара", GREEN_BG, GREEN),
    ]
    for x, title, line1, line2, fill, edge in cards:
        rect(ax, x, 205, 235, 255, fill, edge)
        txt(ax, x + 117, 255, title, 20, NAVY, "bold", "center")
        txt(ax, x + 117, 327, line1, 16, NAVY, align="center")
        txt(ax, x + 117, 366, line2, 15, MUTED, align="center")
    for a, b in [(290, 333), (575, 618), (860, 903)]:
        arr(ax, (a, 330), (b, 330))
    arr(ax, (785, 475), (440, 475), PURPLE, 2, "arc3,rad=-0.15")
    txt(ax, 600, 548, "Продолжать, пока не вернётся $k$", 18,
        PURPLE, "bold", "center")
    rect(ax, 185, 580, 830, 63, "white", BORDER)
    txt(ax, 600, 611, r"Внутри пути: $k$ отсутствует, $\ell$ повторена",
        18, NAVY, align="center")
    save(fig, "01_lemke-pivot.svg")


def path_parity():
    fig, ax = canvas("Почему путь приводит к равновесию",
                     "Невырожденная игра: концы имеют степень 1, внутренние вершины — степень 2")
    for a, b in [((180, 262), (400, 262)), ((400, 262), (620, 262)),
                 ((620, 262), (840, 262))]:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=BLUE, linewidth=5)
    for x, color in [(180, AMBER), (400, BLUE), (620, BLUE), (840, GREEN)]:
        dot(ax, x, 262, 20, color)
    txt(ax, 180, 315, "искусственная", 17, AMBER, "bold", "center")
    txt(ax, 180, 342, "точка", 17, AMBER, align="center")
    txt(ax, 510, 315, "внутренние вершины", 17, BLUE, align="center")
    txt(ax, 840, 315, "настоящее NE", 17, GREEN, "bold", "center")
    rect(ax, 80, 390, 1040, 196, "white", BORDER)
    txt(ax, 600, 438, "Каждый путь имеет два конца; циклы концов не добавляют.",
        20, NAVY, align="center")
    txt(ax, 600, 488, "Один конец — искусственная точка $(0,0)$.",
        20, NAVY, align="center")
    txt(ax, 600, 542, "Поэтому число настоящих равновесий нечётно.",
        23, GREEN, "bold", "center")
    save(fig, "01_path-parity.svg")


def chicken_matrix():
    fig, ax = canvas("Chicken Game: что показывает матрица на доске",
                     "В каждой клетке сначала выигрыш Алисы, затем Боба")
    x0, y0, cw, ch = 302, 208, 285, 145
    txt(ax, 444, 174, "Боб: Stop", 20, NAVY, "bold", "center")
    txt(ax, 729, 174, "Боб: Go", 20, NAVY, "bold", "center")
    txt(ax, 278, 279, "Алиса: Stop", 19, NAVY, "bold", "right")
    txt(ax, 278, 424, "Алиса: Go", 19, NAVY, "bold", "right")
    cells = [
        (x0, y0, "$(4,4)$", AMBER_BG, AMBER, "сумма 8"),
        (x0 + cw, y0, "$(1,5)$", GREEN_BG, GREEN, "чистое NE"),
        (x0, y0 + ch, "$(5,1)$", GREEN_BG, GREEN, "чистое NE"),
        (x0 + cw, y0 + ch, "$(0,0)$", "white", BORDER, "оба едут"),
    ]
    for x, y, pair, fill, edge, note in cells:
        rect(ax, x, y, cw - 8, ch - 8, fill, edge, 10)
        txt(ax, x + (cw - 8) / 2, y + 53, pair, 26, NAVY, "bold", "center")
        txt(ax, x + (cw - 8) / 2, y + 101, note, 17,
            edge if edge != BORDER else MUTED, align="center")
    rect(ax, 225, 550, 755, 76, BLUE_BG, BLUE)
    txt(ax, 602, 588,
        r"$\mu(S,S)=\mu(S,G)=\mu(G,S)=1/3$",
        21, NAVY, align="center")
    save(fig, "02_chicken-payoff-matrix.svg")


def ce_payoff_region():
    fig, ax = canvas("Область выигрышей коррелированных равновесий",
                     "Chicken Game: точная проекция условий CE на плоскость выигрышей")
    x0, y0, sx, sy = 125, 575, 100, 72
    X = lambda u: x0 + sx * u
    Y = lambda u: y0 - sy * u
    ax.plot([X(0), X(6.1)], [Y(0), Y(0)], color=NAVY, linewidth=2)
    ax.plot([X(0), X(0)], [Y(0), Y(6.1)], color=NAVY, linewidth=2)
    for k in range(1, 6):
        ax.plot([X(k), X(k)], [Y(0) - 5, Y(0) + 5], color=MUTED)
        ax.plot([X(0) - 5, X(0) + 5], [Y(k), Y(k)], color=MUTED)
        txt(ax, X(k), 602, str(k), 14, MUTED, align="center")
        txt(ax, 100, Y(k), str(k), 14, MUTED, align="right")
    txt(ax, 755, 577, r"$u_A$", 22, NAVY)
    txt(ax, 110, 121, r"$u_B$", 22, NAVY)
    pts = [(1, 5), (2, 2), (5, 1), (10 / 3, 10 / 3)]
    ax.add_patch(Polygon([(X(a), Y(b)) for a, b in pts], closed=True,
                         facecolor="#e0e7ff", edgecolor=BLUE, linewidth=3,
                         alpha=0.9))
    ax.plot([X(1), X(10 / 3), X(5)], [Y(5), Y(10 / 3), Y(1)],
            color=GREEN, linewidth=5)
    for a, b, color in [(1, 5, GREEN), (5, 1, GREEN), (2, 2, AMBER),
                        (10 / 3, 10 / 3, PURPLE), (2.5, 2.5, BLUE)]:
        dot(ax, X(a), Y(b), 9, color)
    rect(ax, 840, 165, 310, 390, "white", BORDER)
    txt(ax, 868, 206, "Точки на графике", 20, NAVY, "bold")
    legends = [
        (GREEN, "$(1,5)$ и $(5,1)$", "чистые NE"),
        (BLUE, "$(5/2,5/2)$", "смешанное NE"),
        (PURPLE, "$(10/3,10/3)$", "лучшее по сумме CE"),
        (AMBER, "$(2,2)$", "худшее CE"),
    ]
    for j, (color, coord, label) in enumerate(legends):
        yy = 265 + 72 * j
        dot(ax, 875, yy, 8, color)
        txt(ax, 899, yy - 12, coord, 16, NAVY, "bold")
        txt(ax, 899, yy + 15, label, 14, MUTED)
    save(fig, "02_ce-payoff-region.svg")


def swap_map():
    fig, ax = canvas("Swap regret: замена зависит от исходного действия",
                     "Функция $f$ не обязана быть перестановкой")
    txt(ax, 285, 175, "Выбранное действие", 20, BLUE, "bold", "center")
    txt(ax, 915, 175, "Действие по правилу $f$", 20, GREEN, "bold", "center")
    ys = [260, 370, 480]
    for j, y in enumerate(ys, 1):
        rect(ax, 180, y - 35, 210, 70, BLUE_BG, BLUE)
        rect(ax, 810, y - 35, 210, 70, GREEN_BG, GREEN)
        txt(ax, 285, y, f"${j}$", 24, NAVY, "bold", "center")
        txt(ax, 915, y, f"${j}$", 24, NAVY, "bold", "center")
    for a, b in [(0, 1), (1, 1), (2, 0)]:
        arr(ax, (393, ys[a]), (805, ys[b]), PURPLE, 2.8)
    rect(ax, 275, 542, 650, 97, PURPLE_BG, PURPLE)
    txt(ax, 600, 574, r"$f(1)=2,\quad f(2)=2,\quad f(3)=1$",
        21, NAVY, align="center")
    txt(ax, 600, 612, "Две стрелки сходятся в $2$", 17, PURPLE,
        align="center")
    save(fig, "02_swap-map.svg")


def online_full_information():
    fig, ax = canvas("Онлайн-раунд: порядок событий",
                     "Модель полной информации из второй лекции")
    cards = [
        (55, "История", "раунды до $t$", BLUE_BG, BLUE),
        (340, "Агент", r"выбирает $\sigma^t$", PURPLE_BG, PURPLE),
        (625, "Среда", r"задаёт $\ell^t$", AMBER_BG, AMBER),
        (910, "Выбор", r"$I_t\sim\sigma^t$", GREEN_BG, GREEN),
    ]
    for x, title, formula, fill, edge in cards:
        rect(ax, x, 210, 235, 245, fill, edge)
        txt(ax, x + 117, 269, title, 20, NAVY, "bold", "center")
        txt(ax, x + 117, 363, formula, 17, NAVY, align="center")
    for a, b in [(290, 333), (575, 618), (860, 903)]:
        arr(ax, (a, 336), (b, 336))
    rect(ax, 145, 522, 910, 113, "white", BORDER)
    txt(ax, 600, 560, r"После выбора агент видит весь вектор $\ell^t$",
        21, GREEN, "bold", "center")
    txt(ax, 600, 604,
        r"Реальная потеря в раунде: $\ell_{I_t}^t$",
        19, NAVY, align="center")
    save(fig, "02_online-round.svg")


def regret_to_ce():
    fig, ax = canvas("От малого сожаления к приближённому CE",
                     "Результат относится к среднему распределению сыгранных профилей")
    cards = [
        (55, "Повторы", "$T$ раундов", BLUE_BG, BLUE),
        (340, "Сожаление", r"$R_i^{\rm swap}(T)=o(T)$", PURPLE_BG, PURPLE),
        (625, "Усреднение", r"$\hat\mu_T=\frac{1}{T}\sum_t\delta_{s^t}$", AMBER_BG, AMBER),
        (910, "Итог", r"$\varepsilon_T$-CE", GREEN_BG, GREEN),
    ]
    for x, title, formula, fill, edge in cards:
        rect(ax, x, 215, 235, 245, fill, edge)
        txt(ax, x + 117, 270, title, 17, NAVY, "bold", "center")
        txt(ax, x + 117, 355, formula, 16, NAVY, align="center")
    for a, b in [(290, 334), (575, 619), (860, 904)]:
        arr(ax, (a, 337), (b, 337))
    rect(ax, 155, 530, 890, 98, "white", BORDER)
    txt(ax, 600, 565,
        r"$\mathbb{E}_{s\sim\hat\mu_T}[u_i(f_i(s_i),s_{-i})-u_i(s)]\leq R_i^{\rm swap}(T)/T$",
        17, NAVY, align="center")
    txt(ax, 600, 602,
        r"$\varepsilon_T=\max_i R_i^{\rm swap}(T)/T\longrightarrow 0$",
        18, GREEN, "bold", "center")
    save(fig, "02_regret-to-ce.svg")


def comparator_grid():
    fig, ax = canvas("Почему эталон не может меняться каждый раунд",
                     "Пример потерь: динамический план выбирает ноль в каждой строке")
    left, top, cw, ch = 350, 218, 145, 85
    txt(ax, 560, 153, "Действия", 19, NAVY, "bold", "center")
    for j in range(3):
        txt(ax, left + j * cw + cw / 2, 186, f"${j + 1}$",
            19, NAVY, "bold", "center")
    for t in range(3):
        txt(ax, 325, top + t * ch + ch / 2, f"Раунд ${t + 1}$",
            18, NAVY, "bold", "right")
        for j in range(3):
            value = 0 if t == j else 1
            x, y = left + j * cw, top + t * ch
            rect(ax, x, y, cw - 8, ch - 8,
                 GREEN_BG if value == 0 else "white",
                 GREEN if value == 0 else BORDER, 9)
            txt(ax, x + (cw - 8) / 2, y + (ch - 8) / 2,
                str(value), 24, GREEN if value == 0 else MUTED,
                "bold", "center")
    rect(ax, 120, 525, 445, 90, GREEN_BG, GREEN)
    rect(ax, 635, 525, 445, 90, BLUE_BG, BLUE)
    txt(ax, 342, 558, "Меняющийся выбор: $0$", 18,
        GREEN, "bold", "center")
    txt(ax, 342, 590, "по одному нулю в каждом раунде", 15,
        MUTED, align="center")
    txt(ax, 857, 558, "Фиксированное действие: $2$", 18,
        BLUE, "bold", "center")
    txt(ax, 857, 590, "любой из трёх столбцов", 15, MUTED, align="center")
    save(fig, "03_comparator-grid.svg")


def greedy_leaders():
    fig, ax = canvas("Greedy: выбранный лидер выбывает",
                     "Один шаг с бинарными потерями; минимум накопленных потерь остаётся равным 2")
    rect(ax, 55, 180, 485, 350, "white", BORDER)
    rect(ax, 660, 180, 485, 350, "white", BORDER)
    txt(ax, 88, 220, "До раунда", 22, BLUE, "bold")
    txt(ax, 693, 220, "После раунда", 22, GREEN, "bold")
    txt(ax, 88, 272, r"$L^{t-1}=(2,\,2,\,3,\,4)$", 23)
    txt(ax, 693, 272, r"$L^{t}=(3,\,2,\,3,\,4)$", 23)
    txt(ax, 88, 334, r"$S^{t-1}=\{1,2\}$", 22)
    txt(ax, 693, 334, r"$S^t=\{2\}$", 22)
    txt(ax, 88, 407, "Greedy выбирает $1$", 20, BLUE, "bold")
    txt(ax, 693, 407, "Лидер $1$ выбывает", 20, GREEN, "bold")
    txt(ax, 88, 475, r"$L_{\min}^{t-1}=2,\quad |S^{t-1}|=2$", 17, MUTED)
    txt(ax, 693, 475, r"$L_{\min}^{t}=2,\quad |S^{t}|=1$", 17, MUTED)
    arr(ax, (547, 353), (653, 353), PURPLE, 3)
    txt(ax, 600, 155, r"$\ell^t=(1,0,0,0)$", 19,
        PURPLE, "bold", "center")
    rect(ax, 125, 563, 950, 74, AMBER_BG, AMBER)
    txt(ax, 600, 601,
        r"$N L_{\min}^t+N-|S^t|$ возрастает на $1$ и покрывает потерю Greedy",
        18, NAVY, align="center")
    save(fig, "03_greedy-leaders.svg")


def randomized_greedy_leaders():
    fig, ax = canvas("Randomized Greedy: противник видит вероятности",
                     "Четыре текущих лидера, два из них получают единицу потери")
    xs = [220, 470, 720, 970]
    for j, x in enumerate(xs, 1):
        penalized = j in (2, 4)
        rect(ax, x - 90, 230, 180, 190,
             RED_BG if penalized else GREEN_BG,
             RED if penalized else GREEN)
        txt(ax, x, 276, f"Действие ${j}$", 17, NAVY, "bold", "center")
        txt(ax, x, 329, r"$p_i^t=1/4$", 20, BLUE, align="center")
        txt(ax, x, 378, r"$\ell_i^t=1$" if penalized else r"$\ell_i^t=0$",
            21, RED if penalized else GREEN, "bold", "center")
    rect(ax, 90, 493, 480, 120, BLUE_BG, BLUE)
    rect(ax, 630, 493, 480, 120, PURPLE_BG, PURPLE)
    txt(ax, 330, 537, r"$\mathbb{E}[\ell_{I_t}^t]=2/4=1/2$", 21,
        BLUE, "bold", "center")
    txt(ax, 330, 580, "ожидаемая потеря", 16, MUTED, align="center")
    txt(ax, 870, 537, r"$|S^{t-1}|=4\;\longrightarrow\;|S^t|=2$", 19,
        PURPLE, "bold", "center")
    txt(ax, 870, 580, "два лидера выбывают", 16, MUTED, align="center")
    save(fig, "03_randomized-greedy-leaders.svg")


def rwm_update():
    fig, ax = canvas("RWM: потеря плавно уменьшает вес действия",
                     r"Бинарные потери, пример при $\eta=1/4$")
    rect(ax, 85, 190, 1030, 340, "white", BORDER)
    headers = [(290, "Действие"), (485, r"$w_i^t$"),
               (680, r"$\ell_i^t$"), (875, r"$w_i^{t+1}$")]
    for x, name in headers:
        txt(ax, x, 245, name, 21, NAVY, "bold", "center")
    vals = [(1, "1", "0", "1"), (2, "1", "1", "3/4"),
            (3, "1", "1", "3/4")]
    for j, (idx, w, loss, updated) in enumerate(vals):
        y = 315 + 80 * j
        if j:
            ax.plot([160, 1040], [y - 40, y - 40], color=BORDER, linewidth=1)
        for x, value in [(290, str(idx)), (485, w), (680, loss),
                         (875, updated)]:
            color = GREEN if x == 875 and loss == "0" else (
                RED if x == 875 else NAVY)
            txt(ax, x, y, f"${value}$", 22, color,
                "bold" if x == 875 else "normal", "center")
    rect(ax, 85, 563, 1030, 75, BLUE_BG, BLUE)
    txt(ax, 600, 599,
        r"$w_i^{t+1}=w_i^t(1-\eta)^{\ell_i^t},\quad "
        r"p^{t+1}=(2/5,\,3/10,\,3/10)$",
        20, NAVY, "bold", "center")
    save(fig, "03_rwm-update.svg")


def main():
    fully_labeled_pair()
    lemke_pivot()
    path_parity()
    chicken_matrix()
    ce_payoff_region()
    swap_map()
    online_full_information()
    regret_to_ce()
    comparator_grid()
    greedy_leaders()
    randomized_greedy_leaders()
    rwm_update()


if __name__ == "__main__":
    main()
