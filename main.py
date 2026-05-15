import argparse
from pathlib import Path

from converter import convert_mp4_to_m4a
from tagging import tag_m4a
from utils import (
    default_output_path,
    guess_title_from_path,
    is_video_file,
)

DEFAULT_INPUT_DIR = (
    r"Y:\YTF\youtube频道\lifeano会员节目\第零次世界大战\1. 1740-1748.奥地利王位继承战争"
)


def collect_inputs(input_path: Path, recursive: bool = False) -> list[Path]:
    if input_path.is_file():
        return [input_path] if is_video_file(input_path) else []

    if not input_path.is_dir():
        return []

    pattern = "**/*" if recursive else "*"
    return sorted(path for path in input_path.glob(pattern) if is_video_file(path))


def process_one(
    input_path: Path,
    *,
    output_dir: Path | None,
    artist: str,
    album: str,
    description: str,
    bitrate: str,
    no_cover: bool,
    overwrite: bool,
    cover: str | None = None,
) -> bool:
    output_path = default_output_path(input_path, output_dir)

    # 转码
    ok = convert_mp4_to_m4a(
        input_path=input_path,
        output_path=output_path,
        bitrate=bitrate,
        overwrite=overwrite,
    )
    if not ok:
        return False

    title = guess_title_from_path(input_path)

    # 处理封面
    cover_path = None
    if cover:
        cover_path = Path(cover)
    else:
        # 默认用输出目录下的 logo.png
        if output_dir:
            default_logo = output_dir / "logo.png"
            if default_logo.exists():
                cover_path = default_logo

    # 如果显式声明 no_cover 或 logo.png 不存在，则不写封面
    if cover_path and not no_cover:
        tag_m4a(
            output_path,
            title=title,
            artist=artist,
            album=album,
            description=description,
            cover_path=cover_path,
        )
    else:
        # 没有封面时只写基础 metadata
        tag_m4a(
            output_path,
            title=title,
            artist=artist,
            album=album,
            description=description,
            cover_path=None,
        )

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert local MP4 videos into tagged M4A podcast episodes."
    )

    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_INPUT_DIR,
        help="Input MP4 file or folder",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output folder. Default: same folder as source MP4.",
    )

    parser.add_argument(
        "--artist",
        default="lifeano",
        help="Artist / author",
    )

    parser.add_argument(
        "--album",
        default="神圣罗马帝国史 A.D.962-1806",
        help="Album / podcast name",
    )

    parser.add_argument(
        "--description",
        default="",
        help="Episode description",
    )

    parser.add_argument(
        "--bitrate",
        default="128k",
        help="AAC bitrate, default: 128k",
    )

    parser.add_argument(
        "--cover",
        help="Path to album cover image (PNG/JPG). If not provided, default to OUTPUT_DIR/logo.png",
    )

    parser.add_argument(
        "--no-cover",
        action="store_true",
        help="Do not extract cover frame",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Scan folder recursively",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output) if args.output else None

    inputs = collect_inputs(input_path, recursive=args.recursive)

    if not inputs:
        print(f"[ERROR] no supported video files found: {input_path}")
        return 1

    print(f"[INFO] input: {input_path}")
    print(f"[INFO] found mp4 files: {len(inputs)}")
    print(f"[INFO] album: {args.album}")
    print(f"[INFO] artist: {args.artist}")

    success = 0
    failed = 0

    for idx, item in enumerate(inputs, start=1):
        print()
        print(f"[{idx}/{len(inputs)}] {item.name}")

        ok = process_one(
            item,
            output_dir=output_dir,
            artist=args.artist,
            album=args.album,
            description=args.description,
            bitrate=args.bitrate,
            no_cover=args.no_cover,
            overwrite=args.overwrite,
            cover=args.cover,
        )

        if ok:
            success += 1
        else:
            failed += 1

    print()
    print(f"[DONE] success={success}, failed={failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
