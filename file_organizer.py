"""
File Organizer & Duplicate Finder
-----------------------------------
A command-line tool that:
  1. Sorts files in a folder into sub-folders by file type (Images, Documents, Videos, etc.)
  2. Finds duplicate files (by content hash, not just filename) and reports/removes them
  3. Logs every action it takes to organizer_log.txt so changes are auditable

Why this project is a good portfolio piece:
  - Shows real filesystem handling (os, pathlib, shutil)
  - Shows hashing for duplicate detection (hashlib)
  - Shows a proper CLI with argparse (a common freelance "automate my folder" request)
  - Has a --dry-run mode, which clients love because it's safe to test

Usage:
    python file_organizer.py /path/to/folder                 # organize by type
    python file_organizer.py /path/to/folder --dry-run        # preview only, no changes
    python file_organizer.py /path/to/folder --find-duplicates
    python file_organizer.py /path/to/folder --find-duplicates --delete-duplicates
"""

import argparse
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Map file extensions to a destination folder name
CATEGORY_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx", ".csv"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Audio": [".mp3", ".wav", ".m4a", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json"],
}

LOG_FILE = "organizer_log.txt"


def log_action(message: str) -> None:
    """Append a timestamped line to the log file and print it to the console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_category(file_path: Path) -> str:
    """Return the category folder name for a given file, or 'Other' if unknown."""
    ext = file_path.suffix.lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return "Other"


def organize_folder(folder: Path, dry_run: bool = False) -> None:
    """Move every file in `folder` into a sub-folder based on its type."""
    if not folder.is_dir():
        print(f"Error: {folder} is not a valid folder.")
        return

    files = [f for f in folder.iterdir() if f.is_file() and f.name != LOG_FILE]
    if not files:
        print("No files found to organize.")
        return

    moved_count = 0
    for file_path in files:
        category = get_category(file_path)
        dest_folder = folder / category
        dest_path = dest_folder / file_path.name

        if dry_run:
            log_action(f"[DRY RUN] Would move '{file_path.name}' -> {category}/")
        else:
            dest_folder.mkdir(exist_ok=True)
            # avoid overwriting a file with the same name
            counter = 1
            while dest_path.exists():
                dest_path = dest_folder / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1
            shutil.move(str(file_path), str(dest_path))
            log_action(f"Moved '{file_path.name}' -> {category}/{dest_path.name}")
        moved_count += 1

    log_action(f"Done. {moved_count} file(s) processed.")


def file_hash(file_path: Path, block_size: int = 65536) -> str:
    """Return an MD5 hash of a file's contents, read in chunks to handle large files."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(folder: Path, delete: bool = False) -> None:
    """Scan a folder (recursively) for files with identical content and report/remove them."""
    if not folder.is_dir():
        print(f"Error: {folder} is not a valid folder.")
        return

    hashes = defaultdict(list)
    for file_path in folder.rglob("*"):
        if file_path.is_file() and file_path.name != LOG_FILE:
            hashes[file_hash(file_path)].append(file_path)

    duplicate_groups = {h: paths for h, paths in hashes.items() if len(paths) > 1}

    if not duplicate_groups:
        print("No duplicates found.")
        return

    total_wasted_space = 0
    for paths in duplicate_groups.values():
        original, *copies = sorted(paths, key=lambda p: p.stat().st_mtime)
        log_action(f"Duplicate set found (keeping '{original}'):")
        for copy in copies:
            size = copy.stat().st_size
            total_wasted_space += size
            if delete:
                copy.unlink()
                log_action(f"  Deleted duplicate: {copy}")
            else:
                log_action(f"  Duplicate (not deleted): {copy}")

    log_action(
        f"Found {sum(len(p) - 1 for p in duplicate_groups.values())} duplicate file(s), "
        f"wasting {total_wasted_space / 1024:.1f} KB."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Organize a folder by file type and/or find duplicate files."
    )
    parser.add_argument("folder", type=str, help="Path to the folder to process")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without moving any files"
    )
    parser.add_argument(
        "--find-duplicates", action="store_true", help="Scan for duplicate files instead of organizing"
    )
    parser.add_argument(
        "--delete-duplicates",
        action="store_true",
        help="Actually delete duplicates found (use with --find-duplicates)",
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()

    if args.find_duplicates:
        find_duplicates(folder, delete=args.delete_duplicates)
    else:
        organize_folder(folder, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
