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
        starting_row_id=None,
    ):
        super().__init__(existing_field_lookup_cache)
        self.updated_fields_per_table = {}
        self.starting_row_id = starting_row_id

        self.update_statements_per_path = None

    def add_updated_field(self, field):
        table_id = field.table.id
        table_fields = self.updated_fields_per_table.setdefault(table_id, {})
        table_fields[field.id] = field

    def add_field_with_pending_update_statement(
        self,
        field,
        update_statement,
        via_path,
    ):
        self.add_updated_field(field)
        d = self.update_statements_per_path
        if d is None:
            d = self.update_statements_per_path = {
                "updates": {},
                "table": field.table,
                "path": None,
                "sub_paths": {},
            }
        path = []
        for p in via_path:
            path = [p.db_column] + path
            d = d["sub_paths"].setdefault(
                p.db_column,
                {"updates": {}, "table": field.table, "path": path, "sub_paths": {}},
            )
        d["updates"][field.db_column] = update_statement

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

    def apply_updates(self):
        if self.update_statements_per_path is None:
            return
        pending = [self.update_statements_per_path]
        while len(pending) > 0:
            current = pending.pop(0)
            updates = current["updates"]
            if updates.keys():
                model = self.get_model(current["table"])
                qs = model.objects_and_trash
                path = current["path"]
                if self.starting_row_id is not None and path is not None:
                    id_path = path + "__id"
                    qs = qs.filter(**{id_path: self.starting_row_id})
                qs.update(**updates)
            pending += current["sub_paths"].values()
