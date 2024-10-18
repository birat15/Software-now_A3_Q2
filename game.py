import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)

# Clock object to control frame rate
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
button_font = pygame.font.Font(None, 48)

# Global game settings
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = 15
PROJECTILE_SPEED = 10
ENEMY_SPEED = 3
LEVELS = 3

# Scoring per level
LEVEL_SCORES = {
    1: {'enemy_score': 10, 'collectible_score': 5},
    2: {'enemy_score': 20, 'collectible_score': 10},
    3: {'enemy_score': 30, 'collectible_score': 15},
}

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('person.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Resize to 50x50 pixels
        self.rect = self.image.get_rect()
        self.rect.x = 50  # Start position
        self.rect.y = SCREEN_HEIGHT - 100
        self.speed_x = 0
        self.speed_y = 0
        self.on_ground = False
        self.health = 100
        self.lives = 3
        self.score = 0

    def update(self):
        self.move()
        self.gravity()

    def move(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0
        if keys[pygame.K_LEFT]:
            self.speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.speed_x = PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.speed_y = -JUMP_STRENGTH

        self.rect.x += self.speed_x

    def gravity(self):
        if not self.on_ground:
            self.speed_y += GRAVITY
        self.rect.y += self.speed_y

        if self.rect.y >= SCREEN_HEIGHT - 100:  # Player on the ground
            self.rect.y = SCREEN_HEIGHT - 100
            self.on_ground = True
            self.speed_y = 0
        else:
            self.on_ground = False

    def shoot(self):
        projectile = Projectile(self.rect.right, self.rect.centery)
        all_sprites.add(projectile)
        projectiles.add(projectile)

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))  # Placeholder for projectile sprite
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = PROJECTILE_SPEED

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:  # Remove projectile when off-screen
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))  # Placeholder for enemy sprite
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = ENEMY_SPEED
        self.health = 50

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.kill()  # Remove enemy if off-screen

    def take_damage(self, damage, level):
        self.health -= damage
        if self.health <= 0:
            # Use level-specific scoring for defeating enemies
            player.score += LEVEL_SCORES[level]['enemy_score']
            self.kill()

# Collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))  # Placeholder for collectible sprite
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def apply(self, player, level):
        # Use level-specific scoring for collecting items
        player.health = min(player.health + 20, 100)
        player.score += LEVEL_SCORES[level]['collectible_score']
        self.kill()  # Remove collectible once collected

# Level Design
class Level:
    def __init__(self, enemy_count):
        self.enemies = [Enemy(random.randint(500, SCREEN_WIDTH), SCREEN_HEIGHT - 100) for _ in range(enemy_count)]
        self.collectibles = [Collectible(random.randint(300, SCREEN_WIDTH), SCREEN_HEIGHT - 100)]

    def load(self):
        for enemy in self.enemies:
            all_sprites.add(enemy)
            enemy_group.add(enemy)
        
        for collectible in self.collectibles:
            all_sprites.add(collectible)
            collectible_group.add(collectible)

# Camera
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, player):
        x = -player.rect.x + int(SCREEN_WIDTH / 2)
        y = -player.rect.y + int(SCREEN_HEIGHT / 2)

        # Keep camera within bounds
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = max(-(self.height - SCREEN_HEIGHT), y)

        self.camera = pygame.Rect(x, y, self.width, self.height)

# Sprite groups
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

projectiles = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
collectible_group = pygame.sprite.Group()

# Levels with increasing enemy count
levels = [
    Level(3),  # 3 enemies in level 1
    Level(6),  # 6 enemies in level 2
    Level(8)   # 8 enemies in level 3
]

camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

running = True
current_level = 0
levels[current_level].load()  # Load the first level
game_over = False

# Button class for restart and quit
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = button_font

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
            if pygame.mouse.get_pressed()[0]:  # Left mouse click
                if self.action:
                    self.action()
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw text on button
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# Functions for button actions
def restart_game():
    global current_level, game_over, all_sprites, player, projectiles, enemy_group, collectible_group
    current_level = 0
    all_sprites.empty()
    player = Player()
    all_sprites.add(player)
    projectiles.empty()
    enemy_group.empty()
    collectible_group.empty()
    levels[current_level].load()
    game_over = False

def quit_game():
    pygame.quit()
    sys.exit()

# Game loop
def draw_text(text, font, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, [x, y])

restart_button = Button("Restart", 325, 350, 150, 50, DARK_GRAY, BLUE, restart_game)
quit_button = Button("Quit", 325, 420, 150, 50, DARK_GRAY, BLUE, quit_game)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and not game_over:
                player.shoot()

    # Update
    if not game_over:
        all_sprites.update()

        # Check for collisions between projectiles and enemies
        for projectile in projectiles:
            hit_enemies = pygame.sprite.spritecollide(projectile, enemy_group, False)
            for enemy in hit_enemies:
                enemy.take_damage(25, current_level + 1)  # Pass current level for scoring
                projectile.kill()

        # Check for player and enemy collision (game over condition)
        if pygame.sprite.spritecollide(player, enemy_group, False):
            game_over = True

        # Check for player and collectible collision
        collected_items = pygame.sprite.spritecollide(player, collectible_group, False)
        for collectible in collected_items:
            collectible.apply(player, current_level + 1)  # Pass current level for scoring

        # Load next level if all enemies are defeated
        if len(enemy_group) == 0 and current_level < LEVELS - 1:
            current_level += 1
            levels[current_level].load()

        # Trigger game over if all levels are completed
        elif len(enemy_group) == 0 and current_level == LEVELS - 1:
            game_over = True

        # Camera follows player
        camera.update(player)

    # Draw
    screen.fill(WHITE)
    
    if game_over:
        # Game over screen
        if current_level == LEVELS - 1 and len(enemy_group) == 0:
            draw_text("Congrats!", game_over_font, BLACK, SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 100)
        else:
            draw_text("Game Over", game_over_font, BLACK, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100)
        restart_button.draw(screen)
        quit_button.draw(screen)
    else:
        # Draw all sprites
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        
        # Display player health, score, and current level
        draw_text(f"Health: {player.health}", font, BLACK, 10, 10)
        draw_text(f"Score: {player.score}", font, BLACK, 10, 50)
        draw_text(f"Level: {current_level + 1}", font, BLACK, 10, 90)
    
    pygame.display.flip()

    # Control frame rate
    clock.tick(60)

pygame.quit()
