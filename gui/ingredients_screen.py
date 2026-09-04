import tkinter as tk


class IngredientsScreen(tk.Frame):
    """Placeholder screen for viewing/managing ingredients."""

    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Ingredients", font=("Arial", 20, "bold")).pack(pady=(30, 10))
        tk.Label(self, text="(placeholder - ingredient list/add/edit UI goes here)").pack()
