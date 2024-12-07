import random as rd
import pygame
from abc import ABC, abstractmethod

#######################################################

#Banques icones

assets_path = {
    'Freddy' : ".\\assets\\freddy.png",    
    'Chica' : ".\\assets\\chica.jpg",
    'Bonnie' : ".\\assets\\bonnie.jpg", 
    'Foxy' : ".\\assets\\foxy.jpg",
    'Eren' : ".\\assets\\eren.jpg",
    'Armin' : ".\\assets\\armin.jpg",
    'Mikasa' : ".\\assets\\mikasa.jpg",
    'Levi' : ".\\assets\\levi.jpg",
    }


#######################################################


#liste nature possible
#nature = ['timide', 'cool', 'engagé']#, 'passioné', 'ingénieux', 'flamboyant', 'délétère', 'morbide', 'cacophonique', 'puissant', 'aimant', 'voltigeur', 'dépressif', 'désespéré', 'optimiste', 'calme', 'tenace', 'démoniaque', 'divin']


#dictionnaire de dictionnaires contenant les propriétés supp de  des natures
nature_carac = {#'None': {'attack_power_coeff' : 0., 'defense_power_coeff' : 0.,'agility_power_coeff' : 0., 'speed_coeff' : 0.},
        'timide' : {'attack_power_coeff' : -0.1, 'defense_power_coeff' : 0.1,'agility_power_coeff' : -0.1, 'speed_coeff' : 0.4},
        'cool' : {'attack_power_coeff' : 0.2, 'defense_power_coeff' : -0.1,'agility_power_coeff' : 0.1, 'speed_coeff' : 0.2},
        'engagé' : {'attack_power_coeff' : 0.3, 'defense_power_coeff' : -0.2, 'agility_power_coeff' : 0.2, 'speed_coeff' : 0.1},
        'passionné': {'attack_power_coeff': 0.4, 'defense_power_coeff': -0.3, 'agility_power_coeff': 0.1, 'speed_coeff': 0.2},
        'ingénieux': {'attack_power_coeff': 0.1, 'defense_power_coeff': 0.2, 'agility_power_coeff': 0.3, 'speed_coeff': -0.1},
        'flamboyant': {'attack_power_coeff': 0.5, 'defense_power_coeff': -0.5, 'agility_power_coeff': 0.0, 'speed_coeff': 0.3},
        'délétère': {'attack_power_coeff': -0.2, 'defense_power_coeff': 0.5, 'agility_power_coeff': -0.3, 'speed_coeff': 0.1},
        'morbide': {'attack_power_coeff': -0.4, 'defense_power_coeff': 0.3, 'agility_power_coeff': 0.2, 'speed_coeff': 0.0},
        'cacophonique': {'attack_power_coeff': 0.0, 'defense_power_coeff': -0.2, 'agility_power_coeff': 0.5, 'speed_coeff': 0.4},
        'puissant': {'attack_power_coeff': 0.6, 'defense_power_coeff': -0.1, 'agility_power_coeff': -0.4, 'speed_coeff': -0.2},
        'aimant': {'attack_power_coeff': 0.1, 'defense_power_coeff': 0.3, 'agility_power_coeff': 0.2, 'speed_coeff': 0.5},
        'voltigeur': {'attack_power_coeff': 0.2, 'defense_power_coeff': -0.1, 'agility_power_coeff': 0.4, 'speed_coeff': 0.3},
        'dépressif': {'attack_power_coeff': -0.3, 'defense_power_coeff': 0.2, 'agility_power_coeff': -0.2, 'speed_coeff': 0.1},
        'désespéré': {'attack_power_coeff': -0.5, 'defense_power_coeff': 0.4, 'agility_power_coeff': 0.0, 'speed_coeff': 0.0},
        'optimiste': {'attack_power_coeff': 0.3, 'defense_power_coeff': 0.1, 'agility_power_coeff': 0.2, 'speed_coeff': 0.4},
        'calme': {'attack_power_coeff': 0.0, 'defense_power_coeff': 0.2, 'agility_power_coeff': 0.1, 'speed_coeff': 0.1},
        'tenace': {'attack_power_coeff': 0.2, 'defense_power_coeff': 0.4, 'agility_power_coeff': -0.1, 'speed_coeff': 0.0},
        'démoniaque': {'attack_power_coeff': 0.5, 'defense_power_coeff': 0.4, 'agility_power_coeff': 0.0, 'speed_coeff': -0.3},
        'divin': {'attack_power_coeff': 1., 'defense_power_coeff': 1., 'agility_power_coeff': 1., 'speed_coeff': 1.},
}



