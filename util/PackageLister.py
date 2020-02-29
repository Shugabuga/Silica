import json  # Used to parse various JSON files
import os  # Used to navigate files so we know what tweak folders exist.
from PIL import Image  # Used to get image screenshot size.


class PackageLister:
    """
    PackageLister gathers data on packages that will be in the repo.
    It also includes some helper functions related to os.
    """

    def __init__(self, version):
        super(PackageLister, self).__init__()
        self.version = version
        self.root = os.path.dirname(os.path.abspath(__file__)) + "/../"

    def CreateFile(self, path, contents):
        """
        Creates a text file (properly).

        String path: A file location to create a file at. Is relative to project root.
        String contents: The contents of the file to be created.
        """
        with open(self.root + path, "w") as text_file:
            text_file.write(contents)

    def CreateFolder(self, path):
        """
        Creates a folder.

        String path: A file location to create a folder at. Is relative to project root.
        """
        if not os.path.exists(self.root + path):
            os.makedirs(self.root + path)
        else:
            pass

    def ListDirNames(self):
        """
        List the file names for package entries.
        """
        package_list = []
        for folder in os.listdir(self.root + "Packages"):
            if folder.lower() != ".ds_store":
                package_list.append(folder)
        return package_list

    def GetTweakRelease(self):
        """
        Create a "tweak release" object that combines the index.json of every package.
        Analogous to Packages.bz2.
        """
        tweak_release = []
        for tweakEntry in PackageLister.ListDirNames(self):
            with open(self.root + "Packages/" + tweakEntry + "/silica_data/index.json", "r") as content_file:
                try:
                    data = json.load(content_file)
                except Exception:
                    PackageLister.ErrorReporter(self, "Configuration Error!", "The package configuration file at \"" +
                        self.root + "Packages/" + tweakEntry + "/silica_data/index.json\" is malformatted. Please check"
                        " for any syntax errors in a JSON linter and run Silica again.")
                tweak_release.append(data)
        return tweak_release

    def GetScreenshots(self, tweak_data):
        """
        Get an array of screenshot names copied over to the static site.

        Object tweak_data: A single index of a "tweak release" object.
        """
        image_list = []
        try:
            for folder in os.listdir(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/screenshot/"):
                if folder.lower() != ".ds_store":
                    image_list.append(folder)
        except:
            pass
        return image_list

    def GetScreenshotSize(self, tweak_data):
        """
        Get the size of a screenshot.

        Object tweak_data: A single index of a "tweak release" object.
        """
        try:
            for folder in os.listdir(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/screenshot/"):
                if folder.lower() != ".ds_store":
                    with Image.open(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/screenshot/" + folder) as img:
                        width, height = img.size
                        #  Make sure it's not too big.
                        #  If height > width, make height 300, width proportional.
                        #  If height < width, make width 160, height proportional.
                        if height > width:
                            width = round((400 * width)/height)
                            height = 400
                        else:
                            height = round((200 * height) / width)
                            width = 200
                        return "{" + str(width) + "," + str(height) + "}"
        except Exception:
            return False

    def DirNameToBundleID(self, package_name):
        """
        Take a human-readable directory name and find the corresponding bundle id.

        String package_name: The name of a folder in Packages/ that holds tweak information.
        """

        with open(self.root + "Packages/" + package_name + "/silica_data/index.json", "r") as content_file:
            data = json.load(content_file)
            return data['bundle_id']

    def BundleIdToDirName(self, bundle_id):
        """
        Take a bundle id and find the corresponding human-readable directory name.

        String bundle_id: The bundle ID of the tweak.
        """
        for package_name in PackageLister.ListDirNames(self):
            new_bundle = PackageLister.DirNameToBundleID(self, package_name)
            if new_bundle == bundle_id:
                return package_name
        return None
                
    def GetRepoSettings(self):
        with open(self.root + "Styles/settings.json", "r") as content_file:
            try:
                return json.load(content_file)
            except Exception:
                PackageLister.ErrorReporter(self, "Configuration Error!", "The Silica configuration file at \"" +
                    self.root + "Styles/settings.json\" is malformatted. Please check for any syntax errors in a JSON"
                    " linter and run Silica again.")

    def FullPathCname(self, repo_settings):
        """
        Some people may use a sub-folder like "repo" to put repo contents in.
        While this is not recommended, Silica does support this.

        Object repo_settings: An object of repo settings.
        """
        try:
            if repo_settings['subfolder'] != "":
                subfolder = "/" + repo_settings['subfolder']
        except Exception:
            subfolder = ""
        return subfolder

    def ResolveCategory(self, tweak_release, bundle_id):
        """
        Returns the category name when given a bundle ID.

        Object tweak_release: A "tweak release" object.
        String bundle_id: The bundle ID of the tweak.
        """
        for tweak in tweak_release:
            if tweak['bundle_id'] == bundle_id:
                return tweak['section']

    def ResolveVersion(self, tweak_release, bundle_id):
        """
        Returns the version when given a bundle ID.

        Object tweak_release: A "tweak release" object.
        String bundle_id: The bundle ID of the tweak.
        """
        for tweak in tweak_release:
            if tweak['bundle_id'] == bundle_id:
                return tweak['version']

    def ErrorReporter(self, title, message):
        print('\033[91m- {0} -\n{1}\033[0m'.format(title, message))
        quit()