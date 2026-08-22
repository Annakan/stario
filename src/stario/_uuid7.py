"""`uuid7` compatibility.

The stdlib gained `uuid.uuid7()` only in Python 3.14. The vendored fork must
also run on 3.13, where the equivalent backport is `uuid_utils.uuid7` (same
`uuid.UUID` return type, version-7). Import `uuid7` from here, never directly
from `uuid`.
"""
from __future__ import annotations

from uuid import UUID

try:  # Python >= 3.14 stdlib.
    from uuid import uuid7 as uuid7
except ImportError:  # Python 3.15- backport path (`uuid-utils`).
    from uuid_utils import uuid7 as uuid7

__all__ = ("UUID", "uuid7")
