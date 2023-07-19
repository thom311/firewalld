# SPDX-License-Identifier: GPL-2.0-or-later


class Ident:
    """Simple data class for reprecenting the identity of various entities.

    We have different entities, like Zones, Policies, special zones ANY/HOST,
    and policies for zones. A (user created) zone is not the same as the
    special zone ANY, even if the user created zone happens to have the same
    name.  This type represents the identity of such entities, that is, it can
    be used as dictionary keys in place of the name.

    The type is immutable (in the sense that you are not supposed to change an
    instance after creation, not that you couldn't hack it due to the dynamic
    nature of Python).
    """

    _TYPE_ZONE = "zone"
    _TYPE_SPECIAL_ZONE = "special-zone"
    _TYPE_POLICY = "policy"
    _TYPE_ZONE_POLICY = "zone=policy"

    DIRECTION_TO = "to"
    DIRECTION_FROM = "from"

    @staticmethod
    def is_ident(self):
        if not isinstance(self, Ident):
            return False
        t = getattr(self, "type", None)
        assert (
            t is Ident._TYPE_ZONE
            or t is Ident._TYPE_SPECIAL_ZONE
            or t is Ident._TYPE_POLICY
            or t is Ident._TYPE_ZONE_POLICY
        )
        return True

    @staticmethod
    def SpecialZone(zone):
        if isinstance(zone, Ident):
            assert Ident.is_special_zone(zone)
            return zone
        assert isinstance(zone, str) and zone in ("ANY", "HOST")
        self = getattr(Ident, zone, None)
        if self is None:
            self = Ident()
            self.type = Ident._TYPE_SPECIAL_ZONE
            self.zone = zone
            self._key_data = (1, zone)
            setattr(Ident, zone, self)
        return self

    @staticmethod
    def Zone(zone):
        if isinstance(zone, Ident):
            assert Ident.is_zone(zone)
            return zone
        assert isinstance(zone, str) and zone
        self = Ident()
        self.type = Ident._TYPE_ZONE
        self.zone = zone
        self._key_data = (2, zone)
        return self

    @staticmethod
    def Policy(policy):
        if isinstance(policy, Ident):
            assert Ident.is_policy(policy)
            return policy
        assert isinstance(policy, str) and policy
        self = Ident()
        self.type = Ident._TYPE_POLICY
        self.policy = policy
        self._key_data = (3, policy)
        return self

    @staticmethod
    def ZonePolicy(zone, direction, special_zone):
        zone = Ident.Zone(zone)
        special_zone = Ident.SpecialZone(special_zone)
        assert isinstance(direction, str) and direction in ("to", "from")
        is_to = direction == "to"
        direction = Ident.DIRECTION_TO if is_to else Ident.DIRECTION_FROM

        self = Ident()
        self.type = Ident._TYPE_ZONE_POLICY
        self.zone = zone
        self.direction = direction
        self.special_zone = special_zone
        self.to_zone = special_zone if is_to else zone
        self.from_zone = special_zone if not is_to else zone
        self._key_data = (4, zone.zone, direction, special_zone.zone)
        return self

    @staticmethod
    def is_special_zone(self):
        return isinstance(self, Ident) and self.type is Ident._TYPE_SPECIAL_ZONE

    @staticmethod
    def is_zone(self):
        return isinstance(self, Ident) and self.type is Ident._TYPE_ZONE

    @staticmethod
    def is_policy(self):
        return isinstance(self, Ident) and self.type is Ident._TYPE_POLICY

    @staticmethod
    def is_zone_policy(self):
        return isinstance(self, Ident) and self.type is Ident._TYPE_ZONE_POLICY

    @staticmethod
    def is_any_zone(self):
        if isinstance(self, Ident) and (
            self.type is Ident._TYPE_ZONE or self.type is Ident._TYPE_SPECIAL_ZONE
        ):
            return True
        return False

    @staticmethod
    def is_any_policy(self):
        if isinstance(self, Ident) and (
            self.type is Ident._TYPE_POLICY or self.type is Ident._TYPE_ZONE_POLICY
        ):
            return True
        return False

    @staticmethod
    def zone_policy_directions():
        return (
            (Ident.DIRECTION_TO, Ident.HOST),
            (Ident.DIRECTION_FROM, Ident.HOST),
            (Ident.DIRECTION_TO, Ident.ANY),
            (Ident.DIRECTION_FROM, Ident.ANY),
        )

    @staticmethod
    def zone_policies(zone):
        zone = Ident.Zone()
        for direction, special_zone in Ident.zone_policy_directions():
            yield Ident.ZonePolicy(zone, direction, special_zone)

    @staticmethod
    def _key(self):
        assert Ident.is_ident(self)
        return self._key_data

    def __hash__(self):
        return hash(Ident._key(self))

    def __eq__(self, other):
        return Ident._key(self) == Ident._key(other)

    def __lt__(self, other):
        return Ident._key(self) < Ident._key(other)

    def __le__(self, other):
        return Ident._key(self) <= Ident._key(other)

    def __ge__(self, other):
        return Ident._key(self) >= Ident._key(other)

    def __gt__(self, other):
        return Ident._key(self) > Ident._key(other)

    def __repr__(self):
        assert Ident.is_ident(self)
        if self.type is Ident._TYPE_ZONE:
            return f"Zone({self.zone})"
        if self.type is Ident._TYPE_POLICY:
            return f"Policy({self.policy})"
        if self.type is Ident._TYPE_SPECIAL_ZONE:
            return f"SpecialZone({self.zone})"

        assert self.type is Ident._TYPE_ZONE_POLICY
        return f"ZonePolicy({self.zone.zone} {self.direction} {self.special_zone.zone})"

    @property
    def name(self):
        assert Ident.is_ident(self)
        if self.type is Ident._TYPE_ZONE:
            return self.zone
        if self.type is Ident._TYPE_POLICY:
            return self.policy
        if self.type is Ident._TYPE_SPECIAL_ZONE:
            return self.zone

        assert self.type is Ident._TYPE_ZONE_POLICY
        return f"zone_{self.from_zone.zone}_{self.to_zone.zone}"


Ident.ANY = Ident.SpecialZone("ANY")
Ident.HOST = Ident.SpecialZone("HOST")

Ident.ZONE_PUBLIC = Ident.Zone("public")
Ident.ZONE_EXTERNAL = Ident.Zone("external")
Ident.ZONE_BLOCK = Ident.Zone("block")
