import tkinter as tk


class FindRecipesScreen(tk.Frame):
    """Placeholder screen for searching/matching recipes to ingredients on hand."""

    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Find Recipes", font=("Arial", 20, "bold")).pack(pady=(30, 10))
        tk.Label(self, text="(placeholder - recipe search/matching UI goes here)").pack()
