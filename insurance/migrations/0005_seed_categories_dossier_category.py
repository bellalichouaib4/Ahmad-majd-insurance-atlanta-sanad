from django.db import migrations


ATLANTA_SANAD_CATEGORIES = [
    ('3401', 'Automobile'),
    ('3601', 'Cyclo'),
    ('3101', 'Commerce C1'),
    ('3001', 'Commerce C2'),
    ('3501', 'Divers'),
    ('4308', 'Individuelle Accident'),
    ('2101', 'Accident Travail'),
    ('5106', 'MRP'),
    ('5131', 'RC Étudiant'),
    ('9202', 'Marchandise Transportée'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('insurance', 'Category')
    for code, name in ATLANTA_SANAD_CATEGORIES:
        Category.objects.get_or_create(code_categorie=code, defaults={'category_name': name})


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('insurance', 'Category')
    codes = [c[0] for c in ATLANTA_SANAD_CATEGORIES]
    Category.objects.filter(code_categorie__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0004_question'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
