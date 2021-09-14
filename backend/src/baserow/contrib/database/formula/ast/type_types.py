import abc
from typing import Union, TypeVar, Generic, List, Type

from baserow.contrib.database.fields.models import Field, FormulaField
from baserow.contrib.database.formula.ast.type_defs import BaserowFormulaType
from baserow.core.registry import Instance, ModelInstanceMixin

UnTyped = type(None)

InvalidType = str
ValidType = Field
Typed = Union[InvalidType, ValidType]


T = TypeVar("T", bound=BaserowFormulaType)


class BaserowFormulaTypeHandler(ModelInstanceMixin, Instance, abc.ABC, Generic[T]):
    @property
    @abc.abstractmethod
    def type(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def model_class(self) -> Type[T]:
        pass

    @property
    @abc.abstractmethod
    def allowed_fields(self) -> List[str]:
        pass

    def persist_onto_formula_field(self, instance: T, formula_field: FormulaField):
        formula_field.formula_type = self.type
        for field_name in self.allowed_fields:
            setattr(formula_field, field_name, getattr(instance, field_name))

    def construct_type_from_formula_field(self, formula_field: FormulaField) -> T:
        kwargs = {}
        for field_name in self.allowed_fields:
            kwargs[field_name] = getattr(formula_field, field_name)
        return self.model_class(**kwargs)
