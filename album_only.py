from pathlib import Path
import re
from tagging import tag_m4a

TOP_DIR = r"S:\袁腾飞频道"
ARTIST_NAME = "lifeano"

def infer_album_from_path(file_path: Path) -> str:
    # 最近的父目录作为 album
    folder_name = file_path.parent.name
    # 去掉开头数字和点
    return re.sub(r"^\d+\.\s*", "", folder_name)

def fix_album_recursive(top_dir: str):
    top_path = Path(top_dir)
    for m4a_file in top_path.rglob("*.m4a"):  # 递归扫描所有 m4a
        album_name = infer_album_from_path(m4a_file)
        print(f"[INFO] Fixing album for: {m4a_file} -> {album_name}")
        tag_m4a(
            m4a_file,
            title=m4a_file.stem,
            artist=ARTIST_NAME,
            album=album_name,
            description="",      # 可填原来的 description
            cover_path=None,     # 保留原封面
        )

if __name__ == "__main__":
    fix_album_recursive(TOP_DIR)