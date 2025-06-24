import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.25
FLAP_STRENGTH = -7
DRONE_SPEED = 3
DRONE_FREQUENCY = 1500  # milliseconds
BULLET_SPEED = 10
FIRE_COOLDOWN = 300  # milliseconds

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flying Jatt: Aerial Battle")
clock = pygame.time.Clock()

# Load fonts
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)

class FlyingJatt:
    def __init__(self):
        self.width = 50
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.color = GOLD
        self.last_shot = 0
        self.health = 100
        self.max_health = 100
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > FIRE_COOLDOWN:
            self.last_shot = now
            return Bullet(self.x + self.width, self.y + self.height//2)
        return None
        
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Keep the jatt on screen
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity = 0
            
    def draw(self):
        # Draw body
        pygame.draw.ellipse(screen, self.color, (self.x, self.y + 10, self.width, self.height - 20))
        # Draw turban
        pygame.draw.rect(screen, RED, (self.x + 5, self.y, self.width - 10, 15))
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, self.width * (self.health/self.max_health), 5))
            
    def get_mask(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class IronDrone:
    def __init__(self):
        self.width = 60
        self.height = 60
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.color = RED
        self.outline_color = GOLD
        self.health = 30
        self.speed = DRONE_SPEED + random.random() * 2
        self.value = 10
        
    def update(self):
        self.x -= self.speed
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), self.width//2)
        pygame.draw.circle(screen, self.outline_color, (self.x + self.width//2, self.y + self.height//2), self.width//2, 3)
        pygame.draw.arc(screen, self.outline_color, 
                       (self.x + 5, self.y + 5, self.width - 10, self.height - 10),
                       0, math.pi * 2, 3)
        
    def collide(self, obj):
        drone_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return drone_rect.colliderect(obj.get_mask())

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = YELLOW
        self.speed = BULLET_SPEED
        self.damage = 10
        
    def update(self):
        self.x += self.speed
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        
    def get_mask(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.color = ORANGE
        self.growing = True
        
    def update(self):
        if self.growing:
            self.radius += 2
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 2
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 2)
        
    def is_done(self):
        return not self.growing and self.radius <= 0

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def game_over_screen(score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    draw_text("GAME OVER", font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(f"Final Score: {score}", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text("Press SPACE to play again", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    jatt = FlyingJatt()
    drones = []
    bullets = []
    explosions = []
    score = 0
    last_drone = pygame.time.get_ticks()
    game_active = True
    
    # Background elements
    clouds = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT//2)) 
              for _ in range(5)]
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        jatt.flap()
                    else:
                        # Reset game
                        jatt = FlyingJatt()
                        drones = []
                        bullets = []
                        explosions = []
                        score = 0
                        last_drone = pygame.time.get_ticks()
                        game_active = True
                if event.key == pygame.K_f and game_active:  # Fire bullet
                    bullet = jatt.shoot()
                    if bullet:
                        bullets.append(bullet)
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Continuous fire when holding F
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and game_active:
            bullet = jatt.shoot()
            if bullet:
                bullets.append(bullet)
        
        # Game logic
        if game_active:
            # Update jatt
            jatt.update()
            
            # Generate drones
            time_now = pygame.time.get_ticks()
            if time_now - last_drone > DRONE_FREQUENCY:
                drones.append(IronDrone())
                last_drone = time_now
                
            # Update drones
            for drone in drones[:]:
                drone.update()
                
                # Check collision with jatt
                if drone.collide(jatt):
                    jatt.health -= 10
                    drones.remove(drone)
                    explosions.append(Explosion(drone.x + drone.width//2, drone.y + drone.height//2))
                    if jatt.health <= 0:
                        game_active = False
                
                # Check if drone passed left screen
                if drone.x < -drone.width:
                    drones.remove(drone)
            
            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                
                # Remove bullets off screen
                if bullet.x > SCREEN_WIDTH:
                    bullets.remove(bullet)
                    continue
                
                # Check bullet-drone collisions
                for drone in drones[:]:
                    if drone.collide(bullet):
                        drone.health -= bullet.damage
                        if drone.health <= 0:
                            score += drone.value
                            drones.remove(drone)
                            explosions.append(Explosion(drone.x + drone.width//2, drone.y + drone.height//2))
                        bullets.remove(bullet)
                        break
            
            # Update explosions
            for explosion in explosions[:]:
                explosion.update()
                if explosion.is_done():
                    explosions.remove(explosion)
        
        # Drawing
        screen.fill(SKY_BLUE)
        
        # Draw clouds
        for cloud in clouds:
            pygame.draw.circle(screen, WHITE, cloud, 30)
            pygame.draw.circle(screen, WHITE, (cloud[0] + 20, cloud[1] + 10), 25)
            pygame.draw.circle(screen, WHITE, (cloud[0] - 15, cloud[1] + 5), 20)
        
        if game_active:
            # Move clouds
            clouds = [(x - 0.5, y) for x, y in clouds]
            clouds = [(x, y) if x > -50 else (SCREEN_WIDTH + random.randint(0, 100), y) for x, y in clouds]
            
            # Draw drones
            for drone in drones:
                drone.draw()
            
            # Draw bullets
            for bullet in bullets:
                bullet.draw()
            
            # Draw explosions
            for explosion in explosions:
                explosion.draw()
            
            # Draw jatt
            jatt.draw()
            
            # Draw score
            draw_text(f"Score: {score}", small_font, WHITE, SCREEN_WIDTH // 2, 30)
            draw_text(f"Health: {jatt.health}", small_font, WHITE, SCREEN_WIDTH - 100, 30)
            draw_text("Press F to Fire", small_font, WHITE, 100, 30)
        else:
            game_over_screen(score)
        
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
