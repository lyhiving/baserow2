from baserow.contrib.database.views.handler import ViewHandler


class GridViewHandler:
    def get_rows(self, user, view, model, search):
        """
        A behalf of a requesting_user returns all rows sorted, filtered and searched
        for a grid view.
        :param user: The user who is requesting to view the rows, will raise exceptions
           if they do not have the required permissions.
        :param view: The view to lookup rows for.
        :param search: A search term to apply over the rows.
        :return: The filtered, sorted and searched row queryset for the view.
        """

        view.table.database.group.has_user(
            user, raise_error=True, allow_if_template=True
        )
        view_handler = ViewHandler()
        queryset = model.objects.all().enhance_by_fields()

        # Applies the view filters and sortings to the queryset if there are any.
        queryset = view_handler.apply_filters(view, queryset)
        queryset = view_handler.apply_sorting(view, queryset)
        if search:
            queryset = queryset.search_all_fields(search)
        return queryset
