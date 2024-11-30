
import pygame
import random as rd
from abc import ABC, abstractmethod

# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

#liste nature possible
nature = ['timide', 'cool', 'engagé']#, 'passioné', 'ingénieux', 'flamboyant', 'délétère', 'morbide', 'cacophonique', 'puissant', 'aimant', 'voltigeur', 'dépressif', 'désespéré', 'optimiste', 'calme', 'tenace', 'démoniaque', 'divin']

#dictionnaire de dictionnaires contenant les propriétés supp de  des natures
nature_carac = {None : {'attack_power_coeff' : 0., 'defense_power_coeff' : 0.,'agility_power_coeff' : 0., 'speed_coeff' : 0.},
        'timide' : {'attack_power_coeff' : -0.1, 'defense_power_coeff' : 0.1,'agility_power_coeff' : -0.1, 'speed_coeff' : 0.4},
        'cool' : {'attack_power_coeff' : 0.2, 'defense_power_coeff' : -0.1,'agility_power_coeff' : 0.1, 'speed_coeff' : 0.2},
        'engagé' : {'attack_power_coeff' : 0.3, 'defense_power_coeff' : -0.2, 'agility_power_coeff' : 0.2, 'speed_coeff' : 0.1},
        }


class Personnage: #if perso.univers = le selected alors on passe toutes les unités en player1
    def __init__(self, nom, univers, de_type, description=None, biographie=None):
        self.nom = nom #est un attribut public
        self.univers = univers #est un attribut privé non accessible par convention A RECTIFIER
        self.de_type = de_type #est un attribut privé avec getter et setter
        self.de_nature = None
        self.__nature_chooser() #générer la nature de ce personnage pour cette partie
        self.description = description #attribut public
        self.biographie = biographie #attribut public
    

          
    
    @property
    def de_type(self):
        return self.__de_type
    
       
    @property
    def de_nature(self):
        return self.__de_nature
    
        
    @de_type.setter
    def de_type(self, value):
        if value not in ('feu','eau','plante'):
            print(value)
            raise TypeError("le type doit être 'feu', 'eau' ou 'plante'")
        self.__de_type = value
     
    
    @de_nature.setter
    def de_nature(self, value):
        self.__de_nature = value
        #print(f'set nature est {self.__de_nature}')
    
    
    def __nature_chooser(self): #est une méthode privée
        de_nature = nature[rd.randint(0, len(nature)-1)]
        self.de_nature = de_nature #est un attribut privé
        #print(self.de_nature)

    @abstractmethod #will be defined in heritage class, mais j'implémente déjà ici car c'est ici qu'on définit la nature et c'est dans les héritiers de Unit qu'on assigne des stats 
    #aussi in case of developpement futur d'effets différents pour les conséquences de la nature en fonction des classes
    def nature_effect(self):
        pass
    

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

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """Attaque une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.HPloss(20, self) #du point de vue du target, il y a perte de pv

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player1' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE,
                             self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE //
                           2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    
    
    #@abstractmethod #est différente pour chaque type d'unité
    #def resistance
    
    @staticmethod
    def ponderation(a, b): #plus ils sont faibles en niveau plus c'est la différence entre les stats qui va compter
        seuil = max(a,b)/2
        frac = abs(a-b)/max(a,b)
        if abs(a-b) > seuil:
            return 1.0
        return frac
    
    def multiplicateur(self, other_unit):
        vs_def = self.defense_power
        vs_att = other_unit.attack_power
        return Unit.ponderation(vs_def, vs_att)*0.5+1


    def additionneur(self, other, degats):
        comp = self.comparateur_faiblesse_resistance(other)
        faiblesse, resistance = 0, 0
        if comp[0]:
            faiblesse += degats
            print('la faiblesse est appliquée')
        if comp[1]:
            resistance += -(degats/2) 
            print('la résistance est appliquée')
        return int(faiblesse + resistance)
    
    
    def HPloss(self, degats_brut : int, other_unit):
        multiplicateur = self.multiplicateur(other_unit)
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
        
        print(self.perso.de_type)
        if self.perso.de_type == "feu":
            if other.perso.de_type == 'plante':
                resistance = True
        elif self.perso.de_type == "eau":
            print('je suis eau')
            if other.perso.de_type == 'feu':
                resistance = True
        elif self.perso.de_type == "plante":
            if other.perso.de_type == 'eau':
                resistance = True
        
        print(faiblesse, resistance)
        return faiblesse, resistance
    
    
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
        self.objets.add(item)
        
    def use_item(self, item):
        self.objets.pop(item)
        #mettre une série de if pour gérer les effets des items
    

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
        
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        coeff_attack = nature_carac[perso.de_nature]['attack_power_coeff']
        coeff_defense = nature_carac[perso.de_nature]['defense_power_coeff']
        coeff_agility = nature_carac[perso.de_nature]['agility_power_coeff'] 
        coeff_speed = nature_carac[perso.de_nature]['speed_coeff']   
        fixed_power = {}
        fixed_power['attack_power'] = int(coeff_attack * attack_power + attack_power)
        fixed_power['defense_power'] = int(coeff_defense * defense_power + defense_power)
        fixed_power['agility_power'] = int(coeff_agility * agility_power + agility_power)
        fixed_power['speed'] = int(coeff_speed * speed + speed)
        
        return fixed_power

    @property
    def speed(self):
        return self.__x 
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        if not 50<=value:
            print(value)
            if value<50:
                value = 50
            #raise TypeError("la vitesse d'un archer doit être entre 50 et 100")
        self.__health = value
    
    
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
        
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        coeff_attack = nature_carac[perso.de_nature]['attack_power_coeff']
        coeff_defense = nature_carac[perso.de_nature]['defense_power_coeff']
        coeff_agility = nature_carac[perso.de_nature]['agility_power_coeff'] 
        coeff_speed = nature_carac[perso.de_nature]['speed_coeff']   
        fixed_power = {}
        fixed_power['attack_power'] = int(coeff_attack * attack_power + attack_power)
        fixed_power['defense_power'] = int(coeff_defense * defense_power + defense_power)
        fixed_power['agility_power'] = int(coeff_agility * agility_power + agility_power)
        fixed_power['speed'] = int(coeff_speed * speed + speed)
        
        return fixed_power
    
    @property
    def speed(self):
        return self.__x 
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        if not 50<=value:
            print(value)
            if value<50:
                value = 50
            #else:
            #    raise TypeError("la vitesse d'un aerien doit être entre 50 et 100")
        self.__health = value
        
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
        #self.luck = random.randint(a, b) #peut etre rendre agility aléatoire mais bornée un fonction des genres d'unités, à voir
        
    def nature_effect(self, perso, attack_power, defense_power, agility_power, speed):
        coeff_attack = nature_carac[perso.de_nature]['attack_power_coeff']
        coeff_defense = nature_carac[perso.de_nature]['defense_power_coeff']
        coeff_agility = nature_carac[perso.de_nature]['agility_power_coeff'] 
        coeff_speed = nature_carac[perso.de_nature]['speed_coeff']   
        fixed_power = {}
        fixed_power['attack_power'] = int(coeff_attack * attack_power + attack_power)
        fixed_power['defense_power'] = int(coeff_defense * defense_power + defense_power)
        fixed_power['agility_power'] = int(coeff_agility * agility_power + agility_power)
        fixed_power['speed'] = int(coeff_speed * speed + speed)
        
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
        return self.__x 
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, int):
            print(value)
            raise TypeError("l'argument doit etre un int")
        if not 10<=value<=60:
            print(value)
            if value>60:
                value = 60
            else:
                value = 10
            #raise TypeError("la vitesse d'un terrien doit être entre 10 et 60")
        self.__health = value

