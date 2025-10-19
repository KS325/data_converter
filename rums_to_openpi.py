import json
import numpy as np
from pathlib import Path
import shutil

# === パス設定 ===
RUMS_ROOT = Path(r"D:\vscode\dev\muratalab\data_converter\data\robot-utility-model-data\train")
OUT_ROOT = Path(r"D:\vscode\dev\muratalab\data_converter\result")

def convert_episode(mp4_path: Path, json_path: Path, out_dir: Path):
    """1エピソードをOpenPI学習形式に変換して保存"""
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- 動画コピー ----
    shutil.copy(mp4_path, out_dir / "video.mp4")

    # ---- JSON読み込み ----
    with open(json_path, "r") as f:
        data = json.load(f)

    # データ形式を統一
    if "trajectory" in data:
        steps = data["trajectory"]
    else:
        # {"0": {...}, "1": {...}, ...} の形式
        steps = [v for k, v in sorted(data.items(), key=lambda x: int(x[0]))]

    # ---- アクションデータ抽出 ----
    actions = []
    for step in steps:
        try:
            pos = step["xyz"]
            rot = step["quats"]
            grip = [step.get("gripper", 0.0)]
            act = np.concatenate([pos, rot, grip])
            actions.append(act)
        except Exception as e:
            print(f"⚠️ Skipped invalid step in {json_path}: {e}")

    if len(actions) == 0:
        print(f"⚠️ No valid actions found in {json_path}")
        return

    # ---- NumPy保存 ----
    np.save(out_dir / "actions.npy", np.array(actions))
    np.save(out_dir / "timestamps.npy", np.arange(len(actions)))  # timestampがないので連番

    # ---- OpenPI準拠JSONメタ情報 ----
    openpi_json = {
        "metadata": {
            "source": "RUMS",
            "task": mp4_path.parts[-5],
            "env": mp4_path.parts[-4],
            "date": mp4_path.parts[-1],
        },
        "num_frames": len(actions),
    }

    with open(out_dir / "episode.json", "w") as f:
        json.dump(openpi_json, f, indent=2)

    print(f"✅ Converted: {mp4_path.name} → {out_dir}")

def main():
    found = False
    for task_dir in RUMS_ROOT.iterdir():
        if not task_dir.is_dir():
            continue
        print(f"🔹 Task: {task_dir.name}")

        # 例: Bag_Pick_Up/Home23/Env1/2024-05-27--09-15-05/
        for date_dir in task_dir.glob("*/*/*"):
            if not date_dir.is_dir():
                continue

            mp4_files = list(date_dir.glob("*.mp4"))
            json_file = date_dir / "labels.json"
            if not json_file.exists():
                continue

            for mp4 in mp4_files:
                found = True
                demo_name = mp4.stem
                out_dir = OUT_ROOT / task_dir.name / date_dir.name / demo_name
                convert_episode(mp4, json_file, out_dir)

    if not found:
        print("No .mp4 files found. Check directory depth and RUMS_ROOT path.")

if __name__ == "__main__":
    main()

# import json
# from pathlib import Path
# import os
# import shutil

# # 入力・出力ディレクトリ設定
# RUMS_ROOT = Path(r"D:\vscode\dev\muratalab\data_converter\data\robot-utility-model-data\train")
# OUT_ROOT = Path(r"D:\vscode\dev\muratalab\data_converter\result")

# def convert_episode(mp4_path: Path, json_path: Path, out_dir: Path):
#     """1エピソードをOpenPI形式に変換して保存"""
#     out_dir.mkdir(parents=True, exist_ok=True)

#     # mp4コピー
#     shutil.copy(mp4_path, out_dir / "video.mp4")

#     # JSONをOpenPI準拠に変換
#     with open(json_path, "r") as f:
#         labels = json.load(f)

