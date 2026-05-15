from pathlib import Path
import shutil
import subprocess

def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def convert_mp4_to_m4a(
    input_path: Path,
    output_path: Path,
    *,
    bitrate: str = "128k",
    overwrite: bool = False,
    denoise: bool = True,  # 是否开启 afftdn
    use_gpu: bool = True,  # 新增 GPU 参数
) -> bool:
    if not has_ffmpeg():
        print("[ERROR] ffmpeg not found. Please install ffmpeg first.")
        return False

    if not input_path.exists():
        print(f"[ERROR] input not found: {input_path}")
        return False

    if output_path.exists() and not overwrite:
        print(f"[SKIP] output exists: {output_path}")
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 基本命令
    cmd = ["ffmpeg"]

    # GPU 解码加速（仅影响视频解码）
    if use_gpu:
        # cmd += ["-hwaccel", "cuda"]
        # 如果需要显式 GPU 解码器，可写：
        cmd += ["-c:v", "h264_cuvid"]  

    # 输入和基础参数
    cmd += [
        "-y" if overwrite else "-n",
        "-i", str(input_path),
        "-vn",           # 只处理音频
        "-c:a", "aac",
        "-b:a", bitrate,
    ]

    # denoise
    if denoise:
        cmd += ["-af", "afftdn"]

    # 输出
    cmd += ["-movflags", "+faststart", str(output_path)]

    print(f"[INFO] converting: {input_path.name} -> {output_path.name} (denoise={denoise}, use_gpu={use_gpu})")

    try:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"[ERROR] ffmpeg failed: {input_path}")
            return False

        return output_path.exists()

    except KeyboardInterrupt:
        print("[ERROR] interrupted")
        return False