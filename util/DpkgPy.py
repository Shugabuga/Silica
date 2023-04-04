import io
import lzma
import tarfile
import arpy
import os
import pyzstd

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
            
            data_bin_ext = None

            for ext in ['.gz', '.lzma', '.xz', '.zst']:
                if b'data.tar' + ext.encode() in root_ar.archived_files:
                    data_bin_ext = ext
                    break

            if data_bin_ext is None:
                raise ValueError("Unsupported data_bin format")

            data_bin = root_ar.archived_files[b'data.tar' + data_bin_ext.encode()]

            if data_bin_ext == '.gz':
                data_tar = tarfile.open(fileobj=data_bin)
            elif data_bin_ext == '.lzma' or data_bin_ext == '.xz':
                data_data = lzma.decompress(data_bin.read())
                data_tar = tarfile.open(fileobj=io.BytesIO(data_data))
            elif data_bin_ext == '.zst':
                data_data = pyzstd.decompress(data_bin.read())
                data_tar = tarfile.open(fileobj=io.BytesIO(data_data))

            data_tar.extractall(output_path)
            print(output_path)
            return True
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
            
            control_bin_ext = None

            for ext in ['.gz', '.lzma', '.xz', '.zst']:
                if b'control.tar' + ext.encode() in root_ar.archived_files:
                    control_bin_ext = ext
                    break

            if control_bin_ext is None:
                raise ValueError("Unsupported control_bin format")

            control_bin = root_ar.archived_files[b'control.tar' + control_bin_ext.encode()]

            if control_bin_ext == '.gz':
                control_tar = tarfile.open(fileobj=control_bin)
            elif control_bin_ext == '.lzma' or control_bin_ext == '.xz':
                control_data = lzma.decompress(control_bin.read())
                control_tar = tarfile.open(fileobj=io.BytesIO(control_data))
            elif control_bin_ext == '.zst':
                control_data = pyzstd.decompress(control_bin.read())
                control_tar = tarfile.open(fileobj=io.BytesIO(control_data))

            control_tar.extractall(output_path)
            return True
        except Exception:
            return False

    # TODO: Add support for the creation of DEB files without any dependencies, allowing for improved Windows support.
