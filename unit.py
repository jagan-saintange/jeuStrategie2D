import pygame
import random as rd
from personnages import *
from interface import *

class Unit():
    
    _instances = []
    
    @classmethod
    def get_instances(cls):
        # Return a copy of the list of instances
        return cls._instances.copy()

    def __init__(self, perso, x, y, health, team, competences, image_path=None):
        self.perso = perso # Objet représentant le personnage (nom, type, etc.)
        self.x = x # Coordonnée x de l'unité sur le terrain
        self.y = y # Coordonnée y de l'unité sur le terrain
        self.health = health # Points de vie actuels de l'unité
        self.max_health = health # Points de vie maximum de l'unité, utile pour calculer les soins ou les jauges de santé
        self.team = str(team) # # Équipe à laquelle appartient l'unité ('player' ou 'enemy')
        self.is_selected = False # Indique si l'unité est actuellement sélectionnée par le joueur
        self.effects = [] # Liste des effets appliqués (ex: paralysie, bouclier)
        self.competences = competences # Liste des compétences de l'unité
        self.competences_utilisees = set() # Suivi des compétence, utile pour limiter les utilisattions
        self.image_path = image_path # Chemin de l'image associée à l'unité
        
        Unit._instances.append(self) # Ajout de l'unité à une liste d'instances


    def move(self, dx, dy, player_units, enemy_units):
        # Vérifie si le déplacement reste dans les limites de la grille
        new_x = self.x + dx
        new_y = self.y + dy
        if new_x < 0 or new_x >= GRID_SIZE or new_y < 0 or new_y >= GRID_SIZE: # Déplacement en dehors de la grille
            return False

        for unit in player_units + enemy_units:
            if unit.x == new_x and unit.y == new_y: # Dans le cas où la case cible est occupée par une autre unité
                self.x, unit.x = unit.x, self.x
                self.y, unit.y = unit.y, self.y
                return True # Swap réussi

        # Si toutes les vérifications sont passées, déplacer l'unité
        self.x = new_x
        self.y = new_y
        return True # Déplacement réussi

    def effectuer_attaque_directe(self, game, interface, screen, enemy_units):
        """Gère l'attaque directe après sélection de la cible."""
        interface.ajouter_message("Vous avez choisi d'attaquer directement. Veuillez sélectionner une cible.")
        game.flip_display() # Mise à jour de l'affichage
        # Sélection de la cible
        cible_x, cible_y = self.x, self.y # Initialisation des coordonnées de la cible (sur la position de l'utilisateur)
        selecting_target = True # Indique si la cible a été sélectionné
        while selecting_target: # Boucle qui tourne tant que l'utilisateur n'a pas validé la sélection de sa cible
            game.flip_display() # Mise à jour de l'affichage
            rect = pygame.Rect(cible_x * CELL_SIZE, cible_y * CELL_SIZE, CELL_SIZE, CELL_SIZE) # Curseur de sélection
            pygame.draw.rect(screen, (255, 255, 0), rect, 3) # Rectangle de couleur jaune (255, 255, 0) qui correspond au curseur de sélection
            pygame.display.update() # Affichage des modifications à l'écran

            for event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                if event.type == pygame.KEYDOWN: # Dans le cas où une touche du clavier a été enfoncée
                    if event.key == pygame.K_LEFT: # Déplacement du curseur vers la gauche (décrémentation de cible_x)
                        cible_x = max(0, cible_x - 1) # On utilise max(0, cible_x - 1) pour rester dans les limites de la grille
                    elif event.key == pygame.K_RIGHT: # Déplacement du curseur vers la gauche (incrémentation de cible_x)
                        cible_x = min(GRID_SIZE - 1, cible_x + 1) # On utilise min(GRID_SIZE - 1, cible_x + 1) pour rester dans les limites de la grille
                    elif event.key == pygame.K_UP: # Déplacement du curseur vers le haut (décrémentation de cible_y)
                        cible_y = max(0, cible_y - 1) # On utilise max(0, cible_y - 1) pour rester dans les limites de la grille
                    elif event.key == pygame.K_DOWN: # Déplacement du curseur vers le bas (incrémentation de cible_y)
                        cible_y = min(GRID_SIZE - 1, cible_y + 1) # On utilise min(GRID_SIZE - 1, cible_y + 1) pour rester dans les limites de la grille
                    elif event.key == pygame.K_RETURN: # Dans le cas où l'utilisateur presse la touche "Entrée"
                        selecting_target = False # Validation de la cible, arrêt de la boucle de sélection

        # On retourne l'ennemi situé aux coordonnées (cible_x, cible_y) (None s'il n'y en a pas)
        cible = next((enemy for enemy in enemy_units if enemy.x == cible_x and enemy.y == cible_y), None)
        if cible: # Dans le cas où une cible ennemie valide a été trouvée
            if abs(self.x - cible_x) + abs(self.y - cible_y) == 1: # Si elle est à portée (case adjacente à celle de l'utilisateur)
                self.attack_critique_esquive(game, cible, 30) # Dégâts bruts = 30 avant l'ajustement (en fonction de l'attaque/défense/agilité des partis impliqués)
                if cible.health <= 0: # Dans le cas où la cible n'a plus de PdV après l'attaque
                    enemy_units.remove(cible) # On la supprime des unités ennemies
            else: # Si la cible n'est pas à portée
                interface.ajouter_message("La cible n'est pas à votre portée.")
        else: # Si aucune cible n'a été trouvée aux coordonnées spécifiées
            interface.ajouter_message("Aucune cible sélectionnée.")
                
    def appliquer_effet(self, effet, duree, dommages = 0):
        for existing_effet in self.effects:
            if existing_effet["effet"] == effet.lower():
                # Si l'effet est déjà actif, on met à jour sa durée et ses dommages
                existing_effet["duree"] = max(existing_effet["duree"], duree)
                existing_effet["dommages"] = max(existing_effet["dommages"], dommages)
                return
        # Si l'effet n'existe pas, on l'ajoute
        self.effects.append({"effet": effet.lower(), "duree": duree, "dommages": dommages})
     
    def estim_nb_deplacements(self):
        nombre_deplacements = 1
        nombre_deplacements += self.speed//20
        self.nombre_deplacements = nombre_deplacements #on laisse public pour l'instant
        self.current_move = 0 #on le crée que quand le nombre de déplacement est créé
    
    @staticmethod
    def ponderation(a, b): #plus ils sont faibles en niveau plus c'est la différence entre les stats qui va compter
        seuil = max(a,b)/2
        frac = abs(a-b)/max(a,b)
        if abs(a-b) > seuil:
            return 1.0
        return frac
    
    @staticmethod
    def D20():
        commentaire = "" #va nous permettre d'identifier des catégories en plus de récup la valeur exacte pour des calculs
        result = rd.randint(1, 20)
        if result == 1:
            commentaire = "échec critique" 
        elif result <= 5:
            commentaire = "échec important"
        elif result <=9:
            commentaire = "échec faible"
        elif result <= 15:
            commentaire = "réussite faible"
        elif result <= 19:
            commentaire = "réussite importante"
        else:
            commentaire = "réussite critique"
        
        return result, commentaire

    def choix_stat_comp(self, other_unit, choix_stats):
        choix = choix_stats[:2]
        facteur = choix_stats[-1]
        if choix == [False, False]: #selfdéfense conte otherattaque   
            vs_def = self.defense_power
            vs_att = other_unit.attack_power
            return vs_def, vs_att*facteur
        elif choix ==  [True, False]: #selfagilité contre otherattaque
            vs_agi = self.agility_power
            vs_att = other_unit.attack_power
            return vs_agi, vs_att*facteur
        elif choix ==  [False, True]: #selfdéfense contre otheragilité
            vs_def = self.defense_power
            vs_agi = other_unit.agility_power
            return vs_def, vs_agi*facteur
        elif choix ==  [True, True]: #selfagilité contre otheragilité
            vs_agi = self.agility_power
            vs_agi_other = other_unit.agility_power
            return vs_agi, vs_agi_other*facteur
        else:
            raise TypeError('choix_stat_comp')
    
    def multiplicateur(self, other_unit, crit, choix_stats):
        if crit:
            borne_multiplication = 1.5
        else: 
            borne_multiplication = 0.5
        stats = self.choix_stat_comp(other_unit, choix_stats)
        return self.ponderation(stats[0], stats[1])*borne_multiplication+1

    def additionneur(self, other, degats):
        comp = self.comparateur_faiblesse_resistance(other)
        faiblesse, resistance = 0, 0
        if comp[0]:
            faiblesse += degats
            print('la faiblesse est appliquée')
        if comp[1]:
            resistance += -(degats/2) 
            print('la résistance est appliquée')
        return round(faiblesse + resistance)
    
    def minusHP(self, degats_bruts): #attention ce n'est pas la variable minus_hp dans HPloss
        self.health -= degats_bruts
    
    def HPloss(self, game, degats_brut : int, other_unit, crit : bool = False, choix_stats = [False, False, 1]):
        if any(effet["effet"] == "bouclier" for effet in self.effects):
            minus_HP = 0  # Aucun point de vie perdu
        else:
            multiplicateur = self.multiplicateur(other_unit, crit, choix_stats)
            degats = int((multiplicateur * degats_brut))
            comparaison = self.additionneur(other_unit, degats)
            minus_HP = -1 * (degats + comparaison)
            health_bis = self.health
            self.health += minus_HP
            if self.health > 0:
                game.interface.ajouter_message(f"[{minus_HP} PDV POUR {self.perso.nom.upper()}] L'unité passe de {self.health + abs(minus_HP)} à {self.health} points de vie.")
            else:
                self.health = 0
                game.interface.ajouter_message(f"[-{health_bis} PDV POUR {self.perso.nom.upper()}] L'UNITÉ A ÉTÉ ÉLIMINÉE !")
                if self.team == 'player':
                    game.player_units = [unit for unit in game.player_units if unit.health > 0]
                elif self.team == 'enemy':
                    game.enemy_units = [unit for unit in game.enemy_units if unit.health > 0]
        return minus_HP
        
    def comparateur_faiblesse_resistance(self, other):
        faiblesse = False
        resistance = False
        
        if isinstance(self, Archer):
            if isinstance(other, Terrien):
                faiblesse = True
        elif isinstance(self, Terrien):
            if isinstance(other, Aerien):
                faiblesse = True
        elif isinstance(self, Aerien):
            if isinstance(other, Archer):
                faiblesse = True

        if self.perso.de_type == "feu":
            if other.perso.de_type == 'plante':
                resistance = True
        elif self.perso.de_type == "eau":
            if other.perso.de_type == 'feu':
                resistance = True
        elif self.perso.de_type == "plante":
            if other.perso.de_type == 'eau':
                resistance = True

        return faiblesse, resistance
    
    def attack_critique_esquive(self, game, target, dommage, choix_stats=[False, False, 1]):
        if target.health <= 0: # Si la cible est déjà morte
            return
        LIM = 6
        crit = False
        resD20att = Unit.D20()
        print(resD20att, 'est le res du jet de dé de l attaquant', self.perso.nom)

        if resD20att[0] > LIM:
            if "important" in resD20att[1]:
                crit = True
                game.interface.ajouter_message(f"{self.perso.nom} assène un coup CRITIQUE à {target.perso.nom} !")
                target.HPloss(game, dommage, self, crit, choix_stats)
            elif "critique" in resD20att[1]:
                resD20def = Unit.D20()
                if resD20def[0] != 20:
                    crit = True
                    game.interface.ajouter_message(f"{target.perso.nom} rate sa tentative d'esquive !")
                    target.HPloss(game, dommage, self, crit, choix_stats)
                    if target.health > 0 and self.health > 0:
                        crit = False
                        choix_stats = [False, True, 1]
                        game.interface.ajouter_message(f"{self.perso.nom} porte un second coup à {target.perso.nom} !")
                        target.HPloss(game, dommage, self, crit, choix_stats)
                else:
                    game.interface.ajouter_message(f"{target.perso.nom} ESQUIVE miraculeusement !")
            else:
                game.interface.ajouter_message(f"{self.perso.nom} attaque {target.perso.nom} !")
                target.HPloss(game, dommage, self, crit, choix_stats)

        elif resD20att[0] <= LIM:
            game.interface.ajouter_message(f"Oh non, {self.perso.nom} vient de rater son attaque...")
            resD20def = Unit.D20()
            if resD20def[0] > LIM:
                if 'important' in resD20att[1] or 'important' in resD20def[1] and self.health != 0:
                    choix_stats = [False, True, 2] if self.ponderation(self.defense_power, target.agility_power) > self.ponderation(self.agility_power, target.agility_power) else [True, True, 2]
                    game.interface.ajouter_message(f"{target.perso.nom} pare le coup, puis contre-attaque de manière critique !")
                    self.HPloss(game, dommage, target, crit, choix_stats)
                elif "critique" in resD20def[1]:
                    game.interface.ajouter_message(f"{target.perso.nom} CONTRE-ATTAQUE PARFAITEMENT !")
                    resD20att2 = Unit.D20()
                    if resD20att2[0] != 20:
                        choix_stats = [False, True, 2] if self.ponderation(self.defense_power, target.agility_power) > self.ponderation(self.agility_power, target.agility_power) else [True, True, 2]
                        game.interface.ajouter_message(f"{target.perso.nom} porte un coup à {self.perso.nom} !")
                        self.HPloss(game, dommage, target, crit, choix_stats)
                        if self.health > 0 and target.health > 0:
                            choix_stats = [False, True, 1]
                            game.interface.ajouter_message(f"{target.perso.nom} porte un second coup à {self.perso.nom} !")
                            self.HPloss(game, dommage, target, crit, choix_stats)
                    else:
                        game.interface.ajouter_message(f"{self.perso.nom} esquive miraculeusement !")
                else:
                    game.interface.ajouter_message(f"{target.perso.nom} pare le coup, puis contre-attaque immédiatemment !")
                    self.HPloss(game, dommage, target, crit, choix_stats)
        return 0

    # Fonction permettant d'afficher l'unité sur l'écran:
    def draw_unit(self, screen):
        filter_color = (0, 0, 255, 50) if self.team == 'player' else (255, 0, 0, 50)

        if self.is_selected:
            pygame.draw.rect(screen, (0, 255, 0), (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        if self.perso.icon is not None:
            icon_scaled = pygame.transform.scale(self.perso.icon, (CELL_SIZE, CELL_SIZE))
            screen.blit(icon_scaled, (self.x * CELL_SIZE, self.y * CELL_SIZE))

            # Création d'une surface de filtre semi-transparente de la taille de l'icône
            filter_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA) # Surface occupée par le filtre
            filter_surface.fill(filter_color) # Couleur du filtre
            screen.blit(filter_surface, (self.x * CELL_SIZE, self.y * CELL_SIZE)) # Application du filtre sur l'icône

        else:
            pygame.draw.circle(screen, (255, 255, 255), (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

        # Calcul et dessin de la barre de vie
        health_bar_width = CELL_SIZE // 2
        if self.max_health == 0: # Empêchement d'une division par zéro
            health_ratio = 0
        else:
            health_ratio = self.health / self.max_health

        # Validation des valeurs de couleur
        health_bar_color = (max(0, min(255, 255 - int(255 * health_ratio))), max(0, min(255, int(255 * health_ratio))), 0)
        pygame.draw.rect(screen, health_bar_color, (self.x * CELL_SIZE + CELL_SIZE // 4, self.y * CELL_SIZE - 5, int(health_bar_width * health_ratio), 5))
            
###############################################"""""
    
    #MODIF ATTRIBUTS
    @property
    def perso(self):
        return self.__perso
    
    @property
    def x(self):
        return self.__x 
    
    @property
    def y(self):
        return self.__y
    
    @property
    def health(self):
        return self.__health 
    
    @property
    def team(self):
        return self.__team
    
    @perso.setter
    def perso(self, value):
        if not isinstance(value, Personnage):
            print(value)
            raise TypeError('perso doit être un objet de Personnage')
        self.__perso = value
        
    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        self.__x = value
     
    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        self.__y = value
        
    @health.setter #par exemple ceci m'a aidé quand je faisais les calculs des dégats, j'ai set un float sans réfléchir il a raise
    def health(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        self.__health = value
       
    @team.setter
    def team(self, value):
        if not isinstance(value, str):# or value!='enemy' or value!='player':
             print(value)
             raise TypeError("l'argument doit etre un str valide")
        self.__team = value

# Malheureusement, nous n'avons pas eu le temps d'implémenter les collectables (qui vont de pair avec la classe "Inventaire")
"""
class Inventaire: # Classe qui définit la fonction des inventaires dans le scope de l'unité
    def __init__(self):
        self.objets={}
        
    def add(self, item):
        self.objets[item.name] = item
        
    def use_item(self, item_name):
        if item_name in self.objets:
            item = self.objets.pop(item_name)
        #mettre une série de if pour gérer les effets des items
        else: #on sait jamais on met ça temporairement
            print(f"L'objet {item_name} n'est pas dans l'inventaire.")
"""

class Archer(Unit):
    """
    Classe qui définit les unités de type archer
    """
    def __init__(self, perso, x, y, health, team, attack_power, defense_power, agility_power, speed, competences, image_path=None):
        Unit.__init__(self, perso, x, y, health, team, competences, image_path)
        #print('\n',perso.de_nature)
        fixed_power = self.nature_effect(perso, attack_power, defense_power, agility_power, speed)
        self.attack_power = fixed_power['attack_power']
        self.defense_power = fixed_power['defense_power']
        self.agility_power = fixed_power['agility_power']
        self.speed = fixed_power['speed']
        self.estim_nb_deplacements()
        
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        coeff_attack = nature_carac[perso.de_nature]['attack_power_coeff']
        coeff_defense = nature_carac[perso.de_nature]['defense_power_coeff']
        coeff_agility = nature_carac[perso.de_nature]['agility_power_coeff'] 
        coeff_speed = nature_carac[perso.de_nature]['speed_coeff']   
        fixed_power = {}
        fixed_power['attack_power'] = round(coeff_attack * attack_power + attack_power)
        fixed_power['defense_power'] = round(coeff_defense * defense_power + defense_power)
        fixed_power['agility_power'] = round(coeff_agility * agility_power + agility_power)
        fixed_power['speed'] = round(coeff_speed * speed + speed)
        
        return fixed_power

    @property
    def speed(self):
        return self.__speed
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        if not 50<=value:
            #print(value)
            if value<50:
                print(value, "speed value changed to ", end='')
                value = 50
                print(value)
                #raise TypeError("la vitesse d'un archer doit être entre 50 et 100")
        self.__speed = value
        
    
    
class Aerien(Unit):
    """
    Classe qui définit les unités de type archer
    """
    def __init__(self, perso, x, y, health, team, attack_power, defense_power, agility_power, speed, competences, image_path=None):
        Unit.__init__(self, perso, x, y, health, team, competences, image_path)
        #print('\n',perso.de_nature)
        fixed_power = self.nature_effect(perso, attack_power, defense_power, agility_power, speed)
        self.attack_power = fixed_power['attack_power']
        self.defense_power = fixed_power['defense_power']
        self.agility_power = fixed_power['agility_power']
        self.speed = fixed_power['speed']
        self.estim_nb_deplacements()
        
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        coeff_attack = nature_carac[perso.de_nature]['attack_power_coeff']
        coeff_defense = nature_carac[perso.de_nature]['defense_power_coeff']
        coeff_agility = nature_carac[perso.de_nature]['agility_power_coeff'] 
        coeff_speed = nature_carac[perso.de_nature]['speed_coeff']   
        fixed_power = {}
        fixed_power['attack_power'] = round(coeff_attack * attack_power + attack_power)
        fixed_power['defense_power'] = round(coeff_defense * defense_power + defense_power)
        fixed_power['agility_power'] = round(coeff_agility * agility_power + agility_power)
        fixed_power['speed'] = round(coeff_speed * speed + speed)
        
        return fixed_power
    
    @property
    def speed(self):
        return self.__speed 
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        if not 50<=value:
            print(value, "speed value changed to ", end='')
            if value<50:
                value = 50
                print(value)
                
            #else:
            #    raise TypeError("la vitesse d'un aerien doit être entre 50 et 100")
        self.__speed = value
        
class Terrien(Unit):
    """
    Classe qui définit les unités de type archer
    """
    def __init__(self, perso, x, y, health, team, attack_power, defense_power, agility_power, speed, competences, image_path=None):
        Unit.__init__(self, perso, x, y, health, team, competences, image_path)
        #print('\n',perso.de_nature)
        fixed_power = self.nature_effect(perso, attack_power, defense_power, agility_power, speed)
        self.attack_power = fixed_power['attack_power']
        self.defense_power = fixed_power['defense_power']
        self.agility_power = fixed_power['agility_power']
        self.speed = fixed_power['speed']
        #print(self.attack_power)
        self.estim_nb_deplacements()
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        coeff_attack = nature_carac[perso.de_nature]['attack_power_coeff']
        coeff_defense = nature_carac[perso.de_nature]['defense_power_coeff']
        coeff_agility = nature_carac[perso.de_nature]['agility_power_coeff'] 
        coeff_speed = nature_carac[perso.de_nature]['speed_coeff']   
        fixed_power = {}
        fixed_power['attack_power'] = round(coeff_attack * attack_power + attack_power)
        fixed_power['defense_power'] = round(coeff_defense * defense_power + defense_power)
        fixed_power['agility_power'] = round(coeff_agility * agility_power + agility_power)
        fixed_power['speed'] = round(coeff_speed * speed + speed)
        
        return fixed_power

    @property
    def speed(self):
        return self.__speed
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        if not 10<=value<=60:
            print(value, "speed value changed to ", end='')
            if value>60:
                value = 60
            else:
                value = 10
            print(value)
            #raise TypeError("la vitesse d'un terrien doit être entre 10 et 60")
        self.__speed = value