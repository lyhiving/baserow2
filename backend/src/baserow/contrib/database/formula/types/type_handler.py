import abc
from typing import TypeVar, Generic, List, Type

from baserow.contrib.database.fields.models import FormulaField
from baserow.core.registry import Instance, ModelInstanceMixin

T = TypeVar("T")


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
    def user_overridable_formatting_option_fields(self) -> List[str]:
        return []

    @property
    def internal_fields(self) -> List[str]:
        return []

    def all_fields(self):
        return self.user_overridable_formatting_option_fields + self.internal_fields

    def persist_onto_formula_field(self, instance: T, formula_field: FormulaField):
        formula_field.formula_type = self.type
        for field_name in self.user_overridable_formatting_option_fields:
            # Only set the calculated type formatting options if the user has not
            # already set them.
            if getattr(formula_field, field_name) is None:
                setattr(formula_field, field_name, getattr(instance, field_name))

        # TODO Knowledge of error shouldn't be hardcoded here perhaps
        formula_field.error = None
        for field_name in self.internal_fields:
            setattr(formula_field, field_name, getattr(instance, field_name))

    def overwrite_type_options_with_user_defined_ones(
        self, instance: T, formula_field: FormulaField
    ):
        formula_field.formula_type = self.type
        for field_name in self.user_overridable_formatting_option_fields:
            if getattr(formula_field, field_name) is not None:
                setattr(instance, field_name, getattr(formula_field, field_name))

    def construct_type_from_formula_field(self, formula_field: FormulaField) -> T:
        kwargs = {}
        for field_name in self.all_fields():
            kwargs[field_name] = getattr(formula_field, field_name)
        return self.model_class(**kwargs)