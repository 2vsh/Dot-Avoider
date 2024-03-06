import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dot Avoider")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
BACKGROUND_COLOR = (200, 200, 200)  # Light gray background color

# Set up the player
player_size = 10
player_pos = [width // 2, height // 2]
player_speed = 5

# Set up the enemy dots
enemy_size = 10
enemy_pos = []
enemy_vel = []
num_enemies = 5  # Start with 5 enemy dots

# Set the minimum distance between the player and spawned dots
min_spawn_distance = 100

# Set up the font for displaying points, level, and countdown
font = pygame.font.Font(None, 36)

# Game loop
running = True
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
points = 0
last_point_time = start_time
level = 1
last_level_time = start_time
enemy_speed_factor = 1.0
countdown_duration = 5  # Countdown duration in seconds
countdown_start_time = start_time

# Spawn initial enemy dots
for _ in range(num_enemies):
    while True:
        x = random.randint(0, width - enemy_size)
        y = random.randint(0, height - enemy_size)
        if (
            abs(x - player_pos[0]) >= min_spawn_distance
            and abs(y - player_pos[1]) >= min_spawn_distance
        ):
            enemy_pos.append([x, y])
            enemy_vel.append([random.randint(1, 3), random.randint(1, 3)])  # Reduced enemy speed
            break

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_pos[1] > 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_s] and player_pos[1] < height - player_size:
        player_pos[1] += player_speed
    if keys[pygame.K_a] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] and player_pos[0] < width - player_size:
        player_pos[0] += player_speed

    screen.fill(BACKGROUND_COLOR)

    pygame.draw.rect(screen, WHITE, (player_pos[0], player_pos[1], player_size, player_size))

    current_time = pygame.time.get_ticks()
    countdown_time = countdown_duration - (current_time - countdown_start_time) // 1000

    if countdown_time > 0:
        # Display countdown timer
        countdown_text = font.render(f"Countdown: {countdown_time}", True, BLACK)
        screen.blit(countdown_text, (width // 2 - countdown_text.get_width() // 2, height // 2 - countdown_text.get_height() // 2))

        # Display enemy dots in light blue color during countdown
        for i in range(len(enemy_pos)):
            pygame.draw.rect(screen, LIGHT_BLUE, (enemy_pos[i][0], enemy_pos[i][1], enemy_size, enemy_size))
    else:
        for i in range(len(enemy_pos)):
            pygame.draw.rect(screen, RED, (enemy_pos[i][0], enemy_pos[i][1], enemy_size, enemy_size))

            enemy_pos[i][0] += enemy_vel[i][0] * enemy_speed_factor
            enemy_pos[i][1] += enemy_vel[i][1] * enemy_speed_factor

            if enemy_pos[i][0] <= 0 or enemy_pos[i][0] >= width - enemy_size:
                enemy_vel[i][0] = -enemy_vel[i][0]
            if enemy_pos[i][1] <= 0 or enemy_pos[i][1] >= height - enemy_size:
                enemy_vel[i][1] = -enemy_vel[i][1]

            if (
                player_pos[0] < enemy_pos[i][0] + enemy_size
                and player_pos[0] + player_size > enemy_pos[i][0]
                and player_pos[1] < enemy_pos[i][1] + enemy_size
                and player_pos[1] + player_size > enemy_pos[i][1]
            ):
                running = False

        # Calculate points based on real-life seconds
        elapsed_time = (current_time - last_point_time) // 1000  # Convert milliseconds to seconds

        if elapsed_time >= 1:
            points += elapsed_time
            last_point_time = current_time

            for enemy in enemy_pos:
                if (
                    abs(player_pos[0] - enemy[0]) < 50
                    and abs(player_pos[1] - enemy[1]) < 50
                ):
                    points += elapsed_time  # Bonus points for being very close to a red dot

        # Update level every 20 seconds
        if current_time - last_level_time >= 20000:  # 20 seconds
            level += 1
            last_level_time = current_time

            # Add a new enemy dot every level
            while True:
                x = random.randint(0, width - enemy_size)
                y = random.randint(0, height - enemy_size)
                if (
                    abs(x - player_pos[0]) >= min_spawn_distance
                    and abs(y - player_pos[1]) >= min_spawn_distance
                ):
                    enemy_pos.append([x, y])
                    enemy_vel.append([random.randint(1, 3), random.randint(1, 3)])  # Reduced enemy speed
                    break

            # Increase enemy speed every 15 levels
            if level % 15 == 0:
                enemy_speed_factor += 0.05  # Reduced speed increase rate

    # Display points and level on the top left of the screen
    points_text = font.render(f"Points: {points}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(points_text, (10, 10))
    screen.blit(level_text, (10, 40))

    pygame.display.flip()
    clock.tick(60)

# Wait for a moment before closing the window
pygame.time.delay(1000)  # Delay for 1 second (1000 milliseconds)

pygame.quit()
