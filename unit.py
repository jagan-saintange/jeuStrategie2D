import pygame
import random as rd
from abc import ABC, abstractmethod
from personnages import *
from interface import *

class Unit():
    
    _instances = []
    
    @classmethod
    def get_instances(cls):
        # Return a copy of the list of instances
        return cls._instances.copy()

    def __init__(self, perso, x, y, health, team, interface = None):
        #self.name = name
        self.perso = perso
        self.x = x
        self.y = y
        self.health = health 
        self.max_health = health # Ajout de l'attribut max_health
        #self.type_unite = type_unite
        self.team = str(team) # 'player' ou 'enemy'
        self.is_selected = False
        self.effects = [] # Liste des effets appliqués (ex: paralysie, bouclier)
        self.interface = interface # Référence à l'interface pour pouvoir afficher les actions
        
        Unit._instances.append(self) 

    def interf(self, interface):
        self.interface = interface

    def move(self, dx, dy, player_units, enemy_units):
        # Vérifie si l'unité est immobilisée
        if any(effet["effet"] == "immobilisé" for effet in self.effects):
            self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est paralysée et ne peut pas se déplacer.")
            return False # Déplacement impossible
        if self.current_move < self.nombre_deplacements:
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
                try_x = self.x + dx
                try_y = self.y + dy
                #if not self.interface.passable(try_x, try_y):
                #    print('Passage refusé !')
                #    self.interface.ajouter_message(f"Passage refusé vers ({self.x}, {self.y}).")
                #    return 1
                if self in enemy_units:
                    print("move d'un enemy")
                    for enemy in enemy_units:
                        if enemy.x == try_x and enemy.y == try_y:
                            enemy.x, self.x = self.x, enemy.x
                            enemy.y, self.y = self.y, enemy.y
                            print(f'{self.perso.nom} swaps avec {player.perso.nom} !')
                            self.interface.ajouter_message(f'{self.perso.nom} swaps avec {player.perso.nom} !')
                            return 0
                        for player in player_units:
                            if player.x == try_x and player.y == try_y:
                                print('déplacement impossible !')
                                self.interface.ajouter_message(f"déplacement impossible vers ({self.x}, {self.y}).")
                                return 1
                        
                               
                for enemy in enemy_units:
                    if (enemy.x == try_x and enemy.y == try_y):
                        print('déplacement impossible !')
                        self.interface.ajouter_message(f"déplacement impossible vers ({self.x}, {self.y}).")
                        return 1
                for player in player_units:
                    if player.x == try_x and player.y == try_y:
                        player.x, self.x = self.x, player.x
                        player.y, self.y = self.y, player.y
                        print(f'{self.perso.nom} swaps avec {player.perso.nom} !')
                        self.interface.ajouter_message(f'{self.perso.nom} swaps avec {player.perso.nom} !')
                        return 0
                self.x = try_x
                self.y = try_y
                self.current_move += 1
                self.interface.ajouter_message(f"Déplacement réussi vers ({self.x}, {self.y}).")
                return 0

    def attack(self, cible=None, dommage=None):
        """Attaque une unité cible."""
        if cible is not None:
            if any(effet["effet"] == "désarmé" for effet in self.effects): # Dans le cas où l'utilisateur est désarmé
                self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est désarmée.")
                return # Empêche l'attaque
            if abs(self.x - cible.x) <= 1 and abs(self.y - cible.y) <= 1:
                self.attack_critique_esquive(cible, dommage, self.interface) # Dommages infligés
                
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
    
    def minusHP(self, degats_bruts): #attention ce n'est pas la variable minus_hp dans HPloss
        self.health -= degats_bruts
    
    
    def HPloss(self, degats_brut : int, other_unit, crit : bool = False, choix_stats = [False, False, 1], interface = None):
        multiplicateur = self.multiplicateur(other_unit, crit, choix_stats)
        #print(multiplicateur)
        degats = int((multiplicateur * degats_brut))
        comparaison = self.additionneur(other_unit, degats)
        minus_HP = -1 * (degats + comparaison)
        print(degats_brut, interface)
        print(f"{self.perso.nom} de {self.team} passe de {self.health}", end='')
        interface.ajouter_message(f"{self.perso.nom} perd {minus_HP} points de vie.")
        self.health += minus_HP
        if self.health <= 0:
            self.health = 0
            print(f' à {self.health}')
            print(f'unité {self.perso.nom} de {self.team} est neutralisé')
            interface.ajouter_message(f'unité {self.perso.nom} de {self.team} est neutralisé')
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
    

    def attack_critique_esquive(self, target, dommage, interface = None, choix_stats=[False, False, 1]):  
        LIM = 6
        crit = False
        self.interface.ajouter_message(f"============== [Début de l'attaque de {self.perso.nom}] ==============")
        
        resD20att = Unit.D20()
        print(resD20att, 'est le res du jet de dé de l attaquant', self.perso.nom)

        if resD20att[0] > LIM:
            if "important" in resD20att[1]:
                crit = True
                print('coup critique !')
                self.interface.ajouter_message(f"{self.perso.nom} fait un coup critique !")
                target.HPloss(dommage, self, crit, choix_stats, self.interface)
            elif "critique" in resD20att[1]:
                self.interface.ajouter_message(f"{self.perso.nom} fait un COUP PARFAIT !")
                resD20def = Unit.D20()
                print(resD20def, 'est la TENTATIVE D ESQUIVE MIRACULEUSE de', self.perso.nom)
                if resD20def[0] != 20:
                    crit = True
                    target.HPloss(dommage, self, crit, choix_stats, self.interface)
                    if target.health > 0:
                        crit = False
                        choix_stats = [False, True, 1]
                        self.interface.ajouter_message(f"{self.perso.nom} porte un second coup gratuit à {target.perso.nom} !")
                        target.HPloss(dommage, self, crit, choix_stats, self.interface)
                    print("réussite critique + attaque supp")
                else:
                    target.interface.ajouter_message(f"{target.perso.nom} fait UNE ESQUIVE MIRACULEUSE !")
            else:
                target.HPloss(dommage, self, crit, choix_stats, interface=self.interface)

        elif resD20att[0] <= LIM:
            self.interface.ajouter_message(f"Oh non, {self.perso.nom} rate son attaque !")
            resD20def = Unit.D20()
            print(resD20def, 'est le res du jet de dé du defenseur', target.perso.nom)
            if resD20def[0] > LIM:
                if 'important' in resD20att[1] or 'important' in resD20def[1]:
                    choix_stats = [False, True, 2] if Unit.ponderation(self.defense_power, target.agility_power) > Unit.ponderation(self.agility_power, target.agility_power) else [True, True, 2]
                    target.interface.ajouter_message(f"{target.perso.nom} esquive et fait une CONTRE-ATTAQUE CRITIQUE !")
                    self.HPloss(dommage, target, crit, choix_stats, target.interface)
                elif "critique" in resD20def[1]:
                    target.interface.ajouter_message(f"{target.perso.nom} fait UNE CONTRE-ATTAQUE PARFAITE !")
                    resD20att2 = Unit.D20()
                    print(resD20att2, 'est l ULTIME jet de dé de l attaquant', self.perso.nom)
                    if resD20att2[0] != 20:
                        choix_stats = [False, True, 2] if Unit.ponderation(self.defense_power, target.agility_power) > Unit.ponderation(self.agility_power, target.agility_power) else [True, True, 2]
                        self.HPloss(dommage, target, crit, choix_stats, target.interface)
                        if self.health > 0:
                            choix_stats = [False, True, 1]
                            target.interface.ajouter_message(f"{target.perso.nom} porte un second coup gratuit à {self.perso.nom} !")
                            self.HPloss(dommage, target, crit, choix_stats, target.interface)
                    else:
                            self.interface.ajouter_message(f"{self.perso.nom} fait UNE ESQUIVE MIRACULEUSE !")
                else:
                    target.interface.ajouter_message(f"{target.perso.nom} esquive et CONTRE-ATTAQUE !")
                    self.HPloss(dommage, target, crit, choix_stats, interface = target.interface)
        
        self.interface.ajouter_message(f"============== [Fin de l'attaque de {self.perso.nom}] ==============")
        print('\nattaque terminée\n===================================\n')
        
        return 0

    # Fonction permettant d'afficher l'unité sur l'écran:
    def draw_unit(self, screen):
        filter_color = (0, 0, 255, 50) if self.team == 'player1' else (255, 0, 0, 50)

        if self.is_selected:
            pygame.draw.rect(screen, (0, 255, 0), (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        if self.perso.icon is not None:
            icon_scaled = pygame.transform.scale(self.perso.icon, (CELL_SIZE, CELL_SIZE))
            screen.blit(icon_scaled, (self.x * CELL_SIZE, self.y * CELL_SIZE))

            # Création d'une surface de filtre semi-transparente de la taille de l'icône
            filter_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)  # Surface avec canal alpha
            filter_surface.fill(filter_color)  # Applique la couleur du filtre
            screen.blit(filter_surface, (self.x * CELL_SIZE, self.y * CELL_SIZE))  # Applique le filtre sur l'icône

        else:
            pygame.draw.circle(screen, (255, 255, 255), (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

        # Calcul et dessin de la barre de vie
        health_bar_width = CELL_SIZE // 2
        health_ratio = self.health / self.max_health
        health_bar_color = (255 - int(255 * health_ratio), int(255 * health_ratio), 0)
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
fighter_freddy = Terrien(perso=Batman, x=-1, y=-1, health=120, team='undefined', attack_power=7, defense_power=5, agility_power=2, speed=30)
fighter_chica = Aerien(perso=Spiderman, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=70)
fighter_bonnie = Terrien(perso=Captain, x=-1, y=-1, health=110, team='undefined', attack_power=6, defense_power=5, agility_power=2, speed=40)
fighter_foxy = Aerien(perso=Deadpool, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=5, speed=80)

fighter_eren = Terrien(perso=Mario, x=-1, y=-1, health=120, team='undefined', attack_power=8, defense_power=6, agility_power=3, speed=50)
fighter_armin = Archer(perso=Luigi, x=-1, y=-1, health=90, team='undefined', attack_power=3, defense_power=4, agility_power=5, speed=75)
fighter_mikasa = Aerien(perso=Peach, x=-1, y=-1, health=110, team='undefined', attack_power=7, defense_power=5, agility_power=4, speed=60)
fighter_levi = Aerien(perso=Toad, x=-1, y=-1, health=95, team='undefined', attack_power=6, defense_power=4, agility_power=5, speed=85)

fighter_dre = Terrien(perso=Pikachu, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=50)
fighter_eminem = Archer(perso=Charmander, x=-1, y=-1, health=90, team='undefined', attack_power=6, defense_power=3, agility_power=4, speed=60)
fighter_fifty = Terrien(perso=Carapuce, x=-1, y=-1, health=100, team='undefined', attack_power=4, defense_power=5, agility_power=2, speed=40)
fighter_snoop = Aerien(perso=Bulbizarre, x=-1, y=-1, health=95, team='undefined', attack_power=3, defense_power=4, agility_power=5, speed=70)

fighter_nietzsche = Terrien(perso=Clochette,  x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=50)
fighter_marx = Terrien(perso=Widow, x=-1, y=-1, health=110, team='undefined', attack_power=6, defense_power=5, agility_power=2, speed=45)
fighter_camus = Archer(perso=Mickey, x=-1, y=-1, health=95, team='undefined', attack_power=4, defense_power=3, agility_power=4, speed=60)
fighter_socrates = Terrien(perso=Picsou, x=-1, y=-1, health=105, team='undefined', attack_power=5, defense_power=5, agility_power=3, speed=50)

fighter_trump = Aerien(perso=Luffy, x=-1, y=-1, health=110, team='undefined', attack_power=7, defense_power=5, agility_power=2, speed=50)
fighter_biden = Aerien(perso=Naruto, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=3, speed=45)
fighter_obama = Aerien(perso=Obama, x=-1, y=-1, health=105, team='undefined', attack_power=6, defense_power=5, agility_power=3, speed=50)
fighter_bush = Aerien(perso=Bush, x=-1, y=-1, health=100, team='undefined', attack_power=5, defense_power=4, agility_power=2, speed=40)

fighter_stop = Terrien(perso=Stop, x=-1, y=-1, health=150, team='undefined', attack_power=2, defense_power=10, agility_power=1, speed=0)  # Panneau statique
fighter_danger = Terrien(perso=Danger, x=-1, y=-1, health=100, team='undefined', attack_power=3, defense_power=4, agility_power=2, speed=30)
fighter_tourner_a_droite = Terrien(perso=tourner_a_droite, x=-1, y=-1, health=100, team='undefined', attack_power=2, defense_power=3, agility_power=3, speed=30)
fighter_aire_de_repos = Terrien(perso=aire_de_repos, x=-1, y=-1, health=100, team='undefined', attack_power=1, defense_power=2, agility_power=2, speed=20)
