from collections import defaultdict
from typing import Optional

from baserow.contrib.database.fields.field_cache import FieldCache
from baserow.contrib.database.fields.signals import field_updated
from baserow.contrib.database.table.models import GeneratedTableModel


class CachingFieldUpdateCollector(FieldCache):
    """
    An extended FieldCache which also keeps track of fields which have been specifically
    marked as updated. Used so field graph updates can collect together the entire
    set of changed fields to report back to the user.
    """

    def __init__(
        self,
        starting_table,
        existing_field_lookup_cache: Optional[FieldCache] = None,
        existing_model: Optional[GeneratedTableModel] = None,
        starting_row_id=None,
    ):
        super().__init__(existing_field_lookup_cache, existing_model)
        self._updated_fields_per_table = defaultdict(dict)
        self._starting_row_id = starting_row_id
        self._starting_table = starting_table

        self._update_statements_per_path = {
            "updates": {},
            "table": starting_table,
            "path": [],
            "sub_paths": {},
        }

    def add_field_with_pending_update_statement(
        self,
        field,
        update_statement,
        via_path=None,
    ):
        self._updated_fields_per_table[field.table_id][field.id] = field
        d = self._update_statements_per_path
        path = []
        for p in via_path or []:
            path = [p.db_column] + path
            d = d["sub_paths"].setdefault(
                p.db_column,
                {"updates": {}, "table": field.table, "path": path, "sub_paths": {}},
            )
        d["updates"][field.db_column] = update_statement

    def apply_updates(self):
        self._apply_updates()
        return self._for_table(self._starting_table)

    def send_additional_field_updated_signals(self):
        for field, related_fields in self._get_updated_fields_per_table():
            if field.table != self._starting_table:
                field_updated.send(
                    self,
                    field=field,
                    related_fields=related_fields,
                    user=None,
                )

    def _get_updated_fields_per_table(self):
        result = []
        for fields_dict in self._updated_fields_per_table.values():
            fields = list(fields_dict.values())
            result.append((fields[0], fields[1:]))
        return result

    def _for_table(self, table):
        return list(self._updated_fields_per_table.get(table.id, {}).values())

    def _apply_updates(self):
        pending = [self._update_statements_per_path]
        while len(pending) > 0:
            current = pending.pop(0)
            updates = current["updates"]
            if updates.keys():
                model = self.get_model(current["table"])
                qs = model.objects_and_trash
                path = "__".join(current["path"])
                if self._starting_row_id is not None:
                    if path == "":
                        id_path = "id"
                    else:
                        id_path = path + "__id"
                    qs = qs.filter(**{id_path: self._starting_row_id})
                qs.update(**updates)
            pending += current["sub_paths"].values()
