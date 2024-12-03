import pygame

# Constantes pour la grille
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE + 500  # Augmente l'espace pour la colonne des compétences
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Unit:
    def __init__(self, x, y, health, attack_power, team):
        self.x = x # Position x sur la grille
        self.y = y # Position y sur la grille
        self.health = health # Santé de l'unité
        self.max_health = health
        self.attack_power = attack_power # Puissance d'attaque
        self.team = team # Équipe ('player' ou 'enemy')
        self.is_selected = False # Indique si l'unité est sélectionnée
        self.effects = [] # Liste des effets appliqués (ex: paralysie, bouclier)

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        immobilise = False
        for effet in self.effects:
            if effet["effet"] == "immobilisé":
                immobilise = True
                break  # On arrête la recherche dès qu'on trouve l'effet
        if immobilise: # Si l'effet "immobilisé" est actif
            print(f"{self.team} unité à ({self.x}, {self.y}) est immobilisée et ne peut pas se déplacer.")
            return # Empêche le déplacement
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, cible = None, dommage = None):
        if cible is not None: # Dans le cas où une cible est spécifiée
            if any(effet["effet"] == "désarmé" for effet in self.effects): # Dans le cas où l'unité est désarmée
                print(f"{self.team} unité à ({self.x}, {self.y}) est désarmée.")
                return # Empêche l'attaque
            if abs(self.x - cible.x) + abs(self.y - cible.y) <= 1: # Dans le cas où la cible est à portée
                print(f"{self.team} unité à ({self.x}, {self.y}) attaque {cible.team} unité à ({cible.x}, {cible.y}) pour {self.attack_power} dégâts.")
                cible.health -= self.attack_power # Inflige des dégâts à la cible
        elif dommage is not None: # Si des dégâts directs sont appliqués
            if any(effet["effet"] == "bouclier" for effet in self.effects): # Dans le cas où un bouclier est actif
                print(f"{self.team} unité à ({self.x}, {self.y}) est protégée par un bouclier, aucun dégât reçu.")
                return # Absorption des dégâts par le bouclier
            self.health -= dommage # Dégâts infligés à l'unité
            print(f"{self.team} unité à ({self.x}, {self.y}) subit {dommage} dégâts.")
        if self.health <= 0: # Dans le cas où l'unité meurt
            self.health = 0
            print(f"{self.team} unité à ({self.x}, {self.y}) est morte!")

    def appliquer_effet(self, effet, duree, dommages=0):
        for existing_effet in self.effects:
            if existing_effet["effet"] == effet.lower():
                # Si l'effet est déjà actif, on met à jour sa durée et ses dommages
                existing_effet["duree"] = max(existing_effet["duree"], duree)
                existing_effet["dommages"] = max(existing_effet["dommages"], dommages)
                return
        # Si l'effet n'existe pas, on l'ajoute
        self.effects.append({"effet": effet.lower(), "duree": duree, "dommages": dommages})

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

        health_bar_width = CELL_SIZE // 2
        health_ratio = self.health / self.max_health
        health_bar_color = (255 - int(255 * health_ratio), int(255 * health_ratio), 0)
        pygame.draw.rect(screen, health_bar_color, (self.x * CELL_SIZE + CELL_SIZE // 4, self.y * CELL_SIZE - 5, int(health_bar_width * health_ratio), 5))