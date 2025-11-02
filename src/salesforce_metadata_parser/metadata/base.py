# Standard Library imports
from dataclasses import dataclass, field
from typing import Any, Optional, List

@dataclass(kw_only=True)
class XmlNode():
    """Represents an XML Node"""

    _sub_classes: Optional[dict] = field(repr=False, default_factory=lambda: {})
    """Overwritable field. Tells the Parser which Class to use when creating new instances of list items"""

    def _to_dict(self) -> dict:
        return { key: value for key, value in self.__dict__ if not key.startswith("_") }
    
    def _get_value(self, key: str) -> str:
        return self.__dict__.get(key, None)
    
    def _get_list(self, key: str) -> List:
        return self.__dict__.get(key, List())


@dataclass
class XmlRoot:
    """Represents the XML Root node of the Document"""

    _xml_declaration: Optional[dict] = field(repr=False, default_factory=lambda: {
        "version": "1.0",
        "encoding": "UTF-8",
    })

    _Suffix: Optional[str] = field(repr=False, default=None)
    _Directory: Optional[str] = field(repr=False, default=None)
    _TypeName: Optional[str] = field(repr=False, default=None)


def get_value(metadata: XmlNode, key: str) -> Any:
    return metadata.__dict__.get(key, None)

def get_list(metadata: XmlNode, key: str) -> Any:
    if key not in metadata.__dict__.keys():
        metadata.__dict__[key] = List()
    return metadata.__dict__[key]

def set_value(metadata: XmlNode, key: str, value: Any):
    metadata.__dict__[key] = value

def append_list(metadata: XmlNode, key: str, value: Any):
    if key not in metadata.__dict__.keys():
        metadata.__dict__[key] = List()
    metadata.__dict__[key].append(value)
