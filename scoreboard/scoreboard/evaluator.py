import logging
import queue
import threading

from scoreboard import db
from scoreboard import config

logger = logging.getLogger(__name__)

_queue: queue.Queue[int] = queue.Queue()


def compute_individual_params(A: int) -> dict:
    """Compute individual environment parameters from student parameter A."""
    return {
        "gravity": -10.0 + (A % 5) * (-0.5),
        "enable_wind": A > 15,
        "wind_power": (A % 10) * 1.5,
        "turbulence_power": (A % 7) * 0.25,
    }


def _evaluate_model(model_path: str, env_kwargs: dict, n_episodes: int) -> dict:
    """Evaluate a single model. Imports SB3/gym lazily to keep module importable."""
    import gymnasium as gym
    from stable_baselines3 import DQN
    from stable_baselines3.common.evaluation import evaluate_policy

    model = DQN.load(model_path)
    env = gym.make("LunarLander-v3", **env_kwargs)
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=n_episodes)
    env.close()
    return {"mean_reward": float(mean_reward), "std_reward": float(std_reward)}


def _record_video(model_path: str, env_kwargs: dict, output_path: str, seed: int = 42) -> None:
    """Record one deterministic episode as MP4. Requires imageio[ffmpeg]."""
    import imageio
    import gymnasium as gym
    from stable_baselines3 import DQN

    model = DQN.load(model_path)
    env = gym.make("LunarLander-v3", render_mode="rgb_array", **env_kwargs)
    frames = []
    obs, _ = env.reset(seed=seed)
    terminated, truncated = False, False
    while not (terminated or truncated):
        frames.append(env.render())
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = env.step(action)
    frames.append(env.render())
    env.close()
    imageio.mimsave(output_path, frames, fps=30, macro_block_size=1)


def _worker():
    """Background worker thread — processes one submission at a time."""
    while True:
        sub_id = _queue.get()
        try:
            sub = db.get_submission(sub_id)
            if sub is None or sub["superseded_by"] is not None:
                continue

            logger.info(f"Evaluating submission {sub_id} ({sub['name']} {sub['surname']})")
            db.set_status(sub_id, "evaluating")

            n_episodes = config.EVALUATION_EPISODES

            # Standard environment
            std_result = _evaluate_model(sub["model_standard_path"], {}, n_episodes)

            # Individual environment
            ind_params = compute_individual_params(sub["param_a"])
            ind_result = _evaluate_model(sub["model_individual_path"], ind_params, n_episodes)

            db.update_evaluation(
                sub_id,
                standard_mean=std_result["mean_reward"],
                standard_std=std_result["std_reward"],
                individual_mean=ind_result["mean_reward"],
                individual_std=ind_result["std_reward"],
            )
            logger.info(f"Submission {sub_id} done: std={std_result['mean_reward']:.1f}, ind={ind_result['mean_reward']:.1f}")

            # Record demo video for individual model (best-effort)
            video_path = str(config.UPLOADS_DIR / str(sub_id) / "demo_individual.mp4")
            try:
                _record_video(sub["model_individual_path"], ind_params, video_path)
                db.update_video_path(sub_id, video_path)
                logger.info(f"Demo video saved for submission {sub_id}")
            except Exception:
                logger.exception(f"Video recording failed for submission {sub_id} (non-fatal)")

        except Exception as e:
            logger.exception(f"Evaluation failed for submission {sub_id}")
            db.update_evaluation_error(sub_id, str(e))
        finally:
            _queue.task_done()


def enqueue(sub_id: int):
    """Add a submission to the evaluation queue."""
    _queue.put(sub_id)


def start():
    """Start the background evaluator thread. Re-queues any pending submissions."""
    pending = db.get_pending_submissions()
    for sub in pending:
        _queue.put(sub["id"])
    if pending:
        logger.info(f"Re-queued {len(pending)} pending submissions")

    t = threading.Thread(target=_worker, daemon=True, name="evaluator")
    t.start()
    logger.info("Background evaluator started")
