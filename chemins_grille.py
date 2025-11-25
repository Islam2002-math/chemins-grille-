import tkinter as tk
from tkinter import ttk

class GridPathsViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("BOUADJADJ ISLAM – V.1")
        # Plein écran (maximisé) pour profiter de tout l'espace
        self.root.state("zoomed")
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Variables
        self.m = tk.IntVar(value=3)   # largeur en mailles
        self.n = tk.IntVar(value=2)   # hauteur en mailles
        self.paths = []               # liste de tous les chemins
        self.current_path_index = 0   # indice du chemin courant
        self.coords_text = tk.StringVar(value="")       # coordonnées du chemin courant
        self.directions_text = tk.StringVar(value="")   # infos sur les directions du chemin courant
        self.stats_text = tk.StringVar(value="")         # statistiques globales sur tous les chemins

        self.create_widgets()

    # --- Interface graphique ---
    def create_widgets(self):
        # Cadre de contrôle (m, n, Calculer) en haut
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(control_frame, text="Largeur :").grid(row=0, column=0, padx=2)
        ttk.Entry(control_frame, textvariable=self.m, width=5).grid(row=0, column=1, padx=2)

        ttk.Label(control_frame, text="Longueur :").grid(row=0, column=2, padx=2)
        ttk.Entry(control_frame, textvariable=self.n, width=5).grid(row=0, column=3, padx=2)

        ttk.Button(control_frame, text="Calculer", command=self.calculate_paths).grid(row=0, column=4, padx=10)

        # Cadre navigation (Précédent / Suivant + compteur)
        nav_frame = ttk.Frame(self.root, padding=10)
        nav_frame.grid(row=1, column=0, sticky="ew")

        ttk.Button(nav_frame, text="\u00113 Pr\u001ec\u001edent", command=self.previous_path).grid(row=0, column=0, padx=5)
        self.path_label = ttk.Label(nav_frame, text="Chemin: 0/0")
        self.path_label.grid(row=0, column=1, padx=20)
        ttk.Button(nav_frame, text="Suivant \u00112", command=self.next_path).grid(row=0, column=2, padx=5)

        # Cadre principal pour le contenu : canevas + panneau de résultats sur le côté
        content_frame = ttk.Frame(self.root, padding=10)
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # Zone graphique (canvas) à gauche, qui s'agrandit avec la fenêtre
        self.canvas = tk.Canvas(content_frame, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Redessiner automatiquement quand la taille du canevas change
        self.canvas.bind("<Configure>", lambda event: self.draw_grid_and_path())

        # Panneau de résultats à droite (coordonnées + directions + statistiques)
        side_frame = ttk.Frame(content_frame, padding=10)
        side_frame.grid(row=0, column=1, sticky="n")

        # Affichage des coordonnées du chemin courant
        coords_frame = ttk.Frame(side_frame)
        coords_frame.pack(fill="x", anchor="n")
        ttk.Label(coords_frame, text="Coordonnées du chemin courant :").pack(anchor="w")
        self.coords_label = ttk.Label(coords_frame, textvariable=self.coords_text,
                                      wraplength=300, justify="left")
        self.coords_label.pack(anchor="w", pady=(2, 10))

        # Affichage des directions utilisées par le chemin courant
        directions_frame = ttk.Frame(side_frame)
        directions_frame.pack(fill="x", anchor="n", pady=(0, 10))
        ttk.Label(directions_frame, text="Directions (par chemin) :").pack(anchor="w")
        self.directions_label = ttk.Label(directions_frame, textvariable=self.directions_text,
                                          wraplength=300, justify="left")
        self.directions_label.pack(anchor="w")

        # Statistiques globales (tous les chemins)
        stats_frame = ttk.Frame(side_frame)
        stats_frame.pack(fill="x", anchor="n", pady=(10, 0))
        ttk.Label(stats_frame, text="Statistiques globales (tous les chemins) :").pack(anchor="w")
        self.stats_label = ttk.Label(stats_frame, textvariable=self.stats_text,
                                     wraplength=300, justify="left")
        self.stats_label.pack(anchor="w")

    # --- Calcul des chemins ---
    def calculate_paths(self):
        m = self.m.get()
        n = self.n.get()
        if m < 0 or n < 0:
            self.paths = []
            self.current_path_index = 0
            self.path_label.config(text="Chemin: 0/0")
            self.coords_text.set("")
            self.canvas.delete("all")
            return

        self.paths = self.find_all_paths(m, n)
        self.current_path_index = 0

        # Statistiques globales sur les directions haut / gauche
        self.update_global_direction_stats()

        total = len(self.paths)
        if total > 0:
            self.path_label.config(text=f"Chemin: 1/{total}")
        else:
            self.path_label.config(text="Chemin: 0/0")

        self.draw_grid_and_path()

    def find_all_paths(self, m, n):
        """
        Calcule tous les chemins simples (sans revisite de point)
        de A = (0,0) 3 B = (m,n), avec mouvements 4-directions.
        """
        rows = n + 1
        cols = m + 1
        start = (0, 0)
        end = (m, n)

        # mouvements possibles : droite, haut, gauche, bas
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        all_paths = []

        def is_valid(x, y, visited):
            return 0 <= x < cols and 0 <= y < rows and (x, y) not in visited

        def dfs(current, visited, path):
            if current == end:
                all_paths.append(path[:])
                return

            x, y = current
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if is_valid(nx, ny, visited):
                    visited.add((nx, ny))
                    path.append((nx, ny))
                    dfs((nx, ny), visited, path)
                    path.pop()
                    visited.remove((nx, ny))

        visited_set = {start}
        path_list = [start]
        dfs(start, visited_set, path_list)

        return all_paths

    def update_global_direction_stats(self):
        """Calcule des statistiques globales sur tous les chemins :
        - nb de chemins qui ont AU MOINS un mouvement vers le haut (vert)
        - nb de chemins qui ont AU MOINS un mouvement vers la gauche (bleu)
        - nb de chemins qui ont AU MOINS un haut ET AU MOINS une gauche
        """
        if not self.paths:
            self.stats_text.set("Aucun chemin trouvé.")
            return

        count_with_up = 0      # chemins contenant au moins un segment vers le haut
        count_with_left = 0    # chemins contenant au moins un segment vers la gauche

        for path in self.paths:
            has_up = False
            has_left = False
            for (x1, y1), (x2, y2) in zip(path, path[1:]):
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0 and dy == 1:        # haut
                    has_up = True
                elif dx == -1 and dy == 0:     # gauche
                    has_left = True

            if has_up:
                count_with_up += 1
            if has_left:
                count_with_left += 1

        total = len(self.paths)
        self.stats_text.set(
            f"Total chemins : {total}   |   chemins avec direction haut (vert) : {count_with_up}   "
            f"chemins avec direction gauche (bleu) : {count_with_left}"
        )

    # --- Dessin de la grille et du chemin courant ---
    def draw_grid_and_path(self):
        self.canvas.delete("all")

        m = self.m.get()
        n = self.n.get()
        if m < 0 or n < 0:
            return

        # Utiliser toute la taille disponible du canevas pour agrandir le dessin
        canvas_width = max(self.canvas.winfo_width(), 200)
        canvas_height = max(self.canvas.winfo_height(), 200)
        margin = 60  # marge autour du dessin

        # taille des cellules en pixels (en fonction de la taille actuelle du canevas)
        usable_width = max(canvas_width - 2 * margin, 1)
        usable_height = max(canvas_height - 2 * margin, 1)
        cell_size = min(usable_width / max(m, 1), usable_height / max(n, 1))

        # Dessiner la grille et les coordonnes
        for x in range(m + 1):
            for y in range(n + 1):
                x_pixel = margin + x * cell_size
                y_pixel = canvas_height - margin - y * cell_size

                # Point
                self.canvas.create_oval(
                    x_pixel - 3, y_pixel - 3, x_pixel + 3, y_pixel + 3,
                    fill="black", outline="black"
                )

                # 1tiquette (x,y)
                self.canvas.create_text(
                    x_pixel, y_pixel - 15,
                    text=f"({x},{y})",
                    font=("Arial", 8)
                )

        # Dessiner le chemin courant (couleur selon la direction)
        if self.paths and 0 <= self.current_path_index < len(self.paths):
            path = self.paths[self.current_path_index]

            # Compteur de segments par direction
            up_count = left_count = right_count = 0

            # segments + flèches
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]

                dx = x2 - x1
                dy = y2 - y1

                if dx == 1 and dy == 0:          # droite
                    color = "#303030"  # gris plus foncé
                    right_count += 1
                elif dx == -1 and dy == 0:       # gauche
                    color = "blue"
                    left_count += 1
                elif dx == 0 and dy == 1:        # haut
                    color = "green"
                    up_count += 1
                elif dx == 0 and dy == -1:       # bas (on le dessine comme la droite, pas besoin de vert)
                    color = "red"
                else:
                    color = "red"  # sécurité

                x1_pixel = margin + x1 * cell_size
                y1_pixel = canvas_height - margin - y1 * cell_size
                x2_pixel = margin + x2 * cell_size
                y2_pixel = canvas_height - margin - y2 * cell_size

                self.canvas.create_line(
                    x1_pixel, y1_pixel, x2_pixel, y2_pixel,
                    fill=color, width=2, arrow=tk.LAST
                )

            # A en vert, B en bleu
            xA, yA = path[0]
            xB, yB = path[-1]

            xA_pixel = margin + xA * cell_size
            yA_pixel = canvas_height - margin - yA * cell_size
            xB_pixel = margin + xB * cell_size
            yB_pixel = canvas_height - margin - yB * cell_size

            self.canvas.create_oval(
                xA_pixel - 5, yA_pixel - 5, xA_pixel + 5, yA_pixel + 5,
                fill="green", outline="green"
            )
            self.canvas.create_oval(
                xB_pixel - 5, yB_pixel - 5, xB_pixel + 5, yB_pixel + 5,
                fill="blue", outline="blue"
            )

            # Compteur Chemin X/Y dans le canvas
            self.canvas.create_text(
                140, 20,
                text=f"Chemin {self.current_path_index + 1}/{len(self.paths)}",
                font=("Arial", 12, "bold")
            )

            # Affichage des coordonnées du chemin courant
            coords_str = " → ".join(f"({x},{y})" for x, y in path)
            self.coords_text.set(coords_str)

            # Affichage des informations de directions (par chemin)
            self.directions_text.set(
                f"Haut (vert) : {up_count}   Gauche (bleu) : {left_count}   "
                f"Droite (gris foncé) : {right_count}"
            )
        else:
            self.coords_text.set("")
            self.directions_text.set("")

    # --- Navigation entre les chemins ---
    def next_path(self):
        if self.paths and self.current_path_index < len(self.paths) - 1:
            self.current_path_index += 1
            self.path_label.config(
                text=f"Chemin: {self.current_path_index + 1}/{len(self.paths)}"
            )
            self.draw_grid_and_path()

    def previous_path(self):
        if self.paths and self.current_path_index > 0:
            self.current_path_index -= 1
            self.path_label.config(
                text=f"Chemin: {self.current_path_index + 1}/{len(self.paths)}"
            )
            self.draw_grid_and_path()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridPathsViewer(root)
    root.mainloop()
