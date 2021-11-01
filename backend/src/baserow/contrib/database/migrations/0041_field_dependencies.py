# Generated by Django 3.2.6 on 2021-11-01 09:38

from django.db import migrations, models
import django.db.models.deletion


def calc():
    return True


def calc_and_build_graph():
    return "a"


# noinspection PyPep8Naming
def forward(apps, schema_editor):
    FormulaField = apps.get_model("database", "FormulaField")

    for formula in FormulaField.objects.all():
        formula.requires_refresh_after_insert = calc()
        formula.internal_formula = calc_and_build_graph()
        formula.save()


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0040_formulafield_remove_field_by_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="FieldDependencyEdge",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="formulafield",
            name="internal_formula",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="formulafield",
            name="requires_refresh_after_insert",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="FieldDependencyNode",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "broken_reference_field_name",
                    models.TextField(blank=True, null=True),
                ),
                (
                    "children",
                    models.ManyToManyField(
                        blank=True,
                        related_name="parents",
                        through="database.FieldDependencyEdge",
                        to="database.FieldDependencyNode",
                    ),
                ),
                (
                    "field",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nodes",
                        to="database.field",
                    ),
                ),
                (
                    "table",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nodes",
                        to="database.table",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="fielddependencyedge",
            name="child",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="parent_edges",
                to="database.fielddependencynode",
            ),
        ),
        migrations.AddField(
            model_name="fielddependencyedge",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children_edges",
                to="database.fielddependencynode",
            ),
        ),
        migrations.AddField(
            model_name="fielddependencyedge",
            name="via",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vias",
                to="database.field",
            ),
        ),
        migrations.RunPython(forward, None),
        migrations.AlterField(
            model_name="formulafield",
            name="internal_formula",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="formulafield",
            name="requires_refresh_after_insert",
            field=models.BooleanField(),
        ),
    ]
