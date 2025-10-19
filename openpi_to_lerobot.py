
from pathlib import Path
import shutil
import json
import numpy as np

OPENPI_ROOT = Path(r"D:\vscode\dev\muratalab\data_converter\result")
LEROOT_ROOT = Path(r"D:\vscode\dev\muratalab\data_converter\result\lerobot")

def convert_episode(openpi_dir: Path, lerobot_dir: Path):
    lerobot_dir.mkdir(parents=True, exist_ok=True)
    obs_dir = lerobot_dir / "observations"
    obs_dir.mkdir(exist_ok=True)

    # 動画をコピー
    shutil.copy(openpi_dir / "video.mp4", obs_dir / "rgb.mp4")

    # 状態データがある場合は保存（なければダミー）
    np.save(obs_dir / "state.npy", np.zeros((1, 10)))

    # アクションをコピー
    shutil.copy(openpi_dir / "actions.npy", lerobot_dir / "actions.npy")

    # メタ情報
    meta_path = openpi_dir / "episode.json"
    if meta_path.exists():
        with open(meta_path, "r") as f:
            meta = json.load(f)
    else:
        meta = {"metadata": {}}

    with open(lerobot_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"✅ LeRobot format: {lerobot_dir}")

def main():
    for task_dir in OPENPI_ROOT.iterdir():
        if not task_dir.is_dir():
            continue
        for date_dir in task_dir.iterdir():
            for demo_dir in date_dir.iterdir():
                lerobot_dir = LEROOT_ROOT / task_dir.name / demo_dir.name
                convert_episode(demo_dir, lerobot_dir)

if __name__ == "__main__":
    main()


