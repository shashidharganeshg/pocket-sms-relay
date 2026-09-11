#!/usr/bin/env python3
"""Build the pinned, patched Android ARM64 Dropbear client tools."""

import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

ANDROID_DROPBEAR_REPOSITORY = "https://github.com/ribbons/android-dropbear.git"
ANDROID_DROPBEAR_TAG = "DROPBEAR_2026.94"

ROOT = Path(__file__).resolve().parents[1]
PATCH_FILE = ROOT / "patches" / "dropbear-zero-port-errno.patch"
LIB_DIR = ROOT / "libs" / "arm64-v8a"
LICENSE_DIR = ROOT / "third_party" / "licenses"


def run(command, cwd=None, env=None):
    command = [str(item) for item in command]
    print(">>>", " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_arm64_elf(path):
    header = path.read_bytes()[:20]
    if header[:4] != b"\x7fELF":
        raise RuntimeError(f"Not an ELF binary: {path}")
    machine = int.from_bytes(header[18:20], "little")
    if machine != 183:
        raise RuntimeError(
            f"Not an ARM64 ELF binary: {path}; e_machine={machine}"
        )


def main():
    ndk_home = os.environ.get("ANDROID_NDK_HOME")
    if not ndk_home:
        raise RuntimeError("ANDROID_NDK_HOME must point to Android NDK r28c")

    ndk_path = Path(ndk_home).resolve()
    if not (ndk_path / "source.properties").is_file():
        raise RuntimeError(f"Invalid Android NDK directory: {ndk_path}")
    if not PATCH_FILE.is_file():
        raise RuntimeError(f"Missing Dropbear patch: {PATCH_FILE}")

    LIB_DIR.mkdir(parents=True, exist_ok=True)
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="android-dropbear-") as temp_dir:
        checkout = Path(temp_dir) / "android-dropbear"
        run(
            [
                "git", "clone", "--depth", "1", "--branch",
                ANDROID_DROPBEAR_TAG, ANDROID_DROPBEAR_REPOSITORY, checkout,
            ]
        )

        # The upstream Android build script automatically applies every
        # *.patch file found at the checkout root to the Dropbear source.
        shutil.copy2(PATCH_FILE, checkout / "zero-port-errno.patch")

        environment = os.environ.copy()
        environment["ANDROID_NDK_HOME"] = str(ndk_path)
        environment["TARGET"] = "aarch64-linux-android"
        run(["bash", "build"], cwd=checkout, env=environment)

        outputs = {
            "libdbclient.so": checkout / "dropbear" / "dbclient",
            "libdropbearkey.so": checkout / "dropbear" / "dropbearkey",
        }

        metadata = {
            "android_dropbear_repository": ANDROID_DROPBEAR_REPOSITORY,
            "android_dropbear_tag": ANDROID_DROPBEAR_TAG,
            "ndk": ndk_path.name,
            "patch": {
                "path": str(PATCH_FILE.relative_to(ROOT)),
                "sha256": sha256(PATCH_FILE),
            },
            "files": {},
        }

        for output_name, built_binary in outputs.items():
            if not built_binary.is_file():
                raise RuntimeError(f"Dropbear build output is missing: {built_binary}")
            target = LIB_DIR / output_name
            shutil.copy2(built_binary, target)
            target.chmod(
                target.stat().st_mode
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH
            )
            verify_arm64_elf(target)
            metadata["files"][output_name] = {
                "size": target.stat().st_size,
                "sha256": sha256(target),
            }

        license_source = checkout / "dropbear" / "LICENSE"
        shutil.copy2(license_source, LICENSE_DIR / "dropbear.txt")

    (ROOT / "dropbear-build.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
