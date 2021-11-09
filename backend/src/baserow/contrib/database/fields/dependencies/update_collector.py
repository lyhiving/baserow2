from typing import Optional

from baserow.contrib.database.fields.field_cache import FieldCache


class CachingFieldUpdateCollector(FieldCache):
    """
    An extended FieldCache which also keeps track of fields which have been specifically
    marked as updated. Used so field graph updates can collect together the entire
    set of changed fields to report back to the user.
    """

    def __init__(
        self,
        existing_field_lookup_cache: Optional[FieldCache] = None,
    ):
        super().__init__(existing_field_lookup_cache)
        self.updated_fields_per_table = {}

    def add_updated_field(self, field):
        table_id = field.table.id
        table_fields = self.updated_fields_per_table.setdefault(table_id, {})
        table_fields[field.id] = field

    def field_has_been_updated(self, field):
        return field.id in self.updated_fields_per_table.get(field.table_id, {})

    def get_updated_fields_per_table(self):
        result = []
        for fields_dict in self.updated_fields_per_table.values():
            fields = list(fields_dict.values())
            result.append((fields[0], fields[1:]))
        return result

    def for_table(self, table):
        updated_fields = list(self.updated_fields_per_table.get(table.id, {}).values())
        return updated_fields[1:]
