from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_order_address_order_email'),
    ]

    operations = [
        # ── Category: add parent FK ────────────────────────────
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                help_text='Leave blank for top-level categories. Select a parent to make this a subcategory.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subcategories',
                to='store.category',
            ),
        ),
        # ── Category: add order field ──────────────────────────
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Controls display order in the navigation menu (lower = first).',
            ),
        ),
        # ── Category: set Meta ordering ────────────────────────
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order', 'name'], 'verbose_name_plural': 'Categories'},
        ),
        # ── ProductImage: add order field ─────────────────────
        migrations.AddField(
            model_name='productimage',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Display order (lower = first).',
            ),
        ),
        # ── ProductImage: set Meta ordering ───────────────────
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ['order']},
        ),
    ]
