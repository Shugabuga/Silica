# Silica

**Silica** is a static repo generator for jailbroken iOS devices developed by [Shuga](https://shuga.co) and supported by [Ignition](https://ignition.fun).

The goal behind Silica is simple: make it as easy as possible to make a personal repo that plays nicely with both Cydia and Sileo. Silica generates "static" repos, allowing for repos to be hosted on GitHub Pages for free.

## Getting Started

Silica, by default, is relatively straight-forward to configure. This tutorial is going to assume that you have the following already installed on your machine:
- [Python 3](https://www.python.org/downloads/release/python-373/) (to run Silica)
- `pip3` (for installing Python dependencies)
- [Homebrew](https://brew.sh/) (macOS users only)

Silica is only officially supported on macOS and Debian-based OSes at the moment. We can not guarantee Windows support at this time. I'm sure you could get this working on other Linux distributions with a bit of tweaking, too. `btw i don't use arch`

### Silica for Windows Subsystem for Linux (WSL)

**If you are not using Windows, skip down to Dependencies.**

Due to Silica requiring dpkg-deb to properly work, you cannot run Silica in native Windows.
As a result, you need to set your machine up WSL and Ubuntu for Windows, which will allow for Linux
programs to run in Windows via a terminal.

#### 1. Set up WSL
Please follow [this official tutorial](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Please use Ubuntu for ideal results.

#### 2. Setting up WSL for `dpkg-deb`
Due to how `dpkg-deb` handles permissions, we need to change some settings to make things work.

1. Run `sudo nano /etc/wsl.conf` to edit the WSL config.
2. Copy and paste the following text into the file.

```ini
[automount]
enabled = true
root = /mnt/
options = "umask=22,fmask=11"
```

3. Run the following command to update your `umask` to `0022`.
```bash
echo "\numask 0022" >> ~/.bashrc
```

4. Open up Windows PowerShell as an administrator by right-clicking on the Windows button.

5. Run this command to restart WSL:

```powershell
Get-Service LxssManager | Restart-Service
```

(Note: Please always run Silica through the Ubuntu program or Windows Terminal.)

*(Tip courtesy of [/u/zoredache on Reddit](https://www.reddit.com/r/bashonubuntuonwindows/comments/a7v5d8/problems_with_dpkgdeb_bad_permissions_how_do_i/).)*

##### 3. Install dependencies

Like any Debian-based system (like Ubuntu), we need to install some dependencies before downloading Silica.

```bash
apt-get install gnupg
apt-get install git
```

##### 3. Getting Silica

Now it's time to get Silica! Because of how Windows deals with line breaks, we need to download Silica via Git.
If you already downloaded Silica via your web browser, delete it. We'll redownload it in a second.

Once you are in the directory you want to download Silica to, run this command:

```bash
git clone https://github.com/Shugabuga/Silica/
```

This will create a new folder for Silica.

##### 4. Text Editors and line breaks

Due to how Windows deals with line breaks, if you wish to create Silica config files by hand, you need to make sure
your text editor uses Unix line breaks. This varies by text editor and IDE, so look for a setting about line breaks
or EOL characters and set it to Unix.


**From here, you're all set** for Windows-specific instructions! Now follow the Debian instructions.

### Dependencies

We know that some developers will already have these dependencies installed. If you know you already have a dependency, there is no need to re-install it.

macOS users are going to want to install a couple of packages. To do so, run these commands in Terminal:
```bash
brew install dpkg
brew install gnupg
```

Users of Debian or its derivatives (like Ubuntu) need to run the following commands *as root* to install needed dependencies:
```bash
apt-get install gnupg
apt-get install git
```

We also use `find`, `bzip2`, and `xz`, but most people have these installed by default.

(Windows Subsystem for Linux users already did this step.)

### Other Dependencies and Settings

Now that any needed system dependencies are installed, we need to install some Python dependencies and configure `settings.json`. Thankfully, the included `setup.sh` script handles this for you!

Run the following command and follow the on-screen prompts to set up Silica's core settings, including setting the repo name, default tint color, and whether it should automatically run Git when it finishes updating your repo. This script will also generate a key to sign the `Release.gpg` file which will be stored in your keyring.
```bash
./setup.sh
```

If this doesn't work, make sure the the file is set as an executable by running `chmod +x setup.sh`.

The settings you input during the installation process can be later modified in the `Styles/settings.json` file.

### Customization

Most users would like to customize their repos to fit their needs. Everything you need to do this is in the `Styles` folder.

- `index.mustache` is the template file of the repo's main web page.
- `tweak.mustache` is the template file of the web depictions of the tweaks.
- `index.css` is a CSS file that is applied to every web page generated by Silica.
- `index.js` is a JavaScript file that handles version detection and tab switching on web depictions.
- `settings.json` is auto-generated by the setup script, but you can edit it to change your repo's name, description, default tint color, and more.
- `icon.png` is the repo's icon as it will display in Cydia and Sileo.
- The `Generic` folder includes default image assets.

#### Image Assets

All Silica image assets are `.png` files.

- The `Generic` folder, which contains a `Banner` and `Icon` folder, includes default assets for when a package lacks a banner or an icon. These are named after the package's section. If a section does not have its own image, it will use whatever is stored in `Generic.png`.
- `icon.png` is your repo's icon as displayed in Sileo and Cydia.

### Adding Packages

Silica's `Packages` folder includes all the packages that will live on your repo. A folder in `Packages` represents an individual tweak. The name of the folder does not matter and changing it does nothing; Silica references packages via their "bundle id."

Inside of a tweak or theme's folder should include a `silica_data` folder (which will be elaborated on later on) and either a .deb file (useful for tweak developers) or the hierarchy of the generated package (the latter which is useful for theme designers). If a .deb file is present, it will take precedence.

The directory tree should look similar to the following. **Please note how that the .deb file is in its own folder *inside* of `Packages`.**:

```
Packages
    My Tweak
        tweak.deb
        silica_data
            index.json
            description.md
            icon.png
            banner.png
            screenshots
                01.png
                02.png
                a_screenshot.png
            scripts
                prerm
                extrainst_
    My Theme
        Library
            Themes
                MyTheme.theme
                    IconBundles
                        com.anemonetheming.anemone-large.png
        silica_data
            index.json
            description.md
            icon.png
            banner.png
            screenshots
                01.png
                02.png
                a_screenshot.png
```

#### `silica_data`

The `silica_data` folder is where the icon, description, screenshot, and other package (tweak/theme) information live. This package is *not* put in the final package file (the ".deb" file). The following files and folders can go in this folder:

- `index.json` is the only required file. It is a JSON file including information such as the bundle ID, a short tagline description, version compatibility, developer information, changelog data, and more. This file is generated by Silica using user input if it does not exist. More information on this file is in the **Documentation** section of this document.
- `description.md` is a Markdown file that houses the package's description.
- `icon.png` is the package's icon as it appears in depictions and in Sileo. It should be a square PNG file.
- `banner.png` is the package's banner as it appears in depictions and in Sileo. It should be a rectangular PNG file.
- The `screenshots` folder houses any screenshots you want to be displayed alongside the package.
- The `scripts` folder include any pre/post-installation scripts. The contents of this folder will be placed in the package's `DEBIAN` folder.

The `index.json` file, if missing, will be generated when running Silica.

### Generating a Repo

Once everything is configured as you wish, run the following command to "compile" your repo.

```bash
python3 index.py
```

From here, Silica will automatically generate a repo and put the output in the `docs` folder. If a package does not have a `silica_data` file, you will be asked some information to help automatically generate it.

From here, a service such as [GitHub Pages](https://pages.github.com) can be used to host the repo for free.

### Hosting with GitHub Pages

Silica is designed to be used with [GitHub Pages](https://pages.github.com), allowing you to operate a repo for free.

There are multiple ways to go about this, but this method is recommended for those who are totally unfamiliar with `git` (if you can get `git` up  and running, please use that).

1. [Create a GitHub account.](https://github.com/join?source=silica-readme)
2. [Create a new repository.](https://github.com/new) Initialize it with a README.
3. Drag-and-drop all of the contents of the `docs` directory to the newly-created repository.
4. Type something in the text box and click the "Commit Changes" button.
5. Go to your repository's settings and scroll down to the GitHub Pages section.
6. Set "Source" from "None" to "master branch."
7. Follow [these steps](https://help.github.com/en/articles/using-a-custom-domain-with-github-pages) to configure your domain with GitHub Pages

From there, you should be done! Your compiled repo's "source" will have to be publicly viewable if you don't have a Pro account, but that shouldn't matter too much if you only upload the `docs` folder to GitHub.

If you happen to have `git` installed on your computer and run `git clone https://github.com/your_username/repository_name/`, you can use  "master branch /docs folder" as the site source and Silica's automatic Git pushing feature to automate the uploading process. This is recommended if you happen to have a GitHub Pro account.

## Documentation

### `index.json`
Here is a comprehensive example of an `index.json` file. These reside in the package's `silica_data` folder and is required for the repo to properly compile. You **must** include the `bundle_id`, `name`, `version`, `tagline`, `section`, and `works_min`. All other values are optional, but are recommended (if applicable).

```json
{
    "bundle_id": "co.shuga.elementary-lite",
    "name": "Elementary Lite",
    "version": "1.1.2-beta",
    "tagline": "A simplistic, glyph-based theme.",
    "homepage": "https://shuga.co/repo",
    "developer": {
        "name": "Shuga",
        "email": "sileo@shuga.co"
    },
    "maintainer": {
        "name": "Shuga",
        "email": "sileo@shuga.co"
    },
    "social": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HeyItsShuga"
        },
        {
            "name": "Website",
            "url": "https://shuga.co/"
        }
    ],
    "sponsor": {
        "name": "Shuga Studios",
        "email": "studios@shuga.co"
    },
    "section": "Themes",
    "pre_dependencies": "",
    "dependencies": "com.anemonetheming.anemone",
    "conflicts": "",
    "replaces": "",
    "provides": "",
    "other_control": ["Tag: role::enduser", "SomeOtherEntryToControl: True"],

    "tint": "#55c6d3",
    "works_min": "8.0",
    "works_max": "13.0",
    "featured": "true",
    "source": "https://github.com/Shugabuga/Silica",
    "changelog": [
        {
            "version": "1.1.2-beta",
            "changes": "Thank you for participating in the Elementary beta! All future updates will be given a descriptive changelog with a list of changes."
        }
    ]
}
```

### `settings.json`

The `settings.json` file, located in the `Styles` folder, let you configure Silica as a while. Everything in this file is required except for `subfolder`, `social`, `footer`, and `enable_pgp`.

```json
{
    "name": "Silica Beta Repo",
    "description": "A repo used to help develop the Silica static repo compiler.",
    "tint": "#2da9f3",
    "cname": "silica.shuga.co",
    "maintainer": {
        "name": "Shuga",
        "email": "sileo@shuga.co"
    },
    "social": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HeyItsShuga"
        },
        {
            "name": "Website",
            "url": "https://shuga.co/"
        }
    ],
    "automatic_git": "false",
    "subfolder": "repo",
    "footer": "{{repo_name}} Powered by Silica {{silica_version}}",
    "enable_gpg": "false"
}
```

### Templating

The repo's home page and web-based tweak depictions can be customized using a [Mustache-based](https://mustache.github.io/mustache.5.html) templating system. If you want to customize these pages, you can use the following placeholders to extend or personalize your Silica install.

Customizing your repo is optional, but those migrating from a different repo who want to preserve the look of their old depictions may want to do this, as may those who want to push a brand identity.

### `index.mustache` Placeholders

|Placeholder|Description|
|---|---|
|`{{repo_name}}`|The name of the repo.|
|`{{repo_desc}}`|A short tagline of the repo.|
|`{{repo_url}}`|The domain the repo is hosted on.|
|`{{repo_tint}}`|The repo's default tint color.|
|`{{tint_color}}`|An alias to `{{repo_tint}}`.|
|`{{{repo_carousel}}}`|A scrollable carousel that lists any featured packages.|
|`{{{repo_packages}}}`|A list of every package on the repo.|
|`{{silica_compile_date}}`|The date the repo was compiled on (in YYYY-MM-DD).|
|`{{silica_version}}`|The version of Silica that the repo runs on.|
|`{{footer}}`|The footer.|
|`{{tweak_release}}`|An object including all of the tweaks on the repo and their settings.|

### `tweak.mustache` Placeholders

|Placeholder|Description|
|---|---|
|`{{repo_name}}`|The name of the repo.|
|`{{repo_desc}}`|A short tagline of the repo.|
|`{{repo_url}}`|The domain the repo is hosted on.|
|`{{repo_tint}}`|The repo's default tint color.|
|`{{tint_color}}`|The package's tint color. Defaults to the repo's default tint color.|
|`{{silica_compile_date}}`|The date the repo was compiled on (in YYYY-MM-DD).|
|`{{silica_version}}`|The version of Silica that the repo runs on.|
|`{{footer}}`|The footer.|
|`{{tweak_release}}`|An object including all of the tweaks on the repo and their settings.|
|`{{tweak_name}}`|The name of the package to display.|
|`{{tweak_developer}}`|The author of the displayed package.|
|`{{tweak_version}}`|The current version of the displayed package.|
|`{{tweak_section}}`|The category of the displayed package.|
|`{{tweak_bundle_id}}`|The "Bundle ID" of the displayed package.|
|`{{tweak_compatibility}}`|A string to state what iOS versions a package is compatible with.|
|`{{works_min}}`|The minimum iOS version the package is compatible with.|
|`{{works_max}}`|The maximum iOS version the package is compatible with.|
|`{{tweak_tagline}}`|A short tagline of the displayed package.|
|`{{{tweak_carousel}}}`|A scrollable carousel of the displayed package's screenshots.|
|`{{{tweak_description}}}`|A formatted description of the displayed package. Defaults to `{{tweak_tagline}}`.|
|`{{{changelog}}}`|A formatted list of changes to the displayed package.|
|`{{source}}`|A URL to the package's source code.|

### File Structure
This is the structure of user-defined files and folders in Silica. Some of these, such as `settings.json`, may be automatically generated on set-up. Others (such as the `.mustache` template files) don't need to be changed if you want to use the default settings.

```
Packages // All tweak/theme information/data will go here, AKA what will mainly be messed with.
    [Tweak Folder]
        silica_data
            index.json // This will allow you to edit data in the generated Control file, as well as the data that web and native depictions will use (such as compatibility information and color tint; icons and screenshots are automatically dealt with.).
            description.md // A separate description file, because a one-liner in some JSON isn't any fun!
            icon.png // The package icon.
            banner.png // The header image.
            screenshots
                [Assorted images].png
            scripts
                [Everything here will be put in DEBIAN and is for pre/postinst scripts]
        [Mirror of iOS directory listing OR a .deb file]
Styles // Allows users to customize how Silica looks
    index.mustache // This controls the compiled index.html file.
    tweak.mustache // This controls the per-tweak web depictions generated.
    settings.json // This allows you to edit data in the generated Release file, maintainer links, and some other things that Sileo native depictions may need
    index.css // Stylesheet
    index.js // JavaScript
    icon.png // Repo icon.
```
