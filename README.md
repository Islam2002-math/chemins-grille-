# Application de chemins sur grille, cube 3D et hypercube 4D

Ce projet permet de visualiser **tous les chemins possibles** :

- sur une **grille 2D** de taille `m × n`,
- sur un **cube 3D** à 8 sommets (`a000` à `a111`),
- sur un **hypercube 4D** à 16 sommets (`a0000` à `a1111`).

L'interface graphique est réalisée avec **Tkinter** (Python) et affiche plusieurs petits graphes par page.

---

## 1. Lancer l'application (utilisateur simple)

Pour un utilisateur qui ne veut pas installer Python :

1. Télécharger le fichier `chemins_grille_app_v4.zip` (par exemple envoyé par mail ou via un lien).
2. Décompresser le `.zip` dans un dossier.
3. Double‑cliquer sur `chemins_grille.exe`.

L'interface s'ouvre avec :

- en haut : les champs `Largeur`, `Longueur` et les boutons :
  - **Calculer** (grille 2D),
  - **Calculer cube (8 sommets)**,
  - **Calculer cube 4D (16 sommets)**,
- au centre : les boutons **Précédent / Suivant** et l'indication de page,
- en bas : une zone de texte (explications) et plusieurs mini‑graphes.

---

## 2. Lancer depuis le code source (avec Python)

Prérequis :

- Python 3.12 (ou équivalent) installé,
- éventuellement `matplotlib` si on utilise des fonctions 3D (optionnel pour la version actuelle).

Dans un terminal placé dans le dossier du projet :

```bash
python chemins_grille.py
```

Ou sous Windows en double‑cliquant sur `lancer_chemins_grille.bat`.

---

## 3. Utilisation rapide de l'interface

### 3.1 Mode grille 2D

1. Entrer `Largeur = m` et `Longueur = n`.
2. Cliquer sur **Calculer**.
3. Les vignettes du bas affichent différents chemins de `(0,0)` à `(m,n)` :
   - lignes colorées selon la direction (gris = droite, bleu = gauche, vert = haut, rouge = bas),
   - une flèche uniquement à la fin de chaque séquence de pas dans une même direction.
4. Cliquer sur une vignette affiche dans la zone de texte :
   - le chemin (liste de coordonnées),
   - le nombre de pas vers le haut/gauche/droite,
   - des statistiques globales (combien de chemins utilisent au moins une direction donnée).

### 3.2 Mode cube 3D (8 sommets)

1. Cliquer sur **Calculer cube (8 sommets)**.
2. Chaque vignette montre un cube projeté en 2D avec les sommets `a000` à `a111`.
3. Un chemin de `a000` à `a111` est tracé :
   - couleur selon l'axe de déplacement (`x`, `y`, `z`),
   - flèche uniquement au bout de chaque séquence de pas dans une même direction.
4. La zone de texte affiche la suite des sommets : `a000 → a100 → ... → a111`.

### 3.3 Mode hypercube 4D (16 sommets)

1. Cliquer sur **Calculer cube 4D (16 sommets)**.
2. L'écran bascule sur un affichage de 8 hypercubes par page (2 lignes × 4 colonnes).
3. Chaque vignette montre un hypercube (deux cubes reliés) avec les sommets `a0000` à `a1111`.
4. Les chemins sont **monotones** : on part de `a0000` et on passe chaque coordonnée de 0 à 1 une seule fois (24 chemins au total).
5. Les couleurs indiquent quelle coordonnée change :
   - gris : axe `x`,
   - vert : axe `y`,
   - orange : axe `z`,
   - violet : axe `t`.

---

## 4. Contenu principal du dépôt

- `chemins_grille.py` : code principal (Tkinter + calcul des chemins + dessin).
- `chemins_grille.spec` : configuration PyInstaller pour générer `chemins_grille.exe`.
- `lancer_chemins_grille.bat` : script Windows pour lancer facilement le programme Python.
- `explication_chemins_projet.txt` : document détaillant les modèles de graphe, l'algorithme DFS, le calcul des statistiques et les projections 3D/4D.
- `.gitignore` : exclut les dossiers `build/`, `dist/`, les `.exe`, les `.zip`, etc.

Ce fichier `README.md` a pour but d'aider tout utilisateur (professeur, camarade, ami) à **lancer l'application et comprendre rapidement ce qu'elle fait**.
