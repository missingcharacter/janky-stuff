# `mount_ntfs.sh`

## Requirements

- Homebrew
  - Install command:

    ```shell
    /bin/bash \
      -c \
      "$(curl \
        -fsSL \
        https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

- macFUSE
  - Install command: `brew install --cask macfuse`
- ntfs-3g-mac
  - Install command:

    ```shell
    brew tap gromgit/homebrew-fuse
    brew install ntfs-3g-mac
    ```

## How to use?

**NOTE:** `/folder/in/$PATH` means any folder found in environment variable
`$PATH`

```shell
chmod +x mount_ntfs.sh
mv mount_ntfs.sh /folder/in/$PATH
mount_ntfs.sh
```
