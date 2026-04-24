"""
Численные методы, задания 1-8.
Автор: Багрин А.Р 435 группа 2026 год.
Скрипт собран по материалам конспектов занятий:
1) машинная точность и "дыры" между числами;
2) устойчивое решение квадратного уравнения;
3) вычисление sin(x) и ln(x);
4) вычисление интеграла тремя способами;
5) ошибка численного дифференцирования;
6) метод Эйлера для скалярных ОДУ;
7) двумерный метод Эйлера для гармонического осциллятора;
8) творческое задание: метод Ньютона.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


EPS_A_ZERO = 1e-18
DEFAULT_STEPS = [1.0, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]
PLOTS_DIR = Path(__file__).resolve().parent / "plots"


def format_float(value: float, digits: int = 16) -> str:
    """Короткая печать чисел без лишнего шума."""
    return f"{value:.{digits}g}"


def ensure_plots_dir() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)


def frange(start: float, stop: float, count: int) -> list[float]:
    if count < 2:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + i * step for i in range(count)]


def nice_ticks(vmin: float, vmax: float, count: int = 5) -> list[float]:
    if math.isclose(vmin, vmax, rel_tol=0.0, abs_tol=1e-15):
        spread = 1.0 if abs(vmin) < 1.0 else 0.1 * abs(vmin)
        vmin -= spread
        vmax += spread

    span = vmax - vmin
    raw_step = span / max(count - 1, 1)
    power = 10.0 ** math.floor(math.log10(abs(raw_step)))
    normalized = raw_step / power
    if normalized <= 1.0:
        step = 1.0 * power
    elif normalized <= 2.0:
        step = 2.0 * power
    elif normalized <= 5.0:
        step = 5.0 * power
    else:
        step = 10.0 * power

    tick_start = math.floor(vmin / step) * step
    tick_end = math.ceil(vmax / step) * step
    ticks = []
    value = tick_start
    while value <= tick_end + 0.5 * step:
        ticks.append(value)
        value += step
    return ticks


def svg_plot(
    filename: str,
    title: str,
    x_label: str,
    y_label: str,
    series: list[dict[str, object]],
    log_x: bool = False,
    log_y: bool = False,
) -> Path:
    ensure_plots_dir()
    width = 960
    height = 640
    left = 90
    right = 220
    top = 70
    bottom = 90
    plot_width = width - left - right
    plot_height = height - top - bottom

    def to_axis_value(value: float, use_log: bool) -> float:
        if use_log:
            if value <= 0.0:
                raise ValueError("Для логарифмической шкалы нужны только положительные значения.")
            return math.log10(value)
        return value

    all_x = []
    all_y = []
    for item in series:
        all_x.extend(float(x) for x in item["x"])
        all_y.extend(float(y) for y in item["y"])

    x_axis = [to_axis_value(x, log_x) for x in all_x]
    y_axis = [to_axis_value(y, log_y) for y in all_y]
    x_min, x_max = min(x_axis), max(x_axis)
    y_min, y_max = min(y_axis), max(y_axis)

    x_ticks = nice_ticks(x_min, x_max, count=6)
    y_ticks = nice_ticks(y_min, y_max, count=6)

    def map_x(value: float) -> float:
        axis_value = to_axis_value(value, log_x)
        return left + (axis_value - x_min) / (x_max - x_min) * plot_width

    def map_y(value: float) -> float:
        axis_value = to_axis_value(value, log_y)
        return top + plot_height - (axis_value - y_min) / (y_max - y_min) * plot_height

    def format_tick(value: float, use_log: bool) -> str:
        if use_log:
            return f"1e{int(round(value))}"
        if abs(value) >= 1000 or (abs(value) < 0.01 and value != 0.0):
            return f"{value:.1e}"
        return f"{value:.4g}"

    colors = ["#0b6e4f", "#c1121f", "#1d4ed8", "#f59e0b", "#7c3aed", "#0f766e"]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fffdf8"/>',
        f'<text x="{width / 2}" y="36" text-anchor="middle" font-size="24" font-family="Arial">{title}</text>',
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" fill="#ffffff" stroke="#d1d5db"/>',
    ]

    for tick in x_ticks:
        x = left + (tick - x_min) / (x_max - x_min) * plot_width
        lines.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_height}" stroke="#e5e7eb" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{x:.2f}" y="{top + plot_height + 28}" text-anchor="middle" font-size="14" font-family="Arial">{format_tick(tick, log_x)}</text>'
        )

    for tick in y_ticks:
        y = top + plot_height - (tick - y_min) / (y_max - y_min) * plot_height
        lines.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="#e5e7eb" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end" font-size="14" font-family="Arial">{format_tick(tick, log_y)}</text>'
        )

    lines.append(
        f'<text x="{left + plot_width / 2}" y="{height - 24}" text-anchor="middle" font-size="18" font-family="Arial">{x_label}</text>'
    )
    lines.append(
        f'<text x="28" y="{top + plot_height / 2}" text-anchor="middle" font-size="18" font-family="Arial" transform="rotate(-90 28 {top + plot_height / 2})">{y_label}</text>'
    )

    legend_y = top + 30
    for index, item in enumerate(series):
        color = item.get("color", colors[index % len(colors)])
        points = " ".join(f"{map_x(float(x)):.2f},{map_y(float(y)):.2f}" for x, y in zip(item["x"], item["y"]))
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{points}"/>')
        for x, y in zip(item["x"], item["y"]):
            lines.append(
                f'<circle cx="{map_x(float(x)):.2f}" cy="{map_y(float(y)):.2f}" r="3.5" fill="{color}"/>'
            )
        lx = left + plot_width + 30
        ly = legend_y + index * 28
        lines.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 28}" y2="{ly}" stroke="{color}" stroke-width="4"/>')
        lines.append(f'<text x="{lx + 38}" y="{ly + 5}" font-size="15" font-family="Arial">{item["label"]}</text>')

    lines.append("</svg>")
    output = PLOTS_DIR / filename
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def task1_machine_properties() -> tuple[int, int, int]:
    """
    Возвращает:
    1) порядок машинной точности epsilon ~ 10^(-p),
    2) порядок x, для которого x + 1 == x,
    3) порядок y, для которого y + 10^24 == y.
    """
    eps = 1.0
    while 1.0 + eps / 2.0 > 1.0:
        eps /= 2.0

    x = 1.0
    while x + 1.0 > x:
        x *= 2.0

    y = 1.0
    huge = 10.0**24
    while y + huge > y:
        y *= 2.0

    eps_order = int(math.floor(-math.log10(eps)))
    x_order = int(math.floor(math.log10(x)))
    y_order = int(math.floor(math.log10(y)))
    return eps_order, x_order, y_order


def print_task1_answer() -> None:
    eps_order, x_order, y_order = task1_machine_properties()
    print("Задание 1")
    print(f"Порядок машинной точности: 10^(-{eps_order})")
    print(f"Порядок числа, где дырка > 1: 10^{x_order}")
    print(f"Порядок числа, где дырка > 10^24: 10^{y_order}")
    print()


def solve_quadratic(a: float, b: float, c: float) -> list[float]:
    """
    Устойчивое решение квадратного уравнения.
    Возвращает список действительных корней.
    """
    if abs(a) < EPS_A_ZERO:
        if abs(b) < EPS_A_ZERO:
            if abs(c) < EPS_A_ZERO:
                raise ValueError("Бесконечно много решений.")
            raise ValueError("Решений нет.")
        return [-c / b]

    d = b * b - 4.0 * a * c
    if d < 0.0:
        raise ValueError("Действительных корней нет.")

    sqrt_d = math.sqrt(d)
    if b >= 0.0:
        q = -0.5 * (b + sqrt_d)
    else:
        q = -0.5 * (b - sqrt_d)

    x1 = q / a
    if abs(q) < EPS_A_ZERO:
        x2 = -b / (2.0 * a)
    else:
        x2 = c / q

    roots = sorted([x1, x2])
    if abs(roots[0] - roots[1]) < 1e-14 * max(1.0, abs(roots[0]), abs(roots[1])):
        return [roots[0]]
    return roots


def interactive_quadratic() -> None:
    print("Задание 2")
    a = float(input("Введите a: "))
    b = float(input("Введите b: "))
    c = float(input("Введите c: "))
    try:
        roots = solve_quadratic(a, b, c)
        print("Корни:")
        for index, root in enumerate(roots, start=1):
            print(f"x{index} = {format_float(root)}")
    except ValueError as exc:
        print(exc)
    print()


def reduce_angle(x: float) -> float:
    """Приводит x к отрезку [-pi, pi]."""
    twopi = 2.0 * math.pi
    y = math.fmod(x, twopi)
    if y > math.pi:
        y -= twopi
    elif y < -math.pi:
        y += twopi
    return y


def sin_series(x: float, eps: float = 1e-15) -> float:
    """
    Вычисление sin(x) через ряд с уменьшением аргумента.
    """
    x = reduce_angle(x)
    if x > math.pi / 2.0:
        x = math.pi - x
    elif x < -math.pi / 2.0:
        x = -math.pi - x

    term = x
    result = term
    k = 1
    while abs(term) > eps:
        term *= -x * x / ((2 * k) * (2 * k + 1))
        result += term
        k += 1
    return result


def ln_series(x: float, eps: float = 1e-15) -> float:
    """
    Вычисляет ln(x) через ln(1+t), t in [0, 1), после нормализации x = m * 2^p.
    """
    if x <= 0.0:
        raise ValueError("ln(x) определён только при x > 0.")

    mantissa, exponent = math.frexp(x)
    mantissa *= 2.0
    exponent -= 1

    t = mantissa - 1.0
    term = t
    result = 0.0
    k = 1
    sign = 1.0
    while abs(term / k) > eps:
        result += sign * term / k
        term *= t
        sign *= -1.0
        k += 1
    return result + exponent * math.log(2.0)


def demo_task3() -> None:
    print("Задание 3")
    x = float(input("Введите x для sin(x): "))
    y = float(input("Введите x > 0 для ln(x): "))
    print(f"sin_series(x) = {format_float(sin_series(x))}")
    print(f"math.sin(x)   = {format_float(math.sin(x))}")
    print(f"ln_series(y)  = {format_float(ln_series(y))}")
    print(f"math.log(y)   = {format_float(math.log(y))}")
    sin_x = frange(-2.0 * math.pi, 2.0 * math.pi, 400)
    sin_path = svg_plot(
        "task3_sin.svg",
        "Задание 3а: sin(x)",
        "x",
        "y",
        [
            {"label": "sin_series(x)", "x": sin_x, "y": [sin_series(value) for value in sin_x]},
            {"label": "math.sin(x)", "x": sin_x, "y": [math.sin(value) for value in sin_x]},
        ],
    )
    ln_x = frange(0.2, 5.0, 400)
    ln_path = svg_plot(
        "task3_ln.svg",
        "Задание 3б: ln(x)",
        "x",
        "y",
        [
            {"label": "ln_series(x)", "x": ln_x, "y": [ln_series(value) for value in ln_x]},
            {"label": "math.log(x)", "x": ln_x, "y": [math.log(value) for value in ln_x]},
        ],
    )
    print(f"График sin(x): {sin_path}")
    print(f"График ln(x):  {ln_path}")
    print()


def integral_exact() -> float:
    return math.log(7.0 / 6.0)


def integral_recursive_forward(n: int) -> float:
    """
    Рекуррентная формула:
    I_n = 1/n - 6 I_(n-1), I_0 = ln(7/6)
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным.")
    result = integral_exact()
    for k in range(1, n + 1):
        result = 1.0 / k - 6.0 * result
    return result


