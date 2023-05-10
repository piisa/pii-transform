
from typing import Dict, List, Any, Optional


def get_element(src: Dict, taglist: List[str]) -> Optional[Any]:
    """
    Get an element from a (possibly nested) dictionary
    """
    if isinstance(taglist, str):
        taglist = [taglist]
    for tag in taglist:        
        tcomp = tag.split(".")
        for n, elem in enumerate(tcomp, start=1):
            if elem not in src:
                break
            src = src[elem]
            if n == len(tcomp):
                return src


def set_element(src: Dict, taglist: List[str], value: Any) -> bool:
    """
    Set an element in a (possibly nested) dictionary
    """
    if isinstance(taglist, str):
        taglist = [taglist]
    for tag in taglist:
        tcomp = tag.split(".")
        for n, elem in enumerate(tcomp, start=1):
            if elem not in src:
                break
            if n < len(tcomp):
                src = src[elem]
            else:
                src[elem] = value
                return True
    return False
