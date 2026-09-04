import tkinter as tk
from tkinter import ttk, messagebox

from logic import crud
from gui.validators import require_non_empty, require_positive_number


class IngredientsScreen(tk.Frame):
    """
    Lets the user add, view, edit, and delete ingredients.

    The form on the left is used both for adding a new ingredient
    (when nothing is selected) and editing an existing one (after
    clicking a row in the list on the right, which fills the form and
    sets self.selected_id). Save then calls crud.create_ingredient or
    crud.update_ingredient depending on whether self.selected_id is
    set.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.selected_id = None  # id of the ingredient being edited, or None when adding

        self._build_form()
        self._build_list()

        self.refresh_list()

    def on_show(self):
        """Called by MainWindow each time this screen is switched to, so stock changed elsewhere (e.g. cooking a recipe) shows up here."""
        self.refresh_list()

    # -- widgets -------------------------------------------------------

    def _build_form(self):
        form = tk.Frame(self)
        form.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(form, text="Ingredients", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        tk.Label(form, text="Name").grid(row=1, column=0, sticky="w")
        self.name_entry = tk.Entry(form)
        self.name_entry.grid(row=1, column=1, pady=2)

        tk.Label(form, text="Quantity").grid(row=2, column=0, sticky="w")
        self.quantity_entry = tk.Entry(form)
        self.quantity_entry.grid(row=2, column=1, pady=2)

        tk.Label(form, text="Unit").grid(row=3, column=0, sticky="w")
        self.unit_entry = tk.Entry(form)
        self.unit_entry.grid(row=3, column=1, pady=2)

        tk.Label(form, text="Category").grid(row=4, column=0, sticky="w")
        self.category_entry = tk.Entry(form)
        self.category_entry.grid(row=4, column=1, pady=2)

        button_row = tk.Frame(form)
        button_row.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(button_row, text="Save", command=self.save_ingredient).pack(side="left", padx=5)
        tk.Button(button_row, text="Delete", command=self.delete_ingredient).pack(side="left", padx=5)
        tk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

    def _build_list(self):
        list_frame = tk.Frame(self)
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        columns = ("name", "quantity", "unit", "category")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        for column, heading in zip(columns, ("Name", "Quantity", "Unit", "Category")):
            self.tree.heading(column, text=heading)
        self.tree.pack(fill="both", expand=True)

        # Clicking a row loads that ingredient into the form for editing.
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # -- loading data ----------------------------------------------------

    def refresh_list(self):
        """Reload the treeview from the database."""
        self.tree.delete(*self.tree.get_children())
        for ingredient in crud.get_all_ingredients():
            # The row's iid is the ingredient's id (as a string, since
            # Tkinter iids must be strings) so on_select/delete can
            # look the ingredient back up without a separate mapping.
            self.tree.insert(
                "", "end", iid=str(ingredient.id),
                values=(ingredient.name, ingredient.quantity, ingredient.unit or "", ingredient.category),
            )

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        ingredient = crud.get_ingredient(int(selection[0]))
        if ingredient is None:
            return

        self.selected_id = ingredient.id
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, ingredient.name)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, str(ingredient.quantity))
        self.unit_entry.delete(0, tk.END)
        self.unit_entry.insert(0, ingredient.unit or "")
        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, ingredient.category)

    def clear_form(self):
        """Empty the form and deselect, so the next Save creates a new ingredient."""
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        for entry in (self.name_entry, self.quantity_entry, self.unit_entry, self.category_entry):
            entry.delete(0, tk.END)

    # -- actions -----------------------------------------------------------

    def save_ingredient(self):
        """
        Validate the form, then create a new ingredient (if nothing is
        selected) or update the selected one. Validation failures are
        shown to the user with a messagebox instead of reaching the
        database or crashing the app.
        """
        try:
            name = require_non_empty(self.name_entry.get(), "Name")
            quantity = require_positive_number(self.quantity_entry.get(), "Quantity")
            # category is required (ingredients.category is NOT NULL
            # in the schema), so it's validated the same way as name.
            category = require_non_empty(self.category_entry.get(), "Category")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        unit = self.unit_entry.get().strip() or None  # unit is optional

        if self.selected_id is None:
            crud.create_ingredient(name=name, quantity=quantity, unit=unit, category=category)
        else:
            crud.update_ingredient(self.selected_id, name=name, quantity=quantity, unit=unit, category=category)

        self.clear_form()
        self.refresh_list()

    def delete_ingredient(self):
        """Delete the selected ingredient, after confirming with the user."""
        if self.selected_id is None:
            messagebox.showerror("Nothing selected", "Select an ingredient in the list first.")
            return

        if not messagebox.askyesno("Delete ingredient", "Delete this ingredient? This cannot be undone."):
            return

        crud.delete_ingredient(self.selected_id)
        self.clear_form()
        self.refresh_list()