def integral_recursive_backward(n: int, start_n: int = 60) -> float:
    """
    Обратная рекурсия:
    I_(n-1) = 1/(6n) - I_n/6, стартуем с I_start ~ 0.
    """
    if n < 0 or n > start_n:
        raise ValueError("Должно выполняться 0 <= n <= start_n.")
    result = 0.0
    for k in range(start_n, n, -1):
        result = 1.0 / (6.0 * k) - result / 6.0
    return result


def integral_midpoint(n: int, parts: int = 10000) -> float:
    """
    Численное вычисление:
    I_n = \int_0^1 x^n / (x + 6) dx
    методом средних прямоугольников.
    """
    h = 1.0 / parts
    total = 0.0
    for i in range(parts):
        x = (i + 0.5) * h
        total += x**n / (x + 6.0)
    return total * h


def demo_task4(n: int = 31) -> None:
    exact = integral_midpoint(n, parts=200000)
    forward = integral_recursive_forward(n)
    backward = integral_recursive_backward(n)
    midpoint = integral_midpoint(n)

    print("Задание 4")
    print(f"n = {n}")
    print(f"Прямая рекурсия     : {format_float(forward)}")
    print(f"Обратная рекурсия   : {format_float(backward)}")
    print(f"Средние прямоугольн.: {format_float(midpoint)}")
    print(f"Эталонное значение  : {format_float(exact)}")
    n_values = list(range(0, 31))
    exact_values = [integral_midpoint(value, parts=200000) for value in n_values]
    plot_path = svg_plot(
        "task4_errors.svg",
        "Задание 4: ошибки трёх методов",
        "n",
        "|error|",
        [
            {
                "label": "Прямая рекурсия",
                "x": n_values,
                "y": [
                    abs(integral_recursive_forward(value) - exact_value)
                    for value, exact_value in zip(n_values, exact_values)
                ],
            },
            {
                "label": "Обратная рекурсия",
                "x": n_values,
                "y": [
                    abs(integral_recursive_backward(value) - exact_value)
                    for value, exact_value in zip(n_values, exact_values)
                ],
            },
            {
                "label": "Средние прямоугольники",
                "x": n_values,
                "y": [
                    abs(integral_midpoint(value) - exact_value)
                    for value, exact_value in zip(n_values, exact_values)
                ],
            },
        ],
        log_y=True,
    )
    print(f"График ошибок: {plot_path}")
    print()


