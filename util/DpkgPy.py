import arpy
import tarfile


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
            try:
                data_bin = root_ar.archived_files[b'data.tar.gz']
                data_tar = tarfile.open(fileobj=data_bin)
                data_tar.extractall(output_path)
            except Exception:
                try:
                    data_theos_bin = root_ar.archived_files[b'data.tar.lzma']
                    data_theos_bin.seekable = lambda: True
                    data_theos_tar = tarfile.open(fileobj=data_theos_bin, mode='r:xz')
                    data_theos_tar.extractall(output_path)
                except Exception:
                    try:
                        data_theos_bin = root_ar.archived_files[b'data.tar.xz']
                        data_theos_bin.seekable = lambda: True
                        data_theos_tar = tarfile.open(fileobj=data_theos_bin, mode='r:xz')
                        data_theos_tar.extractall(output_path)
                    except Exception:
                        print("\033[91m- DEB Extraction Error -\n"
                              "The DEB file inserted for one of your packages is invalid. Please report this as a bug "
                              "and attach the DEB file at \"" + output_path + "\".\033[0m")

            control_bin = root_ar.archived_files[b'control.tar.gz']
            control_tar = tarfile.open(fileobj=control_bin)
            control_tar.extractall(output_path)
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
            control_bin = root_ar.archived_files[b'control.tar.gz']
            control_tar = tarfile.open(fileobj=control_bin)
            control_tar.extractall(output_path)
            return True
        except Exception:
            return False

    # TODO: Add support for the creation of DEB files without any dependencies, allowing for improved Windows support.
