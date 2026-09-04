import tkinter as tk

from gui.ingredients_screen import IngredientsScreen
from gui.recipes_screen import RecipesScreen
from gui.find_recipes_screen import FindRecipesScreen


class MainWindow(tk.Tk):
    """
    The app's main window: a navigation bar of buttons on top, and a
    container underneath holding all three screens stacked exactly on
    top of each other. Clicking a nav button doesn't create/destroy
    anything - it just raises the matching screen frame to the front
    with .tkraise(), which is Tkinter's standard show/hide pattern for
    switching between screens in one window.
    """

    def __init__(self):
        super().__init__()
        self.title("Meal Planner")
        self.geometry("800x600")

        self._build_nav_bar()
        self._build_screens()

        self.show_screen("Ingredients")

    def _build_nav_bar(self):
        nav_bar = tk.Frame(self)
        nav_bar.pack(side="top", fill="x")

        # One button per screen. `command=lambda name=name: ...` binds
        # the current value of `name` to each button - without that,
        # every button would end up calling show_screen with whatever
        # `name` was left over at the end of the loop.
        self.nav_buttons = {}
        for name in ("Ingredients", "Recipes", "Find Recipes"):
            button = tk.Button(
                nav_bar,
                text=name,
                width=15,
                command=lambda name=name: self.show_screen(name),
            )
            button.pack(side="left", padx=5, pady=5)
            self.nav_buttons[name] = button

    def _build_screens(self):
        # `container` is the shared parent all screens are placed
        # into. Giving every screen the same parent and the same
        # position (relwidth/relheight=1 fills the container exactly)
        # is what makes them stack on top of one another.
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.screens = {
            "Ingredients": IngredientsScreen(container),
            "Recipes": RecipesScreen(container),
            "Find Recipes": FindRecipesScreen(container),
        }

        for screen in self.screens.values():
            screen.place(x=0, y=0, relwidth=1, relheight=1)

    def show_screen(self, name):
        """Bring the named screen to the front, hiding the others."""
        self.screens[name].tkraise()
        self.current_screen = name
