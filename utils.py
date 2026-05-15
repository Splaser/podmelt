from pathlib import Path
import re


VIDEO_EXTS = {".mp4", ".m4v", ".mov"}


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip(" .")


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTS


def default_output_path(input_path: Path, output_dir: Path | None = None) -> Path:
    name = sanitize_filename(input_path.stem) + ".m4a"

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / name

    return input_path.with_name(name)


def guess_title_from_path(input_path: Path) -> str:
    return input_path.stem.strip()