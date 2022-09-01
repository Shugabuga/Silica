import os  # For file path correction
import hashlib  # SHA256 for Release file
import re  # Regular expressions.
import json  # Used to parse various JSON files
import platform  # Detect use of WSL.
from subprocess import call  # Call dpkg-deb
from pydpkg import Dpkg  # Retrieve data from DEBs
from util.PackageLister import PackageLister
from util.DpkgPy import DpkgPy
import shutil  # Used to copy files


class DebianPackager(object):
    """
    DebianPackager deals with making a functional repo and deals
    with dpkg-deb and dpkg-scanpackages.
    """

    def __init__(self, version):
        super(DebianPackager, self).__init__()
        self.version = version
        self.root = os.path.dirname(os.path.abspath(__file__)) + "/../"
        self.PackageLister = PackageLister(self.version)

    def CompileRelease(self, repo_settings):
        """
        Compiles a Release file from a repo_settings object

        Object repo_settings: An object of repo settings.
        """
        release_file = "Origin: " + repo_settings['name'] + "\n"
        release_file += "Label: " + repo_settings['name'] + "\n"
        release_file += "Suite: stable\n"
        release_file += "Version: 1.0\n"
        release_file += "Codename: ios\n"
        release_file += "Architectures: iphoneos-arm\n"
        release_file += "Components: main\n"
        release_file += "Description: " + repo_settings['description'].replace("\n\n", "\n .\n ").replace("\n", "\n ") + "\n"

        return release_file

    def CompileControl(self, tweak_data, repo_settings):
        """
        Compiles a CONTROL file from a tweak_data object

        Object tweak_data: A single index of a "tweak release" object.
        Object repo_settings: An object of repo settings.
        """
        subfolder = PackageLister.FullPathCname(self, repo_settings)

        control_file = "Architecture: iphoneos-arm\n"
        # Mandatory properties include name, bundle id, and version.
        control_file += "Package: " + tweak_data['bundle_id'] + "\n"
        control_file += "Name: " + tweak_data['name'] + "\n"
        control_file += "Version: " + tweak_data['version'] + "\n"
        # Known properties
        control_file += "Depiction: https://" + repo_settings['cname'] + subfolder + "/depiction/web/" + tweak_data[
            'bundle_id'] \
                        + ".html\n"
        control_file += "SileoDepiction: https://" + repo_settings['cname'] + subfolder + "/depiction/native/" \
                        + tweak_data['bundle_id'] + ".json\n"
        control_file += "ModernDepiction: https://" + repo_settings['cname'] + subfolder + "/depiction/native/" \
                        + tweak_data['bundle_id'] + ".json\n"
        control_file += "Icon: https://" + repo_settings['cname'] + subfolder + "/assets/" + tweak_data[
            'bundle_id'] + "/icon.png\n"

        # Optional properties
        try:
            if tweak_data['tagline']:
                # APT note: Multi-line descriptions are in the spec, but must be indicated with a leading space.
                control_file += "Description: " + tweak_data['tagline'].replace("\n\n", "\n .\n ").replace("\n", "\n ") + "\n"
        except Exception:
            control_file += "Description: An awesome package!\n"

        try:
            if tweak_data['homepage']:
                control_file += "Homepage: " + tweak_data['homepage'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['section']:
                control_file += "Section: " + tweak_data['section'] + "\n"
        except Exception:
            control_file += "Section: Unknown\n"

        try:
            if tweak_data['pre_dependencies']:
                control_file += "Pre-Depends: " + tweak_data['pre_dependencies'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['dependencies']:
                control_file += "Depends: firmware (>=" + tweak_data['works_min'] + "), " + tweak_data[
                    'dependencies'] + "\n"
        except Exception:
            control_file += "Depends: firmware (>=" + tweak_data['works_min'] + ")\n"

        try:
            if tweak_data['conflicts']:
                control_file += "Conflicts: " + tweak_data['conflicts'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['replaces']:
                control_file += "Replaces: " + tweak_data['replaces'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['provides']:
                control_file += "Provides: " + tweak_data['provides'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['build_depends']:
                control_file += "Build-Depends: " + tweak_data['build_depends'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['recommends']:
                control_file += "Recommends: " + tweak_data['recommends'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['suggests']:
                control_file += "Suggests: " + tweak_data['suggests'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['enhances']:
                control_file += "Enhances: " + tweak_data['enhances'] + "\n"
        except Exception:
            pass

        try:
            if tweak_data['breaks']:
                control_file += "Breaks: " + tweak_data['breaks'] + "\n"
        except Exception:
            pass
        try:
            if tweak_data['tags']:
                control_file += "Tags: compatible_min::ios" + tweak_data['works_min'] + ", compatible_max::ios" + tweak_data['works_max'] + ", " + tweak_data['tags'] + "\n"
        except Exception:
            control_file += "Tags: compatible_min::ios" + tweak_data['works_min'] + ", compatible_max::ios" + tweak_data['works_max'] + "\n"

        try:
            if tweak_data['developer']:
                try:
                    if tweak_data['developer']['email']:
                        control_file += "Author: " + tweak_data['developer']['name'] + " <" + tweak_data['developer'][
                            'email'] + ">\n"
                except Exception:
                    control_file += "Author: " + tweak_data['developer']['name'] + "\n"
        except Exception:
            control_file += "Author: Unknown\n"

        try:
            if tweak_data['maintainer']['email']:
                control_file += "Maintainer: " + tweak_data['maintainer']['name'] + " <" \
                                + tweak_data['maintainer']['email'] + ">\n"
        except Exception:
            try:
                control_file += "Maintainer: " + tweak_data['maintainer']['name'] + "\n"
            except Exception:
                try:
                    if tweak_data['developer']['email']:
                        control_file += "Maintainer: " + tweak_data['developer']['name'] + " <" \
                                        + tweak_data['developer']['email'] + ">\n"
                except Exception:
                    try:
                        control_file += "Maintainer: " + tweak_data['developer']['name'] + "\n"
                    except Exception:
                        control_file += "Maintainer: Unknown\n"

        try:
            if tweak_data['sponsor']:
                try:
                    if tweak_data['sponsor']['email']:
                        control_file += "Sponsor: " + tweak_data['sponsor']['name'] + " <" + tweak_data['sponsor'][
                            'email'] + ">\n"
                except Exception:
                    control_file += "Sponsor: " + tweak_data['sponsor']['name'] + "\n"
        except Exception:
            pass

        # other_control
        try:
            if tweak_data['other_control']:
                for line in tweak_data['other_control']:
                    control_file += line + "\n"
        except Exception:
            pass

        return control_file

    def CreateDEB(self, bundle_id, recorded_version):
        """
        Creates a DEB from information stored in the "temp" folder.

        String bundle_id: The bundle id of the package to compress.
        String recorded_version: 
        Object tweak_release: A "tweak release" object.
        """
        # TODO: Find a Python-based method to safely delete all DS_Store files.
        call(["find", ".", "-name", ".DS_Store", "-delete"],
             cwd=self.root + "temp/" + bundle_id)  # Remove .DS_Store. Kinda finicky.
        for file_name in os.listdir(self.root + "temp/" + bundle_id):
            if file_name.endswith(".deb"):
                # Check if the DEB is a newer version
                deb = Dpkg(self.root + "temp/" + bundle_id + "/" + file_name)
                if Dpkg.compare_versions(recorded_version, deb.version) == -1:
                    # Update package stuff
                    package_name = PackageLister.BundleIdToDirName(self, bundle_id)
                    with open(self.root + "Packages/" + package_name + "/silica_data/index.json", "r") as content_file:
                        update_json = json.load(content_file)
                        update_json['version'] = deb.version
                        changelog_entry = input("The DEB provided for \"" + update_json['name'] +
                                                "\" has a new version available (" + recorded_version + " -> " +
                                                deb.version + "). What changed in this version?\n(Add multiple lines" +
                                                " by using newline characters [\\n\\n] and use valid Markdown syntax): "
                                                )

                        try:
                            update_json['changelog'].append(
                                {
                                    "version": deb.version,
                                    "changes": changelog_entry
                                }
                            )
                        except Exception:
                            # Make it a list!
                            update_json['changelog'] = []

                            update_json['changelog'].append(
                                {
                                    "version": deb.version,
                                    "changes": changelog_entry
                                }
                            )

                        # A small note: We already created the variables that contain the changelogs and, to
                        # make matters worse, all the web assets. The only way to mitigate this is to re-create the
                        # tweak_release variable again, which wrecks a lot of things (ie runtime).
                        # A Silica rewrite is required to properly fix this bug.
                        print("\nA small warning about adding changelogs mid-run:\n")
                        print("Due to some less-than-ideal design decisions with Silica, for the changelog to show")
                        print("up, you're going to have to run Silica again. Yes, I know this is annoying, and a proper")
                        print("solution is in the works, but the under-the-hood changes that'll be needed to fix")
                        print("it properly would require a rewrite [see issue #22].\n")
                        print("I'm deeply sorry about this.\n    - Shuga.\n")

                        # Get human-readable folder name
                        folder = PackageLister.BundleIdToDirName(self, bundle_id)
                        deb_path = self.root + "Packages/" + folder + "/" + file_name
                        # Extract Control file and scripts from DEB
                        DpkgPy.control_extract(self, deb_path, self.root + "Packages/" + folder +
                                               "/silica_data/scripts/")
                        # Remove the Control; it's not needed.
                        os.remove(self.root + "Packages/" + folder + "/silica_data/scripts/control")
                        if not os.listdir(self.root + "Packages/" + folder + "/silica_data/scripts/"):
                            os.rmdir(self.root + "Packages/" + folder + "/silica_data/scripts/")

                        return_str = json.dumps(update_json)
                        print("Updating package index.json...")
                        PackageLister.CreateFile(self, "Packages/" + package_name +
                                                 "/silica_data/index.json", return_str)
                    pass
                DpkgPy.extract(self, self.root + "temp/" + bundle_id + "/" + file_name, self.root + "temp/" + bundle_id)
                try:
                    os.remove(self.root + "temp/" + bundle_id + "/" + file_name)
                except:
                    pass
                try:
                    os.remove(self.root + "temp/" + bundle_id + "/control")
                except:
                    pass
        else:
            # TODO: Update DpkgPy to generate DEB files without dependencies (for improved win32 support)
            # If the version is consistent, then assume the package is unchanged. Don't regenerate it.
            try:
                # Check for a DEB that already exists.
                docs_deb = Dpkg(self.root + "docs/pkg/" + bundle_id + ".deb")
                if docs_deb.version == recorded_version:
                    shutil.copy(self.root + "docs/pkg/" + bundle_id + ".deb", self.root + "temp/" + bundle_id + ".deb")
                    call_result = 0;
                else:
                    # Sneaky swap.
                    call_result = call(["dpkg-deb", "-b", "-Zgzip", self.root + "temp/" + bundle_id], cwd=self.root + "temp/")  # Compile DEB
            except:
                # Create the DEB again.
                call_result = call(["dpkg-deb", "-b", "-Zgzip", self.root + "temp/" + bundle_id], cwd=self.root + "temp/")  # Compile DEB
            if call_result != 0:
                # Did we run within WSL?
                if "Microsoft" in platform.release():
                    PackageLister.ErrorReporter(self, "Platform Error!", "dpkg-deb failed to run. "
                    "This is likely due to improper configuration of WSL. Please check the Silcia README for "
                    "how to set up WSL for dpkg-deb.")
                else:
                    PackageLister.ErrorReporter(self, "DPKG Error!", "dpkg-deb failed to run. "
                    "This could be due to a faulty system configuration.")

    def CheckForSilicaData(self):
        """
        Ensures that a silica_data file exists and if it doesn't, try to create one with as much data as we have.
        If there is a DEB file, it will take data from its CONTROL file. It will also auto-update the version number.
        If there is no DEB file, it will use the name of the folder, version 1.0.0, try to guess some dependencies,
            and add some placeholder data.
        :return:
        """
        for folder in os.listdir(self.root + "Packages"):
            if folder.lower() != ".ds_store":
                if not os.path.isdir(self.root + "Packages/" + folder + "/silica_data"):
                    print("It seems like the package \"" + folder + "\" is not configured. Let's set it up!")
                    is_deb = False
                    deb_path = ""
                    try:
                        for file_name in os.listdir(self.root + "Packages/" + folder):
                            if file_name.endswith(".deb"):
                                is_deb = True
                                deb_path = self.root + "Packages/" + folder + "/" + file_name
                    except Exception:
                        PackageLister.ErrorReporter(self, "Configuration Error!", "Please put your .deb file inside of "
                            "its own folder. The \"Packages\" directory should be made of multiple folders that each "
                            "contain data for a single package.\n Please fix this issue and try again.")

                    # This will be the default scaffolding for our package. Eventually I'll neuter it to only be the
                    # essential elements; it's also kinda a reference to me.
                    output = {
                        "bundle_id": "co.shuga.silica.unknown",
                        "name": "Unknown Package",
                        "version": "1.0.0",
                        "tagline": "An unknown package.",
                        "homepage": "https://shuga.co/",
                        "developer": {
                            "name": "Unknown",
                            "email": "idk@example.com"
                        },
                        "maintainer": {
                            "name": "Unknown",
                            "email": "idk@example.com"
                        },
                        "section": "Themes",

                        "works_min": "8.0",
                        "works_max": "13.0",
                        "featured": "false"
                    }

                    if is_deb:
                        print("Extracting data from DEB...")
                        deb = Dpkg(deb_path)
                        output['name'] = deb.headers['Name']
                        output['bundle_id'] = deb.headers['Package']
                        try:
                            output['tagline'] = deb.headers['Description']
                        except Exception:
                            output['tagline'] = input("What is a brief description of the package? ")
                        try:
                            output['homepage'] = deb.headers['Homepage']
                        except Exception:
                            pass
                        try:
                            remove_email_regex = re.compile('<.*?>')
                            output['developer']['name'] = remove_email_regex.sub("", deb.headers['Author'])
                        except Exception:
                            output['developer']['name'] = input("Who originally made this package? This may be"
                                                                " your name. ")
                        output['developer']['email'] = input("What is the original author's email address? ")
                        try:
                            remove_email_regex = re.compile('<.*?>')
                            output['maintainer']['name'] = remove_email_regex.sub("", deb.headers['Maintainer'])
                        except Exception:
                            output['maintainer']['name'] = input("Who maintains this package now?"
                                                                 " This is likely your name. ")
                        output['maintainer']['email'] = input("What is the maintainer's email address? ")
                        try:
                            output['sponsor']['name'] = remove_email_regex.sub("", deb.headers['Sponsor'])
                        except Exception:
                            pass
                        try:
                            output['dependencies'] = deb.headers['Depends']
                        except Exception:
                            pass
                        try:
                            output['section'] = deb.headers['Section']
                        except Exception:
                            pass
                        try:
                            output['version'] = deb.headers['Version']
                        except Exception:
                            output['version'] = "1.0.0"
                        try:
                            output['conflicts'] = deb.headers['Conflicts']
                        except Exception:
                            pass
                        try:
                            output['replaces'] = deb.headers['Replaces']
                        except Exception:
                            pass
                        try:
                            output['provides'] = deb.headers['Provides']
                        except Exception:
                            pass
                        try:
                            output['build_depends'] = deb.headers['Build-Depends']
                        except Exception:
                            pass
                        try:
                            output['recommends'] = deb.headers['Recommends']
                        except Exception:
                            pass
                        try:
                            output['suggests'] = deb.headers['Suggests']
                        except Exception:
                            pass
                        try:
                            output['enhances'] = deb.headers['Enhances']
                        except Exception:
                            pass
                        try:
                            output['breaks'] = deb.headers['Breaks']
                        except Exception:
                            pass
                        try:
                            output['tags'] = deb.headers['Tag']
                        except Exception:
                            pass
                        try:
                            output['suggests'] = deb.headers['Suggests']
                        except Exception:
                            pass
                        # These still need data.
                        output['works_min'] = input("What is the lowest iOS version the package works on? ")
                        output['works_max'] = input("What is the highest iOS version the package works on? ")
                        output['featured'] = input("Should this package be featured on your repo? (true/false) ")
                        set_tint = input("What would you like this package's tint color to be? To keep it at"
                                         " the default, leave this blank: ")
                        if set_tint != "":
                            output['tint'] = set_tint
                        print("All done! Please look over the generated \"index.json\" file and consider populating the"
                              " \"silica_data\" folder with a description, screenshots, and an icon.")
                        # Extract Control file and scripts from DEB
                        DpkgPy.control_extract(self, deb_path, self.root + "Packages/" + folder +
                                               "/silica_data/scripts/")
                        # Remove the Control; it's not needed.
                        os.remove(self.root + "Packages/" + folder + "/silica_data/scripts/control")
                        if not os.listdir(self.root + "Packages/" + folder + "/silica_data/scripts/"):
                            os.rmdir(self.root + "Packages/" + folder + "/silica_data/scripts/")
                    else:
                        print("Estimating dependencies...")
                        # Use the filesystem to see if Zeppelin, Anemone, LockGlyph, XenHTML, and similar.
                        # If one of these are found, set it as a dependency.
                        # If multiple of these are found, use a hierarchy system, with Anemone as the highest priority,
                        # for determining the category.
                        output['dependencies'] = ""
                        output['section'] = "Themes"

                        if os.path.isdir(self.root + "Packages/" + folder + "/Library/Zeppelin"):
                            output['section'] = "Themes (Zeppelin)"
                            output['dependencies'] += "com.alexzielenski.zeppelin, "

                        if os.path.isdir(self.root + "Packages/" + folder + "/Library/Application Support/LockGlyph"):
                            output['section'] = "Themes (LockGlyph)"
                            output['dependencies'] += "com.evilgoldfish.lockglypgh, "

                        if os.path.isdir(self.root + "Packages/" + folder + "/var/mobile/Library/iWidgets"):
                            output['section'] = "Widgets"
                            output['dependencies'] += "com.matchstic.xenhtml, "

                        if os.path.isdir(self.root + "Packages/" + folder + "/Library/Wallpaper"):
                            output['section'] = "Wallpapers"

                        if os.path.isdir(self.root + "Packages/" + folder + "/Library/Themes"):
                            output['section'] = "Themes"
                            output['dependencies'] += "com.anemonetheming.anemone, "

                        if output['dependencies'] != "":
                            output['dependencies'] = output['dependencies'][:-2]

                        repo_settings = PackageLister.GetRepoSettings(self)
                        # Ask for name
                        output['name'] = input("What should we name this package? ")
                        # Automatically generate a bundle ID from the package name.
                        domain_breakup = repo_settings['cname'].split(".")[::-1]
                        only_alpha_regex = re.compile('[^a-zA-Z]')
                        machine_safe_name = only_alpha_regex.sub("", output['name']).lower()
                        output['bundle_id'] = ".".join(str(x) for x in domain_breakup) + "." + machine_safe_name
                        output['tagline'] = input("What is a brief description of the package? ")
                        output['homepage'] = "https://" + repo_settings['cname']
                        # I could potentially default this to what is in settings.json but attribution may be an issue.
                        output['developer']['name'] = input("Who made this package? This is likely your name. ")
                        output['developer']['email'] = input("What is the author's email address? ")
                        output['works_min'] = input("What is the lowest iOS version the package works on? ")
                        output['works_max'] = input("What is the highest iOS version the package works on? ")
                        output['featured'] = input("Should this package be featured on your repo? (true/false) ")
                    PackageLister.CreateFolder(self, "Packages/" + folder + "/silica_data/")
                    PackageLister.CreateFile(self, "Packages/" + folder + "/silica_data/index.json", json.dumps(output))

    def CompilePackages(self):
        """
        Creates a Packages.bz2 file.
        """
        # TODO: Update DpkgPy to generate DEB files without dependencies (for improved win32 support)
        call(["dpkg-scanpackages", "-m", "."], cwd=self.root + "docs/", stdout=open(self.root + "docs/Packages", "w"))
        # For this, we're going to have to run it and then get the output. From here, we can make a new file.
        shutil.copy(self.root + "docs/Packages", self.root + "docs/Packages2")
        call(["bzip2", "Packages"], cwd=self.root + "docs/")
        call(["mv", "Packages2", "Packages"], cwd=self.root + "docs/")
        call(["xz", "Packages"], cwd=self.root + "docs/")

    def SignRelease(self):
        """
        Signs Release to create Release.gpg. Also adds hash for Packages.bz2 in Release.
        """
        with open(self.root + "docs/Packages.bz2", "rb") as content_file,\
            open(self.root + "docs/Packages.xz", "rb") as content_file_xz:
            bzip_raw = content_file.read()
            bzip_sha256_hash = hashlib.sha256(bzip_raw).hexdigest()
            bzip_size = os.path.getsize(self.root + "docs/Packages.bz2")
            xz_raw = content_file_xz.read()
            xz_sha256_hash = hashlib.sha256(xz_raw).hexdigest()
            xz_size = os.path.getsize(self.root + "docs/Packages.xz")
            with open(self.root + "docs/Release", "a") as text_file:
                text_file.write("\nSHA256:\n " + str(bzip_sha256_hash) + " " + str(bzip_size) + " Packages.bz2"
                                "\n " + str(xz_sha256_hash) + " " + str(xz_size) + " Packages.xz\n")
                repo_settings = PackageLister.GetRepoSettings(self)
                try:
                    if repo_settings['enable_gpg'].lower() == "true":
                        print("Signing repository with GPG...")
                        key = "Silica MobileAPT Repository"  # Most of the time, this is acceptable.
                        call(["gpg", "-abs", "-u", key, "-o", "Release.gpg", "Release"], cwd=self.root + "docs/")
                        print("Generated Release.gpg!")
                except Exception:
                    pass

    def PushToGit(self):
        """
        Commit and push the repo to a git server (which would likely be GitHub).
        """
        # TODO: use GitPython instead of calling Git directly.
        call(["git", "add", "."], cwd=self.root)
        call(["git", "commit", "-am", "Repo contents updated via Silica"], cwd=self.root)
        call(["git", "push"], cwd=self.root)