def derivative_forward_error(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    hs: Iterable[float],
) -> list[tuple[float, float, float]]:
    rows = []
    exact = df(x0)
    for h in hs:
        approx = (f(x0 + h) - f(x0)) / h
        rows.append((h, approx, abs(approx - exact)))
    return rows


def sample_function(x: float) -> float:
    return math.sin(2.0 * x) + math.exp(x / 3.0) - x**3 / 5.0


def sample_function_derivative(x: float) -> float:
    return 2.0 * math.cos(2.0 * x) + math.exp(x / 3.0) / 3.0 - 3.0 * x * x / 5.0


def demo_task5(x0: float = 1.0) -> None:
    rows = derivative_forward_error(
        sample_function,
        sample_function_derivative,
        x0,
        [10.0**(-k) for k in range(1, 17)],
    )
    print("Задание 5")
    print(f"x0 = {x0}")
    print("h\t\tapprox\t\t\t|error|")
    for h, approx, err in rows:
        print(f"{h:.1e}\t{approx:.12f}\t{err:.3e}")
    plot_path = svg_plot(
        "task5_derivative_error.svg",
        "Задание 5: ошибка производной",
        "h",
        "|error|",
        [
            {
                "label": "Прямая разность",
                "x": [h for h, _, _ in rows],
                "y": [err for _, _, err in rows],
            }
        ],
        log_x=True,
        log_y=True,
    )
    print(f"График ошибки: {plot_path}")
    print()


