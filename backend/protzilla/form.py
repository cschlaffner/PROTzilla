from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
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

    def __lt__(self, other):
        return self.label < other.label

    def __eq__(self, other):
        if isinstance(other, Option):
            return self.value == other.value and self.label == other.label
        return False


@dataclass
class _baseField:
    name: str
    label: str
    value: object
    type: str
    # Camel case for frontend compatibility
    isVisible: bool = True


@dataclass
class TextField(_baseField):
    type: str = "text"
    value: str = ""


@dataclass
class NumberField(_baseField):
    type: str = "number"
    min: int | None = None
    max: int | None = None
    step: float = 1
    value: int = 0
    isInteger: bool = True
    hasStepButtons: bool = False
    separatePrefix: str | None = None
    separateSuffix: str | None = None


@dataclass
class FloatField(_baseField):
    type: str = "number"
    min: float | None = None
    max: float | None = None
    step: float = 1
    value: float = 0.0
    isInteger: bool = False
    hasStepButtons: bool = True
    separatePrefix: str | None = None
    separateSuffix: str | None = None


@dataclass
class SearchField(_baseField):
    type: str = "search"
    placeholder: str = ""
    value: str = ""


@dataclass
class CheckboxField(_baseField):
    type: str = "single-checkbox"
    text: str = ""  # text shown next to the checkbox
    value: bool = False


@dataclass
class RadioSelectField(_baseField):
    type: str = "radio-select"
    options: list[Option] | Enum = field(default_factory=list)
    value: str | None = None


@dataclass
class CheckboxMultiSelectField(_baseField):
    type: str = "checkbox-select"
    options: list[Option] | Enum = field(default_factory=list)
    value: list[str] = field(default_factory=list)


@dataclass
class MultiSelectField(_baseField):
    type: str = "multi-select"
    options: List[Option] = field(default_factory=list)
    value: list[str] = field(default_factory=list)

    def set_options(self, options: list[Option] | Enum) -> None:
        if sorted(options) != sorted(self.options):
            self.options = options
            self.value = []


@dataclass
class DropdownField(_baseField):
    type: str = "dropdown"
    options: list[Option] | Enum = field(default_factory=list)
    value: str | None = None

    def set_options(self, options: list[Option] | Enum) -> None:
        self.options = options
        if options == []:
            self.value = None
        elif options and self.value not in map(lambda o: o.value, options):
            self.value = options[
                0
            ].label  # TODO should be value not label -> see frontend


@dataclass
class MultiSelectWithDropdownsField(_baseField):
    type: str = "multi-select-dropdown"
    value: list[str] = field(default_factory=list)
    options: list[Option] | Enum = field(default_factory=list)
    dropdown_options: List[str] = field(default_factory=list)


@dataclass
class FileInput(_baseField):
    value: str | None = None
    type: str = "file"
    filedata: str = ""


@dataclass
class FormDivider:
    """
    To separate the form into sections.
    `label` is the shown title of the section.
    """

    label: str
    type: str = "form-divider"


@dataclass
class InfoField:
    """
    A field to show additional information for a specific field to the user.
    """

    label: str
    type: str = "info-field"


@dataclass
class HeaderInfoField:
    """
    A field to show additional information to the user at the top of the form.
    """

    label: str
    type: str = "header-info-field"


InputField = Union[
    TextField,
    NumberField,
    SearchField,
    RadioSelectField,
    CheckboxField,
    MultiSelectField,
    DropdownField,
    FileInput,
    FloatField,
]
StructuralField = Union[FormDivider, InfoField, HeaderInfoField]


@dataclass
class Form:
    label: str
    input_fields: List[InputField | StructuralField]
    isAutoSubmit: bool = True

    def __post_init__(self):
        "create a field map for easy access by fieldname"

        self._field_map = {
            field.name: field
            for field in self.input_fields
            if isinstance(field, _baseField)
        }

    def modify_form(self, run: Run) -> None:
        """
        This method should be defined in Step classes to modify the form based on the current state of the run.
        """

        pass

    def update_values(self, values: Dict[str, Any]) -> None:
        "insert new values into the form"
        if values:
            for fieldname, value in values.items():
                self[fieldname].value = value

    def apply_modification(self, run: Run) -> None:
        self.modify_form(run)

    def add_field(self, new_field: InputField):
        self.input_fields.append(new_field)
        self._field_map[new_field.name] = new_field

    def __getitem__(self, fieldname: str) -> InputField:
        "to do form[fieldname] to get the field object"

        if fieldname not in self._field_map:
            raise KeyError(f"Field '{fieldname}' not found in form.")

        return self._field_map[fieldname]

    def __setitem__(self, fieldname: str, field: Any) -> None:
        "to do form[fieldname] = field to set the field object"

        if fieldname in self._field_map:
            self._field_map[fieldname] = field

    def __contains__(self, fieldname: str) -> bool:
        "to do fieldname in form to check if the field exists"

        return fieldname in self._field_map

    def __iter__(self):
        return self.input_fields

    @property
    def values(self) -> Dict[str, str]:
        """
        Returns a dictionary with the values of the form fields.
        The keys are the field names and the values are the field values.
        if the field is a file input, the value is the temporary path to the file.
        """

        values = {}
        for field in self.input_fields:
            if (
                isinstance(field, FormDivider)
                or isinstance(field, InfoField)
                or isinstance(field, HeaderInfoField)
            ):
                continue
            elif isinstance(field, FileInput):
                values[field.name] = (
                    (settings.FILE_UPLOAD_TEMP_DIR / field.value)
                    if field.value
                    else None
                )
            elif isinstance(field.value, Enum):
                values[field.name] = field.value.value
            else:
                values[field.name] = field.value

        return values

    class CustomEncoder(json.JSONEncoder):
        "Custom JSON encoder that handles Enum classes and functions"

        def default(self, obj):
            # serialize functions
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
