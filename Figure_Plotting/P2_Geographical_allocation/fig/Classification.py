import os
import re
import shutil
import sys

def organize_images(src_dir):
    """
    将图片文件按 TECH_YEAR_EDxx 命名的子文件夹归类；
    如果文件夹不存在则自动创建，若已有同名文件则覆盖。
    """
    pattern = re.compile(r'(PEM|SOE)(?:_[^_]+)*_(\d{4})_ED(\d+)', re.IGNORECASE)

    for fname in os.listdir(src_dir):
        if not re.search(r'\.(png|jpe?g|tif(?:f)?|bmp)$', fname, re.IGNORECASE):
            continue

        m = pattern.search(fname)
        if not m:
            print(f"Skipped (no match): {fname}")
            continue

        tech, year, ed = m.groups()
        tech = tech.upper()
        folder_name = f"{tech}_{year}_ED{ed}"
        target_dir = os.path.join(src_dir, folder_name)

                        
        os.makedirs(target_dir, exist_ok=True)

        src_path = os.path.join(src_dir, fname)
        dst_path = os.path.join(target_dir, fname)

        if os.path.exists(dst_path):
            try:
                os.remove(dst_path)
                print(f"Removed existing: {folder_name}/{fname}")
            except OSError as e:
                print(f"Error removing {dst_path}: {e}")
                continue

        try:
            shutil.move(src_path, dst_path)
            print(f"Moved: {fname} -> {folder_name}/")
        except Exception as e:
            print(f"Error moving {fname}: {e}")

if __name__ == "__main__":
                      
    if len(sys.argv) == 1:
        source_directory = os.path.dirname(os.path.abspath(__file__))
        print(f"No directory arg given. Using script directory: {source_directory}")
    elif len(sys.argv) == 2:
        source_directory = sys.argv[1]
    else:
        print("Usage: python organize_images.py [<source_directory>]")
        sys.exit(1)

    if not os.path.isdir(source_directory):
        print(f"Error: '{source_directory}' is not a directory.")
        sys.exit(1)

    organize_images(source_directory)
