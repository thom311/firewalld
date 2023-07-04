#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later

import fwtst  # noqa: F401

import firewall.core.icmp


def test_icmp():
    assert not firewall.core.icmp.check_icmpv6_name("foo")
    assert firewall.core.icmp.check_icmpv6_name("neigbour-solicitation")


if __name__ == "__main__":
    fwtst.pytest_main()
