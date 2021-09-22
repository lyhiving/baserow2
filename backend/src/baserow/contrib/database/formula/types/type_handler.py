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

        for field_name in self.internal_fields:
            setattr(formula_field, field_name, getattr(instance, field_name))

    def new_type_with_user_and_calculated_options_merged(
        self, instance: T, formula_field: FormulaField
    ):
        kwargs = {}
        for field_name in self.user_overridable_formatting_option_fields:
            override_set_by_user = getattr(formula_field, field_name)
            if override_set_by_user is not None:
                kwargs[field_name] = override_set_by_user
            else:
                kwargs[field_name] = getattr(instance, field_name)
        for field_name in self.internal_fields:
            kwargs[field_name] = getattr(instance, field_name)
        return self.model_class(**kwargs)

    def construct_type_from_formula_field(self, formula_field: FormulaField) -> T:
        kwargs = {}
        for field_name in self.all_fields():
            kwargs[field_name] = getattr(formula_field, field_name)
        return self.model_class(**kwargs)
