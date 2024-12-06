import pygame
import pytmx
import pyscroll
import pytmx.util_pygame

from player import Player

class Game:
    
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("pygam-Aventure")

        # Charger la carte TMX
        tmx_data = pytmx.util_pygame.load_pygame('carte.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 0.75
        
        # Créer un joueur (par exemple)
        player_position = tmx_data.get_object_by_name("seydina")
        self.player = Player(player_position.x, player_position.y)
        
        # Créer un autre joueur
        player2_position = [300, 100]  # Une position différente pour le deuxième joueur
        self.player2 = Player(*player2_position)

        # Liste des joueurs
        self.players = [self.player, self.player2]
        self.current_player_index = 0  # Joueur actuellement contrôlé (0 pour player1, 1 pour player2)

        # Liste des murs (collision)
        self.walls = []
        for obj in tmx_data.objects:
            if obj.type == "collision":  # Si l'objet est un mur
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Groupe de sprites
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=3)
        self.group.add(self.player)
        self.group.add(self.player2)

        # Suivre l'état de la touche Espace
        self.space_pressed = False  # Variable pour vérifier si la touche a été pressée

    def handle_input(self):
        pressed = pygame.key.get_pressed()

        # Gérer les déplacements du joueur contrôlé
        player = self.players[self.current_player_index]

        if pressed[pygame.K_UP]:
            player.move_up()
            player.change_animation('up')
        elif pressed[pygame.K_DOWN]:
            player.move_down()
            player.change_animation('down')
        elif pressed[pygame.K_LEFT]:
            player.move_left()
            player.change_animation('left')
        elif pressed[pygame.K_RIGHT]:
            player.move_right()
            player.change_animation('right')

        # Changer de joueur avec la touche espace (détecter un appui unique)
        if pressed[pygame.K_SPACE]:
            if not self.space_pressed:  # Si la touche n'a pas encore été pressée
                self.toggle_player()
                self.space_pressed = True  # Marquer la touche comme pressée
        else:
            self.space_pressed = False  # Si la touche n'est pas enfoncée, réinitialiser

    def update(self):
        self.group.update()

        # Vérification des collisions
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()  # Revenir à la position précédente si une collision se produit

    def toggle_player(self):
        # Change de joueur
        self.current_player_index = 1 - self.current_player_index

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.handle_input()
            self.update()

            # Centrer la caméra sur le joueur actuel
            self.group.center(self.players[self.current_player_index].rect)

            # Dessiner la carte et les joueurs
            self.screen.fill((0, 0, 0))  # Nettoyer l'écran
            self.group.draw(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            clock.tick(60)

        pygame.quit()

# Lancer le jeu
if __name__ == "__main__":
    game = Game()
    game.run()
