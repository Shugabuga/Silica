import pystache  # Used for templating of HTML files
import json  # Used to parse various JSON files
import datetime  # For getting the compile date
import os  # For file path correction
import mistune  # Markdown parser
import random  # If no packages are featured, feature a random one.
from subprocess import check_output  # Get upstream URL for API
from util.PackageLister import PackageLister


class DepictionGenerator:
    """
    DepictionGenerator deals with the rendering and generating of depictions.

    """

    def __init__(self, version):
        super(DepictionGenerator, self).__init__()
        self.version = version
        self.root = os.path.dirname(os.path.abspath(__file__)) + "/../"
        self.PackageLister = PackageLister(self.version)

    def CleanUp(self):
        """
        Cleans up some stuff.
        """
        # Remove all Silica-generated folders in docs/ except for docs/pkg/.
        try:
            shutil.rmtree(root + "docs/api")
        except Exception:
            pass

        try:
            shutil.rmtree(root + "docs/assets")
        except Exception:
            pass

        try:
            shutil.rmtree(root + "docs/depiction")
        except Exception:
            pass

        try:
            shutil.rmtree(root + "docs/web")
        except Exception:
            pass

        # Delete all Silica-generated files in root.
        try:
            os.remove(self.root + "docs/404.html")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/CNAME")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/CydiaIcon.png")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/index.html")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/Packages")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/Packages.bz2")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/Packages.xz")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/Release")
        except Exception:
            pass
        try:
            os.remove(self.root + "docs/sileo-featured.json")
        except Exception:
            pass

        # Clean up temp.
        try:
            shutil.rmtree(root + "temp/")
        except Exception:
            pass

    def RenderPackageHTML(self, tweak_data):
        """
        Renders a package's depiction.

        Object tweak_data: A single index of a "tweak release" object.
        """
        with open(self.root + "Styles/tweak.mustache", "r") as content_file:
            index = content_file.read()
            replacements = DepictionGenerator.RenderDataHTML(self)
            try:
                replacements['tweak_name'] = tweak_data['name']
            except:
                 PackageLister.ErrorReporter(self, "Configuration Error!", "You are missing a package "
                    "name in its index.json. Make sure this and other required properties are set.")
            try:
                replacements['tweak_developer'] = tweak_data['developer']['name']
                replacements['tweak_compatibility'] = "iOS " + tweak_data['works_min'] + " to " + tweak_data['works_max']
                replacements['tweak_version'] = tweak_data['version']
                replacements['tweak_section'] = tweak_data['section']
                replacements['tweak_bundle_id'] = tweak_data['bundle_id']
                replacements['works_min'] = tweak_data['works_min']
                replacements['works_max'] = tweak_data['works_max']
                replacements['tweak_tagline'] = tweak_data['tagline']
            except:
                PackageLister.ErrorReporter(self, "Configuration Error!", "You are missing an essential "
                    "property in " + tweak_data['name'] + "'s index.json. Make sure developer, version, section, "
                    "bundle id, and tagline are set properly.")
            replacements['tweak_carousel'] = DepictionGenerator.ScreenshotCarousel(self, tweak_data)
            replacements['tweak_changelog'] = DepictionGenerator.RenderChangelogHTML(self, tweak_data)
            replacements['footer'] = DepictionGenerator.RenderFooter(self)
            try:
                if tweak_data['source'] != "":
                    replacements['source'] = tweak_data['source']
            except Exception:
                pass

            try:
                replacements['tint_color'] = tweak_data['tint']
            except Exception:
                try:
                    repo_settings = PackageLister.GetRepoSettings(self)
                    replacements['tint_color'] = repo_settings['tint']
                except Exception:
                    replacements['tint_color'] = "#2cb1be"

            try:
                with open(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/description.md", "r") as md_file:
                    raw_md = md_file.read()
                    desc_md = mistune.markdown(raw_md)
                    replacements['tweak_description'] = desc_md
            except Exception:
                replacements['tweak_description'] = tweak_data['tagline']

            # tweak_carousel

            return pystache.render(index, replacements)

    def RenderPackageNative(self, tweak_data):
        """
        Renders a package's depiction using Sileo's "native depiction" format.

        Object tweak_data: A single index of a "tweak release" object.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        try:
            tint = tweak_data['tint']
        except Exception:
            try:
                tint = repo_settings['tint']
            except Exception:
                tint = "#2cb1be"

        try:
            with open(self.root + "docs/assets/" + tweak_data['bundle_id'] + "/description.md", "r") as md_file:
                md_txt = md_file.read()
        except Exception:
            md_txt = tweak_data['tagline']

        date = datetime.datetime.now().strftime("%Y-%m-%d")

        screenshot_obj = []
        image_list = self.PackageLister.GetScreenshots(tweak_data)
        subfolder = PackageLister.FullPathCname(self, repo_settings)
        if len(image_list) > 0:
            for image in image_list:
                screenshot_entry = {
                    "url": "https://" + repo_settings['cname'] + subfolder + "/assets/" + tweak_data['bundle_id'] + "/screenshot/"
                           + image,
                    "accessibilityText": "Screenshot"
                }
                screenshot_obj.append(screenshot_entry)
            # The following code is evil, but is actually easier to maintain. My humblest apologies.
            screenshot_view_title = "DepictionHeaderView"
            screenshot_view_carousel = "DepictionScreenshotsView"
        else:
            # The following code is evil, but is actually easier to maintain. My humblest apologies.
            screenshot_view_title = "HiddenDepictionHeaderView"
            screenshot_view_carousel = "HiddenDepictionScreenshotsView"

        changelog = DepictionGenerator.RenderNativeChangelog(self, tweak_data)
        screenshot_size = PackageLister.GetScreenshotSize(self, tweak_data)

        depiction = {
            "minVersion": "0.1",
            "headerImage": "https://" + repo_settings['cname'] + subfolder + "/assets/" + tweak_data['bundle_id'] + "/banner.png",
            "tintColor": tint,
            "tabs": [
                {
                    "tabname": "Details",
                    "views": [
                        {
                            "class": screenshot_view_carousel,
                            "screenshots": screenshot_obj,
                            "itemCornerRadius": 8,
                            "itemSize": screenshot_size
                        },
                        {
                            "markdown": md_txt,
                            "useSpacing": "true",
                            "class": "DepictionMarkdownView"
                        },
                        {
                            "class": "DepictionSpacerView"
                        },
                        {
                            "class": "DepictionHeaderView",
                            "title": "Information",
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "Developer",
                            "text": tweak_data['developer']['name']
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "Version",
                            "text": tweak_data['version']
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "Compatibility",
                            "text": "iOS " + tweak_data['works_min'] + " to " + tweak_data['works_max']
                        },
                        {
                            "class": "DepictionTableTextView",
                            "title": "Section",
                            "text": tweak_data['section']
                        },
                        {
                            "class": "DepictionSpacerView"
                        },
                        {
                            "class": "DepictionTableButtonView",
                            "title": "Contact Support",
                            "action": "depiction-https://" + repo_settings['cname'] + subfolder +
                                      "/depiction/native/help/" + tweak_data['bundle_id'] + ".json",
                            "openExternal": "true",
                            "tintColor": tint
                        },
                        {
                            "class": "DepictionLabelView",
                            "text": DepictionGenerator.RenderFooter(self),
                            "textColor": "#999999",
                            "fontSize": "10.0",
                            "alignment": 1
                        }
                    ],
                    "class": "DepictionStackView"
                },
                {
                    "tabname": "Changelog",
                    "views": changelog,
                    "class": "DepictionStackView"
                }
            ],
            "class": "DepictionTabView"
        }

        blank = {
                    "class": "DepictionSpacerView"
                }

        try:
            if tweak_data['source'] != "":
                source_btn = {
                                "class": "DepictionTableButtonView",
                                "title": "View Source Code",
                                "action": tweak_data['source'],
                                "openExternal": "true",
                                "tintColor": tint
                            }
                depiction['tabs'][0]['views'].insert(8, source_btn)
                depiction['tabs'][0]['views'].insert(8, blank)
                pass
        except Exception:
            pass

        return json.dumps(depiction, separators=(',', ':'))

    def RenderNativeChangelog(self, tweak_data):
        """
        Generates a changelog for use in native depictions.

        Object tweak_data: A single index of a "tweak release" object.
        """
        try:
            changelog = []
            for version in tweak_data['changelog'][::-1]:
                ver_entry = {
                    "class": "DepictionMarkdownView",
                    "markdown": "#### Version {0}\n\n{1}".format(version['version'], version['changes']),
                }
                changelog.append(ver_entry)
            changelog.append({
                            "class": "DepictionLabelView",
                            "text": DepictionGenerator.RenderFooter(self),
                            "textColor": "#999999",
                            "fontSize": "10.0",
                            "alignment": 1
            })
            return changelog
        except Exception:
            return [
                {
                    "class": "DepictionHeaderView",
                    "title": "Changelog"
                },
                {
                    "class": "DepictionMarkdownView",
                    "markdown": "This package has no changelog.",
                },
                {
                    "class": "DepictionLabelView",
                    "text": DepictionGenerator.RenderFooter(self),
                    "textColor": "#999999",
                    "fontSize": "10.0",
                    "alignment": 1
                }
            ]

    def ChangelogEntry(self, version, raw_md):
        """
        Generates a div for changelog entries.

        String version: The version number.
        String raw_md: The changelog entry text (Markdown-compatible).
        """
        return '''<div class="changelog_entry">
                <h4>{0}</h4>
                <div class="md_view">{1}</div>
            </div>'''.format(version, mistune.markdown(raw_md))

    def RenderChangelogHTML(self, tweak_data):
        """
        Generates a div of changelog entries.

        Object tweak_data: A single index of a "tweak release" object.
        """
        element = ""
        try:
            for version in tweak_data['changelog'][::-1]:
                element += DepictionGenerator.ChangelogEntry(self, version['version'], version['changes'])
            return element
        except Exception:
            return "This package has no changelog."

    def RenderIndexHTML(self):
        """
        Renders the home page (index.html).
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        with open(self.root + "Styles/index.mustache", "r") as content_file:
            index = content_file.read()
            replacements = DepictionGenerator.RenderDataHTML(self)
            replacements['tint_color'] = repo_settings['tint']
            replacements['footer'] = DepictionGenerator.RenderFooter(self)
            replacements['tweak_release'] = PackageLister.GetTweakRelease(self)
            return pystache.render(index, replacements)

    def RenderFooter(self):
        """
        Renders the footer.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        data = DepictionGenerator.RenderDataHTML(self)
        try:
            footer = pystache.render(repo_settings['footer'], data)
        except Exception:
            footer = pystache.render("Silica {{silica_version}} – Updated {{silica_compile_date}}", data)
        return footer

    def RenderDataBasic(self):
        """
        Gets the value of basic repo data to pass to Pystache.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        with open(self.root + "Styles/settings.json", "r") as content_file:
            data = json.load(content_file)
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            subfolder = PackageLister.FullPathCname(self, repo_settings)
            return {
                "silica_version": self.version,
                "silica_compile_date": date,
                "repo_name": data['name'],
                "repo_url": data['cname'] + subfolder,
                "repo_desc": data['description'],
                "repo_tint": data['tint']
            }

    def RenderDataHTML(self):
        data = DepictionGenerator.RenderDataBasic(self)

        tweak_release = PackageLister.GetTweakRelease(self)

        data['repo_packages'] = DepictionGenerator.PackageEntryList(self, tweak_release)

        data['repo_carousel'] = DepictionGenerator.CarouselEntryList(self, tweak_release)

        return data

    def PackageEntry(self, name, author, icon, bundle_id):
        """
        Generates a package entry div.

        String name: The package's name
        String author: The author's name
        String (URL) icon: A URL to an image of the package icon.

        Scope: HTML > Generation > Helpers
        """

        if (bundle_id != "silica_do_not_hyperlink"):
            return '''<a class="subtle_link" href="depiction/web/{3}.html"><div class="package">
            <img src="{0}">
            <div class="package_info">
                <p class="package_name">{1}</p>
                <p class="package_caption">{2}</p>
            </div>
        </div></a>'''.format(icon, name, author, bundle_id)
        else:
            return '''<div class="package">
                <img src="{0}">
                <div class="package_info">
                    <p class="package_name">{1}</p>
                    <p class="package_caption">{2}</p>
                </div>
            </div>'''.format(icon, name, author)

    def ScreenshotCarousel(self, tweak_data):
        """
        Generates a screenshot div.

        Object tweak_data: A single index of a "tweak release" object.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        screenshot_div = "<div class=\"scroll_view\">"
        image_list = self.PackageLister.GetScreenshots(tweak_data)
        if (len(image_list) > 0):
            for image in image_list:
                screenshot_div += '''<img class="img_card" src="../../assets/{1}/screenshot/{2}">'''.format(
                    repo_settings['cname'], tweak_data['bundle_id'], image)
            screenshot_div += "</div>"
        else:
            screenshot_div = ""
        return screenshot_div

    def CarouselEntry(self, name, banner, bundle_id):
        """
        Generates a card to be used in Featured carousels.

        String name: The package's name
        String (URL) banner: A URL to an image of the package banner.
        """
        if len(name) > 18:
            name = name[:18] + "…"
        return '''<a href="depiction/web/{0}.html" style="background-image: url({1})" class="card">
                <p>{2}</p>
            </a>'''.format(bundle_id, banner, name)

    def NativeFeaturedCarousel(self, tweak_release):
        """
        Generate a sileo-featured.json file for featured packages.

        Object carousel_entry_list: A "tweak release" object.
        """
        repo_settings = PackageLister.GetRepoSettings(self)
        subfolder = PackageLister.FullPathCname(self, repo_settings)
        banners = []
        for package in tweak_release:
            try:
                if package['featured'].lower() == "true":
                    ar_el = {
                        "package": package['bundle_id'],
                        "title": package['name'],
                        "url": "https://" + repo_settings['cname'] + subfolder + "/assets/" + package['bundle_id'] + "/banner.png",
                        "hideShadow": "false"

                    }
                    banners.append(ar_el)
            except Exception:
                pass
        if len(banners) == 0:
            try:
                featured_int = random.randint(0,(len(tweak_release)-1))
            except Exception:
                PackageLister.ErrorReporter(self, "Configuration Error!", "You have no packages added to this repo. "
                      "Make sure a folder is created at \"" + self.version + "/Packages\" that contains folders with "
                      "package data inside of them and run Silica again.")
            featured_package = tweak_release[featured_int]
            ar_el = {
                "package": featured_package['bundle_id'],
                "title": featured_package['name'],
                "url": "https://" + repo_settings['cname'] + subfolder + "/assets/" + featured_package['bundle_id'] + "/banner.png",
                "hideShadow": "false"

            }
            banners.append(ar_el)

        featured_json = {
            "class": "FeaturedBannersView",
            "itemSize": "{263, 148}",
            "itemCornerRadius": 8,
            "banners": banners
        }
        return json.dumps(featured_json, separators=(',', ':'))

    def PackageEntryList(self, tweak_release):
        """
        Generate a user-friendly list of packages on the repo.

        Object tweak_release: A "tweak release" object.
        """
        list_el = ""
        for package in tweak_release:
            list_el += DepictionGenerator.PackageEntry(self, package['name'], package['developer']['name'],
                                                       "assets/" + package['bundle_id'] + "/icon.png",
                                                       package['bundle_id'])
        return list_el

    def CarouselEntryList(self, tweak_release):
        """
        Generate a carousel of featured packages on the repo.

        Object tweak_release: A "tweak release" object.
        """
        list_el = ""
        for package in tweak_release:
            try:
                if package['featured'].lower() == "true":
                    list_el += DepictionGenerator.CarouselEntry(self, package['name'],
                                                                "assets/" + package['bundle_id'] + "/banner.png",
                                                                package['bundle_id'])
            except Exception:
                pass
        if list_el == "":
            try:
                featured_int = random.randint(0,(len(tweak_release)-1))
            except Exception:
                PackageLister.ErrorReporter(self, "Configuration Error!", "You have no packages added to this repo."
                    " Make sure a folder is created at \"" + self.version +
                    "/Packages\" that contains folders with package data inside of them and run Silica again.")

            featured_package = tweak_release[featured_int]
            list_el += DepictionGenerator.CarouselEntry(self, featured_package['name'],
                                                        "assets/" + featured_package['bundle_id'] + "/banner.png",
                                                        featured_package['bundle_id'])
        return list_el

    def SilicaAbout(self):
        """
        Returns a JSON object that describes information about the Silica install.
        """

        compile_date = datetime.datetime.now().isoformat()
        try:
            upstream_url = check_output(["git", "config", "--get", "remote.origin.url"], cwd=self.root).decode("utf-8")
        except Exception:
            upstream_url = "undefined"
        return {
            "software": "Silica",
            "version": self.version,
            "compile_date": compile_date,
            "upstream_url": upstream_url
        }

    def RenderNativeHelp(self, tweak_data):
        """
        Generates a help view for Sileo users.

        Object tweak_data: A single index of a "tweak release" object.
        """

        repo_settings = PackageLister.GetRepoSettings(self)

        try:
            tint = tweak_data['tint']
        except Exception:
            try:
                tint = repo_settings['tint']
            except Exception:
                tint = "#2cb1be"

        view = []
        try:
            if tweak_data['developer']['email']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "If you need help with \"" + tweak_data['name'] + "\", you can contact "
                                    + tweak_data['developer']['name'] + ", the developer, via e-mail."
                    }
                )
                view.append(
                    {
                        "class": "DepictionTableButtonView",
                        "title": "Email Developer",
                        "action": "mailto:" + tweak_data['developer']['email'],
                        "openExternal": "true",
                        "tintColor": tint
                    }
                )
        except Exception:
            try:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "If you need help with \"" + tweak_data['name'] + "\", you can contact "
                                    + tweak_data['developer']['name']
                                    + ", who is the developer. Sadly, we don't know their email."
                    }
                )
            except Exception:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "The developer of the package \"" + tweak_data['name']
                                    + "\" is not known. Try contacting the repo owner for more information."
                    }
                )

        try:
            if tweak_data['social']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "You can also contact " + tweak_data['developer']['name'] + " using the following" +
                        " sites:"
                    }
                )
                for entry in tweak_data['social']:
                    view.append({
                        "class": "DepictionTableButtonView",
                        "title": entry['name'],
                        "action": entry['url'],
                        "openExternal": "true",
                        "tintColor": tint
                    })
        except Exception:
            pass

        try:
            if tweak_data['maintainer']['email']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": tweak_data['maintainer']['name'] + " is the maintainer of the package \"" +
                                    tweak_data['name'] + "\". Please contact them via email for any questions on this"
                                    " version of the package."
                    }
                )
                view.append(
                    {
                        "class": "DepictionTableButtonView",
                        "title": "Email Maintainer",
                        "action": "mailto:" + tweak_data['maintainer']['email'],
                        "openExternal": "true",
                        "tintColor": tint
                    }
                )
        except Exception:
            try:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "If you need help with \"" + tweak_data['name'] + "\", you should contact "
                                    + tweak_data['maintainer']['name']
                                    + ", who is the package's current maintainer. Sadly, we don't know their email."
                    }
                )
            except Exception:
                pass

        view.append(
            {
                "class": "DepictionMarkdownView",
                "markdown": "If you found a mistake in the depiction or cannot download the package, you can reach out"
                            + " to the maintainer of the \"" + repo_settings['name'] + "\" repo, "
                            + repo_settings['maintainer']['name'] + "."
            }
        )
        view.append(
            {
                "class": "DepictionTableButtonView",
                "title": "Email Repo Maintainer",
                "action": "mailto:" + repo_settings['maintainer']['email'],
                "openExternal": "true",
                "tintColor": tint
            }
        )

        try:
            if repo_settings['social']:
                view.append(
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": "You can also contact the repo owner via the following" +
                        " sites:"
                    }
                )
                for entry in repo_settings['social']:
                    view.append({
                        "class": "DepictionTableButtonView",
                        "title": entry['name'],
                        "action": entry['url'],
                        "openExternal": "true",
                        "tintColor": tint
                    })
        except Exception:
            pass

        return json.dumps({
            "class": "DepictionStackView",
            "tintColor": tint,
            "title": "Contact Support",
            "views": view
        }, separators=(',', ':'))
