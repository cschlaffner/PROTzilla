from __future__ import annotations
from enum import Enum
import json
from dataclasses import asdict, dataclass, field
from typing import List, Dict, Union, TYPE_CHECKING

# to avoid circular imports
if TYPE_CHECKING:
    from backend.protzilla.run import Run
    

@dataclass
class _baseInputField:
    name: str
    label: str
    value: object
    type: str
    isvisible: bool = True


@dataclass
class TextField(_baseInputField):
    type: str = "text"


@dataclass
class NumberField(_baseInputField):
    type: str = "number"
    min: int|None = None
    max: int|None = None
    step: float = 1


@dataclass
class SearchField(_baseInputField):
    type: str = "search"


@dataclass
class RadioSelectField(_baseInputField):
    type: str = "radio-select"


@dataclass
class CheckboxField(_baseInputField):
    type: str = "checkbox-select"


@dataclass
class MultiSelectField(_baseInputField):
    type: str = "multi-select"


@dataclass
class DropdownField(_baseInputField):
    options: Dict[str, str] = field(default_factory=dict)
    type: str = "dropdown"


@dataclass
class FileInput(_baseInputField):
    type: str = "file"


InputField = Union[TextField, NumberField, SearchField, RadioSelectField, CheckboxField, MultiSelectField, DropdownField, FileInput]


@dataclass
class Form:
    label: str
    fields: List[InputField]    
    isAutoSubmit: bool = True

    def __post_init__(self):
        "create a field map for easy access by fieldname"

        self.field_map = {field.name: field for field in self.fields}

    def modify_form(self, run:Run) -> None:
        "to be implemented by the step"
        pass

    def update_values(self, run:Run, values: Dict[str, str] = {}) -> None:
        "insert new values into the form"

        if values:
            for field in self.fields:
                if (values.get(field.name) is not None):
                    field.value = values.get(field.name, field.value)
        
        self.modify_form(run)
    
    @property
    def values(self) -> Dict[str, str]:
        return {field.name: field.value for field in self.fields}

    class CustomEncoder(json.JSONEncoder):
        """Custom JSON encoder that handles Enum classes and functions"""
        def default(self, obj):
            #serialize functions
            if callable(obj) and type(obj) != type(Enum):
                return obj()
            
            # Serialize Enums as their values
            if isinstance(obj, Enum):
                return obj.value
            
            # Serialize Enum class as dict
            if type(obj) == type(Enum):
                return {item.name: item.value for item in obj}
            
            return super().default(obj)