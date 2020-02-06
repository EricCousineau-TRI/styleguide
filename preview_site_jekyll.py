#!/usr/bin/env python3

"""
Preview site using a consolidated version of instructions from:

https://help.github.com/en/github/working-with-github-pages/testing-your-github-pages-site-locally-with-jekyll
"""

import os
import platform
from subprocess import run, PIPE
import sys

PREREQS = "ruby-full build-essential zlib1g-dev"

INSTALL_TEXT = f"""
Missing prerequisites. Please run:

    sudo apt install {PREREQS}
""".lstrip()

# TODO(eric.cousineau): Figure out right theme / layout for plain site.
# TODO(eric.cousineau): If/when we figure out how to fully sync up output with
# gh-pages, commit `Gemfile` and `_config.yml` to Git.
GEMFILE_CONTENT = """
source "https://rubygems.org"
gem "minima", "~> 2.5"
gem "github-pages", group: :jekyll_plugins
""".lstrip()

CONFIG_CONTENT = """
title: Style Guide
theme: minima
""".lstrip()


def which(prog):
    return run(["which", prog]).returncode == 0


def main():
    if platform.linux_distribution() != ("Ubuntu", "18.04", "bionic"):
        print("Only tested on Ubuntu 18.04")
        sys.exit(1)

    package_check = run(
        ["dpkg", "-s"] + PREREQS.split(), stdout=PIPE, stderr=PIPE)
    if package_check.returncode != 0:
        print(INSTALL_TEXT)
        sys.exit(1)

    # TODO(eric.cousineau): Try to contain generated files within a single
    # directory.
    os.chdir(os.path.dirname(__file__))

    env = dict(os.environ)
    if "GEM_HOME" not in env:
        gem_home = os.path.join(os.getcwd(), "_gems")
        print(f"Setting GEM_HOME to tmpdir: {gem_home}")
        env["GEM_HOME"] = gem_home
        fake_home = "/tmp/robotlocomotion-styleguide-jekyll-home"
        os.makedirs(fake_home, exist_ok=True)
        print(f"Setting HOME to {fake_home}")
        env["HOME"] = fake_home
    else:
        # User has gems configured. Let it operate normally.
        gem_home = env["GEM_HOME"]
    gem_bin = os.path.join(gem_home, "bin")
    path = env.get("PATH", "").split(":")
    if gem_bin not in path:
        path.insert(0, gem_bin)
    env["PATH"] = ":".join(path)

    with open("Gemfile", "w") as f:
        f.write(GEMFILE_CONTENT)
    with open("_config.yml", "w") as f:
        f.write(CONFIG_CONTENT)

    def run_env(args):
        run(args, env=env, check=True)

    print("\n\nSetting up site. May take a while the first time...\n\n")

    run_env(["gem", "install", "bundle"])
    run_env(["bundle", "update"])
    # Use --no-watch because using the gem tmpdir under this folder may
    # overload inotify.
    run_env(["bundle", "exec", "jekyll", "serve", "--no-watch"])


assert __name__ == "__main__"
main()
