from collections import OrderedDict
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist


class LookupFieldByIdCache:
    def __init__(self):
        self.cached_field_by_id = {}

    def cache_field(self, field):
        if not field.trashed:
            self.cached_field_by_id[field.id] = field

    def lookup(self, table, field_name: str):
        try:
            return self.cached_field_by_name_per_table[table.id][field_name]
        except KeyError:
            try:
                field = table.field_set.get(name=field_name).specific
                self.cache_field(field)
                return field
            except ObjectDoesNotExist:
                return None


class LookupFieldByNameCache:
    def __init__(self, existing_cache: Optional["LookupFieldByNameCache"] = None):
        if existing_cache is not None:
            self.cached_field_by_name_per_table = (
                existing_cache.cached_field_by_name_per_table
            )
        else:
            self.cached_field_by_name_per_table = {}

    def cache_field(self, field):
        if not field.trashed:
            table_id = field.table.id
            self.cached_field_by_name_per_table.setdefault(table_id, {})
            self.cached_field_by_name_per_table[table_id][field.name] = field

    def lookup(self, table, field_name: str):
        try:
            return self.cached_field_by_name_per_table[table.id][field_name]
        except KeyError:
            try:
                field = table.field_set.get(name=field_name).specific
                self.cache_field(field)
                return field
            except ObjectDoesNotExist:
                return None


class FieldUpdateCollector(LookupFieldByNameCache):
    def __init__(self, existing_field_lookup_cache=None):
        super().__init__(existing_field_lookup_cache)
        self.updated_fields_per_table = {}
        self.ordered_updated_and_old_fields = OrderedDict()

    def add_field(self, field, old_field):
        table_id = field.table.id
        table_fields = self.updated_fields_per_table.setdefault(table_id, [])
        table_fields.append(field)
        self.cache_field(field)
        self.ordered_updated_and_old_fields[field.id] = field, old_field

    def get_updated_fields_per_table(self):
        return [
            (fields[0], fields[1:]) for fields in self.updated_fields_per_table.values()
        ]

    def for_table(self, table):
        updated_fields = self.updated_fields_per_table.get(table.id, [])
        return updated_fields[1:]
