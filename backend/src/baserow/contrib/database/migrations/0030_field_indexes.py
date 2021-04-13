from django.db import migrations, connections
from django.conf import settings


def forward(apps, schema_editor):
    connection = connections[settings.USER_TABLE_DATABASE]
    cursor = connection.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0029_phonenumberfield'),
    ]

    operations = [
        migrations.RunPython(forward, migrations.RunPython.noop),
    ]
