# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 17:42:46 2024

@author: jag
"""

import pygame
import random

from unit_ import *



 #Personnages par défaut de notre univers
perso1 = Personnage('number1', 'notre jeu', 'feu')
perso2 = Personnage('number2', 'notre jeu', 'eau')
perso3 = Personnage('number3', 'notre jeu', 'plante')

#Personnages par univers
 
#combattants par défaut
fighter_perso1 = Archer(perso=perso1, x=0, y=0, health=100, team='None', attack_power=4, defense_power=3, agility_power=2, speed = 60)
fighter_perso2 = Aerien(perso=perso2, x=1, y=0, health=100, team='None', attack_power=1, defense_power=5, agility_power=1, speed = 85)
fighter_perso3 = Terrien(perso=perso3, x=1, y=0, health=100, team='None', attack_power=6, defense_power=5, agility_power=1, speed = 10)
fighter_perso4 = Terrien(perso=perso2, x=6, y=6, health=80, team='None', attack_power=5, defense_power=4, agility_power=2, speed = 40)
fighter_perso5 = Terrien(perso=perso3, x=6, y=6, health=80, team='None', attack_power=5, defense_power=4, agility_power=2, speed = 40)
fighter_perso6 = Archer(perso=perso1, x=7, y=6, health=80, team='None',  attack_power=2, defense_power=2, agility_power=1, speed = 70)
fighter_perso7 = Aerien(perso=perso2, x=1, y=0, health=100, team='None', attack_power=1, defense_power=5, agility_power=1, speed = 65)
fighter_perso8 = Archer(perso=perso3, x=0, y=0, health=100, team='None', attack_power=4, defense_power=3, agility_power=2, speed = 60)

       
#Combattants par Univers
        

liste_combattants = [fighter_perso1, fighter_perso2, fighter_perso3, fighter_perso4, fighter_perso5, fighter_perso6, fighter_perso7, fighter_perso8]


class Test:
    

    def __init__(self):
        
        
        
        #Combattants CHOISIS
        self.player1_units = [
                             ]

        self.enemy_units = [
                            ]
        
    def selector(self, team, discriminant, nom):
        if discriminant == 'personnage':
            nom.team = team
            if team == 'player1':
                self.player1_units.append(nom)
            if team == 'enemy':
                self.enemy_units.append(nom)
            
        elif discriminant == 'univers':
            selected = []
            for i in range (len(liste_combattants)) :
                if liste_combattants[i].perso.univers == nom :
                    liste_combattants[i].team = team 
                    selected.append(liste_combattants[i].perso.nom)
                    #print(selected)
                if team == 'player1':
                    self.player1_units+=selected
                if team == 'enemy':
                    self.enemy_units+=selected
                selected=[]
                
        else:
            raise TypeError("Sélection impossible, erreur input")
        
        self.show_teams()
        return self.player1_units, self.enemy_units
    

    def show_teams(self):
        print(f"l'equipe du joueur 1 est composé de {self.player1_units}\n")
        print(f"l'equipe de enemy est composé de {self.enemy_units}")
    
        
        #help(perso1)
        #help(Fighter_perso1)


def main():
    """
    class Mere:
        def __init__(self):
            self.attribut_mere = "Je suis un attribut de la mère"
    
    class Fille(Mere):
        def __init__(self):
            super().__init__()  # Appelle le constructeur de la classe mère
            self.attribut_fille = "Je suis un attribut de la fille"
    
        def afficher_attributs(self):
            # Accéder à l'attribut de la mère
            print(self.attribut_mere)
            # Accéder à l'attribut de la fille
            print(self.attribut_fille)
    
    # Création d'une instance de la classe Fille
    fille = Fille()
    print(fille.attribut_mere)
    """
    print(fighter_perso3.team)
    
    test = Test()
    test.selector('player1', 'univers', 'notre jeu')
    print(fighter_perso3.team)
    
    
    """
    hello = 'blabla'
    if hello:
        print(hello)
    if not hello:
        print('None est False, nor None est True')
     """   
    
    
if __name__ == "__main__":
    main()
