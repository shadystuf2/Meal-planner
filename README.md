# Meal Planner

A standalone (non-web) desktop application for logging ingredients you have on hand and suggesting recipes you can cook with them.

## Overview

Meal Planner is an ingredient logger and recipe suggestion tool. Users record the ingredients currently available to them, and the application matches those ingredients against a recipe database to suggest meals that can be made right now. Recipes can also be searched and filtered directly, and cooking a recipe automatically deducts the ingredients it used from the user's inventory.

## Tech Stack

| Concern | Choice | Why |
|---|---|---|
| Language / paradigm | Python, Object-Oriented (OOP) | Ingredients and recipes are naturally modeled as related objects (e.g. a `Recipe` has many `Ingredient`s), which makes matching, filtering, and CRUD logic easier to design and maintain than a purely procedural approach. |
| Data storage | SQLite | A relational database enforces the ingredient/recipe relationships, supports fast queries, and ships as a single local file — no server setup required. |
| GUI | Tkinter | Ships with Python, requires no extra runtime, and is sufficient for a form/table-driven CRUD and browsing application. |
| Deployment | Standalone application | The database is local, so the app works fully offline (e.g. in a kitchen or store with no reliable connectivity). |

## Core Features

- **Ingredient logging** — add, edit, remove, and track quantities of ingredients the user currently has.
- **Recipe management** — store recipes with their required ingredients, quantities, meal category, and cooking time.
- **Recipe suggestions** — given the current ingredient inventory, suggest recipes that can be made.
- **Search & filter** — find recipes by ingredient name, meal category, or cooking time, and filter by cooking time, number of ingredients, or meal category.
- **Inventory deduction** — when a recipe is marked as cooked, its ingredients are subtracted from inventory; an ingredient is removed once its quantity reaches zero.

## Success Criteria

| ID | Criteria |
|---|---|
| SC1 | All buttons are clearly labelled and open the intended screen within 2 seconds, without causing navigation errors. |
| SC2 | The program validates user input and displays errors for invalid input. |
| SC3 | All ingredients and recipes are stored in a relational database. |
| SC4 | Users can perform CRUD (Create, Read, Update, Delete) operations on ingredients and recipes in the database. |
| SC5 | Users can search recipes by ingredient name, meal category, and cooking time, with results returned within 2 seconds. |
| SC6 | Recipes can be filtered by cooking time, number of ingredients, and meal category. |
| SC7 | The recipe-matching algorithm outputs up to 5 recipes that can be made using the ingredients currently available. |
| SC8 | When a recipe is marked as cooked, the quantities of its ingredients decrease accordingly, and an ingredient is removed once its quantity reaches 0. |

## Architecture Notes

- **Data layer**: SQLite database accessed through Python's `sqlite3` module, with tables for ingredients, recipes, and the many-to-many relationship between recipes and the ingredients (with quantities) they require.
- **Domain layer**: OOP models (e.g. `Ingredient`, `Recipe`, `Inventory`) encapsulate data and behavior, including the matching algorithm that compares available ingredients against recipe requirements.
- **Presentation layer**: Tkinter screens/views for logging ingredients, browsing/searching/filtering recipes, viewing suggested recipes, and managing CRUD operations, all driven by the domain layer.

## Status

This project is in the planning/early development stage.
