"""
Турнірна таблиця — Лабораторна робота №3
Оцінює моделі студентів на стандартному та індивідуальному середовищах LunarLander.

Використання:
    python leaderboard_runner.py --models-dir ./submissions/ --output results.csv

Структура директорії submissions/:
    submissions/
        student_name_1/
            model_standard.zip
            model_individual.zip
            params.json          # {"A": 21}
        student_name_2/
            ...
"""

import argparse
import json
import os
from pathlib import Path

import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np

# Перевірка наявності SB3 перед використанням
try:
    from stable_baselines3 import DQN
    from stable_baselines3.common.evaluation import evaluate_policy
except ImportError:
    print("Встановіть stable-baselines3: pip install stable-baselines3")
    raise


def compute_individual_params(A: int) -> dict:
    """Обчислити індивідуальні параметри середовища з параметра A."""
    return {
        "gravity": -10.0 + (A % 5) * (-0.5),
        "enable_wind": A > 15,
        "wind_power": (A % 10) * 1.5,
        "turbulence_power": (A % 7) * 0.25,
    }


def evaluate_model(model_path: str, env_kwargs: dict, n_episodes: int = 100, seed: int = 0) -> dict:
    """Оцінити модель на середовищі з заданими параметрами."""
    try:
        model = DQN.load(model_path)
    except Exception as e:
        print(f"  Помилка завантаження {model_path}: {e}")
        return {"mean_reward": float("nan"), "std_reward": float("nan"), "error": str(e)}

    env = gym.make("LunarLander-v3", **env_kwargs)
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=n_episodes, seed=seed)
    env.close()

    return {"mean_reward": mean_reward, "std_reward": std_reward, "error": None}


def load_submissions(models_dir: str) -> list[dict]:
    """Завантажити інформацію про всі подання студентів."""
    submissions = []
    models_path = Path(models_dir)

    for student_dir in sorted(models_path.iterdir()):
        if not student_dir.is_dir():
            continue

        student_name = student_dir.name

        # Прочитати параметр A
        params_file = student_dir / "params.json"
        if not params_file.exists():
            print(f"  Пропущено {student_name}: немає params.json")
            continue

        with open(params_file) as f:
            params = json.load(f)

        A = params.get("A")
        if A is None:
            print(f"  Пропущено {student_name}: немає параметра A в params.json")
            continue

        model_standard = student_dir / "model_standard.zip"
        model_individual = student_dir / "model_individual.zip"

        submissions.append({
            "name": student_name,
            "A": A,
            "model_standard": str(model_standard) if model_standard.exists() else None,
            "model_individual": str(model_individual) if model_individual.exists() else None,
        })

    return submissions


def run_leaderboard(models_dir: str, n_episodes: int = 100) -> list[dict]:
    """Запустити оцінку всіх студентів."""
    submissions = load_submissions(models_dir)

    if not submissions:
        print("Не знайдено жодного подання!")
        return []

    print(f"Знайдено {len(submissions)} подань\n")

    results = []
    for sub in submissions:
        print(f"Оцінка: {sub['name']} (A={sub['A']})")

        # Стандартне середовище
        std_result = {"mean_reward": float("nan"), "std_reward": float("nan")}
        if sub["model_standard"]:
            print(f"  Стандартне середовище ({n_episodes} епізодів)...")
            std_result = evaluate_model(sub["model_standard"], {}, n_episodes)
            print(f"  -> {std_result['mean_reward']:.1f} +/- {std_result['std_reward']:.1f}")
        else:
            print("  Немає model_standard.zip")

        # Індивідуальне середовище
        ind_params = compute_individual_params(sub["A"])
        ind_result = {"mean_reward": float("nan"), "std_reward": float("nan")}
        if sub["model_individual"]:
            print(f"  Індивідуальне середовище ({n_episodes} епізодів)...")
            ind_result = evaluate_model(sub["model_individual"], ind_params, n_episodes)
            print(f"  -> {ind_result['mean_reward']:.1f} +/- {ind_result['std_reward']:.1f}")
        else:
            print("  Немає model_individual.zip")

        results.append({
            "name": sub["name"],
            "A": sub["A"],
            "standard_mean": std_result["mean_reward"],
            "standard_std": std_result["std_reward"],
            "individual_mean": ind_result["mean_reward"],
            "individual_std": ind_result["std_reward"],
            "gravity": ind_params["gravity"],
            "wind": ind_params["enable_wind"],
            "wind_power": ind_params["wind_power"],
            "turbulence": ind_params["turbulence_power"],
        })

    return results


