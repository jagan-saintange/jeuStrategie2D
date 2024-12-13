from abc import ABC, abstractmethod
from unit import *

# Classe générale dont les autres sous-classes hériteront
class Competence(ABC):
    def __init__(self, nom, portee = 0, dommage = 0, duree = 0): # Initialisation d'une compétence
        self.nom = nom # Nom de la compétence
        self.portee = portee # Portée de la compétence
        self.dommage = dommage # Dégâts infligés par la compétence s'il s'agit d'une attaque
        self.duree = duree # Durée de la compétence

    @abstractmethod
    def utiliser(self, utilisateur, cible, game): # Méthode abstraite à implémenter dans chaque sous-classe pour garantir la cohésion
        raise NotImplementedError("Cette méthode doit être implémentée dans les sous-classes.")
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTIONS RELATIVES AUX COMPÉTENCES:

    # Fonction permettant à l'utilisateur de sélectionner une compétence parmi celles qu'il n'a pas encore utilisé
    @staticmethod
    def selectionner_competence(game, selected_unit):
        # Dictionnaire associant les touches ("A", "B", "C", "D") avec les compétences de l'utilisateur
        competences_disponibles = {}
        touches = ["A", "B", "C", "D"]
        for i in range(len(selected_unit.competences)):
            competences_disponibles[touches[i]] = selected_unit.competences[i]

        # Parcours des compétences de l'utilisateur pour les afficher dans l'interface
        for index, (touche, competence) in enumerate(competences_disponibles.items()):
            # Si la compétence a déjà été utilisée, on l'affiche en gris clair (128, 128, 128), sinon en blanc (255, 255, 255)
            couleur = (128, 128, 128) if competence.nom in selected_unit.competences_utilisees else (255, 255, 255)
            game.interface.messages.append((f"{touche}: {competence.nom}", couleur))

        game.flip_display() # Actualisation de l'affichage pour montrer les compétences (et leurs touches associées)

        competence_choisie = None # Variable dans laquelle on stocke la compétence choisie (initialement égale à None)
        while competence_choisie is None: # Boucle jusqu'à ce qu'une compétence soit sélectionnée
            for event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                if event.type == pygame.KEYDOWN: # Dans le cas où une touche a été enfoncée
                    for touche, competence in competences_disponibles.items(): # Parcours des compétences disponibles (et leurs touches associées)
                        if event.key == getattr(pygame, f"K_{touche.lower()}"):
                            if competence.nom not in selected_unit.competences_utilisees: # On s'assure que la compétence n'a pas encore été utilisée durant ce cycle
                                competence_choisie = competence
                                break # Arrêt de la boucle
        return competence_choisie
    
    # Fonction permettant à l'utilisateur d'utiliser une compétence sur une cible (ou une position s'il s'agit des compétences Vortex et Téléportation)
    @staticmethod
    def utiliser_competence(utilisateur, cible, competence, game, interface):
        if competence and utilisateur and cible: # Dans le cas où la compétence peut être utilisée
            competence.utiliser(utilisateur, cible, game, interface) # On l'utilise
            if isinstance(cible, Unit) and cible.team == "enemy" and cible.health <= 0: # Dans le cas où la cible est une unité ennemie ET qu'elle n'a plus de PdV
                if cible in game.enemy_units:
                    game.enemy_units.remove(cible) # Suppression de la cible de la liste des ennemis
                    interface.ajouter_message(f"{cible.perso.nom} a été éliminé(e).")
        else:
            interface.ajouter_message("Impossible d'utiliser la compétence. Vérifiez l'utilisateur, la cible et la compétence.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTION RELATIVE AU CURSEUR (SÉLÉCTION DE CIBLE ET/OU DE CASE):

    @staticmethod
    def selectionner_cible(utilisateur, game, competence = None):
        curseur_x, curseur_y = utilisateur.x, utilisateur.y # Coordonnées du curseur initialisées avec les coordonnées actuelles de l'utilisateur
        if competence:
            if competence.nom in ["Soin", "Bouclier", "Vortex", "Téléportation"]: # S'il s'agit des compétences "Bouclier", "Soin" ou "Téléportation", pas de sélection extérieure
                return utilisateur
            elif competence.nom == "Missile": # Sélection d'une ligne de 5 cases (horizontale ou verticale) pour la compétence "Missile"
                direction = None # Variable dans laquelle on stocke la direction choisie par l'utilisateur
                curseur_positions = [] # Liste contenant les coordonnées (x, y) des 5 cases du curseur
                while True: # Boucle qui reste active jusqu'à ce que l'utilisateur choisisse une direction
                    game.flip_display() # Mise à jour de l'affichage
                    if direction: # Dans le cas où une direction (haut, bas, gauche, droite) a été choisie
                        for x, y in curseur_positions:
                            pygame.draw.rect(game.screen, (255, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin du curseur (en rouge) qui représente la zone d'effet
                    else: # Dans le cas où aucune direction n'a été choisie
                        pygame.draw.rect(game.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin d'un curseur (en vert) autour de l'utilisateur
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
                    game.flip_display() # Mise à jour de l'affichage
                    for dx in range(-1, 2): # Parcourt les déplacements horizontaux par rapport à la case centrale
                        for dy in range(-1, 2): # Parcourt les déplacements verticaux par rapport à la case centrale
                            if 0 <= curseur_x + dx < GRID_SIZE and 0 <= curseur_y + dy < GRID_SIZE: # On s'assure que la case centrale (calculée en combinant ses coordonnées avec les déplacements dx et dy) ne dépassent pas les bordures de la grille
                                pygame.draw.rect(game.screen, (128, 0, 128), ((curseur_x + dx) * CELL_SIZE, (curseur_y + dy) * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin d'un carré (matrice 3x3) qui représente la zone d'effet
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
                                return Unit(Neutral, curseur_x, curseur_y, 0, 'neutral', None, game.interface) # Dans le cas où aucune unité ennemie n'est trouvée, on retourne une position vide comme cible "neutre"

        while True: # Cas général (compétences sans zone d'effet)
            game.flip_display() # Mise à jour de l'affichage
            pygame.draw.rect(game.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin du curseur habituel (en vert)
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
                        for unit in game.enemy_units: # Parcourt les unités ennemies
                            if unit.x == curseur_x and unit.y == curseur_y: # Dans le cas où le curseur désigne une unité ennemie
                                return unit # Retourne l'unité ennemie comme cible valide
                        return Unit(Neutral, curseur_x, curseur_y, 0, 'neutral', None, game.interface)
                    elif event.key == pygame.K_ESCAPE: # Dans le cas où la touche "Échap" est pressée
                        return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Poison(Competence): # Compétence offensive : une seule cible, portée de 2 cases, effet persistant (-15 PdV par tour)
    def __init__(self): # Initialisation des attributs spécifiques
        super().__init__("Poison", portee = 2, dommage = 15, duree = 2) # Portée de l'attaque = 2, dégâts infligés = -15 PdV, durée = 2 tours

    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee: # Si la cible est à portée, soit dans un rayon de 2 cases autour de l'attaquant
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                dmg = cible.HPloss(self.dommage, utilisateur) # Dommages infligés à la cible
                cible.health = cible.health - dmg
                interface.ajouter_message(f"{cible.perso.nom} a été empoisonné(e) ! L'unité subira {dmg} PdV de dégâts pendant {self.duree} tours.")
                cible.appliquer_effet("poison", duree = self.duree, dommages = self.dommage) # Inflige -15 PdV de dégâts par tour à la cible
            else: # Dans le cas où la case sélectionnée ne contient pas d'unité ennemie
                interface.ajouter_message("Aucune cible sélectionnée.")
        else: # Si la cible est hors de portée
            interface.ajouter_message(f"Hors de portée. Vous devez vous trouver dans un rayon de {self.portee} cases.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class PluieDeProjectiles(Competence): # Compétence offensive : plusieurs cibles, portée de 5 cases, pas d'effet persistant (-40 PdV par cible présente dans le périmètre désigné)
    def __init__(self):
        super().__init__("Pluie de projectiles", portee = 5, dommage = 40) # Portée de l'attaque = 5, dégâts infligés = -40 PdV/cible

    def utiliser(self, utilisateur, cible, game, interface):
        if not isinstance(cible, Unit): # On s'assure que la cible est bien une unité
            interface.ajouter_message("Aucune cible sélectionnée.")
            return # Fin de l'exécution
        cible_x, cible_y = cible.x, cible.y # Décomposition des coordonnées de la cible en 2 variables distinctes : cible_x et cible_y
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) > self.portee: # Calcul de la distance de Manhattan entre l'utilisateur et la cible
            interface.ajouter_message(f"Aucune cible à portée.")
            return # Fin de l'exécution

        interface.ajouter_message(f"Pluie de projectiles lancée sur la zone centrée en ({cible_x}, {cible_y}).")
        for dx in range(-1, 2): # Balayage horizontal dans une zone -1 à +1 (3 colonnes autour de la case désignée par l'utilisateur)
            for dy in range(-1, 2): # Balayage vertical dans une zone -1 à +1 (3 lignes autour de la case désignée par l'utilisateur)
                zone_x, zone_y = cible_x + dx, cible_y + dy # Calcul des coordonnées des cases situés dans la matrice 3x3
                if 0 <= zone_x < GRID_SIZE and 0 <= zone_y < GRID_SIZE: # On s'assure que seules les cases valides (celles qui sont bien dans les limites de la grille) de la matrice 3x3 sont prises en compte
                    for enemy in game.enemy_units[:]: # On s'assure que seuls les ennemis subissent les dégâts
                        if enemy.x == zone_x and enemy.y == zone_y: # Dans le cas où les untiés ennemies sont dans la zone 3x3
                            dmg = enemy.HPloss(self.dommage, utilisateur) # Dommages infligés à/aux cible(s)
                            enemy.health = enemy.health - dmg
                            interface.ajouter_message(f"{enemy.perso.nom} perd {dmg} points de vie.")
                            if enemy.health <= 0: # Dans le cas où l'unité meurt
                                game.enemy_units.remove(enemy) # Suppression de l'unité
                                interface.ajouter_message(f"{enemy.perso.nom} a été éliminé.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Missile(Competence): # Compétence offensive : une ou plusieurs cibles, portée de 10 cases, pas d'effet persistant (-15 PdV immédiat)
    def __init__(self):
        super().__init__("Missile", portee = 5, dommage = 15) # Portée de l'attaque = 5, dégâts infligés = -15 PdV/cible

    def utiliser(self, utilisateur, direction, game, interface):
        if direction not in ['haut', 'bas', 'gauche', 'droite']: # On s'assure que la direction choisie est valide (4 directions possibles)
            interface.ajouter_message("Direction invalide.")
            return # Fin de l'exécution
        dx, dy = 0, 0 # Par défaut, aucune direction n'est choisie
        if direction == 'haut': # Si l'utilisateur choisit la direction 'haut', le déplacement est vers le haut (dy = -1)
            dx, dy = 0, -1
        elif direction == 'bas': # Si l'utilisateur choisit la direction 'bas', le déplacement est vers le bas (dy = 1)
            dx, dy = 0, 1
        elif direction == 'gauche': # Si l'utilisateur choisit la direction 'gauche', le déplacement est vers la gauche (dx = -1)
            dx, dy = -1, 0
        elif direction == 'droite': # Si l'utilisateur choisit la direction 'droite', le déplacement est vers la gauche (dx = 1)
            dx, dy = 1, 0

        ennemis_touches = [] # Liste des ennemis touchés
        for i in range(1, self.portee + 1): # Parcourt des 5 cases du curseur (dans la direction choisie)
            x = utilisateur.x + dx * i # Coordonnée X de la case actuelle (où dx est le déplacement horizontal (par exemple, -1 pour "gauche") et i est la distance de la case par rapport à l'utilisateur)
            y = utilisateur.y + dy * i # Coordonnée Y de la case actuelle (où dx est le déplacement horizontal (par exemple, -1 pour "gauche") et i est la distance de la case par rapport à l'utilisateur)
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE: # On s'assure que la case est dans les limites de la grille (pour éviter les débordements)
                for enemy in game.enemy_units: # Parcourt de toutes les unités ennemies
                    if enemy.x == x and enemy.y == y: # Vérification si un ennemi se trouve exactement sur la case atteinte
                        dmg = enemy.HPloss(self.dommage, utilisateur) # Dommages infligés à/aux cible(s)
                        enemy.health = enemy.health - dmg
                        interface.ajouter_message(f"{enemy.perso.nom} vient d'être frappé par un missile ({dmg} PdV).")
                        ennemis_touches.append(enemy)
                        if enemy.health <= 0: # Dans le cas où l'unité meurt
                            game.enemy_units.remove(enemy) # Suppression de l'unité
                            interface.ajouter_message(f"{enemy.perso.nom} a été éliminé !")
        if not ennemis_touches: # Dans le cas où les 5 cases du curseur ne contiennent aucun ennemi
            interface.ajouter_message("Aucune cible visée.")


#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Drain(Competence): # Compétence offensive : une seule cible, portée de 5 cases, pas d'effet persistant (-10 PdV immédiat)
    def __init__(self):
        super().__init__("Drain", portee = 5, dommage = 10) # Portée de l'attaque = 5, dégâts infligés = -10 PdV

    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee: # Si la cible est à portée, soit dans un rayon de 5 cases autour de l'attaquant
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                dmg = cible.HPloss(self.dommage, utilisateur) # Dommages infligés à la cible
                cible.health = cible.health - dmg
                interface.ajouter_message(f"{cible.perso.nom} perd {dmg} points de vie à cause de Drain.")
                utilisateur.health = utilisateur.health + self.dommage # Régénère +10 PdV à l'unité attaquante.
                interface.ajouter_message(f"{utilisateur.perso.nom} regagne {dmg} points de vie grâce à Drain.")
            else: # Dans le cas où la case sélectionnée ne contient pas d'unité ennemie
                interface.ajouter_message("Aucune cible sélectionnée.")
        else: # Si la cible est hors de portée
            interface.ajouter_message(f"Hors de portée. Vous devez vous trouver dans un rayon de {self.portee} cases.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Soin(Competence): # Compétence défensive : personnel, pas d'effet persistant (+10 PdV immédiat)
    def __init__(self):
        super().__init__("Soin", portee = 0) # Il s'agit d'une compétence personnelle (donc portée = 0)
        self.PdV = 10  # Nombre de points de vie récupérés par l'utilisateur

    def utiliser(self, utilisateur, cible, game, interface):
        if cible is not utilisateur: # On s'assure que l'utilisateur se soigne lui-même
            interface.ajouter_message(f"Échec. {utilisateur.perso.nom} ne peut soigner que lui-même.")
            return
        if utilisateur.health < utilisateur.max_health: # Si les PdV de l'utilisateur sont < 100
            points_recuperes = min(self.PdV, utilisateur.max_health - utilisateur.health) # Calcul du nombre de points de vie à récupérer, sans dépasser la jauge maximale
            utilisateur.health += points_recuperes # Ajout des points de vie récupérés aux PdV de l'utilisateur
            interface.ajouter_message(f"{utilisateur.perso.nom} regagne {points_recuperes} points de vie grâce à Soin.")
        else: # Si la barre de vie de l'utilisateur est déjà pleine
            interface.ajouter_message(f"{utilisateur.perso.nom} a déjà toute sa santé.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Bouclier(Competence): # Compétence défensive : personnel, effet persistant pendant 2 tours
    def __init__(self):
        super().__init__("Bouclier", portee = 0, duree = 1) # Il s'agit d'une compétence personnelle (donc portée = 0)

    def utiliser(self, utilisateur, cible, game, interface):
        if cible is not utilisateur: # On s'assure que l'utilisateur utilise le bouclier sur lui-même
            interface.ajouter_message(f"Échec. {utilisateur.perso.nom} ne peut activer le bouclier que sur lui-même.")
            return
        utilisateur.appliquer_effet("bouclier", self.duree) # Empêche toute attaque adverse de faire des dégâts sur l'unité pendant 1 tour
        interface.ajouter_message(f"Bouclier activé sur {utilisateur.perso.nom} pour {self.duree} tour.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Paralysie(Competence): # Compétence passive : une seule cible, portée de 3 cases, durée = 1 tour
    def __init__(self):
        super().__init__("Paralysie", portee = 2, duree = 1) # Portée de la compétence = 2, l'effet ne dure qu'un tour
    
    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee:  # Si la cible est à portée
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                cible.appliquer_effet("immobilisé", duree = 2)  # Applique l'effet
                interface.ajouter_message(f"{cible.perso.nom} est paralysé pour {self.duree} tour.")
            else: # Dans le cas où la case sélectionnée ne contient pas d'unité ennemie
                interface.ajouter_message("Aucune cible sélectionnée.")
        else: # Si la cible est hors de portée
            interface.ajouter_message(f"Hors de portée. Vous devez vous trouver dans un rayon de {self.portee} cases.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Desarmement(Competence): # Compétence passive : une seule cible, portée de 10 cases, durée = 1 tour
    def __init__(self):
        super().__init__("Désarmement", portee = 10, duree = 1) # Portée de la compétence = 10, l'effet ne dure qu'un tour

    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee: # Si la cible est à portée (dans un rayon de 10 cases)
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                cible.appliquer_effet("désarmé", duree = self.duree) # On empêche l'unité cible d'attaquer pendant 1 tour en la désarmant
                interface.ajouter_message(f"{cible.perso.nom} est désarmé et ne peut pas attaquer pendant {self.duree} tour.")
            else: # Dans le cas où la case sélectionnée ne contient pas d'unité ennemie
                interface.ajouter_message("Aucune cible sélectionnée.")
        else: # Si la cible est hors de portée
            interface.ajouter_message(f"Hors de portée. Vous devez vous trouver dans un rayon de {self.portee} cases.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Vortex(Competence): # Compétence passive : toutes les cibles ennemies, portée infinie
    def __init__(self):
        super().__init__("Vortex", portee = -1) # Portée vaut -1 pour indiquer qu'aucune limitation de portée n'est appliquée

    def utiliser(self, utilisateur, cible, game, interface):
        while True: # Boucle qui tourne jusqu'à ce qu'une case valide soit sélectionnée
            nouvelle_position = Competence.selectionner_cible(utilisateur, game)
            if nouvelle_position:
                if interface.passable(nouvelle_position.y, nouvelle_position.x) == False:
                    interface.ajouter_message("Erreur : Vortex nécessite une case cible valide.") # Message d'erreur si ce n'est pas le cas
                    continue
                else:
                    for unit in game.enemy_units: # On parcourt toutes les unités ennemies présentes sur le plateau
                        unit.x, unit.y = nouvelle_position.x, nouvelle_position.y # Déplacement de chaque unité sur les coordonnées de la case cible (cible.x, cible.y)
                    interface.ajouter_message(f"Vortex activé: regroupement de toutes les unités ennemies sur la case ({cible.x}, {cible.y}).") # Activation du Vortex
                    break

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Teleportation(Competence): # Compétence passive : personnel, aucune portée nécessaire
    def __init__(self):
        super().__init__("Téléportation", portee = -1) # Portée vaut -1 pour indiquer qu'aucune limitation de portée n'est appliquée

    def utiliser(self, utilisateur, cible, game, interface):
        while True: # Boucle qui tourne jusqu'à ce qu'une case valide soit sélectionnée
            nouvelle_position = Competence.selectionner_cible(utilisateur, game)

            if nouvelle_position: # Dans le cas où une case est sélectionnée
                if interface.passable(nouvelle_position.y, nouvelle_position.x) == False: # On s'assure que la case soit libre d'accès
                    interface.ajouter_message(f"Impossible d'accéder à la case de coordonnées ({nouvelle_position.x}, {nouvelle_position.y}).")
                    continue # L'utilisateur doit sélectionner une autre case
                else: # Dans le cas où la case n'est pas "bloquée"
                    utilisateur.x, utilisateur.y = nouvelle_position.x, nouvelle_position.y # Si la nouvelle position est valide, mise à jour des coordonnées de l'utilisateur
                    interface.ajouter_message(f"{utilisateur.perso.nom} a été téléporté en ({utilisateur.x}, {utilisateur.y}).")
                    break # Une fois la téléportation effectuée, on quitte la boucle