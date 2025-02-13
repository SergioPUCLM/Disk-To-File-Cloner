import os
import sys
import ctypes
import time
from ctypes import wintypes

# Constants
SECTOR_SIZE = 512  # Size of disk sector. New drives use 4KB sectors, but 512B is still commonon old drives
BUFFER_SIZE = SECTOR_SIZE * 1024  # 512KB buffer for efficiency

# Windows API access
GENERIC_READ = 0x80000000  # Read access
GENERIC_WRITE = 0x40000000  # Write access
OPEN_EXISTING = 3  # Open existing file
OPEN_ALWAYS = 4  # Create new file if not exists


def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def open_disk(disk_number, write_mode=False):
    """
    Open a disk on read or write mode.
    WARNING: While read mode is relatively safe, write mode can and will destroy the data of your disk!
    """
    device_path = f"\\\\.\\PhysicalDrive{disk_number}"
    access_mode = GENERIC_WRITE if write_mode else GENERIC_READ

    handle = ctypes.windll.kernel32.CreateFileW(
        device_path,
        access_mode,
        0,  # No sharing
        None,
        OPEN_EXISTING,
        0,
        None
    )
    if handle == -1:
        raise OSError(f"Failed to open {device_path}. Run as Administrator?")
    return handle


def read_disk(disk_handle, output_file):
    """Read raw data and save to .dd file."""
    with open(output_file, "wb") as out_file:
        buffer = ctypes.create_string_buffer(BUFFER_SIZE)
        bytes_read = wintypes.DWORD()

        print("\nStarting disk cloning... (This may take a while)")
        while True:
            success = ctypes.windll.kernel32.ReadFile(disk_handle, buffer, BUFFER_SIZE, ctypes.byref(bytes_read), None)
            if not success or bytes_read.value == 0:
                break  # Stop at end of disk
            out_file.write(buffer.raw[:bytes_read.value])
            print(f"{bytes_read.value} bytes copied...", end="\r")

        print("\nDisk cloning complete!")


def write_disk(disk_handle, input_file):
    """Restore .dd file to disk. WARNING: This will overwrite the disk!"""
    with open(input_file, "rb") as in_file:
        buffer = ctypes.create_string_buffer(BUFFER_SIZE)
        bytes_written = wintypes.DWORD()

        print("\nStarting disk restoration... (This will overwrite the disk!)")
        while True:
            chunk = in_file.read(BUFFER_SIZE)
            if not chunk:
                break

            ctypes.memmove(buffer, chunk, len(chunk))
            success = ctypes.windll.kernel32.WriteFile(disk_handle, buffer, len(chunk), ctypes.byref(bytes_written), None)
            if not success:
                raise OSError("Failed to write to disk!")

            print(f"{bytes_written.value} bytes written...", end="\r")

        print("\nDisk restoration complete!")


def close_disk(handle):
    """Close the disk handle."""
    ctypes.windll.kernel32.CloseHandle(handle)


if __name__ == "__main__":
    if not is_admin():
        print("ERROR: This script must be run as Administrator!")
        sys.exit(1)

    if len(sys.argv) < 4:
        print("Usage: python disk_tool.py <clone|restore> <disk_number> <file.dd>")
        print("Example (Clone):   python disk_tool.py clone 0 my_disk.dd")
        print("Example (Restore): python disk_tool.py restore 1 my_disk.dd")
        sys.exit(1)

    mode = sys.argv[1].lower()
    disk_number = sys.argv[2]
    file_path = sys.argv[3]

    try:
        if mode == "clone":
            disk_handle = open_disk(disk_number, write_mode=False)
            read_disk(disk_handle, file_path)
        elif mode == "restore":
            print("⚠️ WARNING: This will OVERWRITE the selected disk! ⚠️")
            confirm = input("Type 'YES' to continue: ")
            if confirm.strip().upper() != "YES":
                print("Restore operation aborted.")
                sys.exit(1)

            disk_handle = open_disk(disk_number, write_mode=True)
            write_disk(disk_handle, file_path)
        else:
            print("Invalid mode! Use 'clone' or 'restore'.")
            sys.exit(1)
    finally:
        close_disk(disk_handle)
