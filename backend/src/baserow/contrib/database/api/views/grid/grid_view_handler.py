from baserow.contrib.database.views.handler import ViewHandler


class GridViewHandler:
    def get_rows(self, user, view, search, exclude_hidden_fields=False):
        view.table.database.group.has_user(
            user, raise_error=True, allow_if_template=True
        )
        view_handler = ViewHandler()
        model = view.table.get_model()
        queryset = model.objects.all().enhance_by_fields()

        if exclude_hidden_fields:
            visible_field_db_names_with_order = [
                f"field_{field_id}"
                for field_id in list(
                    view.get_field_options()
                    .filter(hidden=False)
                    .order_by("field__order")
                    .values_list("field__id", flat=True)
                )
            ]

            visible_field_db_names_with_order.insert(0, "id")
            queryset = queryset.values(*visible_field_db_names_with_order)

        # Applies the view filters and sortings to the queryset if there are any.
        queryset = view_handler.apply_filters(view, queryset)
        queryset = view_handler.apply_sorting(view, queryset)
        if search:
            queryset = queryset.search_all_fields(search)
        return queryset
