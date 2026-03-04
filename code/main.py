from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from random import randint, choice
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu' 
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100  
        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []
        self.enemies_spawned = 0
        self.enemy_health_multiplier = 1.0
        # audio
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music.set_volume(0.5)
        # setup
        self.load_images()
        self.setup()
        # UI
        self.font = pygame.font.Font(None, ui_font_size)
        self.small_font = pygame.font.Font(None, 24)
        self.highscore = self.load_highscore()
        # upgrade menu options
        self.upgrade_options = ['Damage', 'Health', 'Fire Rate', 'Speed']
        self.upgrade_option_rects = []
        # pause menu options
        self.pause_options = ['Resume', 'Options', 'Quit to Menu']
        self.pause_option_rects = []
        # main menu options
        self.main_menu_options = ['Start', 'Options', 'Quit']
        self.main_menu_rects = []

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()
        self.menu_bg = pygame.image.load(join('images', 'menu_bg.png')).convert()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (window_width, window_height))
        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if self.state == 'playing':
            if pygame.mouse.get_pressed()[0] and self.can_shoot:
                self.shoot_sound.play()
                pos = self.gun.rect.center + self.gun.player_direction * 50
                Bullet(self.bullet_surf, pos, self.gun.player_direction,
                       (self.all_sprites, self.bullet_sprites), self.player)
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            cooldown = self.gun_cooldown * self.player.fire_rate_modifier
            if current_time - self.shoot_time >= cooldown:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * tile_size, y * tile_size), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                for enemy in pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask):
                    enemy.take_damage(bullet.damage)
                    self.impact_sound.play()
                    bullet.kill()
                    break  

    def player_collision(self):
        for enemy in pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            if not enemy.dead:
                died = self.player.take_damage(10)  
                if died:
                    self.state = 'game_over'
                    self.update_highscore()
                break  

    def update_highscore(self):
        score = self.player.level * 100 + self.player.xp
        if score > self.highscore:
            self.highscore = score
            with open('highscore.txt', 'w') as f:
                f.write(str(self.highscore))

    def load_highscore(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def draw_ui(self):
            # level
            level_text = self.font.render(f'Level {self.player.level}', True, ui_font_color)
            self.display_surface.blit(level_text, (1000, 1000))

            # highscore
            highscore_text = self.small_font.render(f'Highscore: {self.highscore}', True, ui_font_color)
            self.display_surface.blit(highscore_text, (window_width - 200, 10))

    def draw_menu(self):
        self.display_surface.blit(self.menu_bg, (0, 0))
        title = self.font.render('Isekai Survivor', True, ui_font_color)
        title_rect = title.get_rect(center=(window_width//2, window_height//5))
        self.display_surface.blit(title, title_rect)

        self.main_menu_rects.clear()
        for i, option in enumerate(self.main_menu_options):
            text = self.font.render(option, True, ui_font_color)
            rect = text.get_rect(center=(window_width//2, window_height//2 + i*150))
            self.display_surface.blit(text, rect)
            self.main_menu_rects.append((rect, option))

    def draw_pause(self):
        overlay = pygame.Surface((window_width, window_height))
        overlay.set_alpha(128)
        overlay.fill('black')
        self.display_surface.blit(overlay, (0, 0))

        pause_text = self.font.render('PAUSED', True, ui_font_color)
        pause_rect = pause_text.get_rect(center=(window_width//2, window_height//6))
        self.display_surface.blit(pause_text, pause_rect)

        self.pause_option_rects.clear()
        for i, option in enumerate(self.pause_options):
            text = self.font.render(option, True, ui_font_color)
            rect = text.get_rect(center=(window_width//2, window_height//2 + i*150))
            self.display_surface.blit(text, rect)
            self.pause_option_rects.append((rect, option))

    def draw_upgrade_menu(self):
        overlay = pygame.Surface((window_width, window_height))
        overlay.set_alpha(128)
        overlay.fill('black')
        self.display_surface.blit(overlay, (0, 0))

        title = self.font.render('Choose an Upgrade', True, ui_font_color)
        title_rect = title.get_rect(center=(window_width//2, window_height//6))
        self.display_surface.blit(title, title_rect)

        self.upgrade_option_rects.clear()
        for i, option in enumerate(self.upgrade_options):
            text = self.font.render(option, True, ui_font_color)
            rect = text.get_rect(center=(window_width//2, window_height//3 + i*150))
            self.display_surface.blit(text, rect)
            self.upgrade_option_rects.append((rect, option))

    def draw_game_over(self):
        overlay = pygame.Surface((window_width, window_height))
        overlay.set_alpha(128)
        overlay.fill('black')
        self.display_surface.blit(overlay, (0, 0))

        go_text = self.font.render('GAME OVER', True, ui_font_color)
        go_rect = go_text.get_rect(center=(window_width//2, window_height//3))
        self.display_surface.blit(go_text, go_rect)

        score_text = self.font.render(f'Final Level: {self.player.level}', True, ui_font_color)
        score_rect = score_text.get_rect(center=(window_width//2, window_height//2))
        self.display_surface.blit(score_text, score_rect)

        high_text = self.font.render(f'Highscore: {self.highscore}', True, ui_font_color)
        high_rect = high_text.get_rect(center=(window_width//2, window_height//2 + 150))
        self.display_surface.blit(high_text, high_rect)

        restart_text = self.small_font.render('Press SPACE to return to menu', True, ui_font_color)
        restart_rect = restart_text.get_rect(center=(window_width//2, window_height*3//4))
        self.display_surface.blit(restart_text, restart_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == 'menu':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        for rect, option in self.main_menu_rects:
                            if rect.collidepoint(mouse_pos):
                                if option == 'Start':
                                    self.reset_game()
                                    self.state = 'playing'
                                elif option == 'Options':
                                    pass
                                elif option == 'Quit':
                                    self.running = False

                elif self.state == 'playing':
                    if event.type == self.enemy_event:
                        self.enemies_spawned += 1
                        self.enemy_health_multiplier = 1.0 + (self.enemies_spawned / 100)
                        Enemy(choice(self.spawn_positions),
                              choice(list(self.enemy_frames.values())),
                              (self.all_sprites, self.enemy_sprites),
                              self.player,
                              self.collision_sprites,
                              self.enemy_health_multiplier)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = 'paused'

                elif self.state == 'paused':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = 'playing'
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        for rect, option in self.pause_option_rects:
                            if rect.collidepoint(mouse_pos):
                                if option == 'Resume':
                                    self.state = 'playing'
                                elif option == 'Options':
                                    pass
                                elif option == 'Quit to Menu':
                                    self.state = 'menu'

                elif self.state == 'upgrade':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        for rect, option in self.upgrade_option_rects:
                            if rect.collidepoint(mouse_pos):
                                self.player.apply_upgrade(option)
                                self.state = 'playing'

                elif self.state == 'game_over':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.state = 'menu'

            if self.state == 'playing':
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()

                if hasattr(self.player, 'upgrade_pending') and self.player.upgrade_pending:
                    self.state = 'upgrade'

            # Draw
            self.display_surface.fill('black')
            if self.state in ('playing', 'paused', 'upgrade', 'game_over'):
                self.all_sprites.draw(self.player.rect.center)
                self.draw_ui()

            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'paused':
                self.draw_pause()
            elif self.state == 'upgrade':
                self.draw_upgrade_menu()
            elif self.state == 'game_over':
                self.draw_game_over()

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def reset_game(self):
        # Clear all sprite groups
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.enemies_spawned = 0
        self.enemy_health_multiplier = 1.0
        # Reload map and create player/gun
        self.setup()
        self.can_shoot = True
        self.shoot_time = 0

if __name__ == '__main__':
    game = Game()
    game.run()