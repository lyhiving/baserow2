import abc
from typing import TypeVar, Generic, List, Type

from baserow.contrib.database.fields.models import FormulaField
from baserow.core.registry import Instance, ClsInstanceMixin

T = TypeVar("T")


class BaserowFormulaTypeType(ClsInstanceMixin, Instance, abc.ABC, Generic[T]):
    @property
    def type(self) -> str:
        return self.cls.type

    @property
    @abc.abstractmethod
    def cls(self) -> Type[T]:
        pass

    @property
    def user_overridable_formatting_option_fields(self) -> List[str]:
        """
        :return: The list of FormulaField model field names which control
        formatting for a formula field of this type and should be allowed to be
        controlled and set by a user.
        """

        return []

    @property
    def internal_fields(self) -> List[str]:
        """
        :return: The list of FormulaField model field names which store internal
        information required for a formula of this type.
        """

        return []

    def all_fields(self):
        """
        :returns All FormulaField model field names required for a formula field of
        this type.
        """

        return self.user_overridable_formatting_option_fields + self.internal_fields

    def persist_onto_formula_field(self, instance: T, formula_field: FormulaField):
        """
        Takes a BaserowFormulaType instance and saves it onto the provided formula_field
        instance for later retrieval. Sets the attributes on the formula_field required
        for this formula type and unsets all other formula types attributes. Does not
        save the formula_field.

        :param instance: The instance to store.
        :param formula_field: The formula field to store the type information onto.
        """

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
        """
        Generates a new merged BaserowFormulaType instance from what has been set on the
        formula field and the provided instance of the type. Fields which are set on
        this types user_overridable_formatting_option_fields will be taken from the
        FormulaField instance if set there, otherwise the values from the type instance
        will be used.

        :param instance: The calculated type instance to use values from when not set on
            the formula field.
        :param formula_field: The formula field to get any type option overrides set by
            the user from.
        :return: A new merged object of the formula type using values from both the
            instance and if set values also from the formula field.
        """

        kwargs = {}
        for field_name in self.user_overridable_formatting_option_fields:
            override_set_by_user = getattr(formula_field, field_name)
            if override_set_by_user is not None:
                kwargs[field_name] = override_set_by_user
            else:
                kwargs[field_name] = getattr(instance, field_name)
        for field_name in self.internal_fields:
            kwargs[field_name] = getattr(instance, field_name)
        return self.cls(**kwargs)

    def construct_type_from_formula_field(self, formula_field: FormulaField) -> T:
        """
        Creates a BaserowFormulaType instance based on what is set on the formula field.
        :param formula_field: The formula field to get type info from.
        :return: A new BaserowFormulaType.
        """

        kwargs = {}
        for field_name in self.all_fields():
            kwargs[field_name] = getattr(formula_field, field_name)
        return self.cls(**kwargs)
