import pygame
import random

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Bird:
    def __init__(self):
        self.width = 40
        self.height = 30
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.3
        self.lift = -8

        # Load bird images for up and down
        self.image_up = pygame.image.load("assets/birdup.png")
        self.image_down = pygame.image.load("assets/birddown.png")

        # Scale the images to match bird size
        self.image_up = pygame.transform.scale(self.image_up, (self.width, self.height))
        self.image_down = pygame.transform.scale(self.image_down, (self.width, self.height))

        # Default to the up image (flap)
        self.image = self.image_up

    def update(self):
        self.velocity += self.gravity  # Apply gravity
        self.y += self.velocity  # Update position based on velocity

        # Determine which image to use based on velocity (flap or fall)
        if self.velocity < 0:  # Bird is going up (flapping)
            self.image = self.image_up
        else:  # Bird is going down (falling)
            self.image = self.image_down

        # Prevent the bird from moving out of the screen vertically
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity = 0  # Stop the downward movement when hitting the ground
        elif self.y < 0:
            self.y = 0
            self.velocity = 0  # Stop the upward movement when hitting the top of the screen

    def jump(self):
        if self.y > 0:
            self.velocity = self.lift  # Apply upward force when jumping (flap)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))  # Draw the current image of the bird

class ObstaclePair:
    OBSTACLE_TYPES = ["PIPE", "ROCK", "SPIKE"]

    def __init__(self):
        self.type = random.choice(self.OBSTACLE_TYPES)  # Random obstacle type
        self.width = 60
        self.gap_size = 150  # Jarak antara rintangan atas dan bawah
        self.x = SCREEN_WIDTH
        self.speed = 5
        self.has_scored = False  # Track if score has been added

        # Randomize obstacle heights
        self.top_height = random.randint(100, SCREEN_HEIGHT // 2)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - self.gap_size

        # Load and scale images based on obstacle type
        if self.type == "PIPE":
            image = pygame.image.load("assets/pipe.png")
        elif self.type == "ROCK":
            image = pygame.image.load("assets/rock.png")
        elif self.type == "SPIKE":
            image = pygame.image.load("assets/spike.png")

        # Rintangan atas
        self.top_image = pygame.transform.flip(
            pygame.transform.scale(image, (self.width, self.top_height)), False, True
        )
        # Rintangan bawah
        self.bottom_image = pygame.transform.scale(
            image, (self.width, self.bottom_height)
        )

        # Tentukan posisi Y untuk rintangan
        self.top_y = 0  # Selalu mulai dari atas
        self.bottom_y = SCREEN_HEIGHT - self.bottom_height  # Selalu menempel di bawah

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        # Gambar rintangan atas dan bawah
        screen.blit(self.top_image, (self.x, self.top_y))
        screen.blit(self.bottom_image, (self.x, self.bottom_y))

    def get_top_rect(self):
        return pygame.Rect(self.x, self.top_y, self.width, self.top_height)

    def get_bottom_rect(self):
        return pygame.Rect(self.x, self.bottom_y, self.width, self.bottom_height)

    def check_score(self, bird):
        """Cek apakah rintangan melewati burung dan tambahkan skor"""
        # Menambahkan skor jika rintangan sudah melewati burung dan belum dihitung
        if not self.has_scored and self.x + self.width < bird.x:
            self.has_scored = True
            return True
        return False

class FlyingBirdGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Inisialisasi pygame mixer untuk suara
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Birdly")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.bird = Bird()
        self.obstacles = []
        self.score = 0

        self.background = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load sounds
        self.flap_sound = pygame.mixer.Sound("assets/assets_sfx_flap.wav")  # Suara flap
        self.dead_sound = pygame.mixer.Sound("assets/assets_sfx_dead.wav")  # Suara ketika burung mati
        self.score_sound = pygame.mixer.Sound("assets/assets_sfx_score.wav")  # Suara ketika mendapatkan skor

    def spawn_obstacles(self):
        # Spawn a new obstacle pair if needed
        if not self.obstacles or self.obstacles[-1].x < SCREEN_WIDTH - 300:
            self.obstacles.append(ObstaclePair())

    def check_collision(self):
        bird_rect = pygame.Rect(self.bird.x, self.bird.y, self.bird.width, self.bird.height)
        for obstacle in self.obstacles:
            if bird_rect.colliderect(obstacle.get_top_rect()) or bird_rect.colliderect(obstacle.get_bottom_rect()):
                return True
        return False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.bird.jump()
                        self.flap_sound.play()  # Mainkan suara flap saat burung melompat

            self.bird.update()
            self.spawn_obstacles()

            for obstacle in self.obstacles[:]:
                obstacle.update()

                # Cek jika rintangan sudah melewati burung dan tambahkan skor
                if obstacle.check_score(self.bird):
                    self.score += 1
                    self.score_sound.play()

                # Jika rintangan sudah keluar layar, hapus
                if obstacle.x < -obstacle.width:
                    self.obstacles.remove(obstacle)

            if self.check_collision():
                self.dead_sound.play()
                if self.game_over():
                    self.__init__()
                else:
                    running = False

            self.screen.blit(self.background, (0, 0))
            self.bird.draw(self.screen)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)

            # Tampilkan skor
            score_text = self.font.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def game_over(self):
        # Tampilkan layar putih terlebih dahulu
        self.screen.fill(WHITE)

        # Tampilkan pesan Game Over dengan font yang lebih besar
        game_over_font = pygame.font.Font(None, 72)  # Gunakan ukuran font yang lebih besar
        game_over_text = game_over_font.render("Game Over", True, RED)
        
        # Tampilkan teks "Press ENTER to Restart or ESC to Quit"
        restart_text = self.font.render("Press ENTER to Restart or ESC to Quit", True, BLACK)

        # Hitung posisi teks agar berada di tengah layar
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        # Update layar agar perubahan terlihat
        pygame.display.flip()

        # Tunggu input pemain untuk restart atau keluar
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Jika pemain menutup jendela
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Restart game
                        return True
                    if event.key == pygame.K_ESCAPE:  # Keluar dari game
                        return False

def main():
    game = FlyingBirdGame()
    game.run()

if __name__ == "__main__":
    main()