@dataclass
class EulerResult:
    h: float
    t_values: list[float]
    y_values: list[float]
    exact_values: list[float]

    @property
    def max_error(self) -> float:
        return max(abs(y - e) for y, e in zip(self.y_values, self.exact_values))

    @property
    def end_error(self) -> float:
        return abs(self.y_values[-1] - self.exact_values[-1])


def euler_scalar(
    f: Callable[[float, float], float],
    exact: Callable[[float], float],
    t0: float,
    y0: float,
    t_end: float,
    h: float,
) -> EulerResult:
    steps = int(round((t_end - t0) / h))
    t_values = [t0 + i * h for i in range(steps + 1)]
    y_values = [y0]
    for i in range(steps):
        t = t_values[i]
        y_values.append(y_values[-1] + h * f(t, y_values[-1]))
    exact_values = [exact(t) for t in t_values]
    return EulerResult(h, t_values, y_values, exact_values)


def demo_task6a() -> None:
    print("Задание 6a: y' = 2t, y(0) = 0, точное решение y=t^2")
    summaries = []
    for h in DEFAULT_STEPS:
        result = euler_scalar(
            f=lambda t, y: 2.0 * t,
            exact=lambda t: t * t,
            t0=0.0,
            y0=0.0,
            t_end=10.0,
            h=h,
        )
        print(
            f"h={h:<6g} y(10)={result.y_values[-1]:.10f} "
            f"exact={result.exact_values[-1]:.10f} end_error={result.end_error:.3e}"
        )
        summaries.append(result)
    best = min(summaries, key=lambda item: item.h)
    traj_path = svg_plot(
        "task6a_trajectory.svg",
        "Задание 6а: метод Эйлера для параболы",
        "t",
        "y",
        [
            {"label": f"Эйлер, h={best.h}", "x": best.t_values, "y": best.y_values},
            {"label": "Точное решение", "x": best.t_values, "y": best.exact_values},
        ],
    )
    error_path = svg_plot(
        "task6a_errors.svg",
        "Задание 6а: ошибка от шага",
        "h",
        "end_error",
        [
            {
                "label": "Погрешность в конце",
                "x": [item.h for item in summaries],
                "y": [item.end_error for item in summaries],
            }
        ],
        log_x=True,
        log_y=True,
    )
    print(f"График решения: {traj_path}")
    print(f"График ошибки:  {error_path}")
    print()


