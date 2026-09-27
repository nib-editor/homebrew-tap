"""Writes Formula/nib.rb for nib's latest release, from its archives'
.sha256 files. Run by .github/workflows/update.yml; `python3 update.py`
does the same by hand.
"""
import json
import os
import pathlib
import urllib.error
import urllib.request

REPO = "nib-editor/nib"

# Homebrew's platform blocks and the release's target in each.
TARGETS = {
    ("macos", "arm"): "aarch64-apple-darwin",
    ("macos", "intel"): "x86_64-apple-darwin",
    ("linux", "arm"): "aarch64-unknown-linux-gnu",
    ("linux", "intel"): "x86_64-unknown-linux-gnu",
}


def get(url):
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token := os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        return response.read().decode()


def latest():
    """The latest release's tag and the sha256 of each target's archive."""
    release = json.loads(get(f"https://api.github.com/repos/{REPO}/releases/latest"))
    tag = release["tag_name"]
    assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}
    hashes = {}
    for target in TARGETS.values():
        name = f"nib-{tag}-{target}.tar.gz.sha256"
        hashes[target] = get(assets[name]).split()[0]
    return tag, hashes


def formula(tag, hashes):
    version = tag.removeprefix("v")
    blocks = []
    for os_name in ["macos", "linux"]:
        arches = []
        for arch in ["arm", "intel"]:
            target = TARGETS[(os_name, arch)]
            url = f"https://github.com/{REPO}/releases/download/{tag}/nib-{tag}-{target}.tar.gz"
            arches.append(
                f"    on_{arch} do\n"
                f'      url "{url}"\n'
                f'      sha256 "{hashes[target]}"\n'
                f"    end\n"
            )
        blocks.append(f"  on_{os_name} do\n{''.join(arches)}  end\n")
    return (
        "# Written by update.py from nib's latest release; do not edit.\n"
        "class Nib < Formula\n"
        '  desc "Modal editor made of WebAssembly plugins, the Helix-style keymap included"\n'
        f'  homepage "https://github.com/{REPO}"\n'
        f'  version "{version}"\n'
        '  license any_of: ["MIT", "Apache-2.0"]\n'
        "\n"
        f"{''.join(blocks)}"
        "\n"
        "  def install\n"
        '    bin.install "nib"\n'
        "  end\n"
        "\n"
        "  test do\n"
        '    assert_match "usage: nib", shell_output("#{bin}/nib --help")\n'
        "  end\n"
        "end\n"
    )


def released():
    """Whether nib has a release yet: there is none before 1.0.0."""
    try:
        get(f"https://api.github.com/repos/{REPO}/releases/latest")
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return False
        raise
    return True


if __name__ == "__main__":
    if not released():
        print("nib has no release yet; nothing to do")
        raise SystemExit
    tag, hashes = latest()
    path = pathlib.Path(__file__).parent / "Formula" / "nib.rb"
    path.write_text(formula(tag, hashes))
    print(f"wrote {path} for {tag}")
