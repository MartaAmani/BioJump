"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import customtkinter as ctk
import threading
from FP import (
    connection, find_recipe,
    load_data,  create_score,
)

# ── App theme ──────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ORCHID = "#C875C4"   # Orchid
WHITE   = "#FFFFFF"
GRAY    = "#F5F5F5"
DARK    = "#333333"


# ══════════════════════════════════════════════════════════════════
# MAIN APP CLASS
# ══════════════════════════════════════════════════════════════════

class HUDSScorerApp(ctk.CTk):
    """
    Desktop GUI for the HUDS Nutrition Scorer.
    Inherits from customtkinter.CTk (the main window class).
    """

    def __init__(self):
        super().__init__()

        # ── window setup ───────────────────────────────────────────
        self.title("🍽  HUDS Nutrition Scorer")
        self.geometry("700x750")
        self.minsize(600, 600)
        self.configure(fg_color=GRAY)

        # ── load data once at startup ──────────────────────────────
        self.additives_db = load_data()
        self.history      = []

        # ── build all sections ─────────────────────────────────────
        self._build_header()
        self._build_search_bar()
        self._build_dietary_checkboxes()
        self._build_results_area()
        self._build_history_area()


    # ── SECTION BUILDERS ──────────────────────────────────────────

    def _build_header(self):
        """Top banner with title."""
        header = ctk.CTkFrame(self, fg_color=ORCHID, corner_radius=0)
        header.pack(fill="x", pady=(0, 0))

        ctk.CTkLabel(
            header,
            text       = "🍽  HUDS Nutrition Scorer",
            font       = ctk.CTkFont(size=22, weight="bold"),
            text_color = WHITE,
        ).pack(pady=18)

        ctk.CTkLabel(
            header,
            text       = "Analyze any Harvard Dining recipe instantly",
            font       = ctk.CTkFont(size=13),
            text_color = "#ffcccc",
        ).pack(pady=(0, 16))


    def _build_search_bar(self):
        """Search input + button."""
        frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            frame,
            text       = "Search a recipe",
            font       = ctk.CTkFont(size=14, weight="bold"),
            text_color = DARK,
        ).pack(anchor="w", padx=20, pady=(16, 4))

        # search row — input + button side by side
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))

        self.search_entry = ctk.CTkEntry(
            row,
            placeholder_text = "e.g.  Boom Sauce,  Kale Bowl,  Caesar...",
            font             = ctk.CTkFont(size=13),
            height           = 40,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # pressing Enter also triggers search
        self.search_entry.bind("<Return>", lambda e: self._on_search())

        self.search_button = ctk.CTkButton(
            row,
            text             = "Search",
            font             = ctk.CTkFont(size=13, weight="bold"),
            fg_color         = ORCHID,
            hover_color      = "#6b0f0f",
            height           = 40,
            width            = 100,
            command          = self._on_search,
        )
        self.search_button.pack(side="left")


    def _build_dietary_checkboxes(self):
        """Dietary preference checkboxes."""
        frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            frame,
            text       = "Dietary preferences",
            font       = ctk.CTkFont(size=14, weight="bold"),
            text_color = DARK,
        ).pack(anchor="w", padx=20, pady=(14, 6))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 14))

        # store checkbox variables so we can read them later
        self.pref_vegan      = ctk.BooleanVar(value=False)
        self.pref_vegetarian = ctk.BooleanVar(value=False)
        self.pref_gluten     = ctk.BooleanVar(value=False)
        self.pref_nuts       = ctk.BooleanVar(value=False)

        checkboxes = [
            ("Vegan",        self.pref_vegan),
            ("Vegetarian",   self.pref_vegetarian),
            ("Gluten-Free",  self.pref_gluten),
            ("Nut-Free",     self.pref_nuts),
        ]

        for label, var in checkboxes:
            ctk.CTkCheckBox(
                row,
                text             = label,
                variable         = var,
                font             = ctk.CTkFont(size=13),
                fg_color         = ORCHID,
                hover_color      = "#6b0f0f",
                checkmark_color  = WHITE,
            ).pack(side="left", padx=(0, 20))


    def _build_results_area(self):
        """Scrollable area where results are shown."""
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color      = GRAY,
            corner_radius = 0,
            label_text    = "",
        )
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))


    def _build_history_area(self):
        """Small bar at the bottom showing search history."""
        frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text       = "Session history",
            font       = ctk.CTkFont(size=12, weight="bold"),
            text_color = "#888",
        ).pack(anchor="w", padx=16, pady=(10, 2))

        self.history_label = ctk.CTkLabel(
            frame,
            text       = "No recipes searched yet.",
            font       = ctk.CTkFont(size=12),
            text_color = "#aaa",
        )
        self.history_label.pack(anchor="w", padx=16, pady=(0, 10))


    # ── EVENT HANDLERS ────────────────────────────────────────────

    def _on_search(self):
        """
        Called when user clicks Search or presses Enter.
        Runs the API call in a background thread so the GUI
        does not freeze while waiting for the response.
        """
        query = self.search_entry.get().strip()
        if not query:
            return

        # disable button while searching
        self.search_button.configure(state="disabled", text="Searching...")
        self._clear_results()
        self._show_status("🔍  Searching HUDS database...")

        # run API call in background thread — keeps GUI responsive
        thread = threading.Thread(
            target = self._fetch_and_display,
            args   = (query,),
            daemon = True,
        )
        thread.start()


    def _fetch_and_display(self, query):
        """
        Background thread — fetches recipe and updates GUI.
        Uses after() to safely update GUI from a non-main thread.
        """
        data = connection(query)

        if not data:
            self.after(0, self._show_status,
                       "❌  Could not reach the HUDS server. Try again.")
            self.after(0, self._reset_button)
            return

        recipe = find_recipe(query, data)

        if not recipe:
            self.after(0, self._show_status,
                       f"❌  No recipe found for \"{query}\".\n"
                       f"    Try a single keyword like  'boom'  or  'kale'.")
            self.after(0, self._reset_button)
            return

        # score the recipe
        final_score = create_score(recipe, self.additives_db)

        # check dietary preferences
        warnings = self._check_dietary(recipe)

        # update the GUI on the main thread
        self.after(0, self._display_results, recipe, final_score, warnings)
        self.after(0, self._reset_button)


    def _check_dietary(self, recipe):
        """Check recipe against selected dietary preferences."""
        ingredients = (recipe.get("Ingredient_List") or "").lower()
        warnings    = []

        checks = [
            (self.pref_vegan,      "Vegan",
             ["meat","chicken","fish","egg","milk","cheese","butter","honey"]),
            (self.pref_vegetarian, "Vegetarian",
             ["meat","chicken","fish","gelatin"]),
            (self.pref_gluten,     "Gluten-Free",
             ["wheat","barley","rye","malt"]),
            (self.pref_nuts,       "Nut-Free",
             ["almond","walnut","cashew","peanut","hazelnut","pecan"]),
        ]

        for var, label, forbidden in checks:
            if var.get():
                for word in forbidden:
                    if word in ingredients:
                        warnings.append(f"⚠  Not {label} — contains {word}")
                        break

        return warnings


    # ── DISPLAY HELPERS ───────────────────────────────────────────

    def _clear_results(self):
        """Remove all widgets from the results area."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()


    def _show_status(self, message):
        """Show a simple status message in the results area."""
        self._clear_results()
        ctk.CTkLabel(
            self.results_frame,
            text       = message,
            font       = ctk.CTkFont(size=13),
            text_color = "#888",
        ).pack(pady=40)


    def _reset_button(self):
        """Re-enable the search button."""
        self.search_button.configure(state="normal", text="Search")


    def _display_results(self, recipe, final_score, warnings):
        """Render the full report card in the results area."""
        self._clear_results()

        name        = recipe.get("Recipe_Name", "")
        calories    = recipe.get("Calories", "N/A")
        allergens   = (recipe.get("Allergens") or "").rstrip(", ")
        nova_score  = final_score["score"]

        # ── Recipe name ────────────────────────────────────────
        ctk.CTkLabel(
            self.results_frame,
            text       = name,
            font       = ctk.CTkFont(size=17, weight="bold"),
            text_color = ORCHID,
        ).pack(anchor="w", pady=(8, 12))

        # ── NOVA score pill ────────────────────────────────────
        self._add_score_pill("NOVA Score", nova_score, 100)

        # ── Nutrition info ─────────────────────────────────────
        info_frame = ctk.CTkFrame(
            self.results_frame, fg_color=WHITE, corner_radius=10
        )
        info_frame.pack(fill="x", pady=(8, 0))

        self._add_info_row(info_frame, "🔥 Calories",  str(calories) + " kcal")
        self._add_info_row(info_frame, "🧂 Allergens", allergens or "None listed")

        # ── Dietary warnings ───────────────────────────────────
        if warnings:
            warn_frame = ctk.CTkFrame(
                self.results_frame,
                fg_color      = "#fff8f0",
                corner_radius = 10,
                border_color  = "#f59e0b",
                border_width  = 1,
            )
            warn_frame.pack(fill="x", pady=(8, 0))

            for w in warnings:
                ctk.CTkLabel(
                    warn_frame,
                    text       = w,
                    font       = ctk.CTkFont(size=13),
                    text_color = "#92400e",
                ).pack(anchor="w", padx=14, pady=4)

        # ── Additives list ─────────────────────────────────────
        add_frame = ctk.CTkFrame(
            self.results_frame, fg_color=WHITE, corner_radius=10
        )
        add_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            add_frame,
            text       = "⛔  Ultra-Processed Additives",
            font       = ctk.CTkFont(size=13, weight="bold"),
            text_color = ORCHID,
        ).pack(anchor="w", padx=14, pady=(12, 4))

        if final_score["additives_found"]:
            for item in final_score["additives_found"]:
                row = ctk.CTkFrame(add_frame, fg_color="transparent")
                row.pack(fill="x", padx=14, pady=2)

                ctk.CTkLabel(
                    row,
                    text       = f"• {item['name']}",
                    font       = ctk.CTkFont(size=12),
                    text_color = DARK,
                    width      = 250,
                    anchor     = "w",
                ).pack(side="left")

                ctk.CTkLabel(
                    row,
                    text       = f"[{item['category']}]",
                    font       = ctk.CTkFont(size=11),
                    text_color = "#888",
                ).pack(side="left", padx=8)

            ctk.CTkLabel(
                add_frame,
                text       = "",
                height     = 8,
            ).pack()

        else:
            ctk.CTkLabel(
                add_frame,
                text       = "✅  No ultra-processed additives found!",
                font       = ctk.CTkFont(size=13),
                text_color = "#22c55e",
            ).pack(anchor="w", padx=14, pady=(4, 12))

        # ── Update history bar ─────────────────────────────────
        self.history.append(f"{name}  —  NOVA: {nova_score}/100")
        self.history_label.configure(
            text       = "   |   ".join(self.history[-3:]),
            text_color = "#555",
        )


    def _add_score_pill(self, label, score, max_score):
        """Render one score pill with a progress bar."""
        ratio = score / max_score if max_score else 0
        color = ORCHID if ratio < 0.5 else "#eab308" if ratio < 0.75 else "#22c55e"
        icon  = "🔴" if ratio < 0.5 else "🟡" if ratio < 0.75 else "🟢"

        frame = ctk.CTkFrame(
            self.results_frame, fg_color=WHITE, corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 4))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(
            row,
            text       = f"{icon}  {label}",
            font       = ctk.CTkFont(size=13, weight="bold"),
            text_color = DARK,
            width      = 140,
            anchor     = "w",
        ).pack(side="left")

        bar = ctk.CTkProgressBar(row, height=14)
        bar.set(ratio)
        bar.configure(progress_color=color)
        bar.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkLabel(
            row,
            text       = f"{score} / {max_score}",
            font       = ctk.CTkFont(size=13, weight="bold"),
            text_color = color,
            width      = 75,
            anchor     = "e",
        ).pack(side="left")


    def _add_info_row(self, parent, label, value):
        """Render one label-value row inside a card."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=5)

        ctk.CTkLabel(
            row,
            text       = label,
            font       = ctk.CTkFont(size=13, weight="bold"),
            text_color = DARK,
            width      = 120,
            anchor     = "w",
        ).pack(side="left")

        ctk.CTkLabel(
            row,
            text       = value,
            font       = ctk.CTkFont(size=13),
            text_color = "#555",
            anchor     = "w",
        ).pack(side="left")


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = HUDSScorerApp()
    app.mainloop()
