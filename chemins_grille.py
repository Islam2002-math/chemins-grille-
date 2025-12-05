import tkinter as tk
from tkinter import ttk
from typing import List, Tuple

Point = Tuple[int, int]
Chemin = List[Tuple[int, int]]

class GridPathsViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("BOUADJADJ ISLAM – v.1.1")
        self.root.state("zoomed")
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Variables
        self.m = tk.IntVar(value=3)   # largeur 
        self.n = tk.IntVar(value=2)   # hauteur 
        self.paths = []               # liste de tous les chemins
        self.current_page = 0         # page courante (pour affichage par page)
        self.paths_per_page = 12      # nombre de chemins par page (3 lignes x 4 colonnes)
        self.selected_path_index = None  # indice global du chemin sélectionné
        # mode courant : "grid" (grille m x n), "cube" (8 sommets) ou "cube4" (hypercube 16 sommets)
        self.current_mode = "grid"
        # anciens StringVar gardés pour compatibilité mais plus utilisés pour l'affichage
        self.coords_text = tk.StringVar(value="")
        self.directions_text = tk.StringVar(value="")
        self.stats_text = tk.StringVar(value="")
        self.last_stats = ""          # texte des statistiques globales à afficher dans la zone de texte

        self.create_widgets()

    # Interface graphique 
    def create_widgets(self):
        # Cadre de contrôle (m, n, Calculer) en haut
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(control_frame, text="Largeur :").grid(row=0, column=0, padx=2)
        ttk.Entry(control_frame, textvariable=self.m, width=5).grid(row=0, column=1, padx=2)

        ttk.Label(control_frame, text="Longueur :").grid(row=0, column=2, padx=2)
        ttk.Entry(control_frame, textvariable=self.n, width=5).grid(row=0, column=3, padx=2)

        ttk.Button(control_frame, text="Calculer", command=self.calculate_paths).grid(row=0, column=4, padx=10)

        # Bouton pour calculer les chemins sur un cube (8 sommets)
        ttk.Button(control_frame, text="Calculer cube (8 sommets)", command=self.calculate_cube_paths).grid(row=0, column=5, padx=10)

        # Bouton pour calculer les chemins sur un hypercube (16 sommets)
        ttk.Button(control_frame, text="Calculer cube 4D (16 sommets)", command=self.calculate_hypercube_paths).grid(row=0, column=6, padx=10)

        # Cadre navigation (Précédent / Suivant + compteur de pages)
        nav_frame = ttk.Frame(self.root, padding=10)
        nav_frame.grid(row=1, column=0, sticky="ew")

        ttk.Button(nav_frame, text="Précédent", command=self.previous_page).grid(row=0, column=0, padx=5)
        self.page_label = ttk.Label(nav_frame, text="Page: 0/0")
        self.page_label.grid(row=0, column=1, padx=20)
        ttk.Button(nav_frame, text="Suivant", command=self.next_page).grid(row=0, column=2, padx=5)

        # Cadre principal pour le contenu : zone de saisie + grilles en bas sur toute la largeur
        content_frame = ttk.Frame(self.root, padding=10)
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)  # la rangée du bas (grilles) prend tout l'espace

        # Zone de texte en face (où tu peux mettre les données / commentaires)
        self.user_text = tk.Text(content_frame, height=4)
        self.user_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Zone graphique : grilles qui prennent tout l'espace du bas
        self.canvas_frame = ttk.Frame(content_frame)
        self.canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Création des mini-canevas (3 lignes x 4 colonnes)
        self.thumbnail_canvases = []
        rows, cols = 3, 4
        for r in range(rows):
            self.canvas_frame.rowconfigure(r, weight=1)
        for c in range(cols):
            self.canvas_frame.columnconfigure(c, weight=1)

        for i in range(self.paths_per_page):
            r = i // cols
            c = i % cols
            canvas = tk.Canvas(self.canvas_frame, bg="white")
            canvas.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            canvas.bind("<Button-1>", lambda event, idx=i: self.on_thumbnail_click(idx))
            self.thumbnail_canvases.append(canvas)

        # Mise en page initiale des canevas (adaptée au mode courant)
        self.update_canvas_layout()

    # --- Calcul des chemins ---
    def calculate_paths(self):
        m = self.m.get()
        n = self.n.get()
        if m < 0 or n < 0:
            self.paths = []
            self.current_page = 0
            self.selected_path_index = None
            self.current_mode = "grid"
            self.page_label.config(text="Page: 0/0")
            self.last_stats = ""
            if hasattr(self, "user_text"):
                self.user_text.delete("1.0", "end")
            for canvas in self.thumbnail_canvases:
                canvas.delete("all")
            return

        self.paths = self.find_all_paths(m, n)
        self.current_page = 0
        self.selected_path_index = 0 if self.paths else None
        self.current_mode = "grid"

        # Statistiques globales sur les directions haut / gauche
        self.update_global_direction_stats()

        self.update_canvas_layout()
        self.update_page_label()
        self.draw_current_page()
        self.update_current_path_details()

    def find_all_paths(self, m: int, n: int) -> List[Chemin]:
        rows = n + 1
        cols = m + 1
        start: Point = (0, 0)
        end: Point = (m, n)

        directions: List[Point] = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ]

        all_paths: List[Chemin] = []

        def is_valid(x: int, y: int, visited: set[Point]) -> bool:
            return 0 <= x < cols and 0 <= y < rows and (x, y) not in visited

        def dfs(current: Point, visited: set[Point], path: Chemin) -> None:
            if current == end:
                all_paths.append(list(path))
                return

            x, y = current
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                next_point = (nx, ny)
                if is_valid(nx, ny, visited):
                    visited.add(next_point)
                    path.append(next_point)
                    dfs(next_point, visited, path)
                    path.pop()
                    visited.remove(next_point)

        visited_set: set[Point] = {start}
        path_list: Chemin = [start]
        dfs(start, visited_set, path_list)

        return all_paths

    # --- Chemins sur un cube (8 sommets) ---
    def find_all_cube_paths(self) -> list[list[tuple[int, int, int]]]:
        """Calcule tous les chemins simples entre (0,0,0) et (1,1,1) sur le cube 0/1.

        On travaille uniquement sur les 8 sommets (0 ou 1 pour chaque coordonnée)
        et on n'autorise pas de revisiter un sommet.
        """
        def neighbors(v: tuple[int, int, int]) -> list[tuple[int, int, int]]:
            x, y, z = v
            res: list[tuple[int, int, int]] = []
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                nx, ny, nz = x + dx, y + dy, z + dz
                if nx in (0, 1) and ny in (0, 1) and nz in (0, 1):
                    res.append((nx, ny, nz))
            return res

        start = (0, 0, 0)
        end = (1, 1, 1)
        all_paths: list[list[tuple[int, int, int]]] = []

        def dfs(current: tuple[int, int, int], visited: set[tuple[int, int, int]], path: list[tuple[int, int, int]]) -> None:
            if current == end:
                all_paths.append(list(path))
                return
            for nxt in neighbors(current):
                if nxt in visited:
                    continue
                visited.add(nxt)
                path.append(nxt)
                dfs(nxt, visited, path)
                path.pop()
                visited.remove(nxt)

        dfs(start, {start}, [start])
        return all_paths

    def calculate_cube_paths(self):
        """Calcule tous les chemins sur le cube (8 sommets) et les affiche dans les vignettes."""
        self.paths = self.find_all_cube_paths()
        self.current_page = 0
        self.selected_path_index = 0 if self.paths else None
        self.current_mode = "cube"

        total = len(self.paths)
        self.last_stats = f"Mode cube 8 sommets : {total} chemins simples entre a000 et a111"

        self.update_canvas_layout()
        self.update_page_label()
        self.draw_current_page()
        self.update_current_path_details()

    # --- Chemins sur un hypercube 4D (16 sommets) ---
    def find_all_hypercube_paths_4d(self) -> list[list[tuple[int, int, int, int]]]:
        """Calcule tous les chemins monotones entre (0,0,0,0) et (1,1,1,1) dans le cube 4D.

        On autorise uniquement les mouvements qui changent un 0 en 1 (jamais 1 -> 0),
        donc il y a 4! = 24 chemins au total, chacun de longueur 4.
        """
        start = (0, 0, 0, 0)
        end = (1, 1, 1, 1)
        all_paths: list[list[tuple[int, int, int, int]]] = []

        def dfs(current: tuple[int, int, int, int], path: list[tuple[int, int, int, int]]) -> None:
            if current == end:
                all_paths.append(list(path))
                return

            x, y, z, t = current
            coords = [x, y, z, t]
            for i in range(4):
                if coords[i] == 0:
                    new_coords = coords.copy()
                    new_coords[i] = 1
                    nxt = tuple(new_coords)  # type: ignore[arg-type]
                    path.append(nxt)
                    dfs(nxt, path)
                    path.pop()

        dfs(start, [start])
        return all_paths

    def calculate_hypercube_paths(self):
        """Calcule tous les chemins sur le cube 4D (16 sommets) et les affiche dans les vignettes."""
        self.paths = self.find_all_hypercube_paths_4d()
        self.current_page = 0
        self.selected_path_index = 0 if self.paths else None
        self.current_mode = "cube4"

        total = len(self.paths)
        self.last_stats = f"Mode cube 4D 16 sommets : {total} chemins monotones entre a0000 et a1111"

        self.update_canvas_layout()
        self.update_page_label()
        self.draw_current_page()
        self.update_current_path_details()

    def update_global_direction_stats(self):
        """Calcule des statistiques globales sur tous les chemins :
        - nb de chemins qui ont AU MOINS un mouvement vers le haut (vert)
        - nb de chemins qui ont AU MOINS un mouvement vers la gauche (bleu)
        - nb de chemins qui ont AU MOINS un haut ET AU MOINS une gauche
        """
        if not self.paths:
            self.last_stats = "Aucun chemin trouvé."
            if hasattr(self, "user_text"):
                self.user_text.delete("1.0", "end")
                self.user_text.insert("end", self.last_stats)
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
        self.last_stats = (
            f"Total chemins : {total}\n"\
            f"Chemins avec direction haut (vert) : {count_with_up}\n"\
            f"Chemins avec direction gauche (bleu) : {count_with_left}"
        )

    # --- Dessin du cube (projection 2D) ---
    def draw_single_cube_path_on_canvas(self, canvas, path_3d: list[tuple[int, int, int]]):
        """Dessine un cube projeté en 2D et surligne un chemin sur ce cube.

        Les sommets sont (0,0,0) à (1,1,1) et sont annotés a000, a001, ... a111.
        """
        canvas.delete("all")
        if not path_3d:
            return

        # Projection simple : on décale légèrement selon z pour donner un effet de profondeur
        def project(v: tuple[int, int, int]) -> tuple[float, float]:
            x, y, z = v
            return x + 0.5 * z, y + 0.5 * z

        vertices = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
        proj_coords = {v: project(v) for v in vertices}

        xs = [p[0] for p in proj_coords.values()]
        ys = [p[1] for p in proj_coords.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        canvas_width = max(canvas.winfo_width(), 100)
        canvas_height = max(canvas.winfo_height(), 100)
        margin = 10
        usable_width = max(canvas_width - 2 * margin, 1)
        usable_height = max(canvas_height - 2 * margin, 1)

        # Échelle uniforme pour garder les proportions du cube
        scale = min(
            usable_width / max(max_x - min_x, 1e-3),
            usable_height / max(max_y - min_y, 1e-3),
        )

        # Centrer le dessin dans le canevas
        shape_width = (max_x - min_x) * scale
        shape_height = (max_y - min_y) * scale
        offset_x = margin + (usable_width - shape_width) / 2
        offset_y = margin + (usable_height - shape_height) / 2

        height_logique = max_y - min_y

        def to_pixels(v: tuple[int, int, int]) -> tuple[float, float]:
            ux, uy = proj_coords[v]
            # Inverser verticalement pour que a000 soit en bas comme sur la grille
            rel_x = ux - min_x
            rel_y = uy - min_y
            x_pix = offset_x + rel_x * scale
            y_pix = offset_y + (height_logique - rel_y) * scale
            return x_pix, y_pix

        # Dessiner l'ossature du cube en noir fin
        cube_edges = [
            ((0, 0, 0), (1, 0, 0)),
            ((0, 1, 0), (1, 1, 0)),
            ((0, 0, 1), (1, 0, 1)),
            ((0, 1, 1), (1, 1, 1)),
            ((0, 0, 0), (0, 1, 0)),
            ((1, 0, 0), (1, 1, 0)),
            ((0, 0, 1), (0, 1, 1)),
            ((1, 0, 1), (1, 1, 1)),
            ((0, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (1, 0, 1)),
            ((0, 1, 0), (0, 1, 1)),
            ((1, 1, 0), (1, 1, 1)),
        ]

        for v1, v2 in cube_edges:
            x1, y1 = to_pixels(v1)
            x2, y2 = to_pixels(v2)
            canvas.create_line(x1, y1, x2, y2, fill="black", width=1)

        # Dessiner les sommets avec les étiquettes a000, a001, ...
        for v in vertices:
            x_pix, y_pix = to_pixels(v)
            canvas.create_oval(
                x_pix - 3,
                y_pix - 3,
                x_pix + 3,
                y_pix + 3,
                fill="black",
                outline="black",
            )
            x, y, z = v
            label = f"a{x}{y}{z}"
            canvas.create_text(
                x_pix + 4,
                y_pix - 4,
                text=label,
                font=("Arial", 7),
                fill="black",
                anchor="nw",
            )

        # Dessiner le chemin sur le cube avec couleurs par direction et flèches
        for i in range(len(path_3d) - 1):
            x1, y1, z1 = path_3d[i]
            x2, y2, z2 = path_3d[i + 1]

            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1
            # Couleurs similaires à la grille pour x et y, couleurs dédiées pour z
            if dx == 1 and dy == 0 and dz == 0:      # +x (droite)
                color = "#303030"
            elif dx == -1 and dy == 0 and dz == 0:  # -x (gauche)
                color = "blue"
            elif dy == 1 and dx == 0 and dz == 0:   # +y (haut)
                color = "green"
            elif dy == -1 and dx == 0 and dz == 0:  # -y (bas)
                color = "red"
            elif dz == 1:                           # profondeur +z
                color = "#ff8800"  # orange
            elif dz == -1:                          # profondeur -z
                color = "#8000ff"  # violet
            else:
                color = "black"

            px1, py1 = to_pixels((x1, y1, z1))
            px2, py2 = to_pixels((x2, y2, z2))

            # Dernier segment d'une suite même direction ?
            if i == len(path_3d) - 2:
                last_in_run = True
            else:
                nx1, ny1, nz1 = path_3d[i + 1]
                nx2, ny2, nz2 = path_3d[i + 2]
                next_dx = nx2 - nx1
                next_dy = ny2 - ny1
                next_dz = nz2 - nz1
                last_in_run = (next_dx != dx) or (next_dy != dy) or (next_dz != dz)

            arrow_kwargs = {
                "arrow": tk.LAST,
                "arrowshape": (10, 12, 6),
            } if last_in_run else {}

            canvas.create_line(
                px1, py1, px2, py2,
                fill=color,
                width=5,
                **arrow_kwargs,
            )

    def get_paths_per_page(self) -> int:
        """Renvoie le nombre effectif de chemins par page selon le mode.

        - grille / cube 3D : self.paths_per_page (12)
        - cube 4D (16 sommets) : 8 chemins par page (2 lignes x 4 colonnes).
        """
        if self.current_mode == "cube4":
            return 8
        return self.paths_per_page

    def update_canvas_layout(self) -> None:
        """Met à jour la disposition des mini-canevas selon le mode.

        - Mode grille / cube 3D : 3 lignes x 4 colonnes (12 cases)
        - Mode cube 4D : 2 lignes x 2 colonnes (4 grandes cases)
        """
        # Retirer tous les canevas de la grille
        for canvas in self.thumbnail_canvases:
            canvas.grid_forget()

        if self.current_mode == "cube4":
            rows, cols = 2, 4   # 2 lignes x 4 colonnes = 8 hypercubes par page
            active = 8
        else:
            rows, cols = 3, 4
            active = self.paths_per_page

        # Configurer les poids des lignes/colonnes
        for r in range(3):
            self.canvas_frame.rowconfigure(r, weight=1 if r < rows else 0)
        for c in range(4):
            self.canvas_frame.columnconfigure(c, weight=1 if c < cols else 0)

        # Réinsérer seulement les canevas nécessaires
        for i in range(active):
            r = i // cols
            c = i % cols
            canvas = self.thumbnail_canvases[i]
            canvas.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    # --- Dessin du cube 4D (projection 2D) ---
    def draw_single_hypercube_path_on_canvas(self, canvas, path_4d: list[tuple[int, int, int, int]]):
        """Dessine un cube 4D projeté en 2D (deux cubes reliés) et surligne un chemin.

        Les sommets sont (0,0,0,0) à (1,1,1,1) et sont annotés a0000, ..., a1111.
        """
        canvas.delete("all")
        if not path_4d:
            return

        def project3(x: int, y: int, z: int) -> tuple[float, float]:
            # même projection que pour le cube 3D
            return x + 0.5 * z, y + 0.5 * z

        def project4(v: tuple[int, int, int, int]) -> tuple[float, float]:
            x, y, z, t = v
            ux, uy = project3(x, y, z)
            # décaler le cube t=1 davantage pour bien séparer les sommets
            return ux + 2.5 * t, uy + 0.8 * t

        vertices = [(x, y, z, t) for x in (0, 1) for y in (0, 1) for z in (0, 1) for t in (0, 1)]
        proj_coords = {v: project4(v) for v in vertices}

        xs = [p[0] for p in proj_coords.values()]
        ys = [p[1] for p in proj_coords.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        canvas_width = max(canvas.winfo_width(), 120)
        canvas_height = max(canvas.winfo_height(), 120)
        margin = 10
        usable_width = max(canvas_width - 2 * margin, 1)
        usable_height = max(canvas_height - 2 * margin, 1)

        # Échelle uniforme pour garder les proportions de l'hypercube
        scale = min(
            usable_width / max(max_x - min_x, 1e-3),
            usable_height / max(max_y - min_y, 1e-3),
        )

        # Centrer le dessin dans le canevas
        shape_width = (max_x - min_x) * scale
        shape_height = (max_y - min_y) * scale
        offset_x = margin + (usable_width - shape_width) / 2
        offset_y = margin + (usable_height - shape_height) / 2

        height_logique = max_y - min_y

        def to_pixels(v: tuple[int, int, int, int]) -> tuple[float, float]:
            ux, uy = proj_coords[v]
            rel_x = ux - min_x
            rel_y = uy - min_y
            x_pix = offset_x + rel_x * scale
            # Inversion verticale pour cohérence avec la grille (a0000 en bas)
            y_pix = offset_y + (height_logique - rel_y) * scale
            return x_pix, y_pix

        # Arêtes du cube 4D : paires de sommets qui ne diffèrent que sur une coordonnée
        edges: list[tuple[tuple[int, int, int, int], tuple[int, int, int, int]]] = []
        for v in vertices:
            for i in range(4):
                w = list(v)
                w[i] = 1 - w[i]
                w_t = tuple(w)  # type: ignore[list-item]
                if v < w_t:  # éviter les doublons
                    edges.append((v, w_t))

        # Dessiner la structure du hypercube en gris
        for v1, v2 in edges:
            x1, y1 = to_pixels(v1)
            x2, y2 = to_pixels(v2)
            canvas.create_line(x1, y1, x2, y2, fill="black", width=1)

        # Dessiner les sommets avec les étiquettes a0000, ...
        for v in vertices:
            x_pix, y_pix = to_pixels(v)
            canvas.create_oval(
                x_pix - 3,
                y_pix - 3,
                x_pix + 3,
                y_pix + 3,
                fill="black",
                outline="black",
            )
            x, y, z, t = v
            label = f"a{x}{y}{z}{t}"
            canvas.create_text(
                x_pix + 4,
                y_pix - 4,
                text=label,
                font=("Arial", 7),
                fill="black",
                anchor="nw",
            )

        # Dessiner le chemin en couleurs selon la coordonnée qui change
        for i in range(len(path_4d) - 1):
            x1, y1, z1, t1 = path_4d[i]
            x2, y2, z2, t2 = path_4d[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1
            dt = t2 - t1
            if dx == 1:           # changement sur x
                color = "#303030"  # droite
            elif dy == 1:         # changement sur y
                color = "green"   # haut
            elif dz == 1:         # changement sur z
                color = "#ff8800"  # profondeur
            elif dt == 1:         # changement sur t
                color = "#8000ff"  # dimension 4
            else:
                color = "red"

            px1, py1 = to_pixels((x1, y1, z1, t1))
            px2, py2 = to_pixels((x2, y2, z2, t2))

            # Dernier segment d'une suite dans la même direction 4D ?
            if i == len(path_4d) - 2:
                last_in_run = True
            else:
                nx1, ny1, nz1, nt1 = path_4d[i + 1]
                nx2, ny2, nz2, nt2 = path_4d[i + 2]
                next_dx = nx2 - nx1
                next_dy = ny2 - ny1
                next_dz = nz2 - nz1
                next_dt = nt2 - nt1
                last_in_run = (
                    next_dx != dx
                    or next_dy != dy
                    or next_dz != dz
                    or next_dt != dt
                )

            arrow_kwargs = {
                "arrow": tk.LAST,
                "arrowshape": (10, 12, 6),
            } if last_in_run else {}

            canvas.create_line(
                px1, py1, px2, py2,
                fill=color,
                width=5,
                **arrow_kwargs,
            )

    # --- Dessin des grilles et des chemins (16 par page) ---
    def draw_single_path_on_canvas(self, canvas, path):
        canvas.delete("all")

        if not path:
            return

        m = self.m.get()
        n = self.n.get()
        if m < 0 or n < 0:
            return

        canvas_width = max(canvas.winfo_width(), 100)
        canvas_height = max(canvas.winfo_height(), 100)
        margin = 20

        usable_width = max(canvas_width - 2 * margin, 1)
        usable_height = max(canvas_height - 2 * margin, 1)
        cell_size = min(usable_width / max(m, 1), usable_height / max(n, 1))

        # Dessiner la grille avec les coordonnées (x,y) pour chaque point
        for x in range(m + 1):
            for y in range(n + 1):
                x_pixel = margin + x * cell_size
                y_pixel = canvas_height - margin - y * cell_size

                canvas.create_oval(
                    x_pixel - 2, y_pixel - 2, x_pixel + 2, y_pixel + 2,
                    fill="black", outline="black"
                )

                # Étiquette de point (x,y)
                canvas.create_text(
                    x_pixel + 4, y_pixel - 4,
                    text=f"({x},{y})",
                    font=("Arial", 6),
                    fill="black",
                    anchor="nw"
                )

        # Dessiner le chemin
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]

            dx = x2 - x1
            dy = y2 - y1

            if dx == 1 and dy == 0:          # droite
                color = "#303030"  # gris plus foncé
            elif dx == -1 and dy == 0:       # gauche
                color = "blue"
            elif dx == 0 and dy == 1:        # haut
                color = "green"
            elif dx == 0 and dy == -1:       # bas
                color = "red"
            else:
                color = "red"

            x1_pixel = margin + x1 * cell_size
            y1_pixel = canvas_height - margin - y1 * cell_size
            x2_pixel = margin + x2 * cell_size
            y2_pixel = canvas_height - margin - y2 * cell_size

            # Déterminer si ce segment est le dernier d'une suite dans la même direction
            if i == len(path) - 2:
                last_in_run = True
            else:
                nx1, ny1 = path[i + 1]
                nx2, ny2 = path[i + 2]
                next_dx = nx2 - nx1
                next_dy = ny2 - ny1
                last_in_run = (next_dx != dx) or (next_dy != dy)

            arrow_kwargs = {
                "arrow": tk.LAST,
                "arrowshape": (10, 12, 6),
            } if last_in_run else {}

            canvas.create_line(
                x1_pixel, y1_pixel, x2_pixel, y2_pixel,
                fill=color,
                width=5,
                **arrow_kwargs,
            )

        # A en vert, B en bleu
        xA, yA = path[0]
        xB, yB = path[-1]

        xA_pixel = margin + xA * cell_size
        yA_pixel = canvas_height - margin - yA * cell_size
        xB_pixel = margin + xB * cell_size
        yB_pixel = canvas_height - margin - yB * cell_size

        canvas.create_oval(
            xA_pixel - 4, yA_pixel - 4, xA_pixel + 4, yA_pixel + 4,
            fill="green", outline="green"
        )
        canvas.create_oval(
            xB_pixel - 4, yB_pixel - 4, xB_pixel + 4, yB_pixel + 4,
            fill="blue", outline="blue"
        )

    def draw_current_page(self):
        """Dessine jusqu'à N chemins de la page courante (N dépend du mode)."""
        total_paths = len(self.paths)
        per_page = self.get_paths_per_page()
        start_index = self.current_page * per_page
        end_index = min(start_index + per_page, total_paths)

        # Pour chaque canevas, dessiner le chemin correspondant ou le vider
        for local_idx, canvas in enumerate(self.thumbnail_canvases):
            global_idx = start_index + local_idx
            if start_index <= global_idx < end_index:
                path = self.paths[global_idx]
                if self.current_mode == "cube":
                    self.draw_single_cube_path_on_canvas(canvas, path)
                elif self.current_mode == "cube4":
                    self.draw_single_hypercube_path_on_canvas(canvas, path)
                else:
                    self.draw_single_path_on_canvas(canvas, path)
            else:
                canvas.delete("all")

    def update_page_label(self):
        total = len(self.paths)
        if total == 0:
            self.page_label.config(text="Page: 0/0")
            return
        per_page = self.get_paths_per_page()
        nb_pages = (total - 1) // per_page + 1
        self.page_label.config(text=f"Page: {self.current_page + 1}/{nb_pages}")

    def on_thumbnail_click(self, local_index):
        """Sélection d'un chemin en cliquant sur une des 16 grilles."""
        start_index = self.current_page * self.paths_per_page
        global_index = start_index + local_index
        if 0 <= global_index < len(self.paths):
            self.selected_path_index = global_index
            self.update_current_path_details()

    def update_current_path_details(self):
        """Met à jour les résultats (coordonnées + directions + stats) dans la zone de texte."""
        if self.selected_path_index is None or not self.paths:
            if hasattr(self, "user_text"):
                self.user_text.delete("1.0", "end")
                if self.last_stats:
                    self.user_text.insert("end", self.last_stats)
            return

        path = self.paths[self.selected_path_index]

        if self.current_mode == "cube":
            # Chemin sur le cube : afficher la suite des sommets aXYZ
            labels = [f"a{x}{y}{z}" for x, y, z in path]
            coords_str = " → ".join(labels)
            if hasattr(self, "user_text"):
                self.user_text.delete("1.0", "end")
                index_txt = f"Chemin sélectionné (cube) : {self.selected_path_index + 1}/{len(self.paths)}\n"
                self.user_text.insert(
                    "end",
                    index_txt
                    + "Sommets : " + coords_str + "\n\n"
                    + self.last_stats,
                )
            return

        if self.current_mode == "cube4":
            # Chemin sur l'hypercube 4D : aXYZT
            labels = [f"a{x}{y}{z}{t}" for x, y, z, t in path]
            coords_str = " → ".join(labels)
            if hasattr(self, "user_text"):
                self.user_text.delete("1.0", "end")
                index_txt = f"Chemin sélectionné (cube 4D) : {self.selected_path_index + 1}/{len(self.paths)}\n"
                self.user_text.insert(
                    "end",
                    index_txt
                    + "Sommets : " + coords_str + "\n\n"
                    + self.last_stats,
                )
            return

        # Mode grille classique
        # Coordonnées du chemin
        coords_str = " → ".join(f"({x},{y})" for x, y in path)
        # Compter les directions
        up_count = left_count = right_count = 0
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            dx = x2 - x1
            dy = y2 - y1
            if dx == 1 and dy == 0:          # droite
                right_count += 1
            elif dx == -1 and dy == 0:       # gauche
                left_count += 1
            elif dx == 0 and dy == 1:        # haut
                up_count += 1

        if hasattr(self, "user_text"):
            self.user_text.delete("1.0", "end")
            index_txt = f"Chemin sélectionné : {self.selected_path_index + 1}/{len(self.paths)}\n"
            directions_txt = (
                f"Haut (vert) : {up_count}\n"
                f"Gauche (bleu) : {left_count}\n"
                f"Droite (gris foncé) : {right_count}"
            )
            self.user_text.insert(
                "end",
                index_txt
                + "Coordonnées : " + coords_str + "\n\n"
                + directions_txt + "\n\n"
                + self.last_stats
            )

    # --- Navigation entre les pages ---
    def next_page(self):
        if not self.paths:
            return
        total = len(self.paths)
        per_page = self.get_paths_per_page()
        nb_pages = (total - 1) // per_page + 1
        if self.current_page < nb_pages - 1:
            self.current_page += 1
            self.draw_current_page()
            self.update_page_label()

    def previous_page(self):
        if not self.paths:
            return
        if self.current_page > 0:
            self.current_page -= 1
            self.draw_current_page()
            self.update_page_label()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridPathsViewer(root)
    root.mainloop()
