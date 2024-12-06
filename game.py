import pygame
import random
from unit import *
from abilities import *
from interface import Interface

class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
        self.screen = screen
        self.interface = Interface(self.screen, self)
        self.player_units = [Unit(0, 0, 100, 10, 'player', 0, interface = self.interface),     # Position (x = 0, y = 0), PdV intial = 100, puissance d'attaque = 10
                             Unit(1, 0, 100, 10, 'player', 1, interface = self.interface)]     # Position (x = 1, y = 0), PdV intial = 100, puissance d'attaque = 10
        self.enemy_units = [Unit(6, 6, 100, 10, 'enemy', 0, interface = self.interface),       # Position (x = 6, y = 6), PdV intial = 100, puissance d'attaque = 8
                            Unit(7, 6, 100, 10, 'enemy', 1, interface = self.interface)]       # Position (x = 7, y = 6), PdV intial = 100, puissance d'attaque = 8
        self.player_row = 5
        self.player_col = 5
        self.messages = []
        
        # Initialisation des compétences
        self.competences = [Poison(),
                            PluieDeProjectiles(),
                            Missile(),
                            Drain(),
                            Soin(),
                            Bouclier(),
                            Paralysie(),
                            Desarmement(), 
                            Vortex(),   
                            Teleportation()]
        # Attribution de chaque compétence à une touche du clavier (A, Z, E, R, T, Y, U, I, O, P)
        self.touches_competences = {"Poison": pygame.K_a,
                                    "Pluie de projectiles": pygame.K_z,
                                    "Missile": pygame.K_e,
                                    "Drain": pygame.K_r,
                                    "Soin": pygame.K_t,
                                    "Bouclier": pygame.K_y,
                                    "Paralysie": pygame.K_u,
                                    "Désarmement": pygame.K_i,
                                    "Vortex": pygame.K_o,
                                    "Téléportation": pygame.K_p}

        self.competences_utilisees = set() # Suivi des compétences utilisées

    def flip_display(self):
        """
        Met à jour l'affichage en utilisant l'interface graphique.
        """
        # Affichage du jeu
        self.interface.draw_interface(self.screen, self.player_row, self.player_col)

        # Affichage des unités (alliées et ennemies)
        for unit in self.player_units + self.enemy_units:
            self.interface.draw_unit(self.screen, unit)

        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.interface.afficher_interface(competences_disponibles, self.touches_competences, self.messages)
        pygame.display.flip() # Mise à jour de l'écran

    def handle_player_turn(self):
        """Tour du joueur"""        
        for selected_unit in self.player_units:
            if selected_unit.type == 0:
                self.interface.ajouter_message("Tour du joueur 0 --------------------------")
            elif selected_unit.type == 1:
                self.interface.ajouter_message("Tour du joueur 1 --------------------------")
            
            has_acted = False # Indicateur pour savoir si l'unité a agi ou non pendant ce tour
            for effet in selected_unit.effects[:]: # Gestion de "Poison" qui s'étend sur 2 tours
                if effet["effet"] == "poison":
                    selected_unit.attack(dommage = effet["dommages"]) # Dégats infligés = -15 PdV
                effet["duree"] -= 1 # Réduit la durée de l'effet
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{selected_unit.team} unité à ({selected_unit.x}, {selected_unit.y}) n'est plus affectée par {effet['effet']}.")
                    selected_unit.effects.remove(effet) # Suppression de l'effet, une fois sa durée écoulée
            selected_unit.is_selected = True
            self.flip_display()

            # Étape 1 : Déplacement de l'unité
            self.interface.ajouter_message(f"Déplacez l'unité : ({selected_unit.x}, {selected_unit.y})")
            max_deplacements = 100
            while max_deplacements > 0:
                self.flip_display()
                # Important: cette boucle permet de gérer les événements Pygame
                for event in pygame.event.get():
                    # Gestion de la fermeture de la fenêtre
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    # Gestion des touches du clavier
                    if event.type == pygame.KEYDOWN:
                        # Déplacement (touches fléchées)
                        dx, dy = 0, 0
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        selected_unit.move(dx, dy)
                        max_deplacements -= 1
                        self.interface.ajouter_message(f"L'unité a été déplacée en ({selected_unit.x}, {selected_unit.y}). Déplacements restants : {max_deplacements}")
                        break

            # Étape 2 : Sélection et utilisation d'une compétence
            self.interface.ajouter_message(f"Sélectionnez une compétence pour l'unité : ({selected_unit.x}, {selected_unit.y})")
            while not has_acted: # Tant que l'unité n'a pas agi, on répète la boucle pour permettre la sélection et l'utilisation d'une compétence
                competence = self.selectionner_competence() # Appel de la fonction de sélection pour que le joueur choisisse une compétence disponible
                if competence: # Dans le cas où une compétence a été sélectionnée
                    cible = self.selectionner_cible(selected_unit, competence) # Appel de la fonction de sélection pour que le joueur choisisse une cible qui subira la compétence
                    if cible: # Dans le cas où une cible valide (unité ennemie) a été sélectionnée
                        self.utiliser_competence(selected_unit, cible, competence, self.interface) # Utilisation de la compétence sélectionnée sur la cible choisie
                        self.competences_utilisees.add(competence.nom) # Ajout du nom de la compétence utilisée à l'ensemble des compétences déjà utilisées
                        if len(self.competences_utilisees) == len(self.competences): # On vérifie si toutes les compétences disponibles ont été utilisées
                            self.interface.ajouter_message("Toutes les compétences ont été utilisées. Recharge des compétences...")
                            self.competences_utilisees.clear() # Vide l'ensemble des compétences utilisées pour les rendre toutes disponibles à nouveau (nouveau cycle)
                    has_acted = True # Indique que l'unité a effectué ses actions (déplacement + usage de compétence) pour ce tour
                    selected_unit.is_selected = False # Réinitialisation de l'état de l'unité, indiquant qu'elle n'est plus active
        self.player_units = [unit for unit in self.player_units if unit.health > 0] # Mise à jour de la liste des unités alliées pour ne conserver que celles qui sont encore en vie
        self.enemy_units = [unit for unit in self.enemy_units if unit.health > 0] # Mise à jour de la liste des unités ennemies pour ne conserver que celles qui sont encore en vie
        self.check_game_over() # On vérifie si le jeu est terminé après que l'unité ait agi

    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        for enemy in self.enemy_units:
            if enemy.type == 0:
                self.interface.ajouter_message("Tour du joueur 0 --------------------------")
            elif enemy.type == 1:
                self.interface.ajouter_message("Tour du joueur 1 --------------------------")
            for effet in enemy.effects[:]:
                if effet["effet"] == "poison":
                    enemy.attack(dommage = effet["dommages"])  # Applique les dégâts du poison
                effet["duree"] -= 1  # Réduit la durée de l'effet
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) n'est plus affectée par {effet['effet']}.")
                    enemy.effects.remove(effet)  # Supprime l'effet expiré
            # Vérifie si l'ennemi est immobilisé (paralysie)
            if any(effet["effet"] == "immobilisé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est paralysée et ne peut pas agir ce tour.")
                continue # Passe au prochain ennemi

            # Déplacement aléatoire
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.move(dx, dy)
            self.interface.ajouter_message(f"L'unité a été déplacée à ({enemy.x}, {enemy.y}).")
            # Vérifie si l'ennemi est désarmé (ne peut pas attaquer)
            if any(effet["effet"] == "désarmé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est désarmée.")
                continue # Passe au prochain ennemi

            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)
        self.enemy_units = [enemy for enemy in self.enemy_units if enemy.health > 0] # Mise à jour de la liste des ennemis pour exclure ceux qui sont morts
        self.check_game_over() # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTIONS RELATIVES AUX COMPÉTENCES:

    # Fonction permettant à l'utilisateur de sélectionner une compétence parmi celles qu'il n'a pas encore utilité
    def selectionner_competence(self):
        # Sélection des compétences parmi celles qui n'ont pas encore été utilisées dans ce cycle (un cycle dure 5 tours)
        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.interface.afficher_competences(self.screen, competences_disponibles) # Méthode qui met à jour l'affichage des compétences
        while True: # Boucle principale permettant de gérer la sélection du joueur
            for event in pygame.event.get(): # On parcourt les événements en attente
                if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                elif event.type == pygame.KEYDOWN: # Dans le cas où l'utilisateur presse une touche
                    competence = None # Variable dans laquelle on stockera la compétence sélectionnée parmi celles qui sont disponibles
                    for c in competences_disponibles: # On parcourt les compétences disponibles (celles affichées à l'écran)
                        if event.key == self.touches_competences.get(c.nom): # On s'assure que la touche pressée correspond à celle associée à la compétence
                            competence = c # Si une correspondance est vérifiée, alors cette compétence est attribuée à la variable "competence"
                            break # Aussitôt qu'une compétence valide a été trouvée, on sort de la boucle
                    if competence: # Dans le cas où une compétence valide est sélectionnée
                        return competence # Retourne la compétence sélectionnée pour qu'elle puisse être utilisée

    # Fonction permettant à l'utilisateur d'utiliser une compétence sur une cible (ou une position s'il s'agit des compétences Vortex et Téléportation)
    def utiliser_competence(self, utilisateur, cible, competence, interface):
        if competence and utilisateur and cible: # Dans le cas où la compétence peut être utilisée
            competence.utiliser(utilisateur, cible, self, self.interface) # On l'utilise
            if isinstance(cible, Unit) and cible.team == "enemy" and cible.health <= 0: # Dans le cas où la cible est une unité ennemie ET qu'elle n'a plus de PdV
                if cible in self.enemy_units:
                    self.enemy_units.remove(cible) # Suppression de la cible de la liste des ennemis
        else: # Dans le cas où la cible est une unité alliée
            self.interface.ajouter_message("Impossible d'utiliser la compétence. Vérifiez l'utilisateur, la cible et la compétence.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTION RELATIVE AU CURSEUR (SÉLÉCTION DE CIBLE ET/OU DE CASE):

    def selectionner_cible(self, utilisateur, competence = None):
        curseur_x, curseur_y = utilisateur.x, utilisateur.y # Coordonnées du curseur initialisées avec les coordonnées actuelles de l'utilisateur
        if competence:
            if competence.nom in ["Soin", "Bouclier", "Téléportation"]: # S'il s'agit des compétences "Bouclier", "Soin" ou "Téléportation", pas de sélection extérieure
                return utilisateur
            elif competence.nom == "Missile": # Sélection d'une ligne de 5 cases (horizontale ou verticale) pour la compétence "Missile"
                direction = None # Variable dans laquelle on stocke la direction choisie par l'utilisateur
                curseur_positions = [] # Liste contenant les coordonnées (x, y) des 5 cases du curseur
                while True: # Boucle qui reste active jusqu'à ce que l'utilisateur choisisse une direction
                    self.flip_display() # Mise à jour de l'affichage
                    if direction: # Dans le cas où une direction (haut, bas, gauche, droite) a été choisie
                        for x, y in curseur_positions:
                            pygame.draw.rect(self.screen, (255, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin du curseur (en rouge) qui représente la zone d'effet
                    else: # Dans le cas où aucune direction n'a été choisie
                        pygame.draw.rect(self.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin d'un curseur (en vert) autour de l'utilisateur
                    pygame.display.flip() # Mise à jour de l'affichaget
                    for event in pygame.event.get(): # Gestion des évènements
                        if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                            pygame.quit() # Fermeture de Pygame proprement
                            exit() # Arrêt complet du programme
                        elif event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                            if event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée
                                direction = 'haut'
                            elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée
                                direction = 'bas'
                            elif event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée
                                direction = 'gauche'
                            elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée
                                direction = 'droite'
                            elif event.key == pygame.K_RETURN and direction: # Validation en pressant "Entrée"
                                return direction
                            
                            if direction: # Si l'utilisateur a choisi une direction
                                curseur_positions = [] # Réinitialisation de la liste contenant les coordonnées des cases du curseur
                                dx, dy = 0, 0 # Initialisation des variables de déplacement pour les coordonnées (x, y). Elles détermineront la direction à suivre.
                                if direction == 'haut': # Si la direction choisie est "haut"
                                    dx, dy = 0, -1 # Déplacement vertical du curseur vers le haut (y diminue de 1 à chaque étape)
                                elif direction == 'bas': # Si la direction choisie est "bas"
                                    dx, dy = 0, 1 # Déplacement vertical du curseur vers le bas (y augmente de 1 à chaque étape)
                                elif direction == 'gauche': # Si la direction choisie est "gauche"
                                    dx, dy = -1, 0 # Déplacement horizontal du curseur vers la gauche (x diminue de 1 à chaque étape)
                                elif direction == 'droite': # Si la direction choisie est "droite"
                                    dx, dy = 1, 0 # Déplacement horizontal du curseur vers la droite (x augmente de 1 à chaque étape)
                                for i in range(1, competence.portee + 1): # Parcourt chaque "étape" le long de la direction choisie, en commençant à 1 (case adjacente à l'utilisateur) jusqu'à la portée maximale de la compétence (inclus)
                                    new_x = utilisateur.x + dx * i # Calcul de la nouvelle coordonnée x en partant de la position actuelle de l'utilisateur (utilisateur.x), et en se déplaçant de 'i' étapes dans la direction horizontale déterminée par 'dx'
                                    new_y = utilisateur.y + dy * i # Calcul de la nouvelle coordonnée y en partant de la position actuelle de l'utilisateur (utilisateur.y), et en se déplaçant de 'i' étapes dans la direction verticale déterminée par 'dy'
                                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE: # On s'assure que les coordonnées calculées (new_x et new_y) ne dépassent pas les bordures de la grille
                                        curseur_positions.append((new_x, new_y)) # Ajout des coordonnées à la liste des cases du curseur

            elif competence.nom == "Pluie de projectiles": # Sélection d'une matrice 3x3 pour la compétence "Pluie de projectiles"
                while True: # Boucle qui reste active jusqu'à ce que l'utilisateur choisisse une case (centre de la matrice)
                    self.flip_display() # Mise à jour de l'affichage
                    for dx in range(-1, 2): # Parcourt les déplacements horizontaux par rapport à la case centrale
                        for dy in range(-1, 2): # Parcourt les déplacements verticaux par rapport à la case centrale
                            if 0 <= curseur_x + dx < GRID_SIZE and 0 <= curseur_y + dy < GRID_SIZE: # On s'assure que la case centrale (calculée en combinant ses coordonnées avec les déplacements dx et dy) ne dépassent pas les bordures de la grille
                                pygame.draw.rect(self.screen, (128, 0, 128), ((curseur_x + dx) * CELL_SIZE, (curseur_y + dy) * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin d'un carré (matrice 3x3) qui représente la zone d'effet
                    pygame.display.flip() # Affichage des évènements à l'écran
                    for event in pygame.event.get(): # Gestion des évènements
                        if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                            pygame.quit() # Fermeture de Pygame proprement
                            exit() # Arrêt complet du programme
                        elif event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                            if event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée, le curseur se déplace à gauche
                                curseur_x = max(0, curseur_x - 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                            elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée, le curseur se déplace à droite
                                curseur_x = min(GRID_SIZE - 1, curseur_x + 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                            elif event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée, le curseur se déplace en haut
                                curseur_y = max(0, curseur_y - 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                            elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée, le curseur se déplace en bas
                                curseur_y = min(GRID_SIZE - 1, curseur_y + 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                            elif event.key == pygame.K_RETURN: # Validation en pressant "Entrée"
                                return Unit(curseur_x, curseur_y, 0, 0, 'neutral', None, interface = self.interface) # Dans le cas où aucune unité ennemie n'est trouvée, on retourne une position vide comme cible "neutre"

        while True: # Cas général (compétences sans zone d'effet)
            self.flip_display() # Mise à jour de l'affichage
            pygame.draw.rect(self.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin du curseur habituel (en vert)
            pygame.display.flip() # Affichage des évènements à l'écran
            for event in pygame.event.get(): # Gestion des évènements
                if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                elif event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                    if event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée, le curseur se déplace à gauche
                        curseur_x = max(0, curseur_x - 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                    elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée, le curseur se déplace à droite
                        curseur_x = min(GRID_SIZE - 1, curseur_x + 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                    elif event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée, le curseur se déplace en haut
                        curseur_y = max(0, curseur_y - 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                    elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée, le curseur se déplace en bas
                        curseur_y = min(GRID_SIZE - 1, curseur_y + 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                    elif event.key == pygame.K_RETURN: # Valide en pressant "Entrée"
                        for unit in self.enemy_units: # Parcourt les unités ennemies
                            if unit.x == curseur_x and unit.y == curseur_y: # Dans le cas où le curseur désigne une unité ennemie
                                return unit # Retourne l'unité ennemie comme cible valide
                        return Unit(curseur_x, curseur_y, 0, 0, 'neutral', None, interface = self.interface)
                    elif event.key == pygame.K_ESCAPE: # Dans le cas où la touche "Échap" est pressée
                        return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    # Fonction permettant de s'assurer que le jeu est terminé (toutes les unités d'un camp éliminées)
    def check_game_over(self):
        if not self.player_units: # Si la liste des unités alliées (player_units) est vide
            self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
            pygame.quit() # Fermeture de Pygame proprement
            exit() # Arrêt complet du programme
        elif not self.enemy_units: # Si la liste des unités ennemies (enemy_units) est vide
            self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
            pygame.quit() # Fermeture de Pygame proprement
            exit() # Arrêt complet du programme

def main():
    # Initialisation de Pygame
    pygame.init()
    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")
    # Instanciation du jeu
    game = Game(screen)
    # Boucle principale du jeu
    while True:
        for event in pygame.event.get(): # Gestion des évènements
            if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                pygame.quit() # Fermeture de Pygame proprement
                exit() # Arrêt complet du programme

        game.handle_player_turn()
        game.handle_enemy_turn()


if __name__ == "__main__":
    main()