#     # ここはデータ仕様に合わせて変える（例：gripper pose, actionなど）
#     openpi_json = {
#         "observations": labels.get("observations", []),
#         "actions": labels.get("actions", []),
#         "metadata": {
#             "source": "RUMS",
#             "task": mp4_path.parts[-5],
#             "env": mp4_path.parts[-4],
#             "date": mp4_path.parts[-1],
#         },
#     }

#     with open(out_dir / "episode.json", "w") as f:
#         json.dump(openpi_json, f, indent=2)

#     print(f"✅ Converted: {mp4_path} → {out_dir}")

# def main():
#     found = False
#     for task_dir in RUMS_ROOT.iterdir():
#         if not task_dir.is_dir():
#             continue
#         print(f"🔹 Task: {task_dir.name}")
#         for home_dir in task_dir.glob("*/*/*"):  # Home23/Env1/2024-05-27--09-15-05/
#             if not home_dir.is_dir():
#                 continue

#             mp4_files = list(home_dir.glob("*.mp4"))
#             json_file = home_dir / "labels.json"
#             if not json_file.exists():
#                 continue

#             for mp4 in mp4_files:
#                 found = True
#                 demo_name = mp4.stem
#                 out_dir = OUT_ROOT / task_dir.name / home_dir.name / demo_name
#                 convert_episode(mp4, json_file, out_dir)

#     if not found:
#         print("No .mp4 files found. Check RUMS_ROOT path or folder depth.")

# if __name__ == "__main__":
#     main()
# # import os
# # import json
# # import numpy as np
# # import cv2
# # from pathlib import Path
# # from tqdm import tqdm

# # path_rums_raw = "./data/robot-utility-model-data/train"
# # path_openpi_dataset = "./result/rums/train"

# # def extract_frames(video_path, output_dir):
# #     cap = cv2.VideoCapture(str(video_path))
# #     frame_idx = 0
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break
# #         out_path = output_dir / f"{frame_idx:06d}.png"
# #         cv2.imwrite(str(out_path), frame)
# #         frame_idx += 1
# #     cap.release()
# #     return frame_idx

# # def convert_episode(mp4_path, json_path, out_dir):
# #     """1つのデモをOpenPI形式に変換"""
# #     out_dir.mkdir(parents=True, exist_ok=True)
# #     rgb_dir = out_dir / "rgb"
# #     rgb_dir.mkdir(exist_ok=True)

# #     num_frames = extract_frames(mp4_path, rgb_dir)

# #     with open(json_path, "r") as f:
# #         data = json.load(f)

# #     # JSON内のデータ構造に応じて調整
# #     actions = []
# #     timestamps = []
# #     data_num = len(data)
# #     for i in range(data_num):
# #         # 例: {"gripper_pose": [x,y,z, qx,qy,qz,qw], "gripper_open": 0.7, "timestamp": 12345}
# #         step = data[f"{i}"]
# #         pos = step["xyz"]
# #         rot = step["quats"]
# #         grip = [step["gripper"]]
# #         act = np.concatenate([pos, rot, grip])
# #         actions.append(act)
# #         timestamps.append(step["timestamp"])

# #     np.save(out_dir / "actions.npy", np.array(actions))
# #     np.save(out_dir / "timestamps.npy", np.array(timestamps))

# # def main():
# #     for task_dir in Path(path_rums_raw).iterdir():
# #         if not task_dir.is_dir():
# #             continue
# #         for env_dir in task_dir.iterdir():
# #             if not env_dir.is_dir():
# #                 continue
# #             for date_dir in env_dir.iterdir():
# #                 if not date_dir.is_dir():
# #                     continue
# #                 for mp4_file in date_dir.glob("*.mp4"):
# #                     json_file = mp4_file.with_suffix(".json")
# #                     if not json_file.exists():
# #                         continue

# #                     demo_name = mp4_file.stem  # demo_0001
# #                     out_dir = Path(path_openpi_dataset) / task_dir.name / demo_name
# #                     convert_episode(mp4_file, json_file, out_dir)
# #                     print(f"✅ Converted {mp4_file.relative_to(path_rums_raw)}")

# # if __name__ == "__main__":
# #     main()


