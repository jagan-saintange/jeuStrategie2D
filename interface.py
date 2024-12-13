import pygame

GRID_SIZE = 21 # Taille de la grille
CELL_SIZE = 30 # Taille d'une cellule (case)
WIDTH = GRID_SIZE * CELL_SIZE + 625 # Augmentation de l'espace pour afficher les compétences
HEIGHT = GRID_SIZE * CELL_SIZE # Hauteur de la fenêtre
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Interface:
    def __init__(self, screen, game):
        pygame.init()

        self.screen = screen # Référence à l'écran principal (surface Pygame) où les éléments seront affichés
        self.game = game # Référence à l'objet du jeu principal pour permettre l'intéraction avec ses données
        self.x = 21 # Nombre de cellules sur une ligne (largeur de la grille)
        self.y = 21 # Nombre de cellules sur une colonne (hauteur de la grille)
        self.a = 30 # Taille d'une cellule (en pixels)
        self.b = 400 # Largeur de la zone des actions (en pixels)
        self.WIDTH = self.x * self.a + self.b # Largeur totale de la fenêtre
        self.HEIGHT = self.y * self.a # Hauteur totale de la fenêtre
        self.font = pygame.font.SysFont(None, 20) # Police par défaut (taille 20)
        self.font_competences = pygame.font.SysFont("arial", 15, bold = True) # Police pour l'affichage des compétences
        self.messages = [] # Liste servant à stocker les messages à afficher
        self.font_actions = pygame.font.Font(None, 20) # Police pour l'affichage des actions dans la zone dédiée
        self.max_messages = 20 # Limite du nombre de messages visibles
        # Couleurs
        self.GREY = (200, 200, 200) # Couleur de la grille
        self.ALPHA = 125 # Transparence (0 = transparent, 255 = opaque)
        
        # Chargement du fond d'écran:
        self.background = pygame.transform.scale(pygame.image.load("./assets/bkr.jpg"), (self.x * self.a, self.y * self.a))

        # Zone passable (True = passable, False = bloqué):
        self.zone_passable = [[True] * self.x for _ in range(self.y)]

        # Surfaces pour les éléments de premier plan (arbre, sapin, tente, etc.) ainsi que la grille:
        self.grid_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.foreground_surface = pygame.Surface((self.x * self.a, self.y * self.a), pygame.SRCALPHA)

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
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/sapin.png'), (self.a , self.a * 2)), (12.2 * self.a, 15 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (self.a * 1.9, self.a * 2)), (13.2 * self.a, 14.7 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (self.a * 1.9, self.a * 2)), (12.2 * self.a, 16 * self.a))
        # En bas, à droite
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (self.a * 1.9, self.a * 2)), (17.2 * self.a, 14.8 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/sapin.png'), (self.a , self.a * 2)), (17.9 * self.a, 16 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/arbre.png'), (self.a * 1.9, self.a * 2)), (16 * self.a, 16 * self.a))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/ferme.png'), (self.a * 2.5, self.a * 2.8)), (1.3 * self.a, 12 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/chariot.png'), (self.a *1.5, self.a * 1.5)), (6.8 * self.a, 15.8 * self.a))

        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/tente.png'), (self.a * 2, self.a * 2)), (14 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/tente.png'), (self.a * 2, self.a * 2)), (5 * self.a, 2 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/forestgauche.png'), (self.a * 6, self.a * 6)), (-1 * self.a, -1 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbregauche.png'), (self.a * 3.7, self.a * 3.7)), (4.8 * self.a, 4 * self.a))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/forest.png'), (self.a * 6, self.a * 6)), (16 * self.a, -1 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbre.png'), (self.a * 3.7, self.a * 3.7)), (12.5 * self.a, 4 * self.a))
        
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbre.png'), (self.a * 3.7, self.a * 3.7)), (0 * self.a, 8.9 * self.a))
        self.foreground_surface.blit(pygame.transform.scale(pygame.image.load('./assets/grandarbre.png'), (self.a * 3.7, self.a * 3.7)), (12 * self.a, 10 * self.a))

    # Fonction qui dessine une grille semi-transparente par-dessus la carte
    def draw_grid(self):
        self.grid_surface.fill((0, 0, 0, 0)) # Efface la grille afin qu'à chaque appel, de nouvelles lignes ne se superposent pas à celles déjà existantes
        for row in range(self.y + 1): # Parcours des lignes de la grille (y+1 afin d'inclure les bords)
            pygame.draw.line(self.grid_surface, (*self.GREY, self.ALPHA), (0, row * self.a), (self.x * self.a, row * self.a)) # Surface, couleur, coordonnées de départ, coordonnées d'arrivée
        for col in range(self.x + 1): # Parcours des colonnes de la grille (x+1 afin d'nclure les bords)
            pygame.draw.line(self.grid_surface, (*self.GREY, self.ALPHA), (col * self.a, 0), (col * self.a, self.y * self.a)) # Surface, couleur, coordonnées de départ, coordonnées d'arrivée

    def afficher_statistiques(self, screen, image_path):
        #pygame.draw.rect(screen, BLACK, (GRID_SIZE * CELL_SIZE, 0, WIDTH - GRID_SIZE * CELL_SIZE, HEIGHT))  # Efface la zone
        
        # Efface la zone (rectangle noir remplacé par l'image)
        rect_x = GRID_SIZE * CELL_SIZE
        rect_y = -10
        rect_width = WIDTH - GRID_SIZE * CELL_SIZE
        rect_height = HEIGHT - 250

        if image_path:
            player_image = pygame.image.load(image_path)
            # Redimensionne l'image pour qu'elle couvre toute la zone
            resized_image = pygame.transform.scale(player_image, (rect_width, rect_height))
            screen.blit(resized_image, (rect_x, rect_y))

    def afficher_messages(self, screen):
        x_zone = GRID_SIZE * CELL_SIZE # Coordonnée x du début de la zone des actions
        y_zone = (HEIGHT // 2) - 77 # Coordonnée y du début de la zone des actions
        largeur_zone = WIDTH - GRID_SIZE * CELL_SIZE # Largeur de la zone des actions
        hauteur_zone = HEIGHT // 2 + 100 # Hauteur de la zone des actions

        pygame.draw.rect(screen, (0, 0, 0), (x_zone, y_zone, largeur_zone, hauteur_zone)) # Fond noir
        pygame.draw.line(screen, (255, 255, 255), (x_zone, y_zone), (WIDTH, y_zone), 2) # Ligne de séparation

        y = y_zone + 10  # Position de départ pour l'affichage des actions
        for i, message in enumerate(self.messages[-self.max_messages:]): # Affichage des derniers messages
            if isinstance(message, tuple): # Si le message est un tuple (texte, couleur)
                texte, couleur = message
            else: # Sinon, afficher en blanc par défaut
                texte, couleur = message, (255, 255, 255)

            surface = self.font_actions.render(texte, True, couleur) # On génère le texte avec la couleur
            screen.blit(surface, (x_zone + 10, y + i * 19)) # Affichage le texte

    def ajouter_message(self, message):
        self.messages.append(message) # Ajout d'un nouveau message à la liste des messages (self.messages)
        if len(self.messages) > 100: # Dans le cas où le nombre total de messages dépasse 100
            self.messages.pop(0) # Suppression du message le plus ancien (d'index 0)

    # Fonction pour ajouter un message avec retour à la ligne dans Pygame
    def ajouter_message_multiligne(self, message):
        lignes = message.split("\n") # Diviser le message par ligne
        for ligne in lignes:
            self.ajouter_message(ligne) # Ajout de chaque ligne individuellement

    def afficher_interface(self, competences_disponibles, messages, image_path=None):
        # Affichage des compétences:
        self.afficher_statistiques(self.screen, image_path)
        # Affichage des actions (en dessous des compétences):
        self.afficher_messages(self.screen)            