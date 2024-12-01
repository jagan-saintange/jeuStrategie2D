import pygame
import random
from unit import *
from abilities import *

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
        self.player_units = [Unit(0, 0, 29, 10, 'player'),     # Position (x = 0, y = 0), PdV intial = 100, puissance d'attaque = 10
                             Unit(1, 0, 29, 10, 'player')]     # Position (x = 1, y = 0), PdV intial = 100, puissance d'attaque = 10
        self.enemy_units = [Unit(6, 6, 29, 10, 'enemy'),        # Position (x = 6, y = 6), PdV intial = 100, puissance d'attaque = 8
                            Unit(7, 6, 29, 10, 'enemy')]        # Position (x = 7, y = 6), PdV intial = 100, puissance d'attaque = 8

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

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:
            selected_unit.mettre_a_jour_effets()
            selected_unit.is_selected = True
            self.flip_display()

            # Étape 1 : Déplacement de l'unité
            print(f"Déplacez l'unité : ({selected_unit.x}, {selected_unit.y})")
            max_deplacements = 3
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
                        print(f"L'unité a été déplacée à ({selected_unit.x}, {selected_unit.y}). Déplacements restants : {max_deplacements}")
                        break

            # Étape 2 : Sélection et utilisation d'une compétence
            print(f"Sélectionnez une compétence pour l'unité : ({selected_unit.x}, {selected_unit.y})")
            has_acted = False # Indicateur pour savoir si l'unité a agi ou non pendant ce tour
            while not has_acted: # Tant que l'unité n'a pas agi, on répète la boucle pour permettre la sélection et l'utilisation d'une compétence
                competence = self.selectionner_competence() # Appel de la fonction de sélection pour que le joueur choisisse une compétence disponible
                if competence: # Dans le cas où une compétence a été sélectionnée
                    cible = self.selectionner_cible(selected_unit, competence) # Appel de la fonction de sélection pour que le joueur choisisse une cible qui subira la compétence
                    if cible: # Dans le cas où une cible valide (unité ennemie) a été sélectionnée
                        print(f"Utilisation de {competence.nom} par l'unité à ({selected_unit.x}, {selected_unit.y})")
                        self.utiliser_competence(selected_unit, cible, competence) # Utilisation de la compétence sélectionnée sur la cible choisie
                        self.competences_utilisees.add(competence.nom) # Ajout du nom de la compétence utilisée à l'ensemble des compétences déjà utilisées
                        if len(self.competences_utilisees) == len(self.competences): # On vérifie si toutes les compétences disponibles ont été utilisées
                            print("Toutes les compétences ont été utilisées. Recharge des compétences...")
                            self.competences_utilisees.clear() # Vide l'ensemble des compétences utilisées pour les rendre toutes disponibles à nouveau (nouveau cycle)
                    has_acted = True # Indique que l'unité a effectué ses actions (déplacement + usage de compétence) pour ce tour
                    selected_unit.is_selected = False # Réinitialisation de l'état de l'unité, indiquant qu'elle n'est plus active
        self.player_units = [unit for unit in self.player_units if unit.health > 0]
        self.enemy_units = [unit for unit in self.enemy_units if unit.health > 0]
        self.check_game_over() # On vérifie si le jeu est terminé après que l'unité ait agi

    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        for enemy in self.enemy_units:
            enemy.mettre_a_jour_effets()
            if enemy.is_effect_active("immobilisé"):
                print(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est paralysée et ne peut pas agir ce tour.")
                continue  # Passe au prochain ennemi
            if enemy.health <= 0:
                continue  # Ignorer les unités mortes
            # Vérifie si l'ennemi est immobilisé (paralysie)
            if enemy.is_effect_active("immobilisé"):
                print(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est paralysée et ne peut pas agir ce tour.")
                continue  # Passe au prochain ennemi
            # Déplacement aléatoire
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.move(dx, dy)
            # Vérifie si l'ennemi est désarmé (ne peut pas attaquer)
            if enemy.is_effect_active("désarmé"):
                print(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est désarmée et ne peut pas attaquer.")
                continue  # Passe au prochain ennemi
            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)
        self.enemy_units = [enemy for enemy in self.enemy_units if enemy.health > 0]
        self.check_game_over() # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)


#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTIONS RELATIVES AUX COMPÉTENCES:

    # Fonction qui affiche les compétences disponibles et leurs touches associées à droite du plateau de jeu
    def afficher_competences(self, screen, competences):
        font = pygame.font.SysFont(None, 30) # Police de type "None" de taille 30
        x = GRID_SIZE * CELL_SIZE + 20 # Coordonnée x de la position de départ pour l'affichage
        y = 20  # Coordonnée y de la position de départ pour l'affichage
        for competence in competences: # On parcourt la liste des compétences disponibles à afficher
            # Recherche de la touche associée à la compétence, ou "?" si aucune n'est associée
            touche = self.touches_competences.get(competence.nom, None) # Si aucune touche n'a été associée à cette compétence, retourne "None"
            touche_nom = pygame.key.name(touche).upper() if touche else "?" # Si une touche est trouvée, on récupère son nom sous forme de chaîne en majuscules avec pygame.key.name (sinon "?" pour indiquer qu'aucune touche n'est associée)
            texte = f"{touche_nom}: {competence.nom}" # Affichage > "Touche du clavier" : "Compétence associée"
            texte_surface = font.render(texte, True, WHITE) # Texte en blanc
            screen.blit(texte_surface, (x, y)) # Affichage du texte à l'écran, aux coordonnées (x, y)
            y += 40 # Passage à la ligne suivante pour afficher la compétence suivante
        pygame.display.flip() # Met à jour l'affichage de l'écran

    # Fonction permettant à l'utilisateur de sélectionner une compétence parmi celles qu'il n'a pas encore utilité
    def selectionner_competence(self):
        # Sélection des compétences parmi celles qui n'ont pas encore été utilisées dans ce cycle (un cycle dure 5 tours)
        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.afficher_competences(self.screen, competences_disponibles) # Méthode qui met à jour l'affichage des compétences
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
    def utiliser_competence(self, utilisateur, cible, competence):
        if competence and utilisateur and cible: # Dans le cas où la compétence peut être utilisée
            competence.utiliser(utilisateur, cible, self) # On l'utilise
            if isinstance(cible, Unit) and cible.team == "enemy" and cible.health <= 0: # Dans le cas où la cible est une unité ennemie ET qu'elle n'a plus de PdV
                if cible in self.enemy_units:
                    self.enemy_units.remove(cible) # Suppression de la cible de la liste des ennemis
        else: # Dans le cas où la cible est une unité alliée
            print("Impossible d'utiliser la compétence. Vérifiez l'utilisateur, la cible et la compétence.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTIONS RELATIVES AU CURSEUR (SÉLÉCTION DE CIBLE ET/OU DE CASE):

    # Fonction permettant à l'utilisateur de sélectionner une cible ou une position sur la grille
    def selectionner_cible(self, utilisateur, competence):
        curseur_x, curseur_y = utilisateur.x, utilisateur.y # Coordonnées du curseur initialisées avec les coordonnées actuelles de l'utilisateur
        if competence.nom in ["Soin", "Bouclier", "Téléportation"]: # S'il s'agit des compétences "Bouclier", "Soin" ou "Téléportation", pas de sélection extérieure
            return utilisateur
        while True: # Boucle infinie jusqu'à ce que la cible (untié ou case du plateau) ait été sélectionnée
            self.flip_display() # Mise à jour de l'affichage
            if competence.nom == "Pluie de projectiles":
                for dx in range(-1, 2):  # De -1 à 1 (pour une matrice 3x3)
                    for dy in range(-1, 2):
                        if 0 <= curseur_x + dx < GRID_SIZE and 0 <= curseur_y + dy < GRID_SIZE:
                            pygame.draw.rect(self.screen, (128, 0, 128), ((curseur_x + dx) * CELL_SIZE, (curseur_y + dy) * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
            else:
                pygame.draw.rect(self.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Apparition du curseur (carré vert autour de la cellule)
            pygame.display.flip() # Affichage des évènements à l'écran
            for event in pygame.event.get(): # On parcourt tous les évènements Pygame
                if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                if event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                    if event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée, le curseur se déplace à gauche
                        curseur_x = max(0, curseur_x - 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                    elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée, le curseur se déplace à droite
                        curseur_x = min(GRID_SIZE - 1, curseur_x + 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                    elif event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée, le curseur se déplace en haut
                        curseur_y = max(0, curseur_y - 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                    elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée, le curseur se déplace en bas
                        curseur_y = min(GRID_SIZE - 1, curseur_y + 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                    elif event.key == pygame.K_RETURN: # Dans le cas où la touche "Entrée" est pressée, vérification de la cible
                        for enemy in self.enemy_units: # On parcourt toutes les unités ennemies pour vérifier qu'au moins une corresponde à la position du curseur
                            if enemy.x == curseur_x and enemy.y == curseur_y: # On attribue les coordonnées du curseur à celle de l'unité ennemie trouvée
                                return enemy # Retourne l'ennemi sélectionné comme cible
                        return Unit(curseur_x, curseur_y, 0, 0, 'neutral') # Dans le cas où aucune unité ennemie n'est trouvée, on retourne une position vide comme cible "neutre"

    # Fonction permettant à l'utilisateur de sélectionner une case sur la grille (grâce aux touches fléchées)
    def selectionner_case(self):
        curseur_x, curseur_y = 0, 0  # Initialisation des coordonnées du curseur en haut à gauche de la grille (position (0, 0))
        while True: # Boucle infinie (jusqu'à validation ou annulation) pour effectuer la sélection
            self.flip_display() # Mise à jour de l'affichage du jeu (grille, unités, etc.)
            # Dessin d'un carré vert pour indiquer la position actuelle du curseur
            pygame.draw.rect(self.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Curseur (carré vert autour de la cellule)
            pygame.display.flip() # Mise à jour de l'écran pour afficher les modifications
            for event in pygame.event.get(): # On parcourt tous les événements utilisateur (clavier, souris, etc.)
                if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                if event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                    if event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée, le curseur se déplace à gauche
                        curseur_x = max(0, curseur_x - 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                    elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée, le curseur se déplace à droite
                        curseur_x = min(GRID_SIZE - 1, curseur_x + 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                    elif event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée, le curseur se déplace en haut
                        curseur_y = max(0, curseur_y - 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                    elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée, le curseur se déplace en bas
                        curseur_y = min(GRID_SIZE - 1, curseur_y + 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                    elif event.key == pygame.K_RETURN:  # Dans le cas où la touche "Entrée" est pressée, on valide la sélection
                        return (curseur_x, curseur_y) # Retourne les coordonnées (x, y) de la case sélectionnée
                    elif event.key == pygame.K_ESCAPE:  # Dans le cas où la touche "Échap" est pressée, on annule la sélection et on retourne "None"
                        return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def flip_display(self):
        """Affiche le jeu."""
        # Affiche la grille
        self.screen.fill(BLACK)
        for x in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
            for y in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
                pygame.draw.rect(self.screen, WHITE, pygame.Rect(x, y, CELL_SIZE, CELL_SIZE), 1)
        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)
        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.afficher_competences(self.screen, competences_disponibles)
        # Rafraîchit l'écran
        pygame.display.flip()

    # Fonction permettant de s'assurer que le jeu est terminé (toutes les unités d'un camp éliminées)
    def check_game_over(self):
        if not self.player_units: # Si la liste des unités alliées (player_units) est vide
            print("Défaite ! Toutes vos unités ont été éliminées.")
            pygame.quit() # Fermeture de Pygame proprement
            exit() # Arrêt complet du programme
        elif not self.enemy_units: # Si la liste des unités ennemies (enemy_units) est vide
            print("Victoire ! Tous les ennemis ont été éliminés.")
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