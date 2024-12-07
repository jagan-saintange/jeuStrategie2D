# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 23:28:53 2024

@author: jag
"""


import pygame
import random

from unit import *
from personnages import *

##########################################"


startposP1 = [(0,0), (1,0), (1,1), (0,1)]
startposE = [(GRID_SIZE-1,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-2), (GRID_SIZE-1,GRID_SIZE-2)]
random.shuffle(startposP1)
random.shuffle(startposE)
       

        
class Ui:

            
        
    def __init__(self):
        self.liste_combattants = Unit.get_instances()
        #print('\n', self.liste_combattants)
        self.player1_units = []
        self.enemy_units = [] #laissons-les publiques
        
        
    def ajout(self, team, i):
        if not (i in self.player1_units or i in self.enemy_units):
            if team == 'player1':
                i.team = 'player1'
                x, y = startposP1.pop(0)
                i.x = x
                i.y = y
                self.player1_units.append(i)
            elif team == 'enemy':
                i.team = 'enemy'
                x, y = startposE.pop(0)
                i.x = x
                i.y = y
                self.enemy_units.append(i)
            else:
                raise TypeError('probleme ajout de combattants')
    
    def selector(self, team, discriminant, nom=None):
        
        if discriminant == 'hasard':
            i = random.choice(self.liste_combattants)
            #print(i)
            self.ajout(team, i)
                
        elif discriminant == 'personnage':
            for i in self.liste_combattants:
                #print(i.perso.nom, nom)
                if i.perso.nom == nom:
                    #print('BIP')
                    self.ajout(team, i)

    
        elif discriminant == 'univers':
            for i in self.liste_combattants:
                if i.perso.univers == nom :
                    i.perso.team = team 
                    self.ajout(team, i)
                
        else:
            raise TypeError("Sélection impossible, erreur input")
        
        return self.player1_units, self.enemy_units
    

    def show_teams(self):
        show1=[_.perso.nom for _ in self.player1_units]
        show2=[_.perso.nom for _ in self.enemy_units]
        print(f"\nl'equipe du joueur 1 est composé de {show1}")
        print(f"l'equipe de enemy est composé de {show2}")
    
    
    
    def run_ui(self):
        """Run the command-line interface for selecting fighters."""
        equipe = 'player1'
        print(self.liste_combattants)
        continuer = (len(self.player1_units)  < 4) or (len(self.enemy_units) < 4)
        while continuer:
            
            
            print("\n\n===============\nMenu:")
            print("1. Sélection par personnage")
            print("2. Sélection par univers")
            print("3. Sélection au hasard")
            print("4. Afficher les équipes")
            print("5. Fin")
            
            
            if len(self.player1_units) < 4:
                equipe = 'player1'
                print("\n===================\nc'est à player1 de choisir")    
                
            elif len(self.enemy_units) < 4 :
                equipe = 'enemy'
                print("\n==================\nc'est à l'adversaire de choisir")    
                
            
            choice = input("\nEntrez l'option souhaitée (1-4): ")
            
                
            if choice == '1':
                
                while len(self.player1_units) <4 and len(self.enemy_units)<4:
                    print("Combattants dispo:")
                    for i, fighter in enumerate(self.liste_combattants):
                        #if fighter.team == 'undefined':  # Only show unselected fighters
                        print(f"{i + 1}: {fighter.perso.nom} Team: {fighter.team})")
                        
                    fighter_choice = input("Entrez le numéro du combattant choisi: ")
                    j = int(fighter_choice) - 1
                    if 0 <= j < len(self.liste_combattants):
                        print('BIP')
                        selected_fighter = self.liste_combattants[j]
                        print('\n',selected_fighter.perso.nom)
                        if selected_fighter.team =='undefined':
                            self.selector(equipe, 'personnage', selected_fighter.perso.nom)
                        else:
                            print("LE COMBATTANT EST DEJA SELECTIONÉ ! ")
                        self.show_teams()
                    else:
                        print("NOMBRE INVALIDE")
    
            elif choice == '2':
                universe_name = input("Entrez le nom de l'univers des persos à sélectionner': ")
                self.selector(equipe, 'univers', universe_name)
                self.show_teams()
                equipe = 'enemy'
                
            elif choice == '3':
                while len(self.player1_units) <4 or len(self.enemy_units)<4:

                    if len(self.player1_units) < 4:
                        self.selector('player1', 'hasard')
                    elif len(self.enemy_units) < 4:
                        equipe = 'enemy'    
                        self.selector('enemy', 'hasard')
                self.show_teams()
                print('BEEP')
            
            elif choice == '4':
                self.show_teams()
                
            elif choice == '5':
                print("Fin")
                break #mettre un print lancement du jeu en sortie
            else:
                print("Invalid choice. Please try again.")
            print('BEEP')
            continuer = (len(self.player1_units) < 4) or (len(self.enemy_units) < 4)
        
        print('choix validé, la partie va commencer. Les équipes sont les suivantes')
        self.show_teams()
        print('Bon fight !')
        return self.player1_units, self.enemy_units
    
    