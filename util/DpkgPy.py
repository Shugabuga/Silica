import arpy
import os
import tarfile
import lzma

try:
    import zstandard as zstd
except Exception:
    zstd = None


def _extract_control_scripts(control_tar, output_path):
    """
    Puts the members of a DEB's control archive (postinst, prerm, ...) into output_path/DEBIAN instead of the
    package root, so they stay maintainer scripts instead of being installed as files.
    Anything already in DEBIAN (Silica's generated control, silica_data/scripts) takes priority.
    """
    debian_path = os.path.join(output_path, "DEBIAN")
    os.makedirs(debian_path, exist_ok=True)
    for member in control_tar:
        if not os.path.lexists(os.path.join(debian_path, member.name)):
            control_tar.extract(member, debian_path)


class DpkgPy:
    """
    DpkgPy is a Python library designed to create and manipulate Debian packages in pure Python.
    It has no dependencies besides other Python libraries.

    (c) 2019 Shuga Holdings. All rights reserved!
    """
    def __init__(self):
        super(DpkgPy, self).__init__()

    def extract(self, input_path, output_path):
        """
        Extracts data from a DEB file.
        :param input_path: A String of the file path of the DEB to extract.
        :param output_path: A String of the file path to put the extracted DEB. Folder must already exist.
        :return: A Boolean on whether the extraction succeeded or failed.
        """
        try:
            root_ar = arpy.Archive(input_path)
            root_ar.read_all_headers()
            # data.*
            extracted_data = False
            # Prefer common formats first
            for key, mode in [
                (b'data.tar.gz', 'r:*'),
                (b'data.tar.xz', 'r:xz'),
                (b'data.tar.lzma', 'r:xz'),
            ]:
                if extracted_data:
                    break
                try:
                    data_bin = root_ar.archived_files[key]
                    data_bin.seekable = lambda: True
                    data_tar = tarfile.open(fileobj=data_bin, mode=mode)
                    data_tar.extractall(output_path)
                    extracted_data = True
                except Exception:
                    pass

            # Zstandard support: data.tar.zst
            if not extracted_data:
                try:
                    data_zst_bin = root_ar.archived_files[b'data.tar.zst']
                    if zstd is None:
                        raise RuntimeError("Missing zstandard module; install with: pip install zstandard")
                    dctx = zstd.ZstdDecompressor()
                    stream = dctx.stream_reader(data_zst_bin)
                    data_tar = tarfile.open(fileobj=stream, mode='r|*')
                    data_tar.extractall(output_path)
                    extracted_data = True
                except Exception:
                    pass

            if not extracted_data:
                print("\033[91m- DEB Extraction Error -\n"
                      "The DEB file inserted for one of your packages is invalid. Please report this as a bug "
                      "and attach the DEB file at \"" + output_path + "\".\033[0m")

            # control.*
            extracted_control = False
            for key, mode in [
                (b'control.tar.gz', 'r:*'),
                (b'control.tar.xz', 'r:xz'),
                (b'control.tar.lzma', 'r:xz'),
            ]:
                if extracted_control:
                    break
                try:
                    control_bin = root_ar.archived_files[key]
                    control_bin.seekable = lambda: True
                    control_tar = tarfile.open(fileobj=control_bin, mode=mode)
                    _extract_control_scripts(control_tar, output_path)
                    extracted_control = True
                except Exception:
                    pass

            # Zstandard support: control.tar.zst
            if not extracted_control:
                try:
                    control_zst_bin = root_ar.archived_files[b'control.tar.zst']
                    if zstd is None:
                        raise RuntimeError("Missing zstandard module; install with: pip install zstandard")
                    dctx = zstd.ZstdDecompressor()
                    stream = dctx.stream_reader(control_zst_bin)
                    control_tar = tarfile.open(fileobj=stream, mode='r|*')
                    _extract_control_scripts(control_tar, output_path)
                    extracted_control = True
                except Exception:
                    pass

            return extracted_data and extracted_control
        except Exception:
            return False

    def control_extract(self, input_path, output_path):
        """
        Extracts only the Control file(s) from a DEB
        :param input_path: A String of the file path of the DEB to extract.
        :param output_path: A String of the file path to put the extracted DEB. Folder must already exist.
        :return: A Boolean on whether the extraction succeeded or failed.
        """
        try:
            root_ar = arpy.Archive(input_path)
            root_ar.read_all_headers()
            extracted_control = False
            for key, mode in [
                (b'control.tar.gz', 'r:*'),
                (b'control.tar.xz', 'r:xz'),
                (b'control.tar.lzma', 'r:xz'),
            ]:
                if extracted_control:
                    break
                try:
                    control_bin = root_ar.archived_files[key]
                    control_bin.seekable = lambda: True
                    control_tar = tarfile.open(fileobj=control_bin, mode=mode)
                    control_tar.extractall(output_path)
                    extracted_control = True
                except Exception:
                    pass

            if not extracted_control:
                try:
                    control_zst_bin = root_ar.archived_files[b'control.tar.zst']
                    if zstd is None:
                        raise RuntimeError("Missing zstandard module; install with: pip install zstandard")
                    dctx = zstd.ZstdDecompressor()
                    stream = dctx.stream_reader(control_zst_bin)
                    control_tar = tarfile.open(fileobj=stream, mode='r|*')
                    control_tar.extractall(output_path)
                    extracted_control = True
                except Exception:
                    pass

            return extracted_control
        except Exception:
            return False

    # TODO: Add support for the creation of DEB files without any dependencies, allowing for improved Windows support.
