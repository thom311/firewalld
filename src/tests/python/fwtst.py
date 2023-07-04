# SPDX-License-Identifier: GPL-2.0-or-later

import os
import pytest
import sys

###############################################################################


def str_to_bool(val, default_val=False):
    if isinstance(val, str):
        val = val.lower().strip()
        if val in ("", "default", "-1"):
            return default_val
        if val in ("0", "n", "no", "false"):
            return False
        if val in ("1", "y", "yes", "true"):
            return True
        # Invalid. Fall through.
    elif val is None:
        return default_val

    # No nonsense.
    raise ValueError(f"Unexpcted value for str_to_bool({repr(val)})")


###############################################################################

d = os.path.dirname(__file__)
d = os.path.realpath(d)
testdir = d

d = os.path.join(testdir, "..", "..", "..")
d = os.path.realpath(d)
if not os.path.isdir(d) or not os.path.isfile(d + "/firewalld.spec"):
    # This doesn't look like our source directory. More likely, the
    # test suite was installed. There is no top_srcdir.
    d = None
top_srcdir = d

del d

is_srcdir = top_srcdir is not None


def srcdir(*path_components):
    d = top_srcdir
    if not d:
        raise Exception("not inside a firewalld src directory")
    return os.path.join(d, *path_components)


###############################################################################


def pytest_main():
    sys.exit(pytest.main([sys.argv[0]]))


###############################################################################

# Automatically set up PYTHONPATH= so that import firewalld gives the firewalld
# from our source tree. You can opt out with FWTST_AUTO_PYTHONPATH=0
if not is_srcdir:
    # we are not inside a source directory. Skip.
    pass
elif not str_to_bool(
    os.environ.get("FWTST_AUTO_PYTHONPATH"),
    True,
):
    # The user opted out via FWTST_AUTO_PYTHONPATH=0
    pass
else:
    sys.path.insert(0, srcdir("src"))
