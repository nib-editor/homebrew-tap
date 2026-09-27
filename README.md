# homebrew-tap

The [Homebrew](https://brew.sh) tap for [nib](https://github.com/nib-editor/nib), a modal editor made of WebAssembly plugins.

```sh
brew install nib-editor/tap/nib
```

`Formula/nib.rb` installs the prebuilt binary from nib's latest release. A [workflow](.github/workflows/update.yml) rewrites it from the release daily, and can be run by hand; `python3 update.py` does the same locally.
