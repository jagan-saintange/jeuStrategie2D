import pygame
from unit import *

class Interface:
    def __init__(self, screen, game):
        pygame.init()

        self.screen = screen
        self.game = game
        self.x = 21 # Nombre de carrés sur une ligne
        self.y = 21 # Nombre de carrés sur une colonne
        self.a = 30 # Taille d'un carré (en pixels)
        self.b = 400 # Largeur de la zone des actions (en pixels)
        self.WIDTH = self.x * self.a + self.b # Largeur totale de la fenêtre
        self.HEIGHT = self.y * self.a # Hauteur totale de la fenêtre
        self.font = pygame.font.SysFont(None, 20)
        self.font_competences = pygame.font.SysFont("arial", 15, bold = True)
        self.messages = [] # Liste servant à stocker les messages à afficher
        self.font_actions = pygame.font.Font(None, 20)
        self.max_messages = 20 # Limite du nombre de messages visibles
        # Couleurs
        self.WHITE = (255, 255, 255)
        self.GREY = (200, 200, 200) # Couleur de la grille
        self.ALPHA = 125 # Transparence (0 = transparent, 255 = opaque)

        # Images représentant les unités:
        self.player_unit_images = [pygame.transform.scale(pygame.image.load("buissonrouge.png"), (self.a, self.a)),
                                   pygame.transform.scale(pygame.image.load("skeleton.png"), (self.a, self.a))]
        self.enemy_unit_images = [pygame.transform.scale(pygame.image.load("rosier.png"), (self.a, self.a)),
                                  pygame.transform.scale(pygame.image.load("skeleton.png"), (self.a, self.a))]
        
        # Chargement des images du décor:
        self.background = pygame.transform.scale(pygame.image.load("bkr.jpg"), (self.x * self.a, self.y * self.a))
        self.campfire = pygame.transform.scale(pygame.image.load("campfire.png"), (self.a, self.a))

        # Grille de passabilité (True = passable, False = bloqué):
        self.passability_grid = [[True] * self.x for _ in range(self.y)]

        # Surfaces pour les éléments de premier plan (arbre, sapin, tente, etc.) ainsi que la grille:
        self.grid_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.foreground_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        # Définir les cases bloquées
        self.define_blocked_areas()

    def define_blocked_areas(self): # Fonction pour bloquer certaines zones de la grille
        def blocage(x_min, x_max, y_min, y_max):
            for row in range(y_min, y_max):
                for col in range(x_min, x_max):
                    self.passability_grid[row][col] = False

        blocage(8, 13, 0, 7) # Bassin
        blocage(9, 12, 7, 14) # 2ème partie de la cascade
        blocage(9, 12, 15, 18) # 3ème parite de la cascade
        blocage(9, 12, 19, 21) # 4ème parite de la cascade
        blocage(0, 2, 8, 9) # 1er muret
        blocage(6, 9, 8, 10) # 2ème muret
        blocage(12, 15, 8, 10) # 3ème muret
        blocage(18, 21, 8, 10) # 4ème muret
        blocage(4, 5, 4, 5) # Feu de camp (gauche)
        blocage(16, 17, 4, 5) # Feu de camp (droite)
        blocage(19, 20, 12, 13) # Bûches

    def is_passable(self, row, col):
        if 0 <= row < self.y and 0 <= col < self.x:
            return self.passability_grid[row][col]
        return False

    def place_image_at(self, screen, image, row, col):
        if 0 <= row < self.y and 0 <= col < self.x:
            position = (col * self.a, row * self.a)
            screen.blit(image, position)

    def draw_foreground(self):
        
        # En bas, à gauche
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a , self.a * 2)), (12.2 * self.a, 15 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (13.2 * self.a, 14.7 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (12.2 * self.a, 16 * self.a))
        # En bas, à droite
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (17.2 * self.a, 14.8 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a , self.a * 2)), (17.9 * self.a, 16 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (16 * self.a, 16 * self.a))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('ferme.png'), (self.a * 2.5, self.a * 2.8)), (1.3 * self.a, 12 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('chariot.png'), (self.a *1.5, self.a * 1.5)), (6.8 * self.a, 15.8 * self.a))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('tente.png'), (self.a * 2, self.a * 2)), (14 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('tente.png'), (self.a * 2, self.a * 2)), (5 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('forestgauche.png'), (self.a * 6, self.a * 6)), (-1 * self.a, -1 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('grandarbregauche.png'), (self.a * 3.7, self.a * 3.7)), (4.8 * self.a, 4 * self.a))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('forest.png'), (self.a * 6, self.a * 6)), (16 * self.a, -1 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('grandarbre.png'), (self.a * 3.7, self.a * 3.7)), (12.5 * self.a, 4 * self.a))

        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('grandarbre.png'), (self.a * 3.7, self.a * 3.7)), (0 * self.a, 8.9 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('grandarbre.png'), (self.a * 3.7, self.a * 3.7)), (12 * self.a, 10 * self.a))


    def draw_grid(self):
        self.grid_surface.fill((0, 0, 0, 0)) # Effacer la surface
        for row in range(self.y + 1):
            pygame.draw.line(self.grid_surface, (*self.GREY, self.ALPHA), (0, row * self.a), (self.x * self.a, row * self.a))
        for col in range(self.x + 1):
            pygame.draw.line(self.grid_surface, (*self.GREY, self.ALPHA), (col * self.a, 0), (col * self.a, self.y * self.a))


    def draw_unit(self, screen, unit):
        """
        Affiche une unité sur l'écran.
        """
        # Sélectionner l'image en fonction de l'équipe et du type d'unité
        if unit.team == 'player':
            unit_image = self.player_unit_images[unit.type]
        else:
            unit_image = self.enemy_unit_images[unit.type]

        # Surbrillance lorsque l'unité est sélectionnée
        if unit.is_selected:
            pygame.draw.rect(screen, (0, 255, 0), (unit.x * self.a, unit.y * self.a, self.a, self.a), 2)
        screen.blit(unit_image, (unit.x * self.a, unit.y * self.a)) # Dessin de l'unité

        # Calcul et dessin de la barre de vie
        health_bar_width = self.a // 2
        health_ratio = unit.health / unit.max_health
        health_bar_color = (255 - int(255 * health_ratio), int(255 * health_ratio), 0) # Du rouge au vert

        pygame.draw.rect(screen, health_bar_color, (unit.x * self.a + self.a // 4, unit.y * self.a - 5, int(health_bar_width * health_ratio), 5))
        
    # Fonction qui affiche les compétences disponibles et leurs touches associées à droite du plateau de jeu
    def afficher_competences(self, screen, competences):
        pygame.draw.rect(screen, BLACK, (GRID_SIZE * CELL_SIZE, 0, WIDTH - GRID_SIZE * CELL_SIZE, HEIGHT)) # On efface la zone des compétences
        x = 640 # Coordonnée x de la position de départ pour l'affichage
        y = 10  # Coordonnée y de la position de départ pour l'affichage

        largeur_max_touche = max(self.font_competences.size(pygame.key.name(touche_code).upper())[0] for touche_code in self.game.touches_competences.values() if touche_code is not None)
        for competence in competences: # On parcourt la liste des compétences disponibles à afficher
            touche_code = self.game.touches_competences.get(competence.nom, None) # Code numérique des touches
            if touche_code is not None: # Dans le cas où la touche est associée à une compétence
                touche = pygame.key.name(touche_code).upper() # Conversion du code en lettre majuscule
                espace = largeur_max_touche + 10 # Espace entre les touches et la colonne des compétences
            surface_touche = self.font_competences.render(touche, True, (255, 255, 255))
            surface_competence = self.font_competences.render(competence.nom, True, (255, 255, 255))
            screen.blit(surface_touche, (x, y)) # Affichage des touches à l'écran, aux coordonnées (x, y)
            screen.blit(surface_competence, (x + espace, y)) # Affichage des compétences à l'écran
            y += 20 # Passage à la ligne pour afficher la compétence suivante

    def afficher_messages(self, screen):
        x_zone = GRID_SIZE * CELL_SIZE # Coordonnée x du début de la zone des actions
        y_zone = (HEIGHT // 2) - 100 # Coordonnée y du début de la zone des actions
        largeur_zone = WIDTH - GRID_SIZE * CELL_SIZE # Largeur de la zone des actions
        hauteur_zone = HEIGHT // 2 # Hauteur de la zone des actions
        pygame.draw.rect(screen, (0, 0, 0), (x_zone, y_zone, largeur_zone, hauteur_zone)) # Fond noir
        pygame.draw.line(screen, (255, 255, 255), (x_zone, y_zone), (WIDTH, y_zone), 2) # Ligne de séparation

        y = y_zone + 10 # Position de départ pour l'affichage des actions
        for i, message in enumerate(self.messages[-self.max_messages:]): # On parcourt les messages générés jusqu'à atteindre la limite (ici, max_message = 20)
            surface = self.font_actions.render(message, True, (255, 255, 255)) # Police d'écriture utilisée
            screen.blit(surface, (x_zone + 10, y + i * 20)) # Affichage de l'action à l'écran, à la position (x, y) donnée

    def ajouter_message(self, message):
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

    def afficher_interface(self, competences_disponibles, touches_competences, messages):
        pygame.draw.rect(self.screen, (0, 0, 0), (GRID_SIZE * CELL_SIZE, 0, self.WIDTH - GRID_SIZE * CELL_SIZE + 500, self.HEIGHT))
        # Affichage des compétences:
        self.afficher_competences(self.screen, competences_disponibles)
        # Affichage des actions (en dessous des compétences):
        self.afficher_messages(self.screen)

    def draw_interface(self, screen, player_row, player_col):
        screen.blit(self.background, (0, 0)) # Arrière-plan
        screen.blit(self.campfire, (4 * self.a, 4 * self.a)) # Feu de camp (camp gauche)
        screen.blit(self.campfire, (16 * self.a, 4 * self.a)) # Feu de camp (camp droit)
        self.draw_foreground() # Objets au premier plan (arbre, sapin, tente, etc.)
        screen.blit(self.foreground_surface, (0, 0))
        self.draw_grid() # Grille
        screen.blit(self.grid_surface, (0, 0))
