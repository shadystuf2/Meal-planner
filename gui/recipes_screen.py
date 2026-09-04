import tkinter as tk


class RecipesScreen(tk.Frame):
    """Placeholder screen for viewing/managing recipes."""

    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Recipes", font=("Arial", 20, "bold")).pack(pady=(30, 10))
        tk.Label(self, text="(placeholder - recipe list/add/edit UI goes here)").pack()