def demo_task6b() -> None:
    print("Задание 6b: y' = y - t^2 + 1, y(0)=0.5")
    print("Точное решение: y(t)=(t+1)^2 - 0.5*e^t")
    exact = lambda t: (t + 1.0) ** 2 - 0.5 * math.exp(t)
    summaries = []
    for h in DEFAULT_STEPS:
        result = euler_scalar(
            f=lambda t, y: y - t * t + 1.0,
            exact=exact,
            t0=0.0,
            y0=0.5,
            t_end=2.0,
            h=h,
        )
        print(
            f"h={h:<6g} y(2)={result.y_values[-1]:.10f} "
            f"exact={result.exact_values[-1]:.10f} end_error={result.end_error:.3e}"
        )
        summaries.append(result)
    best = min(summaries, key=lambda item: item.h)
    traj_path = svg_plot(
        "task6b_trajectory.svg",
        "Задание 6б: метод Эйлера для своей функции",
        "t",
        "y",
        [
            {"label": f"Эйлер, h={best.h}", "x": best.t_values, "y": best.y_values},
            {"label": "Точное решение", "x": best.t_values, "y": best.exact_values},
        ],
    )
    error_path = svg_plot(
        "task6b_errors.svg",
        "Задание 6б: ошибка от шага",
        "h",
        "end_error",
        [
            {
                "label": "Погрешность в конце",
                "x": [item.h for item in summaries],
                "y": [item.end_error for item in summaries],
            }
        ],
        log_x=True,
        log_y=True,
    )
    print(f"График решения: {traj_path}")
    print(f"График ошибки:  {error_path}")
    print()


@dataclass
class Euler2DResult:
    h: float
    t_values: list[float]
    x_values: list[float]
    z_values: list[float]
    exact_x: list[float]
    exact_z: list[float]

    @property
    def end_error_x(self) -> float:
        return abs(self.x_values[-1] - self.exact_x[-1])

    @property
    def end_error_z(self) -> float:
        return abs(self.z_values[-1] - self.exact_z[-1])


def euler_2d_oscillator(t_end: float, h: float) -> Euler2DResult:
    steps = int(round(t_end / h))
    t_values = [i * h for i in range(steps + 1)]
    x_values = [0.0]
    z_values = [1.0]
    for i in range(steps):
        x = x_values[-1]
        z = z_values[-1]
        x_values.append(x + h * z)
        z_values.append(z - h * x)
    exact_x = [math.sin(t) for t in t_values]
    exact_z = [math.cos(t) for t in t_values]
    return Euler2DResult(h, t_values, x_values, z_values, exact_x, exact_z)


