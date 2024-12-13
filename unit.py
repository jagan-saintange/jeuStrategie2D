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

    def __init__(self, perso, x, y, health, team, competences, image_path=None):
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
        self.competences = competences
        self.competences_utilisees = set() # Suivi des compétences utilisées uniquement pour cette unité
        self.image_path = image_path # Chemin de l'image associée à l'unité
        
        Unit._instances.append(self) 


    def move(self, dx, dy, player_units, enemy_units):
        # Vérifie si l'unité est immobilisée
        if any(effet["effet"] == "immobilisé" for effet in self.effects):
            print(f"{self.perso.nom} est paralysé(e).")
            return False # Déplacement impossible

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

    def attack(self, cible=None, dommage=None):
        """Attaque une unité cible."""
        if cible is not None:
            if any(effet["effet"] == "désarmé" for effet in self.effects): # Dans le cas où l'utilisateur est désarmé
                print(f"{self.perso.nom} est désarmé(e).")
                return # Empêche l'attaque
            if abs(self.x - cible.x) <= 1 and abs(self.y - cible.y) <= 1:
                self.attack_critique_esquive(cible, dommage) # Dommages infligés
                
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
    
    def HPloss(self, degats_brut : int, other_unit, crit : bool = False, choix_stats = [False, False, 1]):
        if any(effet["effet"] == "bouclier" for effet in self.effects):
            minus_HP = 0  # Aucun point de vie perdu
        else:
            multiplicateur = self.multiplicateur(other_unit, crit, choix_stats)
            #print(multiplicateur)
            degats = int((multiplicateur * degats_brut))
            comparaison = self.additionneur(other_unit, degats)
            minus_HP = -1 * (degats + comparaison)
            print(degats_brut)
            print(f"{self.perso.nom} de passe de {self.health}", end='')
            print(f"{self.perso.nom} subit une attaque (-{minus_HP} Pdv).")
            self.health += minus_HP
            if self.health <= 0:
                self.health = 0
                print(f' à {self.health}')
                print(f'unité {self.perso.nom} de {self.team} est neutralisé')
            else:
                print(f' à {self.health}')
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
    

    def attack_critique_esquive(self, target, dommage, choix_stats=[False, False, 1]):
        LIM = 6
        crit = False
        print(f"{self.perso.nom}] ATTAQUE !")
        resD20att = Unit.D20()
        print(resD20att, 'est le res du jet de dé de l attaquant', self.perso.nom)

        if resD20att[0] > LIM:
            if "important" in resD20att[1]:
                crit = True
                print('coup critique !')
                print(f"{self.perso.nom} fait un coup critique !")
                target.HPloss(dommage, self, crit, choix_stats)
            elif "critique" in resD20att[1]:
                print(f"{self.perso.nom} fait un COUP PARFAIT !")
                resD20def = Unit.D20()
                print(resD20def, 'est la TENTATIVE D ESQUIVE MIRACULEUSE de', self.perso.nom)
                if resD20def[0] != 20:
                    crit = True
                    target.HPloss(dommage, self, crit, choix_stats)
                    if target.health > 0:
                        crit = False
                        choix_stats = [False, True, 1]
                        print(f"{self.perso.nom} porte un second coup gratuit à {target.perso.nom} !")
                        target.HPloss(dommage, self, crit, choix_stats)
                    print("réussite critique + attaque supp")
                else:
                    print(f"{target.perso.nom} fait UNE ESQUIVE MIRACULEUSE !")
            else:
                print(dommage, self, crit, choix_stats)

        elif resD20att[0] <= LIM:
            print(f"Oh non, {self.perso.nom} rate son attaque !")
            resD20def = Unit.D20()
            print(resD20def, 'est le res du jet de dé du defenseur', target.perso.nom)
            if resD20def[0] > LIM:
                if 'important' in resD20att[1] or 'important' in resD20def[1]:
                    choix_stats = [False, True, 2] if self.ponderation(self.defense_power, target.agility_power) > self.ponderation(self.agility_power, target.agility_power) else [True, True, 2]
                    print(f"{target.perso.nom} esquive et fait une CONTRE-ATTAQUE CRITIQUE !")
                    self.HPloss(dommage, target, crit, choix_stats)
                elif "critique" in resD20def[1]:
                    print(f"{target.perso.nom} fait UNE CONTRE-ATTAQUE PARFAITE !")
                    resD20att2 = Unit.D20()
                    print(resD20att2, 'est l ULTIME jet de dé de l attaquant', self.perso.nom)
                    if resD20att2[0] != 20:
                        choix_stats = [False, True, 2] if self.ponderation(self.defense_power, target.agility_power) > self.ponderation(self.agility_power, target.agility_power) else [True, True, 2]
                        self.HPloss(dommage, target, crit, choix_stats)
                        if self.health > 0:
                            choix_stats = [False, True, 1]
                            print(f"{target.perso.nom} porte un second coup gratuit à {self.perso.nom} !")
                            self.HPloss(dommage, target, crit, choix_stats)
                    else:
                        print(f"{self.perso.nom} fait UNE ESQUIVE MIRACULEUSE !")
                else:
                    print(f"{target.perso.nom} esquive et CONTRE-ATTAQUE !")
                    self.HPloss(dommage, target, crit, choix_stats)

        print(f"============== [Fin de l'attaque de {self.perso.nom}] ==============")
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