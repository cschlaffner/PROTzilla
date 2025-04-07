from __future__ import annotations
from enum import Enum
import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, List, Dict, Union, TYPE_CHECKING

from backend.main import settings

# to avoid circular imports
if TYPE_CHECKING:
    from backend.protzilla.run import Run


@dataclass
class Option:
    """
    Options for the dropdown and multi-select fields.
    `value` is the value of the option, `label` is the label shown to the user.
    """
    value: str
    label: str

@dataclass
class _baseField:
    name: str
    label: str
    value: object
    type: str
    isVisible: bool = True


@dataclass
class TextField(_baseField):
    type: str = "text"


@dataclass
class NumberField(_baseField):
    type: str = "number"
    min: int|None = None
    max: int|None = None
    step: float = 1


@dataclass
class FloatField(_baseField):
    type: str = "number"
    min: int|None = None
    max: int|None = None
    step: float = 1


@dataclass
class SearchField(_baseField):
    type: str = "search"


@dataclass
class CheckboxField(_baseField):
    type: str = "checkbox"


@dataclass
class RadioSelectField(_baseField):
    type: str = "radio-select"


@dataclass
class CheckboxMultiSelectField(_baseField):
    type: str = "checkbox-select"


@dataclass
class MultiSelectField(_baseField):
    type: str = "multi-select"
    choices: List[str] = field(default_factory=list)


@dataclass
class DropdownField(_baseField):
    options: list[Option] | Enum = field(default_factory=list)
    type: str = "dropdown"


@dataclass
class MultiSelectWithDropdownsField(_baseField):
    type: str = "multi-select-dropdown"
    options: list[Option] | Enum = field(default_factory=dict)
    dropdown_choices: List[str] = field(default_factory=list)


@dataclass
class FileInput(_baseField):
    type: str = "file"
    filedata: str = ""


@dataclass
class FormDivider():
    """
    To separate the form into sections.
    `label` is the shown title of the section.
    """
    label: str
    type: str = "form-divider"

InputField = Union[TextField, NumberField, SearchField, RadioSelectField, CheckboxField, MultiSelectField, DropdownField, FileInput]
StructualField = Union[FormDivider]


@dataclass
class Form:
    label: str
    input_fields: List[InputField|StructualField]
    isAutoSubmit: bool = True

    def __post_init__(self):
        "create a field map for easy access by fieldname"

        self._field_map = {field.name: field for field in self.input_fields if isinstance(field, _baseField)}

    def modify_form(self, run:Run) -> None:
        """
        This method should be defined in Step classes to modify the form based on the current state of the run.
        """
        
        pass

    def update_values(self, values: Dict[str, Any]) -> None:
        "insert new values into the form"
        if values:
            for fieldname, value in values.items():
                self[fieldname].value = value
        
    def apply_modification(self, run:Run) -> None:
        self.modify_form(run)
    
    def __getitem__(self, fieldname: str) -> InputField:
        "to do form[fieldname] to get the field object"

        return self._field_map[fieldname]
    
    def __setitem__(self, fieldname: str, field: Any) -> None:
        "to do form[fieldname] = field to set the field object"
        
        if fieldname in self._field_map:
            self._field_map[fieldname] = field
    
    def __contains__(self, fieldname: str) -> bool:
        "to do fieldname in form to check if the field exists"
        
        return fieldname in self._field_map

    @property
    def values(self) -> Dict[str, str]:
        """
        Returns a dictionary with the values of the form fields.
        The keys are the field names and the values are the field values.
        if the field is a file input, the value is the temporary path to the file.
        """

        values = {}
        for field in self.input_fields:
            if isinstance(field, FormDivider):
                continue
            elif isinstance(field, FileInput):
                values[field.name] = (settings.FILE_UPLOAD_TEMP_DIR / field.value) if field.value else None
                print("Path", (settings.FILE_UPLOAD_TEMP_DIR / field.value) if field.value else None)
            elif isinstance(field.value, Enum):
                values[field.name] = field.value.value
            else:
                values[field.name] = field.value

        return values

    class CustomEncoder(json.JSONEncoder):
        "Custom JSON encoder that handles Enum classes and functions"

        def default(self, obj):
            #serialize functions
            if callable(obj) and type(obj) != type(Enum):
                return obj()
            
            if is_dataclass(obj):
                return asdict(obj)
            
            # Serialize Enums as their values
            if isinstance(obj, Enum):
                return obj.value
            
            # Serialize Enum class as dict
            if type(obj) == type(Enum):
                return [Option(item.name, item.value) for item in obj]
            
            return super().default(obj)