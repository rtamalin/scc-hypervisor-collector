"""SCC Hypervisor Collector API utility code."""

import getpass
import stat
from pathlib import Path
from typing import Type

from .exceptions import (
    CollectorException,
    FilePermissionsError,
)


def check_permissions(
    path: Path,
    fail_exc: Type[CollectorException] = FilePermissionsError
) -> None:
    """Check if path has the required permissions.

    If issues are found the exception specified by fail_exc will be raised.
    """
    # collect required details
    current_user = getpass.getuser()
    stats = path.stat()
    mode = stats.st_mode

    # check the path owner
    if path.owner() != current_user:
        msg = f"{path} not owned by the user {current_user}"
        raise fail_exc(msg)

    # verify directory permissions
    if path.is_dir() and stat.S_IMODE(mode) != 0o700:
        msg = f"User { current_user } should have full access to " \
              f"{path} but group and others should have no access."
        raise fail_exc(msg)

    # verify file permissions
    if path.is_file() and stat.S_IMODE(mode) != 0o600:
        msg = f"User {current_user} should have read/write access " \
              f"to {path} but group and others should have no access."
        raise fail_exc(msg)
