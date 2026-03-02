from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Isekai Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # update

            # draw
            pygame.display.update()
        
        pygame.quit()

game = Game()
game.run()