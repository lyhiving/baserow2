from baserow_premium.license.handler import active_premium_user_registry


class PremiumFixtures:
    def create_user(self, *args, **kwargs):
        has_active_premium_license = kwargs.pop("has_active_premium_license", False)
        user = super().create_user(*args, **kwargs)

        if has_active_premium_license:
            self.create_active_premium_license_for_user(user)

        return user

    def create_active_premium_license_for_user(self, user):
        """
        This is a temporary way of marking that the user has a valid premium license.
        It will be removed in a future merge requests and replaced by creating an
        actual license object that's valid until somewhere in the year 2999.
        """

        active_premium_user_registry[user.id] = True

    def remove_all_active_premium_licenses(self, user):
        active_premium_user_registry[user.id] = False