def demo_task7() -> None:
    print("Задание 7: гармонический осциллятор")
    print("x' = z, z' = -x, x(0)=0, z(0)=1")
    summaries = []
    for h in [0.1, 0.05, 0.01, 0.005, 0.001]:
        result = euler_2d_oscillator(t_end=2.0 * math.pi, h=h)
        print(
            f"h={h:<6g} x(T)={result.x_values[-1]:.10f} z(T)={result.z_values[-1]:.10f} "
            f"err_x={result.end_error_x:.3e} err_z={result.end_error_z:.3e}"
        )
        summaries.append(result)
    best = min(summaries, key=lambda item: item.h)
    traj_path = svg_plot(
        "task7_oscillator_x.svg",
        "Задание 7: гармонический осциллятор",
        "t",
        "x(t)",
        [
            {"label": f"Эйлер, h={best.h}", "x": best.t_values, "y": best.x_values},
            {"label": "sin(t)", "x": best.t_values, "y": best.exact_x},
        ],
    )
    error_path = svg_plot(
        "task7_errors.svg",
        "Задание 7: ошибка от шага",
        "h",
        "error",
        [
            {"label": "Ошибка x(T)", "x": [item.h for item in summaries], "y": [item.end_error_x for item in summaries]},
            {"label": "Ошибка z(T)", "x": [item.h for item in summaries], "y": [item.end_error_z for item in summaries]},
        ],
        log_x=True,
        log_y=True,
    )
    print(f"График x(t):   {traj_path}")
    print(f"График ошибки: {error_path}")
    print()


def newton_method(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    eps: float = 1e-12,
    max_iter: int = 50,
    damping: float = 1.0,
) -> tuple[float, int, list[float]]:
    x = x0
    history = [x]
    for iteration in range(1, max_iter + 1):
        dfx = df(x)
        if abs(dfx) < EPS_A_ZERO:
            raise ValueError("Производная слишком мала, метод Ньютона остановлен.")
        x_next = x - damping * f(x) / dfx
        history.append(x_next)
        if abs(x_next - x) < eps:
            return x_next, iteration, history
        x = x_next
    raise ValueError("Метод Ньютона не сошёлся за отведённое число итераций.")


def demo_task8() -> None:
    print("Задание 8: метод Ньютона")
    print("Исследуем f(x)=x^3-x-2, корень около 1.52138")
    f = lambda x: x**3 - x - 2.0
    df = lambda x: 3.0 * x * x - 1.0
    cases = [
        ("x0=1.5, gamma=1", 1.5, 1.0),
        ("x0=10, gamma=1", 10.0, 1.0),
        ("x0=10, gamma=0.2", 10.0, 0.2),
    ]
    histories = []
    for label, x0, damping in cases:
        try:
            root, steps, history = newton_method(f, df, x0=x0, damping=damping)
            print(f"{label:<18} root={root:.12f} iterations={steps}")
            histories.append((label, history, root))
        except ValueError as exc:
            print(f"{label:<18} {exc}")
    if histories:
        reference_root = histories[0][2]
        plot_path = svg_plot(
            "task8_newton_convergence.svg",
            "Задание 8: сходимость метода Ньютона",
            "Итерация",
            "|x_k - root|",
            [
                {
                    "label": label,
                    "x": list(range(len(history))),
                    "y": [abs(value - reference_root) + 1e-16 for value in history],
                }
                for label, history, _ in histories
            ],
            log_y=True,
        )
        print(f"График сходимости: {plot_path}")
    print()


def run_all_demos() -> None:
    print_task1_answer()
    demo_task4()
    demo_task5()
    demo_task6a()
    demo_task6b()
    demo_task7()
    demo_task8()


def menu() -> None:
    actions = {
        "1": print_task1_answer,
        "2": interactive_quadratic,
        "3": demo_task3,
        "4": demo_task4,
        "5": demo_task5,
        "6a": demo_task6a,
        "6b": demo_task6b,
        "7": demo_task7,
        "8": demo_task8,
        "all": run_all_demos,
    }

    print("Доступные режимы: 1, 2, 3, 4, 5, 6a, 6b, 7, 8, all")
    choice = input("Что запустить? ").strip().lower()
    action = actions.get(choice)
    if action is None:
        print("Неизвестный режим.")
        return
    action()


if __name__ == "__main__":
    menu()

