from settings import *
from player import Player
from sprites import *
from random import randint

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Isekai Survivor')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        #sprites
        self.player = Player((400,300), self.all_sprites, self.collision_sprites)
        for i in range(6):
            x, y = randint(0, window_width), randint(0, window_height)
            w, h = randint(60,100), randint(50,100)
            CollisionSprite((x,y),(w,h),(self.all_sprites, self.collision_sprites))

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # update
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()