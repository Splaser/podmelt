from pathlib import Path
import re
from tagging import tag_m4a
from utils import is_video_file, default_output_path

FOLDERS = [
    r"S:\袁腾飞频道\第零次世界大战\01. 日俄战争 1904–1905",
    r"S:\袁腾飞频道\第零次世界大战\02. 奥地利王位继承战争 1740–1748",
    r"S:\袁腾飞频道\第零次世界大战\03. 七年战争 1756–1763",
]

def infer_album_from_path(folder_path: Path) -> str:
    folder_name = folder_path.name
    return re.sub(r"^\d+\.\s*", "", folder_name)

for folder in FOLDERS:
    folder_path = Path(folder)
    album_name = infer_album_from_path(folder_path)

    for file in folder_path.iterdir():
        if file.suffix.lower() == ".m4a":
            print(f"[INFO] Fixing album for: {file}")
            tag_m4a(
                file,
                title=file.stem,
                artist="lifeano",          # 或你想保留的作者
                album=album_name,
                description="",            # 可填原来的描述
                cover_path=None,           # 保留原封面
            )