class Personnage: #if perso.univers = le selected alors on passe toutes les unités en player1
    
    _instances = [] #on va se souvenir de toutes les instances de la classe Personnage dans une liste pour l'utiliser après

    def __init__(self, nom, univers, de_type, description=None, biographie=None, icon = None):
        self.nom = nom #est un attribut public
        self.univers = univers #est un attribut privé non accessible par convention A RECTIFIER
        self.de_type = de_type #est un attribut privé avec getter et setter
        self.de_nature = None
        self.__nature_chooser() #générer la nature de ce personnage pour cette partie
        self.description = description #attribut public
        self.biographie = biographie #attribut public
        
        self.icon_set(icon)
        
        Personnage._instances.append(self) #on récup à chaque init le nom du nouveau objet Personnage

          

    def icon_set(self, icon):
        if icon != None:
            icon_img = pygame.image.load(icon)
            
        elif self.nom in assets_path:
            icon_img = assets_path[self.nom]
            self.icon = pygame.image.load(icon_img)
            #self.icon = pygame.transform.scale(self.icon, (64, 64)) 
        
        else:
            self.icon = None
        #print(self.icon)
    
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
        de_nature = [keys for keys in nature_carac.keys()][rd.randint(0, len(nature_carac.keys())-1)]
        self.de_nature = de_nature #est un attribut privé
        print(f'{self.nom} est de nature {self.de_nature}')

    
    @classmethod
    def get_instances(cls):
        # Return a copy of the list of instances
        return cls._instances.copy()

    @abstractmethod #will be defined in heritage class, mais j'implémente déjà ici car c'est ici qu'on définit la nature et c'est dans les héritiers de Unit qu'on assigne des stats 
    #aussi in case of developpement de futur d'effets différents pour les conséquences de la nature en fonction des classes
    def nature_effect(self):
        pass
    
    

#####################################

#Personnages par univers
Neutral = Personnage('Neutral', 'Generic', 'plante')

Freddy = Personnage('Freddy', 'FNAF', 'plante')
Chica = Personnage('Chica', 'FNAF', 'feu')
Bonnie = Personnage('Bonnie', 'FNAF', 'eau')
Foxy = Personnage('Foxy', 'FNAF', 'feu')

Eren = Personnage('Eren', 'SNK', 'feu')
Armin = Personnage('Armin', 'SNK', 'eau')
Mikasa = Personnage('Mikasa', 'SNK', 'feu')
Levi = Personnage('Levi', 'SNK', 'eau')

Dre = Personnage('Snoop', 'WestCoast', 'eau')
Eminem = Personnage('Eminem', 'WestCoast', 'feu')
Fifty = Personnage('Fifty', 'WestCoast', 'eau')
Snoop = Personnage('Snoop', 'WestCoast', 'plante')

Nietzsche = Personnage('Nietzsche', 'philosophe', 'eau')
Marx = Personnage('Marx', 'philosophe', 'feu')
Camus = Personnage('Camus', 'philosophe', 'plante')
Socrates = Personnage('Socrates', 'philosophe', 'plante')

Trump = Personnage('Trump', 'USA', 'feu', 'orange', 'président des états Unis')
Biden = Personnage('Biden', 'USA', 'feu', 'vieux', 'président des états Unis')
Obama = Personnage('Obama', 'USA', 'feu', 'noir', 'président des états Unis')
Bush = Personnage('Bush (père et fils)', 'USA', 'feu', 'blancs', 'présidents des états Unis')

Stop = Personnage('Stop', 'Panneaux de signalisation', 'feu', 'rond rouge, il est écrit "STOP" en gros dessus', 'est le panneau Stop')
Danger = Personnage('Danger', 'Panneaux de signalisation', 'plante')
tourner_a_droite = Personnage('tourner_a_droite', 'Panneaux de signalisation', 'plante')
aire_de_repos = Personnage('aire_de_repos', 'Panneaux de signalisation', 'plante')


perso1 = Personnage('number1', 'notre jeu', 'feu')
perso2 = Personnage('number2', 'notre jeu', 'eau')
perso3 = Personnage('number3', 'notre jeu', 'plante')

#print(Personnage.get_instances())




