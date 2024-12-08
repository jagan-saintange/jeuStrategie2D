
<<<<<<< HEAD
import pygame
import random as rd
from abc import ABC, abstractmethod
from personnages import *


# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
=======
GRID_SIZE = 21 # Taille de la grille
CELL_SIZE = 30 # Taille d'une cellule (case)
WIDTH = GRID_SIZE * CELL_SIZE + 450 # Augmentation de l'espace pour afficher les compétences
>>>>>>> e0964fe (Interface + corrections de bugs)
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

<<<<<<< HEAD


class Unit():
    """
    Classe pour représenter une unité.

    ...
    Attributs
    ---------
    x : int
        La position x de l'unité sur la grille.
    y : int
        La position y de l'unité sur la grille.
    health : int
        La santé de l'unité.
    attack_power : int
        La puissance d'attaque de l'unité.
    team : str
        L'équipe de l'unité ('player' ou 'enemy').
    is_selected : bool
        Si l'unité est sélectionnée ou non.

    Méthodes
    --------
    move(dx, dy)
        Déplace l'unité de dx, dy.
    attack(target)
        Attaque une unité cible.
    draw(screen)
        Dessine l'unité sur la grille.
    """
    
    _instances = []
    
    @classmethod
    def get_instances(cls):
        # Return a copy of the list of instances
        return cls._instances.copy()


    def __init__(self, perso, x, y, health, team):
        """
        Construit une unité avec une position, une santé, une puissance d'attaque et une équipe.

        Paramètres
        ----------
        x : int
            La position x de l'unité sur la grille.
        y : int
            La position y de l'unité sur la grille.
        health : int
            La santé de l'unité.
        attack_power : int
            La puissance d'attaque de l'unité.
        team : str
            L'équipe de l'unité ('player' ou 'enemy').
        """
        #self.name = name
        self.perso = perso
        self.x = x
        self.y = y
        self.health = health 
        #self.type_unite = type_unite
        self.team = str(team)  # 'player' ou 'enemy'
        #print(f'{self} est self.team)
        self.is_selected = False
        
        Unit._instances.append(self) 
        

    def move(self, dx, dy, player_units, enemy_units):
        """
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy
            #print(dx, dy)
        """
        #print('déplacement déctecté') 
        if self.current_move < self.nombre_deplacements:
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
                try_x = self.x + dx
                try_y = self.y + dy
                test = 0
                for enemy in enemy_units:
                    if (enemy.x == try_x and enemy.y == try_y):
                        test = 1
                        break
                if test==0:
                    for player in player_units:
                        if player.x == try_x and player.y == try_y:
                            test = 2
                            break
                if test == 1:
                    print('déplacement impossible !')
                    return 1
                else:
                    if test == 2:
                        player.x, self.x = self.x, player.x
                        player.y, self.y = self.y, player.y
                        print(f'{self.perso.nom} swaps avec {player.perso.nom} !')
                        return 0
                    else:
                        self.x = try_x
                        self.y = try_y
                    self.current_move += 1
                    return 0
                    
                    
                        
                #print(self.current_move)
                #print(f'il vous reste {self.nombre_deplacements - self.current_move}')
        else:
            #print('impossible, il ne vous reste plus de moves')
            pass  

    def attack(self, target):
        """Attaque une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            self.attack_critique_esquive(target) #j'avais inversé self et target avant aaaa
            #target.HPloss(30, self, crit, choix) #du point de vue du target, il y a perte de pv
            print('attack done')
            
            
    def filter_draw(self, icon_scaled ,color):
        # Create a color filter surface
        filtre = (color[0], color[1], color[2], 70)  # Red color with some transparency
        filtre_surface = pygame.Surface(icon_scaled.get_size(), pygame.SRCALPHA)
        filtre_surface.fill(filtre)
        return filtre_surface
=======
class Unit:
    def __init__(self, x, y, health, attack_power, team, type, interface):
        self.x = x # Position x sur la grille
        self.y = y # Position y sur la grille
        self.health = health # Santé de l'unité
        self.max_health = health
        self.attack_power = attack_power # Puissance d'attaque
        self.team = team # Équipe ('player' ou 'enemy')
        self.type = type # Paramètre pour différencier les unités
        self.is_selected = False # Indique si l'unité est sélectionnée
        self.effects = [] # Liste des effets appliqués (ex: paralysie, bouclier)
        self.interface = interface # Référence à l'interface pour pouvoir afficher les actions

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        immobilise = False
        for effet in self.effects:
            if effet["effet"] == "immobilisé":
                immobilise = True
                break # On arrête la recherche dès qu'on trouve l'effet
        if immobilise: # Si l'effet "immobilisé" est actif
            self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est paralysée et ne peut pas se déplacer.")
            return # Empêche le déplacement
        if not (0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE): # On s'assure de rester à l'intérieur de la grille
            return # Empêche le déplacement
        if not self.interface.is_passable(self.y + dy, self.x + dx):  # Vérifie la passabilité de la case cible
            self.interface.ajouter_message(f"Déplacement impossible : la case ({self.x + dx}, {self.y + dy}) est bloquée.")
            return # Empêche le déplacement
        self.x += dx
        self.y += dy

    def attack(self, cible = None, dommage = None):
        if cible is not None: # Dans le cas où une cible est spécifiée
            if any(effet["effet"] == "désarmé" for effet in self.effects): # Dans le cas où l'unité est désarmée
                self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est désarmée.")
                return # Empêche l'attaque
            if abs(self.x - cible.x) + abs(self.y - cible.y) <= 1: # Dans le cas où la cible est à portée
                self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) attaque {cible.team} unité à ({cible.x}, {cible.y}) (-{self.attack_power} PdV).")
                cible.health -= self.attack_power # Inflige des dégâts à la cible
        elif dommage is not None: # Si des dégâts directs sont appliqués
            if any(effet["effet"] == "bouclier" for effet in self.effects): # Dans le cas où un bouclier est actif
                self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est protégée par un bouclier, aucun dégât reçu.")
                return # Absorption des dégâts par le bouclier
            self.health -= dommage # Dégâts infligés à l'unité
            self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) subit {dommage} dégâts.")
        if self.health <= 0: # Dans le cas où l'unité meurt
            self.health = 0
            self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est morte!")
>>>>>>> e0964fe (Interface + corrections de bugs)

    def draw(self, screen, liste_perso):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player1' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE,
                             self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
        if self.perso.icon !=None:
            icon_scaled = pygame.transform.scale(self.perso.icon, (CELL_SIZE, CELL_SIZE))
            screen.blit(icon_scaled, (self.x * CELL_SIZE, self.y * CELL_SIZE))
            filtre = self.filter_draw(icon_scaled ,color)
            screen.blit(filtre, (self.x * CELL_SIZE, self.y * CELL_SIZE))
            
        elif self.perso.icon == None:
            pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE //
                           2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
            
        


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
        return Unit.ponderation(stats[0], stats[1])*borne_multiplication+1


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
    
    
    def HPloss(self, degats_brut : int, other_unit, crit : bool, choix_stats = [False, False, 1]):
        multiplicateur = self.multiplicateur(other_unit, crit, choix_stats)
        #print(multiplicateur)
        degats = int((multiplicateur * degats_brut))
        comparaison = self.additionneur(other_unit, degats)
        minus_HP = -1 * (degats + comparaison)
        print(f"{self.perso.nom} de {self.team} passe de {self.health}", end='')
        self.health += minus_HP
        if self.health <= 0:
            self.health = 0
            print(f' à {self.health}')
            print(f'unité {self.perso.nom} de {self.team} est neutralisé')
        else:
            print(f' à {self.health}')
        
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
        
        #print(self.perso.de_type)
        if self.perso.de_type == "feu":
            if other.perso.de_type == 'plante':
                resistance = True
        elif self.perso.de_type == "eau":
            #print('je suis eau')
            if other.perso.de_type == 'feu':
                resistance = True
        elif self.perso.de_type == "plante":
            if other.perso.de_type == 'eau':
                resistance = True
        
        #print(faiblesse, resistance)
        return faiblesse, resistance
    

    def attack_critique_esquive(self, target, choix_stats = [False, False, 1]):
        print('===================================\n')    
         
        LIM = 6 #Très important ! est la limite pour lequel un jet de dé est considéré comme un succès ou un échec, indépendemment du commentaire du dé
                #on pourrait imaginer le modifier avec la constante LEVEL voire, de donner des lim indépendante pour chaque jet de dé
                #voir aussi l'equilibrage du jeu, ne pas donner trop de place à l'aléatoire dans un jeu de strat de manière générale même si ici la volonté est de constament bousculer la stratégie du joueur et le forcer à s'adapter
        
        crit = False #on active ou non une comparaison par la stat agilité au lieu de [défense, attaque] classique, le chiffre est le facteur de la stat de l'attaquant
        #normalement est déjà set par défaut comme ça à l'appel de la fonction HPloss
        resD20att = Unit.D20()
        print(resD20att, 'est le res du jet de dé de l attaquant', self.perso.nom)
        if resD20att[0]>LIM:
            if "important" in resD20att[1]:
                #•print(resD20att[1])
                crit = True
                print('coup critique !')
                target.HPloss(30, self, crit, choix_stats)
            elif "critique" in resD20att[1]:
                resD20def = Unit.D20()
                print(resD20def, 'est la TENTATIVE D ESQUIVE MIRACULEUSE de', self.perso.nom)
                if resD20def[0] == 20:
                    print("esquive miraculeuse !")
                else:
                    crit = True
                    target.HPloss(30, self, crit, choix_stats)
                    if target.health >0:
                        crit = False
                        choix_stats = [False, True, 1]
                        target.HPloss(30, self, crit, choix_stats)
                    print("réussite critique + attaque supp")
            
            else:
                target.HPloss(30, self, crit, choix_stats)
            #    raise TypeError('attack_critique_esquive, attaque error')
                
                
        elif resD20att[0]<=LIM:
            resD20def = Unit.D20()
            print(resD20def, 'est le res du jet de dé du defenseur', target.perso.nom)
            if resD20def[0]>LIM:
                if ('important' in resD20att[1]) or ('important' in resD20def[1]):
                    if Unit.ponderation(self.defense_power, target.agility_power) > Unit.ponderation(self.agility_power, target.agility_power):
                       choix_stats = [False, True, 2]
                    else : 
                       choix_stats = [True, True, 2]
                    self.HPloss(30, target, crit, choix_stats) #self redevient la cible de la perte de pv !
            
                elif "critique" in resD20def[1]:
                    resD20att2 = Unit.D20()
                    print(resD20att2, 'est l ULTIME jet de dé de l attaquant', self.perso.nom)
                    if resD20att2[0] == 20:
                        print("esquive miraculeuse !")
                    else:
                        if Unit.ponderation(self.defense_power, target.agility_power) > Unit.ponderation(self.agility_power, target.agility_power):
                           choix_stats = [False, True, 2]
                        else : 
                           choix_stats = [True, True, 2]
                        self.HPloss(30, target, crit, choix_stats) #self redevient la cible de la perte de pv !
                        if self.health > 0:
                            choix_stats = [False, True, 1]
                            self.HPloss(30, target, crit, choix_stats)
                            
                #else:
                #    raise TypeError('attack_critique_esquive, contre-attaque error')
                else:
                    #target.attack_critique_esquive(self, choix_stats = [False, False, 2])
                    target.HPloss(30, self, crit, choix_stats)
        else:
            raise TypeError('attack_critique_esquive, logic error')
        
        #print(self.health, target.health)
        print('\nattaque terminée\n===================================\n')    
            
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
        
#classe composition normalement
class Inventaire:
    """
    Classe qui définit la fonction des inventaires dans le scope de l'unité
    """
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

class Archer(Unit):
    """
    Classe qui définit les unités de type archer
    """
    def __init__(self, perso, x, y, health, team, attack_power, defense_power, agility_power, speed):
        Unit.__init__(self, perso, x, y, health, team)
        #print('\n',perso.de_nature)
        fixed_power = self.nature_effect(perso, attack_power, defense_power, agility_power, speed)
        self.attack_power = fixed_power['attack_power']
        self.defense_power = fixed_power['defense_power']
        self.agility_power = fixed_power['agility_power']
        self.speed = fixed_power['speed']
        self.estim_nb_deplacements()
        
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        """

        Parameters
        ----------
        perso : TYPE
            DESCRIPTION.
        attack_power : TYPE
            DESCRIPTION.
        defense_power : TYPE
            DESCRIPTION.
        agility_power : TYPE
            DESCRIPTION.
        speed : TYPE
            DESCRIPTION.

        Returns
        -------
        fixed_power : TYPE
            DESCRIPTION.

        """
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
    def __init__(self, perso, x, y, health, team, attack_power, defense_power, agility_power, speed):
        Unit.__init__(self, perso, x, y, health, team)
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
    def __init__(self, perso, x, y, health, team, attack_power, defense_power, agility_power, speed):
        Unit.__init__(self, perso, x, y, health, team)
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
        
    # @abstractmethod    
    # def attack(self, target):
    #     """Attaque une unité cible."""
    #     pass
 
    
    # @abstractmethod    
    # def avoid_attack(self):
    #     """calcul le coeff d'esquive d'une attaque"""
    #     #utilise la precision de l'adversaire, la rapidité du joueur, et possiblement la luck des joueurs
    #     pass
    


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


############################################
############################################
fighter_freddy = Terrien(perso=Freddy, x=-1, y=-1, health=120, team='undefined', attack_power=7, defense_power=5, agility_power=2, speed=30)
fighter_chica = Aerien(perso=Chica, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=70)
fighter_bonnie = Terrien(perso=Bonnie, x=-1, y=-1, health=110, team='undefined', attack_power=6, defense_power=5, agility_power=2, speed=40)
fighter_foxy = Aerien(perso=Foxy, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=5, speed=80)

fighter_eren = Terrien(perso=Eren, x=-1, y=-1, health=120, team='undefined', attack_power=8, defense_power=6, agility_power=3, speed=50)
fighter_armin = Archer(perso=Armin, x=-1, y=-1, health=90, team='undefined', attack_power=3, defense_power=4, agility_power=5, speed=75)
fighter_mikasa = Aerien(perso=Mikasa, x=-1, y=-1, health=110, team='undefined', attack_power=7, defense_power=5, agility_power=4, speed=60)
fighter_levi = Aerien(perso=Levi, x=-1, y=-1, health=95, team='undefined', attack_power=6, defense_power=4, agility_power=5, speed=85)

fighter_dre = Terrien(perso=Dre, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=50)
fighter_eminem = Archer(perso=Eminem, x=-1, y=-1, health=90, team='undefined', attack_power=6, defense_power=3, agility_power=4, speed=60)
fighter_fifty = Terrien(perso=Fifty, x=-1, y=-1, health=100, team='undefined', attack_power=4, defense_power=5, agility_power=2, speed=40)
fighter_snoop = Aerien(perso=Snoop, x=-1, y=-1, health=95, team='undefined', attack_power=3, defense_power=4, agility_power=5, speed=70)

fighter_nietzsche = Terrien(perso=Nietzsche,  x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=50)
fighter_marx = Terrien(perso=Marx, x=-1, y=-1, health=110, team='undefined', attack_power=6, defense_power=5, agility_power=2, speed=45)
fighter_camus = Archer(perso=Camus, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=4, speed=60)
fighter_socrates = Terrien(perso=Socrates, x=-1, y=-1, health=105, team='undefined', attack_power=5, defense_power=5, agility_power=3, speed=50)

fighter_trump = Aerien(perso=Trump, x=-1, y=-1, health=110, team='undefined', attack_power=7, defense_power=5, agility_power=2, speed=50)
fighter_biden = Aerien(perso=Biden, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=45)
fighter_obama = Aerien(perso=Obama, x=-1, y=-1, health=105, team='undefined', attack_power=6, defense_power=5, agility_power=3, speed=50)
fighter_bush = Aerien(perso=Bush, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=2, speed=40)

fighter_stop = Terrien(perso=Stop, x=-1, y=-1, health=150, team='undefined', attack_power=0, defense_power=10, agility_power=1, speed=0)  # Panneau statique
fighter_danger = Terrien(perso=Danger, x=-1, y=-1, health=100, team='undefined', attack_power=3, defense_power=4, agility_power=2, speed=30)
fighter_tourner_a_droite = Terrien(perso=tourner_a_droite, x=-1, y=-1, health=100, team='undefined', attack_power=2, defense_power=3, agility_power=3, speed=30)
fighter_aire_de_repos = Terrien(perso=aire_de_repos, x=-1, y=-1, health=100, team='undefined', attack_power=1, defense_power=2, agility_power=2, speed=20)
