from pathlib import Path
import shutil
import subprocess
import tempfile

_album_cover_cache: dict[str, Path] = {}  # 全局缓存专辑封面


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def convert_mp4_to_m4a(
    input_path: Path,
    output_path: Path,
    *,
    bitrate: str = "128k",
    overwrite: bool = False,
    denoise: bool = True,  # 新增参数
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

    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-i",
        str(input_path),
        "-vn",
        "-c:a",
        "aac",
        "-b:a",
        bitrate,
    ]

    if denoise:
        # 加上 afftdn 滤波
        cmd += ["-af", "afftdn"]

    cmd += ["-movflags", "+faststart", str(output_path)]

    print(f"[INFO] converting: {input_path.name} -> {output_path.name} (denoise={denoise})")

    try:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"[ERROR] ffmpeg failed: {input_path}")
            return False

        return output_path.exists()

    except KeyboardInterrupt:
        print("[ERROR] interrupted")
        return False


def extract_cover_frame(
    input_path: Path,
    *,
    seek_time: str = "00:00:03",
    album_name: str = "default_album"
) -> Path | None:
    """
    Extract one video frame as album cover for the entire album.

    - Only extracts once per album_name
    - Returns cached Path for subsequent calls
    """
    global _album_cover_cache

    # 如果已经生成过，直接返回缓存
    if album_name in _album_cover_cache:
        return _album_cover_cache[album_name]

    if not has_ffmpeg():
        print("[ERROR] ffmpeg not found. Please install ffmpeg first.")
        return None

    if not input_path.exists():
        print(f"[ERROR] input not found: {input_path}")
        return None

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"podmelt_{album_name}_"))
    cover_path = tmp_dir / "cover.jpg"

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        seek_time,
        "-i",
        str(input_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(cover_path),
    ]

    print(f"[INFO] extracting album cover: {input_path.name} @ {seek_time}")

    try:
        result = subprocess.run(cmd)
        if result.returncode != 0 or not cover_path.exists():
            print(f"[WARN] cover frame extraction failed: {input_path}")
            return None

        # 缓存起来，全专辑复用
        _album_cover_cache[album_name] = cover_path
        return cover_path

    except KeyboardInterrupt:
        print("[ERROR] interrupted")
        return None
