# Disk-To-File-Cloner
A tool developed for an exercise in the subject of Forensic Analysis to create .dd image files of disk clones.

THIS TOOL REQUIRES ADMIN PRIVILEGES. RUN A POWERSHELL AS ADMINISTRATOR.

Usage:
Clone a disk to a file:
python windows-disk-cloner.py clone <disk_number> <output_file.dd>

Restore a clone to a disk (THIS ACTION WILL REPLACE ALL FILES AND STRUCTURE OF THE DISK):
python windows-disk-cloner.py restore <disk_number> <input_file.dd>

Inspired by: https://github.com/levitation-opensource/DiskClone
