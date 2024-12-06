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
        self.font_competences = pygame.font.Font(None, 10)  # Police des compétences
        self.messages = [] # Liste servant à stocker les messages à afficher
        self.font_actions = pygame.font.Font(None, 20) # Police pour les actions
        self.max_messages = 5 # Limite du nombre de messages visibles à la fois

        # Couleurs
        self.WHITE = (255, 255, 255)
        self.GREY = (200, 200, 200) # Couleur de la grille
        self.ALPHA = 125 # Transparence (0 = transparent, 255 = opaque)

        # Images représentant les unités:
        self.player_unit_images = [pygame.transform.scale(pygame.image.load("rosier.png"), (self.a, self.a)),
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

    def define_blocked_areas(self):
        # Fonction pour bloquer certaines zones de la grille
        def blocage(x_min, x_max, y_min, y_max):
            for row in range(y_min, y_max):
                for col in range(x_min, x_max):
                    self.passability_grid[row][col] = False

        blocage(8, 13, 0, 7)
        blocage(9, 12, 7, 14)
        blocage(9, 12, 15, 18)
        blocage(0, 3, 8, 10)

    def is_passable(self, row, col):
        if 0 <= row < self.y and 0 <= col < self.x:
            return self.passability_grid[row][col]
        return False

    def place_image_at(self, screen, image, row, col):
        if 0 <= row < self.y and 0 <= col < self.x:
            position = (col * self.a, row * self.a)
            screen.blit(image, position)

    def draw_foreground(self):
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (5 * self.a, 15 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (7 * self.a, 15 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (6 * self.a, 16 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (13 * self.a, 15 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (17 * self.a, 15 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a , self.a * 2)), (17 * self.a, 16 * self.a))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('foret.png'), (self.a * 1.9, self.a * 2)), (19 * self.a, 0 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (18 * self.a, 0 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (19 * self.a, 1 * self.a))

        # Forêt    
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (13 * self.a, 0 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (16 * self.a, 0 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (17 * self.a, 1 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (17 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (20 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (15 * self.a, 0 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 1.9)), (12 * self.a, 16 * self.a))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (18 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (18 * self.a, 4 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (20 * self.a, 4 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 2)), (18 * self.a, 5 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (19 * self.a, 6 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('sapin.png'), (self.a, self.a * 1.9)), (16 * self.a, 1 * self.a))


        # Foret (coté droit)
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (13 * self.a, 5 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (12 * self.a, 6 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('arbre.png'), (self.a * 1.9, self.a * 2)), (14 * self.a, 6 * self.a))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('tente.png'), (self.a * 2, self.a * 2)), (14 * self.a, 2 * self.a))

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

        pygame.draw.rect(screen, health_bar_color,
                        (unit.x * self.a + self.a // 4, unit.y * self.a - 5, int(health_bar_width * health_ratio), 5))

    # Fonction qui affiche les compétences disponibles et leurs touches associées à droite du plateau de jeu
    def afficher_competences(self, screen, competences):
        pygame.draw.rect(screen, BLACK, (GRID_SIZE * CELL_SIZE, 0, WIDTH - GRID_SIZE * CELL_SIZE, HEIGHT)) # On efface la zone des compétences
        x = 640 # Coordonnée x de la position de départ pour l'affichage
        y = 10  # Coordonnée y de la position de départ pour l'affichage
        for competence in competences: # On parcourt la liste des compétences disponibles à afficher
            # Recherche de la touche associée à la compétence, ou "?" si aucune n'est associée
            touche = self.game.touches_competences.get(competence.nom, None) # Si aucune touche n'a été associée à cette compétence, retourne "None"
            texte = f"{touche}: {competence.nom}" # Affichage > "Touche du clavier" : "Compétence associée"
            surface = self.font_competences.render(texte, True, (255, 255, 255))
            screen.blit(surface, (x, y)) # Affichage du texte à l'écran, aux coordonnées (x, y)
            y += 40 # Passage à la ligne suivante pour afficher la compétence suivante

    def afficher_messages(self, x, start_y):
        pygame.draw.rect(self.screen, BLACK, (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE // 2, self.WIDTH - GRID_SIZE * CELL_SIZE, self.HEIGHT - GRID_SIZE * CELL_SIZE // 2))
        pygame.draw.line(self.screen, WHITE, (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE // 2), (self.WIDTH, GRID_SIZE * CELL_SIZE // 2), 2)
        x, y = 640, start_y
        # Affichage des messages:
        for message in self.messages[-self.max_messages:]:
            surface = self.font_actions.render(message, True, (255, 255, 255))
            self.screen.blit(surface, (x, y))
            y += 20 # Espacement vertical entre les messages

    def ajouter_message(self, message):
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

    def afficher_interface(self, competences_disponibles, touches_competences, messages):
        pygame.draw.rect(self.screen, (0, 0, 0), (GRID_SIZE * CELL_SIZE, 0, self.WIDTH - GRID_SIZE * CELL_SIZE + 500, self.HEIGHT))
        x_competences = GRID_SIZE * CELL_SIZE + 10 # Colonne à droite de la grille
        y_competences = 10 # Point de départ pour les compétences

        # Affichage des compétences disponibles:
        for competence in competences_disponibles:
            touche = touches_competences.get(competence.nom, None)
            touche_nom = pygame.key.name(touche).upper() if touche else "?"
            texte = f"{touche_nom}: {competence.nom}"
            texte_surface = self.font.render(texte, True, WHITE)
            self.screen.blit(texte_surface, (x_competences, y_competences))
            y_competences += 15 # Espacement entre les lignes

        pygame.draw.line(self.screen, WHITE, (GRID_SIZE * CELL_SIZE, len(competences_disponibles) * 40), (GRID_SIZE * CELL_SIZE + 500, len(competences_disponibles) * 40), 2)
        # Zone des actions
        x_messages = GRID_SIZE * CELL_SIZE + 20
        y_messages = y_competences + 20 # Espacement sous les compétences

        # Afficher les messages
        for message in messages:
            texte_surface = self.font.render(message, True, WHITE)
            self.screen.blit(texte_surface, (x_messages, y_messages))
            y_messages += 30 # Espacement vertical entre les messages

    def draw_interface(self, screen, player_row, player_col):
        screen.blit(self.background, (0, 0)) # Arrière-plan
        screen.blit(self.campfire, (16 * self.a, 4 * self.a)) # Feu de camp
        self.draw_foreground() # Objets au premier plan (arbre, sapin, tente, etc.)
        screen.blit(self.foreground_surface, (0, 0))
        self.draw_grid() # Grille
        screen.blit(self.grid_surface, (0, 0))
