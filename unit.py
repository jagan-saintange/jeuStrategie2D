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
    """
    Classe pour représenter une unité dans le jeu.
    """

    def __init__(self, x, y, health, attack_power, team):
        """
        Initialise une unité avec une position, une santé, une puissance d'attaque et une équipe.

        Paramètres
        ----------
        x : int : Position x sur la grille.
        y : int : Position y sur la grille.
        health : int : Santé de l'unité.
        attack_power : int : Puissance d'attaque.
        team : str : Équipe ('player' ou 'enemy').
        """
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.team = team
        self.is_selected = False  # Indique si l'unité est sélectionnée
        self.effects = []  # Liste des effets appliqués (ex: désarmement, bouclier)

    def move(self, dx, dy):
        """
        Déplace l'unité de dx, dy si le déplacement est dans les limites de la grille.
        """
        if self.is_effect_active("immobilisé"):  # Vérifie si l'unité est immobilisée
            print(f"{self.team} unité à ({self.x}, {self.y}) est immobilisée et ne peut pas se déplacer.")
            return  # Empêche le déplacement
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """
        Attaque une unité cible si elle est à portée immédiate (1 case)
        et si l'unité n'est pas désarmée.
        """
        if self.is_effect_active("désarmé"):
            print(f"{self.team} unité à ({self.x}, {self.y}) est désarmée et ne peut pas attaquer!")
            return

        if abs(self.x - target.x) + abs(self.y - target.y) <= 1:  # Vérifie si la cible est à portée
            target.take_damage(self.attack_power)
            print(f"{self.team} unité à ({self.x}, {self.y}) attaque {target.team} unité à ({target.x}, {target.y}) pour {self.attack_power} dégâts!")
    
    def take_damage(self, damage):
        """
        Réduit la santé de l'unité après avoir subi des dégâts,
        sauf si elle est protégée par un bouclier.
        """
        if self.is_effect_active("bouclier"):
            print(f"{self.team} unité à ({self.x}, {self.y}) est protégée par un bouclier, aucun dégât reçu!")
            return

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            print(f"{self.team} unité à ({self.x}, {self.y}) est morte!")

    def appliquer_effet(self, effet, duree, dommages=0):
        """
        Applique un effet temporaire à l'unité (ex: poison, désarmement, bouclier).
        """
        for existing_effet in self.effects:
            if existing_effet["effet"] == effet.lower():
                # Si l'effet est déjà actif, on met à jour sa durée et ses dommages
                existing_effet["duree"] = max(existing_effet["duree"], duree)
                existing_effet["dommages"] = max(existing_effet["dommages"], dommages)
                print(f"{self.team} unité à ({self.x}, {self.y}) voit l'effet {effet} prolongé à {existing_effet['duree']} tours!")
                return

        # Si l'effet n'existe pas, on l'ajoute
        self.effects.append({"effet": effet.lower(), "duree": duree, "dommages": dommages})
        print(f"Effet appliqué : {effet}, Durée : {duree}, Dommages : {dommages}, Unité : ({self.x}, {self.y}) - {self.team}")
        print(f"{self.team} unité à ({self.x}, {self.y}) est affectée par {effet} pour {duree} tours!")

    def mettre_a_jour_effets(self):
        effets_restants = []
        for effet in self.effects:
            if effet["effet"] == "poison":
                self.take_damage(effet["dommages"]) # Applique les dégâts de poison
            print(f"Effet actif : {effet['effet']}, Durée restante : {effet['duree']}, Unité : ({self.x}, {self.y}) - {self.team}")
            effet["duree"] -= 1
            if effet["duree"] > 0:
                effets_restants.append(effet)
            else:
                print(f"{self.team} unité à ({self.x}, {self.y}) a perdu l'effet {effet['effet']}.")

        self.effects = effets_restants

    def is_effect_active(self, effet_name):
        """
        Vérifie si un effet spécifique est actif sur l'unité.
        """
        for effet in self.effects:
            if effet["effet"] == effet_name:
                return True
        return False

    def draw(self, screen):
        """
        Dessine l'unité sur l'écran avec une barre de santé.
        """
        color = BLUE if self.team == 'player' else RED

        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

        health_bar_width = CELL_SIZE // 2
        health_ratio = self.health / self.max_health
        health_bar_color = (255 - int(255 * health_ratio), int(255 * health_ratio), 0)
        pygame.draw.rect(screen, health_bar_color, (self.x * CELL_SIZE + CELL_SIZE // 4, self.y * CELL_SIZE - 5, int(health_bar_width * health_ratio), 5))