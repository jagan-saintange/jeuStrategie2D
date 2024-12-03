# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 11:05:04 2024

@author: jag
"""

import random as rd
from abc import ABC, abstractmethod


#######################################################
#######################################################


#liste nature possible
#nature = ['timide', 'cool', 'engagé']#, 'passioné', 'ingénieux', 'flamboyant', 'délétère', 'morbide', 'cacophonique', 'puissant', 'aimant', 'voltigeur', 'dépressif', 'désespéré', 'optimiste', 'calme', 'tenace', 'démoniaque', 'divin']


#dictionnaire de dictionnaires contenant les propriétés supp de  des natures
nature_carac = {'None': {'attack_power_coeff' : 0., 'defense_power_coeff' : 0.,'agility_power_coeff' : 0., 'speed_coeff' : 0.},
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
        de_nature = [keys for keys in nature_carac.keys()][rd.randint(0, len(nature_carac.keys())-1)]
        self.de_nature = de_nature #est un attribut privé
        #print(self.de_nature)

    @abstractmethod #will be defined in heritage class, mais j'implémente déjà ici car c'est ici qu'on définit la nature et c'est dans les héritiers de Unit qu'on assigne des stats 
    #aussi in case of developpement de futur d'effets différents pour les conséquences de la nature en fonction des classes
    def nature_effect(self):
        pass

#####################################

#Personnages par univers
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

