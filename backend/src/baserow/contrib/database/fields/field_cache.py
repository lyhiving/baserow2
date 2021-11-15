from typing import Optional

from django.core.exceptions import ObjectDoesNotExist


class FieldCache:
    """
    A cache which can be used to get the specific version of a field given a
    non-specific version or to get a field using a table and field name. If a cache
    miss occurs it will actually lookup the field from the database, cache it and
    return it, otherwise if the field does not exist None will be returned.

    Trashed fields are excluded from the cache.
    """

    def __init__(self, existing_cache: Optional["FieldCache"] = None):
        if existing_cache is not None:
            self.cached_field_by_name_per_table = (
                existing_cache.cached_field_by_name_per_table
            )
            self.model_cache = existing_cache.model_cache
        else:
            self.cached_field_by_name_per_table = {}
            self.model_cache = {}

    def cache_field(self, field):
        if not field.trashed:
            table_id = field.table_id
            self.cached_field_by_name_per_table.setdefault(table_id, {})
            self.cached_field_by_name_per_table[table_id][field.name] = field

    def get_model(self, table):
        table_id = table.id
        if table_id not in self.model_cache:
            self.model_cache[table_id] = table.get_model()
        return self.model_cache[table_id]

    def lookup_specific(self, non_specific_field):
        try:
            return self.cached_field_by_name_per_table[non_specific_field.table_id][
                non_specific_field.name
            ]
        except KeyError:
            try:
                field = non_specific_field.specific
                if field.trashed:
                    return None
                self.cache_field(field)
                return field
            except ObjectDoesNotExist:
                return None

    def lookup_by_name(self, table, field_name: str):
        try:
            return self.cached_field_by_name_per_table[table.id][field_name]
        except KeyError:
            try:
                field = table.field_set.get(name=field_name).specific
                if field.trashed:
                    # Inside migrations field_set wont be using the non trashed manager.
                    return None
                self.cache_field(field)
                return field
            except ObjectDoesNotExist:
                return None
