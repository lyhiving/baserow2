import pytest

# noinspection PyPep8Naming
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db import DEFAULT_DB_ALIAS
from django.core.management import call_command

migrate_from = [("core", "0008_trash")]
migrate_to = [("core", "0009_user_file_unique_together")]


# noinspection PyPep8Naming
@pytest.mark.django_db
def test_migration_fixes_duplicate_original_name_and_sha256_hash(transactional_db):
    old_state = migrate(migrate_from)
    UserFile = old_state.apps.get_model("core", "UserFile")

    user_files = [
        # original_name, sha256_hash, expected original_name after migrate
        ["test_1.jpg", "a", "test_1.jpg"],
        ["test_1.jpg", "a", "test_1 2.jpg"],
        ["test_1.jpg", "a", "test_1 3.jpg"],
        ["test_1.jpg", "b", "test_1.jpg"],
        # 255 chars is the limit of the original name and it must net exceed that
        # length.
        [f"{'a' * 251}.jpg", "c", f"{'a' * 251}.jpg"],
        [f"{'a' * 251}.jpg", "c", f"{'a' * 249} 2.jpg"],
        [f"{'a' * 251}.jpg", "c", f"{'a' * 249} 3.jpg"],
        ["without_extension", "d", "without_extension"],
        ["without_extension", "d", "without_extension 2"],
        ["without_extension", "d", "without_extension 3"],
        [f"{'a' * 255}", "d", f"{'a' * 255}"],
        [f"{'a' * 255}", "d", f"{'a' * 253} 2"],
        [f"{'a' * 255}", "d", f"{'a' * 253} 3"],
    ]
    for u in user_files:
        UserFile.objects.create(
            original_name=u[0],
            sha256_hash=u[1],
            uploaded_by=None,
            mime_type="",
            size=0,
            unique="a",
        )

    new_state = migrate(migrate_to)
    UserFile = new_state.apps.get_model("core", "UserFile")
    fetched_user_files = list(UserFile.objects.all().order_by("id"))

    for index, u in enumerate(user_files):
        assert fetched_user_files[index].original_name == u[2]

    # We need to apply the latest migration otherwise other tests might fail.
    call_command("migrate", verbosity=0, database=DEFAULT_DB_ALIAS)


def migrate(target):
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()  # reload.
    executor.migrate(target)
    new_state = executor.loader.project_state(target)
    return new_state
