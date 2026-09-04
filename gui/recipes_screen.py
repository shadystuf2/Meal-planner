import tkinter as tk
from tkinter import ttk, messagebox

from logic import crud
from gui.validators import require_non_empty, require_positive_number, require_positive_int


class RecipesScreen(tk.Frame):
    """
    Lets the user add, view, edit, and delete recipes, including which
    ingredients (and how much of each) a recipe needs.

    The ingredients for the recipe currently in the form are kept in
    self.current_ingredients (a plain Python list) and only written
    to the database - via crud.create_recipe/update_recipe, which
    handle the recipe_ingredients junction table - when Save is
    clicked. Adding/removing a row in the "Ingredients" list below
    only changes this in-memory list.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.selected_id = None  # id of the recipe being edited, or None when adding
        self.current_ingredients = []  # [{"ingredient_id", "name", "quantity_required"}, ...]

        self._build_form()
        self._build_list()

        self.refresh_list()
        self.refresh_ingredient_choices()

    # -- widgets -------------------------------------------------------

    def _build_form(self):
        form = tk.Frame(self)
        form.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(form, text="Recipes", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        tk.Label(form, text="Name").grid(row=1, column=0, sticky="w")
        self.name_entry = tk.Entry(form)
        self.name_entry.grid(row=1, column=1, pady=2)

        tk.Label(form, text="Meal category").grid(row=2, column=0, sticky="w")
        self.meal_category_entry = tk.Entry(form)
        self.meal_category_entry.grid(row=2, column=1, pady=2)

        tk.Label(form, text="Cooking time (min)").grid(row=3, column=0, sticky="w")
        self.cooking_time_entry = tk.Entry(form)
        self.cooking_time_entry.grid(row=3, column=1, pady=2)

        tk.Label(form, text="Instructions").grid(row=4, column=0, sticky="nw")
        self.instructions_text = tk.Text(form, width=25, height=5)
        self.instructions_text.grid(row=4, column=1, pady=2)

        # -- ingredients required by this recipe --
        tk.Label(form, text="Ingredients", font=("Arial", 11, "bold")).grid(
            row=5, column=0, columnspan=2, pady=(10, 2)
        )

        self.ingredient_choice = ttk.Combobox(form, state="readonly", width=14)
        self.ingredient_choice.grid(row=6, column=0, pady=2)

        self.ingredient_qty_entry = tk.Entry(form, width=8)
        self.ingredient_qty_entry.grid(row=6, column=1, sticky="w", pady=2)

        tk.Button(form, text="Add ingredient", command=self.add_ingredient_row).grid(
            row=7, column=0, columnspan=2, pady=2
        )

        self.ingredients_listbox = tk.Listbox(form, height=5)
        self.ingredients_listbox.grid(row=8, column=0, columnspan=2, pady=2, sticky="ew")

        tk.Button(form, text="Remove selected ingredient", command=self.remove_ingredient_row).grid(
            row=9, column=0, columnspan=2, pady=2
        )

        button_row = tk.Frame(form)
        button_row.grid(row=10, column=0, columnspan=2, pady=10)
        tk.Button(button_row, text="Save", command=self.save_recipe).pack(side="left", padx=5)
        tk.Button(button_row, text="Delete", command=self.delete_recipe).pack(side="left", padx=5)
        tk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

    def _build_list(self):
        list_frame = tk.Frame(self)
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        columns = ("name", "meal_category", "cooking_time_minutes")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        for column, heading in zip(columns, ("Name", "Meal category", "Cooking time (min)")):
            self.tree.heading(column, text=heading)
        self.tree.pack(fill="both", expand=True)

        # Clicking a row loads that recipe (and its ingredients) into the form.
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # -- loading data ----------------------------------------------------

    def refresh_list(self):
        """Reload the recipe treeview from the database."""
        self.tree.delete(*self.tree.get_children())
        for recipe in crud.get_all_recipes():
            self.tree.insert(
                "", "end", iid=str(recipe.id),
                values=(recipe.name, recipe.meal_category, recipe.cooking_time_minutes),
            )

    def refresh_ingredient_choices(self):
        """
        Reload the "add ingredient" dropdown from the database, so
        ingredients added on the Ingredients screen show up here too.
        self.ingredients_by_name maps each displayed name back to its
        id, since the combobox itself only stores/shows text.
        """
        ingredients = crud.get_all_ingredients()
        self.ingredients_by_name = {ingredient.name: ingredient.id for ingredient in ingredients}
        self.ingredient_choice["values"] = list(self.ingredients_by_name.keys())

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        recipe = crud.get_recipe(int(selection[0]))
        if recipe is None:
            return

        self.selected_id = recipe.id
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, recipe.name)
        self.meal_category_entry.delete(0, tk.END)
        self.meal_category_entry.insert(0, recipe.meal_category)
        self.cooking_time_entry.delete(0, tk.END)
        self.cooking_time_entry.insert(0, str(recipe.cooking_time_minutes))
        self.instructions_text.delete("1.0", tk.END)
        self.instructions_text.insert("1.0", recipe.instructions)

        self.current_ingredients = [
            {
                "ingredient_id": row["ingredient_id"],
                "name": row["name"],
                "quantity_required": row["quantity_required"],
            }
            for row in crud.get_recipe_ingredients(recipe.id)
        ]
        self.refresh_ingredients_listbox()

    def refresh_ingredients_listbox(self):
        """Redraw the small list of ingredients currently attached to this recipe form."""
        self.ingredients_listbox.delete(0, tk.END)
        for item in self.current_ingredients:
            self.ingredients_listbox.insert(tk.END, f'{item["name"]} - {item["quantity_required"]}')

    def clear_form(self):
        """Empty the form and deselect, so the next Save creates a new recipe."""
        self.selected_id = None
        self.current_ingredients = []
        self.tree.selection_remove(self.tree.selection())
        self.name_entry.delete(0, tk.END)
        self.meal_category_entry.delete(0, tk.END)
        self.cooking_time_entry.delete(0, tk.END)
        self.instructions_text.delete("1.0", tk.END)
        self.refresh_ingredients_listbox()
        self.refresh_ingredient_choices()

    # -- actions -----------------------------------------------------------

    def add_ingredient_row(self):
        """
        Validate the chosen ingredient/quantity and add them to this
        recipe's in-memory ingredient list; nothing is written to the
        database until Save.
        """
        ingredient_name = self.ingredient_choice.get()
        if ingredient_name not in self.ingredients_by_name:
            messagebox.showerror("Invalid input", "Choose an ingredient from the list first.")
            return

        try:
            quantity_required = require_positive_number(self.ingredient_qty_entry.get(), "Ingredient quantity")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        self.current_ingredients.append({
            "ingredient_id": self.ingredients_by_name[ingredient_name],
            "name": ingredient_name,
            "quantity_required": quantity_required,
        })
        self.refresh_ingredients_listbox()
        self.ingredient_qty_entry.delete(0, tk.END)

    def remove_ingredient_row(self):
        """Remove the selected row from this recipe's in-memory ingredient list."""
        selection = self.ingredients_listbox.curselection()
        if not selection:
            messagebox.showerror("Nothing selected", "Select an ingredient in the list first.")
            return

        del self.current_ingredients[selection[0]]
        self.refresh_ingredients_listbox()

    def save_recipe(self):
        """
        Validate the form, then create a new recipe (if nothing is
        selected) or update the selected one, including its
        ingredient list.
        """
        try:
            name = require_non_empty(self.name_entry.get(), "Name")
            meal_category = require_non_empty(self.meal_category_entry.get(), "Meal category")
            cooking_time_minutes = require_positive_int(self.cooking_time_entry.get(), "Cooking time")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        instructions = self.instructions_text.get("1.0", tk.END).strip()
        if not instructions:
            messagebox.showerror("Invalid input", "Instructions cannot be empty.")
            return

        ingredients = [
            {"ingredient_id": item["ingredient_id"], "quantity_required": item["quantity_required"]}
            for item in self.current_ingredients
        ]

        if self.selected_id is None:
            crud.create_recipe(name, meal_category, cooking_time_minutes, instructions, ingredients)
        else:
            crud.update_recipe(
                self.selected_id,
                ingredients=ingredients,
                name=name,
                meal_category=meal_category,
                cooking_time_minutes=cooking_time_minutes,
                instructions=instructions,
            )

        self.clear_form()
        self.refresh_list()

    def delete_recipe(self):
        """Delete the selected recipe, after confirming with the user."""
        if self.selected_id is None:
            messagebox.showerror("Nothing selected", "Select a recipe in the list first.")
            return

        if not messagebox.askyesno("Delete recipe", "Delete this recipe? This cannot be undone."):
            return

        crud.delete_recipe(self.selected_id)
        self.clear_form()
        self.refresh_list()
