from __future__ import annotations

import re

_RAW_PATTERNS = [
    r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/",   # rm -rf* / (any flag order containing r and f)
    r"rm\s+-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+/",  # rm -fr / (f before r)
    r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+~",  # rm -rf* ~
    r"rm\s+-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+~",  # rm -fr ~
    r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+\$HOME",  # rm -rf* $HOME
    r"rm\s+-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+\$HOME",  # rm -fr $HOME
    r"dd\s+if=",                                   # dd if= (disk wipe)
    r"mkfs\.",                                     # mkfs.* (format filesystem)
    r"mkfs\s+",
    r":\s*\(\s*\)\s*\{\s*:\s*\|",                 # fork bomb :(){ :|:& };:
    r">\s*/dev/sd[a-z]",                           # overwrite raw disk
    r">\s*/dev/nvme",
    r"chmod\s+-[a-zA-Z]*R[a-zA-Z]*\s+777\s+/",   # chmod -R 777 /
    r"chown\s+-[a-zA-Z]*R[a-zA-Z]*\s+.*\s+/[^/]",# chown -R ... /
    r"curl\s+.*\|\s*(ba)?sh",                      # curl | bash/sh
    r"wget\s+.*\|\s*(ba)?sh",                      # wget | sh
    r"python[23]?\s+-c\s+.*os\.system",            # python -c os.system abuse
    r"mv\s+/\s+",                                  # mv / ...
    r"cp\s+-[a-zA-Z]*r[a-zA-Z]*\s+/\s+",         # cp -r / ...
    r"shutdown\s+(-h|-r|now)",                     # shutdown
    r"halt\b",
    r"poweroff\b",
    r"reboot\b",
    r"fdisk\s+/dev/",                              # fdisk on raw device
    r"parted\s+/dev/",
]

_COMPILED = [(pat, re.compile(pat, re.IGNORECASE)) for pat in _RAW_PATTERNS]


class BlockedCommandError(Exception):
    def __init__(self, command: str, pattern: str) -> None:
        super().__init__(f"Command blocked by safety rule: {pattern!r}")
        self.command = command
        self.pattern = pattern


def check(command: str) -> None:
    for pattern, regex in _COMPILED:
        if regex.search(command):
            raise BlockedCommandError(command, pattern)
