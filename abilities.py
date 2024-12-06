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

class Poison(Competence): # Compétence offensive : une seule cible, portée de 2 cases, effet persistant (-15 PdV par tour)
    def __init__(self): # Initialisation des attributs spécifiques
        super().__init__("Poison", portee = 2, dommage = 15, duree = 3) # Portée de l'attaque = 2, dégâts infligés = -15 PdV, durée = 2 tours

    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee: # Si la cible est à portée, soit dans un rayon de 2 cases autour de l'attaquant
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                cible.attack(dommage = self.dommage) # Dégâts immédiats (-15 PdV)
                interface.ajouter_message(f"{cible.team} unité à ({cible.x}, {cible.y}) a été empoisonnée ! Elle subira {self.dommage} PdV de dégâts pendant {self.duree} tour(s).")
                cible.appliquer_effet("poison", duree = self.duree, dommages = self.dommage) # Inflige -15 PdV de dégâts par tour à la cible
            else: # Dans le cas où la case sélectionnée ne contient pas d'unité ennemie
                interface.ajouter_message("Aucune cible sélectionnée.")
        else: # Si la cible est hors de portée
            interface.ajouter_message(f"Hors de portée. Vous devez vous trouver dans un rayon de {self.portee} cases.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class PluieDeProjectiles(Competence): # Compétence offensive : plusieurs cibles, portée de 2 cases, pas d'effet persistant (-40 PdV par cible présente dans le périmètre désigné)
    def __init__(self):
        super().__init__("Pluie de projectiles", portee = 5, dommage = 40) # Portée de l'attaque = 5, dégâts infligés = -40 PdV/cible

    def utiliser(self, utilisateur, cible, game, interface):
        if not isinstance(cible, Unit): # On s'assure que la cible est bien une unité
            interface.ajouter_message("Aucune cible sélectionnée.")
            return # Fin de l'exécution
        cible_x, cible_y = cible.x, cible.y # Décomposition des coordonnées de la cible en 2 variables distinctes : cible_x et cible_y
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) > self.portee: # Calcul de la distance de Manhattan entre l'utilisateur et la cible
            interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) est trop loin pour lancer Pluie de Projectiles.")
            return # Fin de l'exécution

        interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) lance Pluie de Projectiles sur la zone centrée en ({cible_x}, {cible_y})!")
        for dx in range(-1, 2): # Balayage horizontal dans une zone -1 à +1 (3 colonnes autour de la case désignée par l'utilisateur)
            for dy in range(-1, 2): # Balayage vertical dans une zone -1 à +1 (3 ligneses autour de la case désignée par l'utilisateur)
                zone_x, zone_y = cible_x + dx, cible_y + dy # Calcul des coordonnées des cases situés dans la matrice 3x3
                if 0 <= zone_x < GRID_SIZE and 0 <= zone_y < GRID_SIZE: # On s'assure que seules les cases valides (celles qui sont bien dans les limites de la grille) de la matrice 3x3 sont prises en compte
                    for unit in game.enemy_units[:]: # On s'assure que seuls les ennemis subissent les dégâts
                        if unit.x == zone_x and unit.y == zone_y: # Dans le cas où les untiés ennemies sont dans la zone 3x3
                            unit.attack(dommage = self.dommage) # Dégâts infligés à/aux cible(s)
                            interface.ajouter_message(f"{unit.team} unité à ({unit.x}, {unit.y}) perd {self.dommage} points de vie.")
                            if unit.health <= 0: # Dans le cas où l'unité meurt
                                game.enemy_units.remove(unit) # Suppression de l'unité
                                interface.ajouter_message(f"{unit.team} unité à ({unit.x}, {unit.y}) a été éliminée.")

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
        for i in range(1, self.portee + 1): # Parcourt des 5 cases du curseur (dans la direction choisie)
            x = utilisateur.x + dx * i # Coordonnée X de la case actuelle (où dx est le déplacement horizontal (par exemple, -1 pour "gauche") et i est la distance de la case par rapport à l'utilisateur)
            y = utilisateur.y + dy * i # Coordonnée Y de la case actuelle (où dx est le déplacement horizontal (par exemple, -1 pour "gauche") et i est la distance de la case par rapport à l'utilisateur)
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE: # On s'assure que la case est dans les limites de la grille (pour éviter les débordements)
                for enemy in game.enemy_units[:]: # Parcourt de toutes les unités ennemies
                    if enemy.x == x and enemy.y == y: # Vérification si un ennemi se trouve exactement sur la case atteinte
                        enemy.attack(dommage = self.dommage) # Dégâts infligés (-15 PdV / cible)
                        interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) subit {self.dommage} PdV à cause de Missile !")
                        if enemy.health <= 0: # Dans le cas où l'unité meurt
                            game.enemy_units.remove(enemy) # Suppression de l'unité
                            interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) a été éliminée !")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Drain(Competence): # Compétence offensive : une seule cible, portée de 5 cases, pas d'effet persistant (-10 PdV immédiat)
    def __init__(self):
        super().__init__("Drain", portee = 5, dommage = 10) # Portée de l'attaque = 5, dégâts infligés = -10 PdV

    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee: # Si la cible est à portée, soit dans un rayon de 5 cases autour de l'attaquant
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                cible.attack(dommage = self.dommage) # Inflige -10 PdV à l'unité cible.
                interface.ajouter_message(f"{cible.team} unité à ({cible.x}, {cible.y}) perd {self.dommage} points de vie à cause de Drain!")
                utilisateur.health = min(utilisateur.max_health, utilisateur.health + self.dommage) # Régénère +10 PdV à l'unité attaquante.
                interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) regagne {self.dommage} points de vie grâce à Drain!")
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
            interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) ne peut soigner que lui-même !")
            return
        if utilisateur.health < utilisateur.max_health: # Si les PdV de l'utilisateur sont < 100
            points_recuperes = min(self.PdV, utilisateur.max_health - utilisateur.health) # Calcul du nombre de points de vie à récupérer, sans dépasser la jauge maximale
            utilisateur.health += points_recuperes # Ajout des points de vie récupérés aux PdV de l'utilisateur
            interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) regagne {points_recuperes} points de vie grâce à Soin !")
        else: # Si la barre de vie de l'utilisateur est déjà pleine
            interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) a déjà toute sa santé.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Bouclier(Competence): # Compétence défensive : personnel, effet persistant pendant 2 tours
    def __init__(self):
        super().__init__("Bouclier", portee = 0, duree = 1) # Il s'agit d'une compétence personnelle (donc portée = 0)

    def utiliser(self, utilisateur, cible, game, interface):
        if cible is not utilisateur: # On s'assure que l'utilisateur utilise le bouclier sur lui-même
            interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) ne peut activer le bouclier que sur lui-même !")
            return
        utilisateur.appliquer_effet("bouclier", self.duree) # Empêche toute attaque adverse de faire des dégâts sur l'unité pendant 2 tours
        interface.ajouter_message(f"Bouclier activé sur {utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) pour {self.duree} tours !")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Paralysie(Competence): # Compétence passive : une seule cible, portée de 3 cases, durée = 1 tour
    def __init__(self):
        super().__init__("Paralysie", portee = 300, duree = 2) # Portée de la compétence = 2, l'effet ne dure qu'un tour
    
    def utiliser(self, utilisateur, cible, game, interface):
        if abs(utilisateur.x - cible.x) + abs(utilisateur.y - cible.y) <= self.portee:  # Si la cible est à portée
            if isinstance(cible, Unit) and cible.team == "enemy": # Dans le cas où la case sélectionnée contient une unité ennemie
                cible.appliquer_effet("immobilisé", duree = 2)  # Applique l'effet
                interface.ajouter_message(f"{cible.team} unité à ({cible.x}, {cible.y}) est paralysée pour {self.duree} tour(s)!")
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
                interface.ajouter_message(f"{cible.team} unité à ({cible.x}, {cible.y}) est désarmée et ne peut pas attaquer pendant {self.duree} tour(s)!")
            else: # Dans le cas où la case sélectionnée ne contient pas d'unité ennemie
                interface.ajouter_message("Aucune cible sélectionnée.")
        else: # Si la cible est hors de portée
            interface.ajouter_message(f"Hors de portée. Vous devez vous trouver dans un rayon de {self.portee} cases.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Vortex(Competence): # Compétence passive : toutes les cibles ennemies, portée infinie
    def __init__(self):
        super().__init__("Vortex", portee = -1) # Portée vaut -1 pour indiquer qu'aucune limitation de portée n'est appliquée

    def utiliser(self, utilisateur, cible, game, interface):
        if cible is None or not hasattr(cible, 'x') or not hasattr(cible, 'y'): # On s'assure qu'une case a bien été spécifiée
            interface.ajouter_message("Erreur : Vortex nécessite une case cible valide.") # Message d'erreur si ce n'est pas le cas
            return
        interface.ajouter_message(f"Vortex activé, regroupement de toutes les unités ennemies sur la case ({cible.x}, {cible.y}) !") # Activation du Vortex
        for unit in game.enemy_units: # On parcourt toutes les unités ennemies présentes sur le plateau
            unit.x, unit.y = cible.x, cible.y # Déplacement de chaque unité sur les coordonnées de la case cible (cible.x, cible.y)
            interface.ajouter_message(f"{unit.team} unité à ({unit.x}, {unit.y}) a été déplacée sur la case Vortex ({cible.x}, {cible.y}).")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

class Teleportation(Competence): # Compétence passive : personnel, aucune portée nécessaire
    def __init__(self):
        super().__init__("Téléportation", portee = -1) # Portée vaut -1 pour indiquer qu'aucune limitation de portée n'est appliquée

    def utiliser(self, utilisateur, cible, game, interface): # "Cible" n'est pas utilisé ici, car la téléportation est personnelle
        interface.ajouter_message(f"{utilisateur.team} unité à ({utilisateur.x}, {utilisateur.y}) prépare une Téléportation!")
        nouvelle_position = game.selectionner_cible(utilisateur) # Méthode du jeu qui permet au joueur de choisir une nouvelle position

        if nouvelle_position: # Si une nouvelle position est sélectionnée
            utilisateur.x, utilisateur.y = nouvelle_position.x, nouvelle_position.y # Si la nouvelle position est valide, mise à jour des coordonnées de l'utilisateur
            interface.ajouter_message(f"{utilisateur.team} unité téléportée à ({utilisateur.x}, {utilisateur.y})!")
        else: # Si aucune nouvelle position n'est sélectionnée
            interface.ajouter_message("Téléportation annulée.")