from pathlib import Path
import re
from converter import convert_mp4_to_m4a
from tagging import tag_m4a
from utils import is_video_file, guess_title_from_path, sanitize_filename

# 输入 / 输出
INPUT_DIR = r"Y:\YTF\youtube频道\lifeano会员节目\中东战争"
OUTPUT_ROOT = r"S:\袁腾飞频道\中东战争"
ARTIST_NAME = "lifeano"
BITRATE = "128k"
OVERWRITE = False


def infer_album_from_path(file_path: Path) -> str:
    """用最近父目录名生成 album，去掉开头数字和点"""
    folder_name = file_path.parent.name
    return re.sub(r"^\d+\.\s*", "", folder_name)


def collect_mp4_files(top_path: Path):
    """递归收集所有支持的视频文件"""
    return [f for f in top_path.rglob("*") if is_video_file(f)]


def process_one(
    input_path: Path, input_root: Path, output_root: Path, cover_path: Path | None
):
    """单文件处理：转码 + 写标签，保持原目录结构"""
    # 构造输出目录：在 output_root 下保留原输入结构
    relative_path = input_path.parent.relative_to(input_root)
    output_dir = output_root / relative_path
    output_dir.mkdir(parents=True, exist_ok=True)

    # 输出文件路径
    output_file = output_dir / (sanitize_filename(input_path.stem) + ".m4a")

    # 转码
    ok = convert_mp4_to_m4a(
        input_path=input_path,
        output_path=output_file,
        bitrate=BITRATE,
        overwrite=OVERWRITE,
    )
    if not ok:
        print(f"[ERROR] convert failed: {input_path}")
        return False

    # 写标签
    album = infer_album_from_path(output_file)

    tag_m4a(
        output_file,
        title=guess_title_from_path(input_path),
        artist=ARTIST_NAME,
        album=album,
        description="",
        cover_path=cover_path,  # 统一封面
    )
    return True


def main():
    input_root = Path(INPUT_DIR)
    output_root = Path(OUTPUT_ROOT)
    output_root.mkdir(parents=True, exist_ok=True)

    # 默认封面：OUTPUT_ROOT/logo.png
    cover_path = output_root / "logo.png"
    if cover_path.exists():
        print(f"[INFO] using cover: {cover_path}")
    else:
        print(f"[WARN] logo not found, cover will be skipped: {cover_path}")
        cover_path = None

    files = collect_mp4_files(input_root)
    print(f"[INFO] Found {len(files)} video files under {INPUT_DIR}")

    success = 0
    failed = 0

    for idx, f in enumerate(files, start=1):
        print(f"\n[{idx}/{len(files)}] Processing: {f}")
        if process_one(f, input_root, output_root, cover_path):
            success += 1
        else:
            failed += 1

    print(f"\n[DONE] success={success}, failed={failed}")


if __name__ == "__main__":
    main()
