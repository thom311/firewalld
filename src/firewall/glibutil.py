# SPDX-License-Identifier: GPL-2.0-or-later

from gi.repository import GLib


###############################################################################


class _Timeout:
    class _Handle:
        def __init__(handle, self, key, timeout, callback, tags, timeout_exact):
            if tags is None:
                tags = ()
            else:
                tags = tuple(dict.fromkeys(tags))

            if key is None:
                # If the caller provided no key, the timeout cannot
                # be cancelled via the key. The internally used key,
                # is the handle instance itself.
                key = handle

            handle.self = self
            handle.key = key

            handle.callback = callback
            handle.tags = tags
            handle._gsourceid_id = 0

            for tag in tags:
                handle._tags_register(tag)
            self._handles[key] = handle
            handle._gsourceid_attach(timeout, timeout_exact)

        def _destroy(handle):
            self = handle.self
            handle._gsourceid_remove()
            del self._handles[handle.key]
            for tag in handle.tags:
                handle._tags_unregister(tag)

        def _reschedule(handle, timeout, callback, tags, replace_tags, timeout_exact):
            add_tags = True
            if replace_tags or not handle.tags:
                if tags is None:
                    new_tags = ()
                else:
                    new_tags = dict.fromkeys(tags)
            else:
                if tags is None:
                    new_tags = handle.tags
                    add_tags = False
                else:
                    new_tags = dict.fromkeys(handle.tags)
                    for t in tags:
                        new_tags[t] = None

            # `new_tags` is either a (unique) tuple or a dict.  Both is fine, we
            # will convert it to a tuple for `handle.tags`.
            if add_tags:
                for tag in new_tags:
                    handle._tags_register(tag)
            if replace_tags:
                for tag in handle.tags:
                    # At this place, `new_tags` is either an empty tuple or a
                    # set. So the entire loop is O(n).
                    if tag not in new_tags:
                        handle._tags_unregister(tag)

            handle.callback = callback
            handle.tags = tuple(new_tags)

            handle._gsourceid_remove()
            handle._gsourceid_attach(timeout, timeout_exact)

        def _gsourceid_remove(handle):
            if handle._gsourceid_id != 0:
                GLib.source_remove(handle._gsourceid_id)
                handle._gsourceid_id = 0

        def _gsourceid_attach(handle, timeout, timeout_exact):
            if timeout_exact or isinstance(timeout, float):
                timeout = timeout * 1000.0
                if timeout < 1:
                    timeout = 1
                elif timeout > 0xFFFFFFFF:
                    timeout = 0xFFFFFFFF
                sid = GLib.timeout_add(int(timeout), handle._timeout_cb)
            else:
                if timeout > 0xFFFFFFFF:
                    timeout = 0xFFFFFFFF
                sid = GLib.timeout_add_seconds(timeout, handle._timeout_cb)
            handle._gsourceid_id = sid

        def _timeout_cb(handle):
            callback = handle.callback
            handle._gsourceid_id = 0
            handle._destroy()
            try:
                callback()
            except Exception:
                import traceback

                traceback.print_exc()
            return False

        def _tags_register(handle, tag):
            # We allow that handle may or may not be registered already.
            self = handle.self
            s = self._tags.get(tag)
            if s is None:
                s = set()
                self._tags[tag] = s
            s.add(handle)

        def _tags_unregister(handle, tag):
            # We expect that handle is registered under tag.
            self = handle.self
            s = self._tags[tag]
            s.remove(handle)
            if not s:
                del self._tags[tag]

    def __init__(self):
        self._handles = {}
        self._tags = {}

    def _parse_timeout(self, timeout):
        timeout0 = timeout
        if isinstance(timeout, int) or isinstance(timeout, float):
            pass
        elif isinstance(timeout, str):
            # For convenience, also accept timeout as a string.
            try:
                timeout = int(timeout)
            except ValueError:
                try:
                    timeout = float(timeout)
                except ValueError:
                    timeout = None
        else:
            timeout = None

        if timeout is None:
            raise TypeError(f"timeout expects a number but is '{timeout0}'")
        if timeout < 0:
            raise TypeError("timeout cannot be negative")

        return timeout

    def schedule(
        self,
        timeout,
        callback,
        key=None,
        tags=None,
        *,
        replace_tags=True,
        timeout_exact=False,
        cancel_on_zero=False,
    ):
        assert callback
        timeout = self._parse_timeout(timeout)

        if key is not None:
            handle = self._handles.get(key)
            if handle is not None:
                if cancel_on_zero and timeout == 0:
                    handle._destroy()
                    return None
                handle._reschedule(timeout, callback, tags, replace_tags, timeout_exact)
                return handle

        if cancel_on_zero and timeout == 0:
            return None

        return self._Handle(self, key, timeout, callback, tags, timeout_exact)

    def has(self, key):
        # This returns the handle instance or None, which also
        # can be used in a boolean context.
        return self._handles.get(key)

    def has_handle(self, handle):
        return (
            isinstance(handle, self._Handle) and self._handles.get(handle.key) is handle
        )

    def cancel(self, key):
        handle = self._handles.get(key)
        if handle is None:
            return False
        handle._destroy()
        return True

    def cancel_handle(self, handle):
        if not self.has_handle(handle):
            return False
        handle._destroy()
        return True

    def cancel_tag(self, *tags):
        n = 0
        for tag in tags:
            s = self._tags.get(tag)
            if s is None:
                continue
            s = tuple(s)
            for handle in s:
                n += 1
                handle._destroy()
        return n


timeout = _Timeout()
