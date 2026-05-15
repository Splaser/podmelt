from pathlib import Path
import sys

from mutagen.mp4 import MP4, MP4Cover


def detect_cover_format(data: bytes) -> int:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return MP4Cover.FORMAT_PNG
    return MP4Cover.FORMAT_JPEG


def write_m4a_cover_only(m4a_path: Path, cover_path: Path) -> bool:
    try:
        if not m4a_path.exists():
            print(f"[WARN] file not found: {m4a_path}")
            return False

        if not cover_path.exists():
            print(f"[WARN] cover not found: {cover_path}")
            return False

        cover_data = cover_path.read_bytes()
        image_format = detect_cover_format(cover_data)

        audio = MP4(str(m4a_path))
        audio["covr"] = [MP4Cover(cover_data, imageformat=image_format)]
        audio.save()

        print(f"[INFO] cover saved: {m4a_path}")
        return True

    except Exception as e:
        print(f"[WARN] cover write failed: {m4a_path} | {e}")
        return False


def batch_apply_cover(folder: Path, cover_path: Path, recursive: bool = False):
    pattern = "**/*.m4a" if recursive else "*.m4a"
    files = sorted(folder.glob(pattern))

    if not files:
        print(f"[ERROR] no m4a files found in: {folder}")
        return 1

    success = 0
    failed = 0

    for f in files:
        ok = write_m4a_cover_only(f, cover_path)
        if ok:
            success += 1
        else:
            failed += 1

    print(f"[DONE] success={success}, failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print('  py cover_only.py "S:\\袁腾飞频道\\神圣罗马帝国史 A.D.962-1806" "cover.png"')
        sys.exit(1)

    folder = Path(sys.argv[1])
    cover = Path(sys.argv[2])

    raise SystemExit(batch_apply_cover(folder, cover))