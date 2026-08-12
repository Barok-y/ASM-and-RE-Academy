from __future__ import annotations

import datetime
import hashlib
import random
from typing import List, Optional

from .content import sample_challenges
from .ctf import ctf_challenges
from .grading import Challenge


def pool(include_ctf: bool = True) -> List[Challenge]:
    challenges = list(sample_challenges())
    if include_ctf:
        challenges.extend(ctf_challenges())
    return challenges


def daily_challenge(
    day: Optional[str] = None, pool_: Optional[List[Challenge]] = None
) -> Challenge:
    """Deterministic daily challenge keyed on YYYY-MM-DD."""
    day = day or datetime.date.today().isoformat()
    source = pool_ if pool_ is not None else pool()
    if not source:
        raise ValueError("no challenges available")
    digest = int(hashlib.sha256(day.encode()).hexdigest(), 16)
    return source[digest % len(source)]


def random_challenge(pool_: Optional[List[Challenge]] = None) -> Challenge:
    source = pool_ if pool_ is not None else pool()
    if not source:
        raise ValueError("no challenges available")
    return random.choice(source)
