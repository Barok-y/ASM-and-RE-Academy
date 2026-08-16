from __future__ import annotations

from typing import Dict, List, Optional

from ..models import Module
from .module1 import module1
from .module2 import module2
from .module3 import module3
from .module4 import module4
from .module5 import module5
from .module6 import module6
from .module7 import module7
from .module8 import module8
from .module9 import module9


def all_modules() -> List[Module]:
    return [
        module1(),
        module2(),
        module3(),
        module4(),
        module5(),
        module6(),
        module7(),
        module8(),
        module9(),
    ]


def get_module(module_id: str) -> Optional[Module]:
    for module in all_modules():
        if module.id == module_id:
            return module
    return None


def module_index() -> Dict[str, Module]:
    return {module.id: module for module in all_modules()}
