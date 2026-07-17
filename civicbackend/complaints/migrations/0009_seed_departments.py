from django.db import migrations


DEPARTMENTS = [
    ("streetlight", "streetlight@example.com", "0000000000", "Streetlight Department"),
    ("potholes", "potholes@example.com", "0000000000", "Potholes Department"),
    ("trash_bins", "trash@example.com", "0000000000", "Garbage Department"),
    ("water_leakage", "water@example.com", "0000000000", "Water Leakage Department"),
]


def seed_departments(apps, schema_editor):
    Department = apps.get_model("complaints", "Department")
    for name, email, phone, description in DEPARTMENTS:
        Department.objects.update_or_create(
            name=name,
            defaults={
                "email": email,
                "phone": phone,
                "description": description,
            },
        )


def unseed_departments(apps, schema_editor):
    Department = apps.get_model("complaints", "Department")
    Department.objects.filter(name__in=[name for name, *_ in DEPARTMENTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("complaints", "0008_complaint_user_email"),
    ]

    operations = [
        migrations.RunPython(seed_departments, unseed_departments),
    ]
