"""
Throwaway manual test for logic/crud.py - run this from the terminal
to check ingredient CRUD works before any GUI exists:

    python3 test_crud_manual.py

Safe to delete once you're confident CRUD works; it isn't part of the
app itself.
"""

from logic import crud

print("Creating ingredient...")
ingredient = crud.create_ingredient(name="Flour", quantity=1.5, unit="kg", category="baking")
print(f"  -> {ingredient}")

print("\nListing all ingredients...")
for item in crud.get_all_ingredients():
    print(f"  -> {item}")

print("\nUpdating ingredient (quantity -> 3, unit -> g)...")
ingredient = crud.update_ingredient(ingredient.id, quantity=3, unit="g")
print(f"  -> {ingredient}")

print("\nFetching it directly by id to confirm the update was saved...")
fetched = crud.get_ingredient(ingredient.id)
print(f"  -> {fetched}")

print("\nDeleting ingredient...")
crud.delete_ingredient(ingredient.id)

print("\nConfirming it's gone...")
gone = crud.get_ingredient(fetched.id)
print(f"  -> {gone}  (should be None)")

print("\nDone.")
