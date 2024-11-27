import pygame as pg
import sys
import time
from bird import Bird
from pipe import Pipe

pg.init()

class Game:
    def __init__(self):
        # Setting window config
        self.width = 600
        self.height = 600
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("Birdly")
        self.clock = pg.time.Clock()
        self.move_speed = 250
        self.bird = Bird(self.scale_factor)

        self.is_enter_pressed = False
        self.pipes = []
        self.pipe_generate_counter = 71
        self.score = 0
        self.game_over = False

        # Load font Ponderosa
        self.font_ponderosa = pg.font.Font("assets/Ponderosa.ttf", 24) 
        self.font_ponderosa_large = pg.font.Font("assets/Ponderosa.ttf", 42)

        self.setUpBgAndGround()
        self.gameLoop()

    def gameLoop(self):
        last_time = time.time()
        while True:
            # Calculating delta time
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        if self.game_over:
                            self.reset_game()  # Restart game if over
                        else:
                            self.is_enter_pressed = True  # Start game
                            self.bird.update_on = True
                    if event.key == pg.K_SPACE and self.is_enter_pressed and not self.game_over:
                        self.bird.flap(dt)

            if not self.game_over:
                self.updateEverything(dt)
                self.checkCollisions()

            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    def checkCollisions(self):
        if len(self.pipes):
            if self.bird.rect.bottom > 568:
                self.game_over = True
                self.is_enter_pressed = False
            if (self.bird.rect.colliderect(self.pipes[0].rect_down) or
                self.bird.rect.colliderect(self.pipes[0].rect_up)):
                self.game_over = True
                self.is_enter_pressed = False

    def updateEverything(self, dt):
        if self.is_enter_pressed and not self.game_over:
            # Moving the ground
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            # Generating pipes
            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0
                
            self.pipe_generate_counter += 1

            # Moving the pipes
            for pipe in self.pipes:
                pipe.update(dt)

            # Removing pipes if out of screen
            if len(self.pipes) != 0:
                if self.pipes[0].rect_up.right < 0:
                    self.pipes.pop(0)
                    self.score += 1  # Increment score when a pipe is passed

            # Moving the bird
            self.bird.update(dt)

    def drawEverything(self):
        # Gambarkan latar belakang dan elemen permainan
        self.win.blit(self.bg_img, (0, -300))
        for pipe in self.pipes:
            pipe.drawPipe(self.win)
        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        # Tampilkan skor
        score_surface = self.font_ponderosa.render(f'Score: {self.score}', True, (255, 255, 255))
        self.win.blit(score_surface, (10, 10))

        # Jika permainan belum dimulai, tampilkan teks "Press ENTER to Start"
        if not self.is_enter_pressed and not self.game_over:
            start_surface = self.font_ponderosa.render("Press ENTER to Start", True, (47, 79, 79))
            self.win.blit(start_surface, (self.width // 2 - start_surface.get_width() // 2, 300))

        # Tampilkan pesan Game Over jika perlu
        if self.game_over:
            game_over_surface = self.font_ponderosa_large.render('Game Over!', True, (255, 0, 0))
            restart_surface = self.font_ponderosa.render('Press Enter to Restart', True, (47, 79, 79))
            self.win.blit(game_over_surface, (self.width // 2 - game_over_surface.get_width() // 2, self.height // 2 - 40))
            self.win.blit(restart_surface, (self.width // 2 - restart_surface.get_width() // 2, self.height // 2 + 20))

    def setUpBgAndGround(self):
        # Loading images for bg and ground
        self.bg_img = pg.transform.scale_by(pg.image.load("assets/bg.png").convert(), self.scale_factor)
        self.ground1_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)
        self.ground2_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.pipes.clear()
        self.bird.rect.y = self.height // 2  # Reset bird position
        self.is_enter_pressed = False

game = Game()