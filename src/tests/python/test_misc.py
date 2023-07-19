#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fwtst  # noqa: F401

import firewall.core.icmp
import firewall.core.ident


def test_icmp():
    assert not firewall.core.icmp.check_icmpv6_name("foo")
    assert firewall.core.icmp.check_icmpv6_name("neigbour-solicitation")


def test_zone_ident():
    Ident = firewall.core.ident.Ident

    assert repr(Ident.ANY) == "SpecialZone(ANY)"
    assert str(Ident.ANY) == "SpecialZone(ANY)"
    assert Ident.ANY.name == "ANY"

    assert repr(Ident.HOST) == "SpecialZone(HOST)"
    assert str(Ident.HOST) == "SpecialZone(HOST)"
    assert Ident.HOST.name == "HOST"

    assert Ident.is_special_zone(Ident.HOST)
    assert Ident.is_special_zone(Ident.ANY)

    assert Ident.ANY is Ident.SpecialZone("ANY")
    assert Ident.ANY == Ident.SpecialZone("ANY")
    assert Ident.HOST is Ident.SpecialZone("HOST")
    assert Ident.HOST == Ident.SpecialZone("HOST")

    assert Ident.ANY < Ident.SpecialZone("HOST")
    assert Ident.HOST > Ident.ANY

    assert Ident.SpecialZone(Ident.ANY) is Ident.ANY
    assert Ident.SpecialZone(Ident.HOST) is Ident.HOST

    z = Ident.Zone("foo")
    assert Ident.is_zone(z)
    assert not Ident.is_special_zone(z)
    assert not Ident.is_zone_policy(z)
    assert Ident.Zone("foo") == z
    assert Ident.Zone("foo") is not z
    assert Ident.Zone(z) is z
    assert repr(z) == "Zone(foo)"
    assert str(z) == "Zone(foo)"
    assert z.name == "foo"

    p = Ident.Policy("bar")
    assert Ident.is_policy(p)
    assert Ident.Policy("bar") == p
    assert Ident.Policy("bar") is not p
    assert Ident.Policy(p) is p
    assert repr(p) == "Policy(bar)"
    assert str(p) == "Policy(bar)"
    assert p.name == "bar"

    assert z != p
    assert z == Ident.Zone("foo")
    assert z != Ident.Zone("foo2")
    assert z != Ident.Policy("foo")
    assert Ident.Zone("ANY") != Ident.ANY

    assert Ident.ANY < z
    assert z < p

    assert Ident.ANY in set([Ident.ANY])
    assert Ident.Zone("foo") in set([Ident.Zone("foo")])
    assert Ident.Zone("foo2") not in set([Ident.Zone("foo")])
    assert Ident.Zone("foo") not in set([Ident.Policy("foo")])

    z2 = Ident.ZonePolicy("zone", "to", "ANY")
    assert Ident.is_zone_policy(z2)
    assert repr(z2) == "ZonePolicy(zone to ANY)"
    assert str(z2) == repr(z2)
    assert z2.name == "zone_zone_ANY"
    z3 = Ident.ZonePolicy("zone", "to", Ident.ANY)
    z4 = Ident.ZonePolicy(Ident.Zone("zone"), "to", Ident.ANY)
    assert z4.name == "zone_zone_ANY"
    assert z2 == z3
    assert z2 == z4
    assert z4 == z3
    assert not (z4 != z3)
    assert not (z2 < z3)
    assert z2 <= z3
    assert not (z2 > z3)
    assert z2 >= z3

    assert Ident.ZonePolicy("xyz", "from", "HOST").name == "zone_HOST_xyz"

    assert Ident.Zone("zone_HOST_xyz") != Ident.ZonePolicy("xyz", "from", "HOST")

    with pytest.raises(AssertionError):
        Ident.Zone("foo") == "foo"
    with pytest.raises(AssertionError):
        Ident.Policy("foo") < "foo"

    assert Ident.ZONE_PUBLIC.name == "public"
    assert Ident.ZONE_EXTERNAL.name == "external"
    assert Ident.ZONE_BLOCK.name == "block"


if __name__ == "__main__":
    fwtst.pytest_main()
