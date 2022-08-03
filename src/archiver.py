import os
import shutil
import zipfile
from pathlib import Path


class Archiver(object):
    @staticmethod
    def is_dir_in_zip(fileinfo):
        # type: (zipfile.ZipInfo) -> bool
        hi = fileinfo.external_attr >> 16
        return (hi & 0x4000) > 0

    @staticmethod
    def zip_dir(dirpath, zippath):
        with zipfile.ZipFile(zippath, "w", zipfile.ZIP_DEFLATED) as zfile:
            for root, dirs, files in os.walk(dirpath):
                if os.path.basename(root)[0] == ".":
                    continue  # skip hidden directories
                for f in files:
                    if f[-1] == "~" or (f[0] == "." and f != ".htaccess"):
                        # skip backup files and all hidden files except .htaccess
                        continue
                    zfile.write(os.path.join(root, f))

    @staticmethod
    def extract_specific_folder(extract_to_path, zfile, extract_dir_name):
        # type: (Path, zipfile.ZipFile, str) -> Path
        target_dir = extract_to_path.joinpath(extract_dir_name)

        # if `extract_dir_name` dir not present in archive raise an exception
        if not all(
            True
            for m in zfile.filelist
            if Archiver.is_dir_in_zip(m) and extract_dir_name in m.filename
        ):
            raise RuntimeError("`{}` not present in archive")

        # find index of searched dir to split in the future
        extract_dir_name_index = -1
        for member in zfile.filelist:
            if not Archiver.is_dir_in_zip(member):
                continue

            splitted_path = member.filename.split("/")
            try:
                found_dir_index = splitted_path.index(extract_dir_name)
            except ValueError:
                continue
            if found_dir_index != -1:
                extract_dir_name_index = found_dir_index
                break

        for member in zfile.filelist:
            splitted_path = member.filename.split("/")
            filename = "/".join(splitted_path[extract_dir_name_index:])
            # skip top directories
            if not filename.startswith(extract_dir_name):
                continue
            targetpath = extract_to_path.joinpath(filename)
            # Create all upper directories if necessary.
            upperdirs = targetpath.parent
            if upperdirs and not upperdirs.exists():
                os.makedirs(upperdirs)

            if Archiver.is_dir_in_zip(member):
                if not targetpath.is_dir():
                    os.mkdir(targetpath)
                continue

            with zfile.open(member) as source, open(targetpath, "wb") as target:
                shutil.copyfileobj(source, target)
            # Required to get android scripts working
            os.chmod(targetpath, 0o775)
        return target_dir
