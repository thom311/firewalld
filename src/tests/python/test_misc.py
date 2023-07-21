#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest
import random

from gi.repository import GLib

import fwtst  # noqa: F401

import firewall.core.icmp
import firewall.glibutil


def test_icmp():
    assert not firewall.core.icmp.check_icmpv6_name("foo")
    assert firewall.core.icmp.check_icmpv6_name("neigbour-solicitation")


def test_timeout():

    maincontext = GLib.main_context_default()

    lst_cnt = [0]

    def cb_not_called():
        raise AssertionError("I should not be called")

    def cb_cnt():
        lst_cnt[0] += 1

    def cb_cancel(key):
        firewall.glibutil.timeout.cancel(key)

    firewall.glibutil.timeout.schedule(0.005, lambda: cb_cancel("key2"), "key1")
    firewall.glibutil.timeout.schedule(0.006, cb_not_called, "key2")

    firewall.glibutil.timeout.schedule(0.01, cb_not_called, "key3")
    firewall.glibutil.timeout.schedule(0.01, cb_cnt, key="key3")

    h = firewall.glibutil.timeout.schedule(1, cb_not_called, "key4")
    assert h.key == "key4"
    assert h.callback == cb_not_called
    assert h.tags == ()
    assert firewall.glibutil.timeout.has("key4") is h
    assert firewall.glibutil.timeout.has("foo") is None
    assert firewall.glibutil.timeout.cancel("key4")
    assert firewall.glibutil.timeout.has("key4") is None

    h = firewall.glibutil.timeout.schedule(1, cb_not_called)
    assert firewall.glibutil.timeout.has_handle(h)
    assert firewall.glibutil.timeout.cancel_handle(h)

    firewall.glibutil.timeout.schedule(0.001, cb_not_called, tags=("tag1",))
    assert firewall.glibutil.timeout.cancel_tag("tag1") == 1

    assert not firewall.glibutil.timeout.cancel("keyfoo")
    assert firewall.glibutil.timeout.cancel_tag("tagfoo") == 0

    while lst_cnt[0] == 0:
        maincontext.iteration(True)

    assert lst_cnt == [1]

    h = firewall.glibutil.timeout.schedule(1, cb_not_called, "x", tags=["tag1"])
    assert h.tags == ("tag1",)
    h2 = firewall.glibutil.timeout.schedule(1, cb_not_called, "x", tags=("tag2",))
    assert h is h2
    assert h.tags == ("tag2",)
    assert firewall.glibutil.timeout.cancel_tag("tag1") == 0
    assert firewall.glibutil.timeout.cancel_tag("tag2") == 1

    extra_tags = [1, 2, 3, 4]
    random.shuffle(extra_tags)

    h = firewall.glibutil.timeout.schedule("1", cb_not_called, "x", tags=("tag1",))
    h2 = firewall.glibutil.timeout.schedule(
        1, cb_not_called, "x", tags=("tag2",), replace_tags=False
    )
    assert h is h2
    assert h.tags == ("tag1", "tag2")
    h2 = firewall.glibutil.timeout.schedule(
        1, cb_not_called, "x", tags=extra_tags, replace_tags=False
    )
    assert h is h2
    assert h.tags == ("tag1", "tag2") + tuple(extra_tags)
    assert firewall.glibutil.timeout.has("x") is h
    assert firewall.glibutil.timeout.cancel_tag("tag1") == 1
    assert firewall.glibutil.timeout.cancel_tag("tag2") == 0
    assert firewall.glibutil.timeout.has("x") is None

    assert firewall.glibutil.timeout._handles == {}
    assert firewall.glibutil.timeout._tags == {}

    with pytest.raises(TypeError):
        firewall.glibutil.timeout.schedule("err", cb_not_called)


if __name__ == "__main__":
    fwtst.pytest_main()
