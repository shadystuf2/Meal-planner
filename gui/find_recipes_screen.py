import tkinter as tk
from tkinter import ttk, messagebox

from logic import crud, search
from gui.validators import optional_positive_int, optional_non_negative_int


class FindRecipesScreen(tk.Frame):
    """
    Lets the user look up recipes either with a quick single-criterion
    search (by ingredient, meal category, or cooking time) or a
    combined filter (meal category + cooking time + ingredient count
    together). Selecting a result on the left shows its ingredients
    and instructions on the right.

    The results list always comes from logic/search.py, never
    logic/crud.py directly, so every row shown here is a plain
    sqlite3.Row with recipes.* columns - that keeps row["name"] etc.
    working the same way no matter which search/filter produced it.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self._build_search_bar()
        self._build_filter_bar()
        self._build_results()

        self.show_all()

    # -- widgets -------------------------------------------------------

    def _build_search_bar(self):
        bar = tk.LabelFrame(self, text="Quick search (one criterion)")
        bar.pack(side="top", fill="x", padx=10, pady=(10, 5))

        tk.Label(bar, text="Ingredient name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ingredient_search_entry = tk.Entry(bar, width=15)
        self.ingredient_search_entry.grid(row=0, column=1, padx=5)
        tk.Button(bar, text="Search", command=self.search_by_ingredient).grid(row=0, column=2, padx=5)

        tk.Label(bar, text="Meal category:").grid(row=0, column=3, sticky="w", padx=(20, 5))
        self.category_search_entry = tk.Entry(bar, width=15)
        self.category_search_entry.grid(row=0, column=4, padx=5)
        tk.Button(bar, text="Search", command=self.search_by_category).grid(row=0, column=5, padx=5)

        tk.Label(bar, text="Max cooking time (min):").grid(row=0, column=6, sticky="w", padx=(20, 5))
        self.time_search_entry = tk.Entry(bar, width=6)
        self.time_search_entry.grid(row=0, column=7, padx=5)
        tk.Button(bar, text="Search", command=self.search_by_time).grid(row=0, column=8, padx=5)

    def _build_filter_bar(self):
        bar = tk.LabelFrame(self, text="Filter (combine criteria - leave a field blank to ignore it)")
        bar.pack(side="top", fill="x", padx=10, pady=5)

        tk.Label(bar, text="Meal category:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_category_entry = tk.Entry(bar, width=15)
        self.filter_category_entry.grid(row=0, column=1, padx=5)

        tk.Label(bar, text="Max cooking time (min):").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.filter_time_entry = tk.Entry(bar, width=6)
        self.filter_time_entry.grid(row=0, column=3, padx=5)

        tk.Label(bar, text="Min ingredients:").grid(row=0, column=4, sticky="w", padx=(20, 5))
        self.filter_min_ingredients_entry = tk.Entry(bar, width=5)
        self.filter_min_ingredients_entry.grid(row=0, column=5, padx=5)

        tk.Label(bar, text="Max ingredients:").grid(row=0, column=6, sticky="w", padx=5)
        self.filter_max_ingredients_entry = tk.Entry(bar, width=5)
        self.filter_max_ingredients_entry.grid(row=0, column=7, padx=5)

        tk.Button(bar, text="Apply filter", command=self.apply_filter).grid(row=0, column=8, padx=(20, 5))
        tk.Button(bar, text="Show all", command=self.show_all).grid(row=0, column=9, padx=5)

    def _build_results(self):
        results_frame = tk.Frame(self)
        results_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        columns = ("name", "meal_category", "cooking_time_minutes")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", selectmode="browse")
        for column, heading in zip(columns, ("Name", "Meal category", "Cooking time (min)")):
            self.tree.heading(column, text=heading)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        details_frame = tk.Frame(results_frame, width=250)
        details_frame.pack(side="left", fill="y", padx=(10, 0))

        tk.Label(details_frame, text="Ingredients", font=("Arial", 11, "bold")).pack(anchor="w")
        self.ingredients_label = tk.Label(details_frame, text="", justify="left", wraplength=230)
        self.ingredients_label.pack(anchor="w", pady=(0, 10))

        tk.Label(details_frame, text="Instructions", font=("Arial", 11, "bold")).pack(anchor="w")
        self.instructions_label = tk.Label(details_frame, text="", justify="left", wraplength=230)
        self.instructions_label.pack(anchor="w")

    # -- results -------------------------------------------------------

    def show_results(self, recipe_rows):
        """Replace the results list with the given recipes.* rows."""
        self.tree.delete(*self.tree.get_children())
        for row in recipe_rows:
            self.tree.insert(
                "", "end", iid=str(row["id"]),
                values=(row["name"], row["meal_category"], row["cooking_time_minutes"]),
            )
        self.ingredients_label.config(text="")
        self.instructions_label.config(text="")

    def show_all(self):
        """Show every recipe (filter_recipes with no criteria set)."""
        self.show_results(search.filter_recipes())

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        recipe_id = int(selection[0])

        ingredient_rows = crud.get_recipe_ingredients(recipe_id)
        if ingredient_rows:
            text = "\n".join(
                f'{row["name"]} - {row["quantity_required"]} {row["unit"] or ""}'.strip()
                for row in ingredient_rows
            )
        else:
            text = "(none recorded)"
        self.ingredients_label.config(text=text)

        recipe = crud.get_recipe(recipe_id)
        self.instructions_label.config(text=recipe.instructions if recipe else "")

    # -- quick search actions -----------------------------------------

    def search_by_ingredient(self):
        name = self.ingredient_search_entry.get().strip()
        if not name:
            messagebox.showerror("Invalid input", "Enter an ingredient name to search for.")
            return
        self.show_results(search.search_by_ingredient_name(name))

    def search_by_category(self):
        category = self.category_search_entry.get().strip()
        if not category:
            messagebox.showerror("Invalid input", "Enter a meal category to search for.")
            return
        self.show_results(search.search_by_meal_category(category))

    def search_by_time(self):
        try:
            max_minutes = optional_positive_int(self.time_search_entry.get(), "Cooking time")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        if max_minutes is None:
            messagebox.showerror("Invalid input", "Enter a maximum cooking time to search for.")
            return

        self.show_results(search.search_by_cooking_time(max_minutes))

    # -- filter action ---------------------------------------------------

    def apply_filter(self):
        """
        Validate every (optional) filter field, then run one combined
        query via search.filter_recipes. A blank field is simply left
        out of the call, so it doesn't restrict the results.
        """
        try:
            meal_category = self.filter_category_entry.get().strip() or None
            max_cooking_time = optional_positive_int(self.filter_time_entry.get(), "Max cooking time")
            min_ingredients = optional_non_negative_int(self.filter_min_ingredients_entry.get(), "Min ingredients")
            max_ingredients = optional_non_negative_int(self.filter_max_ingredients_entry.get(), "Max ingredients")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        if min_ingredients is not None and max_ingredients is not None and min_ingredients > max_ingredients:
            messagebox.showerror("Invalid input", "Min ingredients cannot be greater than max ingredients.")
            return

        self.show_results(search.filter_recipes(
            meal_category=meal_category,
            max_cooking_time=max_cooking_time,
            min_ingredients=min_ingredients,
            max_ingredients=max_ingredients,
        ))
