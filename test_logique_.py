# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 17:42:46 2024

@author: jag
"""

import pygame
import random

from unit_ import *
from personnages import *



 #Personnages par défaut de notre univers
perso1 = Personnage('number1', 'notre jeu', 'feu')
perso2 = Personnage('number2', 'notre jeu', 'eau')
perso3 = Personnage('number3', 'notre jeu', 'plante')

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


 
#combattants par défaut
fighter_perso1 = Archer(perso=perso1, x=0, y=0, health=100, team='undefined', attack_power=4, defense_power=3, agility_power=2, speed = 60)
fighter_perso2 = Aerien(perso=perso2, x=1, y=0, health=100, team='undefined', attack_power=1, defense_power=5, agility_power=1, speed = 85)
fighter_perso3 = Terrien(perso=perso3, x=1, y=1, health=100, team='undefined', attack_power=6, defense_power=5, agility_power=1, speed = 10)
fighter_perso4 = Terrien(perso=perso2, x=0, y=1, health=80, team='undefined', attack_power=5, defense_power=4, agility_power=2, speed = 40)
fighter_perso5 = Terrien(perso=perso3, x=6, y=6, health=80, team='undefined', attack_power=5, defense_power=4, agility_power=2, speed = 40)
fighter_perso6 = Archer(perso=perso1, x=7, y=6, health=80, team='undefined',  attack_power=2, defense_power=2, agility_power=1, speed = 70)
fighter_perso7 = Aerien(perso=perso2, x=7, y=7, health=100, team='undefined', attack_power=1, defense_power=5, agility_power=1, speed = 65)
fighter_perso8 = Archer(perso=perso3, x=6, y=6, health=100, team='undefined', attack_power=4, defense_power=3, agility_power=2, speed = 60)

       
#Combattants par Univers

class Test:
    
    
    def __init__(self):
        
        
        
        #Combattants CHOISIS
        self.player1_units = [
                             ]

        self.enemy_units = [
                            ]
        
        
        self.liste_combattants = Unit.get_instances()
        #print('\n', self.liste_combattants)
        
    def selector(self, team, discriminant, nom):
        if discriminant == 'personnage':
            for i in self.liste_combattants:
                if i.perso.nom == nom:
                    if team == 'player1':
                        i.team = 'player1'
                        self.player1_units.append(i)
                    else:
                        i.team = 'enemy'
                        self.enemy_units.append(i)
                    self.liste_combattants.pop(i)
            
        elif discriminant == 'univers':
            selected = []
            for j, i in enumerate (self.liste_combattants) :
                if i.perso.univers == nom :
                    i.perso.team = team 
                    selected.append(i.perso.nom)
                    print(selected)
                if team == 'player1':
                    i.team = team
                    self.player1_units+=selected
                else:
                    i.team = 'enemy'
                    self.enemy_units+=selected
                selected = []
                print(self.liste_combattants)
                
        else:
            raise TypeError("Sélection impossible, erreur input")
        
        self.show_teams()
        return self.player1_units, self.enemy_units
    

    def show_teams(self):
        print(f"\nl'equipe du joueur 1 est composé de {self.player1_units}")
        print(f"l'equipe de enemy est composé de {self.enemy_units}")
    
        
        #help(perso1)
        #help(Fighter_perso1)
    
    def run_ui(self):
        """Run the command-line interface for selecting fighters."""
        
        print(self.liste_combattants)
        while True:
            
            if len(self.player1_units) < 4:
                equipe = 'player1'
                print("\n===================\nc'est à player1 de choisir")    
                
            elif len(self.enemy_units) < 4 :
                equipe = 'enemy'
                print("\n==================\nc'est à l'adversaire de choisir")    
                
            else:
                print('fin choix, la partie va commencer. Les équipes sont les suivantes')
                self.show_teams()
                break
            
            print("Menu:")
            print("1. Sélection par personnage")
            print("2. Sélection par univers")
            print("3. Afficher les équipes")
            print("4. Fin")
            
            choice = input("Entrez l'option souhaitée (1-4): ")
            
                
            if choice == '1':
                print("Combattants dispo:")
                for i, fighter in enumerate(self.liste_combattants):
                    #if fighter.team == 'undefined':  # Only show unselected fighters
                    print(f"{i + 1}: {fighter.perso.nom} Team: {fighter.team})")
                    
                fighter_choice = input("Entrez le numéro du combattant choisi: ")
                if int(fighter_choice) - 1 < len(self.liste_combattants):
                    selected_fighter = self.liste_combattants[num]
                    print(selected_fighter)
                    if selected_fighter.team =='undefined':
                        self.selector(equipe, 'personnage', selected_fighter)
                    else:
                        print("Le combattant est déjà sélectionnné")
                else
                    print("Nombre invalide")
    
            elif choice == '2':
                universe_name = input("Enter the universe name (e.g., 'notre jeu', 'FNAF', 'SNK'): ")
                self.selector(equipe, 'univers', universe_name)
                
            elif choice == '3':
                self.show_teams()
                
            elif choice == '4':
                print("Lancement du jeu...")
                break
            else:
                print("Invalid choice. Please try again.")


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
    #test.selector('player1', 'univers', 'notre jeu')
    #print(fighter_perso3.team)
    
    
    class Mere:
        def test(self):
            print(isinstance(self, Fille))
    
    class Fille(Mere):
        pass
        
    a = Fille()
    a.test()
    
    test.run_ui()
    
    """
    hello = 'blabla'
    if hello:
        print(hello)
    if not hello:
        print('None est False, nor None est True')
     """   
    
    
if __name__ == "__main__":
    main()
