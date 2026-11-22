"""
Automated File Organizer & Cleanup Utility
------------------------------------------
- Scans a folder (e.g. Downloads) and checks every file's extension
- Creates category subfolders: Documents, Images, Videos, Archives, Code
- Safely moves files with shutil.move(), handling:
    * naming collisions (renames to name_1.ext, name_2.ext ...)
    * permission errors and other OS errors (logged, then skipped)
- Files with unknown extensions and existing subfolders are left untouched
- Supports a dry-run preview and logs every action to organizer.log
- Prints a formatted execution summary at the end
"""

import logging
import os
import shutil
from collections import Counter
from datetime import datetime

EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".ppt": "Documents", ".pptx": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".csv": "Documents",
    ".odt": "Documents", ".rtf": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".bmp": "Images", ".svg": "Images", ".webp": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos",
    ".wmv": "Videos", ".flv": "Videos",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".html": "Code", ".css": "Code",
    ".java": "Code", ".c": "Code", ".cpp": "Code", ".ino": "Code",
    ".json": "Code", ".ipynb": "Code",
}

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organizer.log")


def setup_logging():
    logger = logging.getLogger("organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger


def unique_destination(dest_dir, filename):
    """Return a path in dest_dir that doesn't clash with an existing file."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_dir, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def organize(folder, dry_run, logger):
    stats = Counter()
    per_category = Counter()
    this_script = os.path.abspath(__file__)

    logger.info("Scanning: %s (%s)", folder, "DRY RUN" if dry_run else "LIVE")
    try:
        entries = [e for e in os.scandir(folder) if e.is_file()]
    except (FileNotFoundError, PermissionError, NotADirectoryError) as err:
        logger.error("Cannot read folder: %s", err)
        return stats, per_category

    for entry in entries:
        if os.path.abspath(entry.path) == this_script or entry.name == "organizer.log":
            continue
        ext = os.path.splitext(entry.name)[1].lower()
        category = EXTENSION_MAP.get(ext)
        if category is None:
            stats["skipped"] += 1
            logger.info("SKIP    %s (unknown type '%s')", entry.name, ext or "none")
            continue

        dest_dir = os.path.join(folder, category)
        try:
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
            dest_path = unique_destination(dest_dir, entry.name)
            renamed = os.path.basename(dest_path) != entry.name
            if dry_run:
                logger.info("WOULD MOVE  %s -> %s/%s", entry.name, category, os.path.basename(dest_path))
            else:
                shutil.move(entry.path, dest_path)
                logger.info("MOVED   %s -> %s/%s", entry.name, category, os.path.basename(dest_path))
            stats["moved"] += 1
            per_category[category] += 1
            if renamed:
                stats["renamed"] += 1
        except PermissionError:
            stats["errors"] += 1
            logger.error("PERMISSION DENIED: %s", entry.name)
        except FileExistsError:
            stats["errors"] += 1
            logger.error("FILE EXISTS: %s", entry.name)
        except OSError as err:
            stats["errors"] += 1
            logger.error("FAILED %s: %s", entry.name, err)
    return stats, per_category


def print_summary(folder, stats, per_category, dry_run):
    print("\n" + "=" * 48)
    print("          EXECUTION SUMMARY" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 48)
    print(f"Folder          : {folder}")
    print(f"Run time        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Files {'to move' if dry_run else 'moved'}   : {stats['moved']}")
    print(f"Renamed (clash) : {stats['renamed']}")
    print(f"Skipped         : {stats['skipped']}")
    print(f"Errors          : {stats['errors']}")
    if per_category:
        print("-" * 48)
        for category, count in sorted(per_category.items()):
            print(f"  {category:<12}: {count}")
    print("=" * 48)
    print(f"Log file: {LOG_FILE}")


def main():
    print("=== AUTOMATED FILE ORGANIZER ===\n")
    default = os.path.join(os.path.expanduser("~"), "Downloads")
    folder = input(f"Folder to organize [{default}]: ").strip().strip('"') or default
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        print("That folder does not exist.")
        return

    logger = setup_logging()

    # Always preview first, so nothing is moved by surprise
    stats, per_category = organize(folder, dry_run=True, logger=logger)
    print_summary(folder, stats, per_category, dry_run=True)
    if stats["moved"] == 0:
        print("\nNothing to organize.")
        return

    if input("\nProceed and move these files? (y/n): ").strip().lower() != "y":
        print("Cancelled. No files were moved.")
        return

    stats, per_category = organize(folder, dry_run=False, logger=logger)
    print_summary(folder, stats, per_category, dry_run=False)


if __name__ == "__main__":
    main()
