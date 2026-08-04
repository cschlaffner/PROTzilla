"""
Guards against form fields whose values cannot be serialized by CustomEncoder whenever get_step_form is called.
"""

from dataclasses import dataclass

from datetime import datetime
from pathlib import PurePath, PurePosixPath

import collections.abc
import json
import pytest
import types
import typing
from enum import Enum

from backend.protzilla.form import (
    DropdownField,
    FileInput,
    Form,
    Option,
    RadioSelectField,
    _baseField,
)

# These are the types that need to be serialized by CustomEncoder when get_step_form is called. If this set is extended,
# make sure that CustomEncoder can handle it as well.
ALLOWED_LEAVES = {str, int, float, bool, type(None), list, dict, PurePath}


def all_field_classes(root=_baseField):
    """Recursively collect every loaded subclass of ``_baseField``."""
    seen = set()
    stack = [root]
    while stack:
        for sub in stack.pop().__subclasses__():
            if sub not in seen:
                seen.add(sub)
                stack.append(sub)
    return seen


def leaf_types(annotation) -> set:
    """Flatten an annotation (unions, generics) into its set of leaf types."""
    origin = typing.get_origin(annotation)
    if origin in (typing.Union, types.UnionType):  # e.g. str | None
        return set().union(*(leaf_types(a) for a in typing.get_args(annotation)))
    if origin in (list, collections.abc.Sequence):  # e.g. list[str]
        leaves = {list}
        for arg in typing.get_args(annotation):
            leaves.update(leaf_types(arg))
        return leaves
    if origin is not None:  # any other parameterized generic
        return {origin}
    # Is a primitive or non-generic class (e.g. str, PurePath)
    return {annotation}


@pytest.mark.parametrize("field_cls", all_field_classes(), ids=lambda c: c.__name__)
def test_field_value_types_are_serializable(field_cls):
    # get_type_hints resolves the string annotations produced by `from __future__ import annotations` in form.py, using
    # the module globals where PurePath/Enum/etc. are imported.
    hints = typing.get_type_hints(field_cls)
    assert "value" in hints, f"{field_cls.__name__} has no 'value' annotation"

    unknown = leaf_types(hints["value"]) - ALLOWED_LEAVES
    assert not unknown, (
        f"{field_cls.__name__}.value may contain {unknown}, which the form's CustomEncoder does not handle. Either "
        "add encoder support and extend ALLOWED_LEAVES, or change the field's value type."
    )


@dataclass
class MockDateTimeField:
    name: str
    label: str
    type: str = "datetime"
    value: datetime = datetime.now()
    isVisible: bool = True


def test_datetime_field_fails_encoding():
    field = MockDateTimeField(name="field", label="Field")
    assert type(field.value) not in ALLOWED_LEAVES
    with pytest.raises(TypeError, match="is not JSON serializable"):
        json.dumps(field, cls=Form.CustomEncoder)


@pytest.mark.parametrize("field_cls", all_field_classes(), ids=lambda c: c.__name__)
def test_default_fields_round_trip_through_encoder(field_cls):
    """Every field, built with its defaults, must survive json.dumps."""
    field = field_cls(name="field", label="Field")
    json.dumps(field, cls=Form.CustomEncoder)


class _SampleEnum(Enum):
    A = "a"
    B = "b"


def _dumps(field) -> str:
    return json.dumps(field, cls=Form.CustomEncoder)


def test_enum_instance_value_round_trips():
    field = RadioSelectField(name="f", label="F", value=_SampleEnum.A)
    assert json.loads(_dumps(field))["value"] == "a"


def test_enum_class_as_options_round_trips():
    field = DropdownField(name="f", label="F", options=_SampleEnum)
    options = json.loads(_dumps(field))["options"]
    assert {"value": "A", "label": "a"} in options


def test_purepath_value_round_trips():
    field = FileInput(name="f", label="F", value=PurePosixPath("/tmp/data/x.csv"))
    assert json.loads(_dumps(field))["value"] == "x.csv"


def test_option_dataclass_round_trips():
    field = DropdownField(name="f", label="F", options=[Option("v", "Label")])
    assert json.loads(_dumps(field))["options"][0] == {"value": "v", "label": "Label"}
