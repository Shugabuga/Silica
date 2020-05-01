#!/usr/bin/env python3

# Import stuff.
import shutil  # Used to copy files
import os  # Used for identifying project root
from pathlib import Path  # Identify if folder exists.
import re  # Regular expressions
import json  # API endpoint generation

# Import Silica classes.
from util.DepictionGenerator import DepictionGenerator
from util.PackageLister import PackageLister
from util.DebianPackager import DebianPackager

version = "1.2.2"


def main():
    print("Silica Compiler {0}".format(version))

    ###########
    # Step 0: Clean up "docs" and "temp" folder
    ###########

    root = os.path.dirname(os.path.abspath(__file__)) + "/"

    # Remove everything except for the DEBs.
    DepictionGenerator.CleanUp()

    try:
        shutil.rmtree(root + "temp/")
    except Exception:
        pass

    ###########
    # Step 1: Generate folders, files, and variables needed (including temp)
    ###########
    PackageLister.CreateFolder("docs")
    PackageLister.CreateFolder("docs/web")
    PackageLister.CreateFolder("docs/depiction")
    PackageLister.CreateFolder("docs/depiction/web")
    PackageLister.CreateFolder("docs/depiction/native")
    PackageLister.CreateFolder("docs/depiction/native/help")
    PackageLister.CreateFolder("docs/pkg")
    PackageLister.CreateFolder("docs/assets")
    PackageLister.CreateFolder("docs/api")

    # Make sure all index.json files are generated (if using DEBs)
    DebianPackager.CheckForSilicaData()

    tweak_release = PackageLister.GetTweakRelease()
    repo_settings = PackageLister.GetRepoSettings()

    # Create folder for each tweak
    for tweak in tweak_release:
        PackageLister.CreateFolder("docs/assets/" + tweak['bundle_id'])

    ###########
    # Step 2: Copy all images
    ###########
    for package_name in PackageLister.ListDirNames():
        package_bundle_id = PackageLister.DirNameToBundleID(package_name)

        try:
            shutil.copy(root + "Packages/" + package_name + "/silica_data/icon.png",
                        root + "docs/assets/" + package_bundle_id + "/icon.png")
        except Exception:
            category = PackageLister.ResolveCategory(tweak_release, package_bundle_id)
            category = re.sub(r'\([^)]*\)', '', category).strip()
            try:
                shutil.copy(root + "Styles/Generic/Icon/" + category + ".png",
                            root + "docs/assets/" + package_bundle_id + "/icon.png")
            except Exception:
                try:
                    shutil.copy(root + "Styles/Generic/Icon/Generic.png",
                                root + "docs/assets/" + package_bundle_id + "/icon.png")
                except Exception:
                    PackageLister.ErrorReporter("Configuration Error!", "You are missing a file at " + root +
                        "Styles/Generic/Icon/Generic.png. Please place an icon here to be the repo's default.")

        try:
            shutil.copy(root + "Packages/" + package_name + "/silica_data/banner.png",
                        root + "docs/assets/" + package_bundle_id + "/banner.png")
        except Exception:
            category = PackageLister.ResolveCategory(tweak_release, package_bundle_id)
            category = re.sub(r'\([^)]*\)', '', category).strip()
            try:
                shutil.copy(root + "Styles/Generic/Banner/" + category + ".png",
                            root + "docs/assets/" + package_bundle_id + "/banner.png")
            except Exception:
                try:
                    shutil.copy(root + "Styles/Generic/Banner/Generic.png",
                               root + "docs/assets/" + package_bundle_id + "/banner.png")
                except Exception:
                    PackageLister.ErrorReporter("Configuration Error!", "You are missing a file at " + root +
                        "Styles/Generic/Banner/Generic.png. Please place a banner here to be the repo's default.")

        try:
            shutil.copy(root + "Packages/" + package_name + "/silica_data/description.md",
                        root + "docs/assets/" + package_bundle_id + "/description.md")
        except Exception:
            pass

        try:
            shutil.copytree(root + "Packages/" + package_name + "/silica_data/screenshots",
                            root + "docs/assets/" + package_bundle_id + "/screenshot")
        except Exception:
            pass
    try:
        shutil.copy(root + "Styles/icon.png", root + "docs/CydiaIcon.png")
    except Exception:
        PackageLister.ErrorReporter("Configuration Error!", "You are missing a file at " + root + "Styles/icon.png. "
            "Please add a PNG here to act as the repo's icon.")

    ###########
    # Step 3: Generate HTML depictions and copy stylesheet
    ###########

    # Copy CSS and JS over
    shutil.copy(root + "Styles/index.css", root + "docs/web/index.css")
    shutil.copy(root + "Styles/index.js", root + "docs/web/index.js")

    # Generate index.html
    index_html = DepictionGenerator.RenderIndexHTML()
    PackageLister.CreateFile("docs/index.html", index_html)
    PackageLister.CreateFile("docs/404.html", index_html)

    # Generate per-tweak depictions
    for tweak_data in tweak_release:
        tweak_html = DepictionGenerator.RenderPackageHTML(tweak_data)
        PackageLister.CreateFile("docs/depiction/web/" + tweak_data['bundle_id'] + ".html", tweak_html)

    if "github.io" not in repo_settings['cname'].lower():
        PackageLister.CreateFile("docs/CNAME", repo_settings['cname'])

    ###########
    # Step 4: Generate Sileo depictions and featured JSON
    ###########

    # Generate sileo-featured.json
    carousel_obj = DepictionGenerator.NativeFeaturedCarousel(tweak_release)
    PackageLister.CreateFile("docs/sileo-featured.json", carousel_obj)

    # Generate per-tweak depictions
    for tweak_data in tweak_release:
        tweak_json = DepictionGenerator.RenderPackageNative(tweak_data)
        PackageLister.CreateFile("docs/depiction/native/" + tweak_data['bundle_id'] + ".json", tweak_json)
        help_depiction = DepictionGenerator.RenderNativeHelp(tweak_data)
        PackageLister.CreateFile("docs/depiction/native/help/" + tweak_data['bundle_id'] + ".json", help_depiction)

    ###########
    # Step 5: Generate Release file from settings.json.
    ###########

    release_file = DebianPackager.CompileRelease(repo_settings)
    PackageLister.CreateFile("docs/Release", release_file)

    ###########
    # Step 6: Copy packages to temp
    ###########

    # You should remove .DS_Store files AFTER copying to temp.
    PackageLister.CreateFolder("temp")
    for package_name in PackageLister.ListDirNames():
        bundle_id = PackageLister.DirNameToBundleID(package_name)
        try:
            shutil.copytree(root + "Packages/" + package_name, root + "temp/" + bundle_id)
            shutil.rmtree(root + "temp/" + bundle_id + "/silica_data")
        except Exception:
            try:
                shutil.rmtree(root + "temp/" + bundle_id + "/silica_data")
            except Exception:
                pass

        script_check = Path(root + "Packages/" + package_name + "/silica_data/scripts/")
        if script_check.is_dir():
            shutil.copytree(root + "Packages/" + package_name + "/silica_data/scripts", root + "temp/" + bundle_id
                            + "/DEBIAN")
        else:
            PackageLister.CreateFolder("temp/" + bundle_id + "/DEBIAN")

    ###########
    # Step 7: Generate CONTROL and DEB files and move them to docs/
    ###########

    for tweak_data in tweak_release:
        control_file = DebianPackager.CompileControl(tweak_data, repo_settings)
        PackageLister.CreateFile("temp/" + tweak_data['bundle_id'] + "/DEBIAN/control", control_file)
        DebianPackager.CreateDEB(tweak_data['bundle_id'], tweak_data['version'])
        shutil.copy(root + "temp/" + tweak_data['bundle_id'] + ".deb", root + "docs/pkg/" + tweak_data['bundle_id']
                    + ".deb")

    ###########
    # Step 8: Generate Package file and hash/sign the Release file.
    ###########

    DebianPackager.CompilePackages()
    DebianPackager.SignRelease()

    ###########
    # Step 9: Make API endpoints
    ###########

    PackageLister.CreateFile("docs/api/tweak_release.json", json.dumps(tweak_release, separators=(',', ':')))
    PackageLister.CreateFile("docs/api/repo_settings.json", json.dumps(repo_settings, separators=(',', ':')))
    PackageLister.CreateFile("docs/api/about.json", json.dumps(DepictionGenerator.SilicaAbout(), separators=(',', ':')))

    ###########
    # Step 10: Push to GitHub
    ###########

    shutil.rmtree(root + "temp/")  # Clean-up the now-unneeded temp folder.

    try:
        if repo_settings['automatic_git'].lower() == "true":
            DebianPackager.PushToGit()  # Push the repo to GitHub automatically.
    except Exception:
        pass


if __name__ == '__main__':
    DepictionGenerator = DepictionGenerator(version)
    PackageLister = PackageLister(version)
    DebianPackager = DebianPackager(version)
    main()
