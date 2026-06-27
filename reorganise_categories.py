"""
WEMISI – Category Reorganisation Script
Restructures the flat category list into 4 major parent groups
with their subcategories as defined in the navigation proposal.

Run with:
    python manage.py shell < reorganise_categories.py
"""
from store.models import Category

# ── Helper: get-or-create a category by slug ──────────────────────────────
def upsert(name, slug, parent=None, order=0):
    cat, created = Category.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'parent': parent, 'order': order}
    )
    if not created:
        cat.name = name
        cat.parent = parent
        cat.order = order
        cat.save()
    status = "CREATED" if created else "UPDATED"
    print(f"  [{status}] {cat}")
    return cat


print("\n══════════════════════════════════════════════")
print(" WEMISI – Reorganising Navigation Categories")
print("══════════════════════════════════════════════\n")

# ─────────────────────────────────────────────────────────────────────────────
# 1.  PARENT: Construction & Engineering  (order=1)
# ─────────────────────────────────────────────────────────────────────────────
print("▶  Creating parent: Construction & Engineering")
construction = upsert(
    name="Construction & Engineering",
    slug="construction-engineering",
    parent=None,
    order=1,
)

# Move / link existing categories as subcategories
print("   └─ Subcategories:")
upsert("Block Making Machines & Cabro", "block-making-machines-cabro",  parent=construction, order=1)
upsert("Hardware and Metal Work",       "hardware-and-metal-work",       parent=construction, order=2)
upsert("Major Projects and Engineering","major-projects-and-engineering", parent=construction, order=3)
upsert("Interior Design",               "interior-design",               parent=construction, order=4)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  PARENT: Mining & Heavy Equipment  (order=2)
# ─────────────────────────────────────────────────────────────────────────────
print("\n▶  Creating parent: Mining & Heavy Equipment")
mining = upsert(
    name="Mining & Heavy Equipment",
    slug="mining-heavy-equipment",
    parent=None,
    order=2,
)

print("   └─ Subcategories:")
upsert("Drilling Equipments", "drilling-equipments", parent=mining, order=1)
upsert("Jaw Crusher",         "jaw-crusher",         parent=mining, order=2)
upsert("Mining",              "mining",              parent=mining, order=3)


# ─────────────────────────────────────────────────────────────────────────────
# 3.  PARENT: Stones & Raw Materials  (order=3)
# ─────────────────────────────────────────────────────────────────────────────
print("\n▶  Creating parent: Stones & Raw Materials")
stones = upsert(
    name="Stones & Raw Materials",
    slug="stones-raw-materials",
    parent=None,
    order=3,
)

print("   └─ Subcategories:")
upsert("Granite",                   "granite",                    parent=stones, order=1)
upsert("Marble",                    "marble",                     parent=stones, order=2)
upsert("Quartz",                    "quartz",                     parent=stones, order=3)
upsert("Manufacturing and Processing","manufacturing-and-processing", parent=stones, order=4)


# ─────────────────────────────────────────────────────────────────────────────
# 4.  PARENT: Agriculture  (order=4)
# ─────────────────────────────────────────────────────────────────────────────
print("\n▶  Creating parent: Agriculture")
agriculture = upsert(
    name="Agriculture",
    slug="agriculture",
    parent=None,
    order=4,
)

print("   └─ Subcategories:")
upsert("Agricultural Equipments", "agricultural-equipments", parent=agriculture, order=1)


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Remove old flat parents that are now subcategories
#     (Only delete if they have NO products directly assigned)
# ─────────────────────────────────────────────────────────────────────────────
print("\n▶  Cleaning up old flat top-level entries …")

old_flat_slugs = [
    # Old slugs that existed before reorganisation
    "agricultural-equipments",   # now a child of Agriculture
    "block-making-machines-cabro",
    "drilling-equipments",
    "granite",
    "hardware-and-metal-work",
    "interior-design",
    "jaw-crusher",
    "major-projects-and-engineering",
    "manufacturing--and-processing",   # note: DB has extra space, slug may differ
    "manufacturing-and-processing",
    "marble",
    "mining",
    "quartz",
    "construction",
]

for slug in old_flat_slugs:
    try:
        old = Category.objects.get(slug=slug)
        # Only care about entries that are STILL top-level (no parent)
        if old.parent is None:
            product_count = old.products.count()
            if product_count == 0:
                print(f"   🗑  Deleting old top-level [{old.id}] {old.name} (no products)")
                old.delete()
            else:
                print(f"   ⚠️  [{old.id}] {old.name} has {product_count} product(s) – NOT deleted (reassign manually)")
    except Category.DoesNotExist:
        pass   # already gone or never existed with that slug


# ─────────────────────────────────────────────────────────────────────────────
# 6.  Summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════════")
print(" Final category tree:")
print("══════════════════════════════════════════════")
for parent in Category.objects.filter(parent=None).order_by('order'):
    print(f"\n  [{parent.order}] {parent.name}  (id={parent.id})")
    for sub in parent.subcategories.order_by('order'):
        prod_count = sub.products.count()
        print(f"       └─ {sub.name}  ({prod_count} products, id={sub.id})")

print("\n✅  Done. Refresh your admin panel to see the new structure.\n")
