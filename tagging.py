from pathlib import Path
from mutagen.mp4 import MP4, MP4Cover


def _read_cover_file(cover_path: Path | None) -> bytes | None:
    if not cover_path:
        return None

    if not cover_path.exists():
        print(f"[WARN] cover not found: {cover_path}")
        return None

    if not cover_path.is_file():
        print(f"[WARN] cover is not a file: {cover_path}")
        return None

    return cover_path.read_bytes()


def _guess_mp4_cover_format(data: bytes) -> int:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return MP4Cover.FORMAT_PNG

    # mutagen MP4Cover only officially supports JPEG / PNG.
    # Unknown formats fallback to JPEG.
    return MP4Cover.FORMAT_JPEG


def has_m4a_basic_tags(filename: str | Path) -> bool:
    try:
        audio = MP4(str(filename))

        title = audio.get("\xa9nam")
        artist = audio.get("\xa9ART")
        album = audio.get("\xa9alb")

        return bool(title and artist and album)

    except Exception:
        return False


def has_m4a_cover(filename: str | Path) -> bool:
    try:
        audio = MP4(str(filename))
        return bool(audio.get("covr"))

    except Exception:
        return False


def tag_m4a(
    filename: str | Path,
    *,
    title: str,
    artist: str = "Podmelt",
    album: str = "Podmelt",
    description: str = "",
    cover_path: str | Path | None = None,
) -> bool:
    """
    Write M4A metadata.

    MP4 atoms:
    - ©nam: title
    - ©ART: artist
    - ©alb: album
    - desc: description
    - covr: cover
    """

    filename = Path(filename)
    cover_path = Path(cover_path) if cover_path else None

    try:
        audio = MP4(str(filename))

        audio["\xa9nam"] = [title]
        audio["\xa9ART"] = [artist]
        audio["\xa9alb"] = [album]

        if description:
            audio["desc"] = [description]

        cover_data = _read_cover_file(cover_path)
        if cover_data:
            image_format = _guess_mp4_cover_format(cover_data)
            audio["covr"] = [MP4Cover(cover_data, imageformat=image_format)]

        audio.save()
        print(f"[INFO] m4a metadata saved: {filename}")
        return True

    except Exception as e:
        print(f"[WARN] m4a tagging failed: {filename} | {e}")
        return False


def write_m4a_cover_only(filename: str | Path, cover_path: str | Path) -> bool:
    try:
        filename = Path(filename)
        cover_path = Path(cover_path)

        cover_data = cover_path.read_bytes()
        image_format = MP4Cover.FORMAT_PNG if cover_data.startswith(b"\x89PNG\r\n\x1a\n") else MP4Cover.FORMAT_JPEG

        audio = MP4(str(filename))
        audio["covr"] = [MP4Cover(cover_data, imageformat=image_format)]
        audio.save()

        print(f"[INFO] m4a cover saved: {filename}")
        return True

    except Exception as e:
        print(f"[WARN] m4a cover fix failed: {filename} | {e}")
        return False