def save_csv(results: list[dict], output_path: str):
    """Зберегти результати в CSV."""
    import csv

    fieldnames = [
        "rank", "name", "A", "standard_mean", "standard_std",
        "individual_mean", "individual_std",
        "gravity", "wind", "wind_power", "turbulence",
    ]

    # Сортування за стандартною винагородою (найкращі зверху)
    sorted_results = sorted(results, key=lambda x: x["standard_mean"]
                            if not np.isnan(x["standard_mean"]) else -1e6, reverse=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rank, r in enumerate(sorted_results, 1):
            r["rank"] = rank
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"\nCSV збережено: {output_path}")


def plot_leaderboard(results: list[dict], output_path: str = "leaderboard.png"):
    """Побудувати візуальну турнірну таблицю."""
    # Сортування за стандартною винагородою
    sorted_results = sorted(results, key=lambda x: x["standard_mean"]
                            if not np.isnan(x["standard_mean"]) else -1e6, reverse=True)

    names = [r["name"] for r in sorted_results]
    standard_means = [r["standard_mean"] for r in sorted_results]
    standard_stds = [r["standard_std"] for r in sorted_results]
    individual_means = [r["individual_mean"] for r in sorted_results]
    has_wind = [r["wind"] for r in sorted_results]

    fig, ax = plt.subplots(figsize=(12, max(6, len(names) * 0.5)))

    y_pos = np.arange(len(names))
    bar_height = 0.35

    # Стандартне середовище
    colors_std = []
    for mean in standard_means:
        if np.isnan(mean):
            colors_std.append("gray")
        elif mean >= 200:
            colors_std.append("#2ecc71")  # зелений — розв'язано
        elif mean >= 0:
            colors_std.append("#3498db")  # синій — вище нуля
        else:
            colors_std.append("#e74c3c")  # червоний — нижче нуля

    bars_std = ax.barh(y_pos + bar_height / 2, standard_means, bar_height,
                       xerr=standard_stds, label="Стандартне середовище",
                       color=colors_std, alpha=0.8, capsize=3)

    # Індивідуальне середовище
    colors_ind = ["#f39c12" if w else "#9b59b6" for w in has_wind]
    bars_ind = ax.barh(y_pos - bar_height / 2, individual_means, bar_height,
                       label="Індивідуальне середовище",
                       color=colors_ind, alpha=0.6, capsize=3)

    # Оформлення
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{i+1} {n}" for i, n in enumerate(names)])
    ax.set_xlabel("Середня винагорода (100 епізодів)")
    ax.set_title("Турнірна таблиця — Лабораторна робота №3\nLunarLander DQN", fontsize=14, fontweight="bold")

    # Вертикальні лінії-орієнтири
    ax.axvline(x=200, color="green", linestyle="--", alpha=0.5, label='Поріг "розв\'язано" (200)')
    ax.axvline(x=0, color="gray", linestyle="--", alpha=0.3)

    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.2, axis="x")
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Графік збережено: {output_path}")


def print_leaderboard(results: list[dict]):
    """Вивести турнірну таблицю в консоль."""
    sorted_results = sorted(results, key=lambda x: x["standard_mean"]
                            if not np.isnan(x["standard_mean"]) else -1e6, reverse=True)

    print("\n" + "=" * 80)
    print("ТУРНІРНА ТАБЛИЦЯ — Лабораторна робота №3")
    print("=" * 80)
    print(f"{'#':<4} {'Студент':<20} {'A':>3} {'Стандарт':>10} {'Індивід.':>10} {'Вітер':>6} {'Гравітація':>10}")
    print("-" * 80)

    for rank, r in enumerate(sorted_results, 1):
        std_str = f"{r['standard_mean']:.1f}" if not np.isnan(r["standard_mean"]) else "N/A"
        ind_str = f"{r['individual_mean']:.1f}" if not np.isnan(r["individual_mean"]) else "N/A"
        wind_str = "Так" if r["wind"] else "Ні"
        print(f"{rank:<4} {r['name']:<20} {r['A']:>3} {std_str:>10} {ind_str:>10} {wind_str:>6} {r['gravity']:>10.1f}")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Турнірна таблиця — ЛР №3 LunarLander")
    parser.add_argument("--models-dir", required=True, help="Директорія з поданнями студентів")
    parser.add_argument("--output", default="results.csv", help="Шлях до CSV з результатами")
    parser.add_argument("--episodes", type=int, default=100, help="Кількість епізодів для оцінки")
    parser.add_argument("--plot", default="leaderboard.png", help="Шлях до графіку турнірної таблиці")
    args = parser.parse_args()

    results = run_leaderboard(args.models_dir, args.episodes)

    if results:
        print_leaderboard(results)
        save_csv(results, args.output)
        plot_leaderboard(results, args.plot)


if __name__ == "__main__":
    main()
