import pygame

GRID_SIZE = 21 # Taille de la grille
CELL_SIZE = 30 # Taille d'une cellule (en pixels)
WIDTH = GRID_SIZE * CELL_SIZE + 625 # Largeur totale de la fenêtre (400 = largeur de la zone des actions)
HEIGHT = GRID_SIZE * CELL_SIZE # Hauteur totale de la fenêtre
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GREY = (200, 200, 200)

class Interface:
    def __init__(self, screen, game):
        pygame.init()
        self.screen = screen # Référence à l'écran principal (surface Pygame) où les éléments seront affichés
        self.game = game # Référence à l'objet du jeu principal pour permettre l'intéraction avec ses données
        self.x = 21 # Nombre de cellules sur une ligne (largeur de la grille)
        self.y = 21 # Nombre de cellules sur une colonne (hauteur de la grille)
        self.messages = [] # Liste servant à stocker les messages à afficher
        self.font = pygame.font.Font(None, 20) # Police pour l'affichage des actions dans la zone dédiée
        self.max_messages = 20 # Limite du nombre de messages visibles
        
        # Chargement du fond d'écran:
        self.background = pygame.transform.scale(pygame.image.load("./assets/bkr.jpg"), (self.x * CELL_SIZE, self.y * CELL_SIZE))

        # Zone passable (True = passable, False = bloquée):
        self.zone_passable = [[True] * self.x for _ in range(self.y)]

        # Surfaces pour les éléments de premier plan (arbre, sapin, tente, etc.) ainsi que la grille:
        self.grid_surface = pygame.Surface((WIDTH - 225, HEIGHT), pygame.SRCALPHA)
        self.foreground_surface = pygame.Surface((self.x * CELL_SIZE, self.y * CELL_SIZE), pygame.SRCALPHA)

        # Définir les cases bloquées
        self.define_blocked_areas()

    # Fonction qui initialise la grille de passabilité en définissant les zones bloquées
    def define_blocked_areas(self):
        def blocage(x_min, x_max, y_min, y_max): # Sous-fonction qui bloque une région rectangulaire donnée dans la grille
            for ligne in range(y_min, y_max): # Parcours de toutes les lignes de la région spécifiée
                for colonne in range(x_min, x_max): # Parcours de toutes les colonnes de la région spécifiée
                    self.zone_passable[ligne][colonne] = False # On marque la cellule correspondante comme bloquée (False)
        # Zones bloquées (non accessibles aux joueurs)
        blocage(8, 13, 0, 7) # Bassin
        blocage(9, 12, 7, 14) # 2ème partie de la cascade
        blocage(9, 12, 15, 18) # 3ème partie de la cascade
        blocage(9, 12, 19, 21) # 4ème partie de la cascade
        blocage(0, 3, 8, 10) # 1er muret
        blocage(6, 9, 8, 10) # 2ème muret
        blocage(12, 15, 8, 10) # 3ème muret
        blocage(18, 21, 8, 10) # 4ème muret
        blocage(4, 5, 4, 5) # Feu de camp (gauche)
        blocage(16, 17, 4, 5) # Feu de camp (droite)
        blocage(7, 8, 3, 4) # Caisse de lances (gauche)
        blocage(13, 14, 3, 4) # Caisse d'épées (droite)
        blocage(19, 20, 12, 13) # Bûches
        blocage(1, 6, 19, 20) # Barrières (tout en bas)
        blocage(5, 6, 15, 18) # Barrières (près des ponts)
        blocage(7, 8, 16, 17) # Charette

    # Fonction qui s'assure qu'une case donnée de la grille "zone_passable" est accessible
    def passable(self, ligne, colonne):
        if 0 <= ligne < self.y and 0 <= colonne < self.x: # On s'assure que la position (ligne, colonne) est dans les limites de la grille ([0, self.y[ et [0, self.x[)
            return self.zone_passable[ligne][colonne] # True si la case n'a pas été préalablement bloquée
        return False

    def draw_foreground(self):
        # En bas, à gauche
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/sapin.png'), (CELL_SIZE , CELL_SIZE * 2)), (12.2 * CELL_SIZE, 15 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (CELL_SIZE * 1.9, CELL_SIZE * 2)), (13.2 * CELL_SIZE, 14.7 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (CELL_SIZE * 1.9, CELL_SIZE * 2)), (12.2 * CELL_SIZE, 16 * CELL_SIZE))
        # En bas, à droite
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (CELL_SIZE * 1.9, CELL_SIZE * 2)), (17.2 * CELL_SIZE, 14.8 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/sapin.png'), (CELL_SIZE , CELL_SIZE * 2)), (17.9 * CELL_SIZE, 16 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (CELL_SIZE * 1.9, CELL_SIZE * 2)), (16 * CELL_SIZE, 16 * CELL_SIZE))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/ferme.png'), (CELL_SIZE * 2.5, CELL_SIZE * 2.8)), (1.3 * CELL_SIZE, 12 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/chariot.png'), (CELL_SIZE *1.5, CELL_SIZE * 1.5)), (6.8 * CELL_SIZE, 15.8 * CELL_SIZE))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/tente.png'), (CELL_SIZE * 2, CELL_SIZE * 2)), (14 * CELL_SIZE, 2 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/tente.png'), (CELL_SIZE * 2, CELL_SIZE * 2)), (5 * CELL_SIZE, 2 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/forestgauche.png'), (CELL_SIZE * 6, CELL_SIZE * 6)), (-1 * CELL_SIZE, -1 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbregauche.png'), (CELL_SIZE * 3.7, CELL_SIZE * 3.7)), (4.8 * CELL_SIZE, 4 * CELL_SIZE))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/forest.png'), (CELL_SIZE * 6, CELL_SIZE * 6)), (16 * CELL_SIZE, -1 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbre.png'), (CELL_SIZE * 3.7, CELL_SIZE * 3.7)), (12.5 * CELL_SIZE, 4 * CELL_SIZE))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbre.png'), (CELL_SIZE * 3.7, CELL_SIZE * 3.7)), (0 * CELL_SIZE, 8.9 * CELL_SIZE))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbre.png'), (CELL_SIZE * 3.7, CELL_SIZE * 3.7)), (12 * CELL_SIZE, 10 * CELL_SIZE))

    # Fonction qui dessine une grille semi-transparente par-dessus la carte
    def draw_grid(self):
        self.grid_surface.fill((0, 0, 0, 0)) # Efface la grille afin qu'à chaque appel, de nouvelles lignes ne se superposent pas à celles déjà existantes
        for ligne in range(self.y + 1): # Parcours des lignes de la grille (y+1 afin d'inclure les bords)
            pygame.draw.line(self.grid_surface, (*GREY, 125), (0, ligne * CELL_SIZE), (self.x * CELL_SIZE, ligne * CELL_SIZE)) # Surface, couleur, coordonnées de départ, coordonnées d'arrivée
        for colonne in range(self.x + 1): # Parcours des colonnes de la grille (x+1 afin d'nclure les bords)
            pygame.draw.line(self.grid_surface, (*GREY, 125), (colonne * CELL_SIZE, 0), (colonne * CELL_SIZE, self.y * CELL_SIZE)) # Transparence (0 = transparent, 255 = opaque)

    def afficher_statistiques(self, screen, image_path):        
        # Efface la zone (rectangle noir remplacé par l'image)
        stat_x = GRID_SIZE * CELL_SIZE # Coordonnée x du début de la zone des statistiques
        stat_y = -10 # Coordonnée y du début de la zone des statistiques
        stat_largeur = WIDTH - GRID_SIZE * CELL_SIZE # Largeur de la zone des statistiques
        stat_hauteur = HEIGHT - 250 # Hauteur de la zone des statistiques

        if image_path:
            # On redimensionne l'image pour qu'elle couvre toute la zone réservée aux statistiques
            stat_joueur = pygame.transform.scale(pygame.image.load(image_path), (stat_largeur, stat_hauteur))
            screen.blit(stat_joueur, (stat_x, stat_y))

    def afficher_messages(self, screen):
        x_zone = GRID_SIZE * CELL_SIZE # Coordonnée x du début de la zone des actions
        y_zone = (HEIGHT // 2) - 77 # Coordonnée y du début de la zone des actions
        largeur_zone = WIDTH - GRID_SIZE * CELL_SIZE # Largeur de la zone des actions
        hauteur_zone = HEIGHT // 2 + 100 # Hauteur de la zone des actions

        pygame.draw.rect(screen, (0, 0, 0), (x_zone, y_zone, largeur_zone, hauteur_zone)) # Fond noir
        pygame.draw.line(screen, (255, 255, 255), (x_zone, y_zone), (WIDTH, y_zone), 2) # Ligne de séparation

        y = y_zone + 10 # Position de départ pour l'affichage des actions
        for i, message in enumerate(self.messages[-self.max_messages:]): # Affichage des derniers messages
            if isinstance(message, tuple): # Si le message est un tuple (texte, couleur)
                texte, couleur = message
            else: # Sinon, afficher en blanc par défaut
                texte, couleur = message, (255, 255, 255)

            surface = self.font.render(texte, True, couleur) # On génère le message avec la couleur
            screen.blit(surface, (x_zone + 10, y + i * 19)) # Affichage du message

    def ajouter_message(self, message):
        self.messages.append(str(message)) # Ajout d'un nouveau message à la liste des messages (self.messages)
        if len(self.messages) > 100: # Dans le cas où le nombre total de messages dépasse 100
            self.messages.pop(0) # Suppression du message le plus ancien (d'index 0)

    # Fonction pour ajouter un message avec retour à la ligne dans Pygame
    def ajouter_message_multiligne(self, message):
        lignes = message.split("\n") # Diviser le message par ligne
        for ligne in lignes:
            self.ajouter_message(ligne) # Ajout de chaque ligne individuellement

    def afficher_interface(self, competences_disponibles, messages, image_path=None):
        # Affichage des statistiques:
        self.afficher_statistiques(self.screen, image_path)
        # Affichage des actions (en dessous des statistiques):
        self.afficher_messages(self.screen)            