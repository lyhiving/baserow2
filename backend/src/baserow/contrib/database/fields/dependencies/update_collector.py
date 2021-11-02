from collections import OrderedDict


class FieldUpdateCollector:
    def __init__(self):
        self.tables_with_updated_fields = {}
        self.fields = OrderedDict()

    def add_field(self, field, old_field):
        table_fields = self.tables_with_updated_fields.setdefault(field.table.id, [])
        table_fields.append(field)
        self.fields[field.id] = field, old_field

    def for_table(self, table):
        return self.tables_with_updated_fields[table.id]


