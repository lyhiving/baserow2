from baserow.contrib.database.views.handler import ViewHandler


class GridViewHandler:
    def get_rows(self, user, view, search):
        view.table.database.group.has_user(
            user, raise_error=True, allow_if_template=True
        )
        view_handler = ViewHandler()
        model = view.table.get_model()
        queryset = model.objects.all().enhance_by_fields()

        # Applies the view filters and sortings to the queryset if there are any.
        queryset = view_handler.apply_filters(view, queryset)
        queryset = view_handler.apply_sorting(view, queryset)
        if search:
            queryset = queryset.search_all_fields(search)
        return queryset
