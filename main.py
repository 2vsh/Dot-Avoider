import pygame
import random
import requests

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
FADED_BACKGROUND_COLOR = (128, 128, 128)  # Faded background color for start screen
INPUT_BOX_COLOR = (255, 255, 255)  # Color of the input box

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

# Set up the Discord webhook URL
webhook_url = "[Hook Here]"

def spawn_initial_enemies():
    enemy_pos.clear()
    enemy_vel.clear()
    for _ in range(num_enemies):
        while True:
            x = random.randint(0, width - enemy_size)
            y = random.randint(0, height - enemy_size)
            if (
                abs(x - player_pos[0]) >= min_spawn_distance
                and abs(y - player_pos[1]) >= min_spawn_distance
            ):
                enemy_pos.append([x, y])
                enemy_vel.append([random.randint(1, 3), random.randint(1, 3)])
                break

# Game loop
running = True
clock = pygame.time.Clock()
points = 0
level = 1
enemy_speed_factor = 1.0
countdown_duration = 5  # Countdown duration in seconds
best_score = 0  # Track the best score in the current session

# Start screen loop
start_screen = True
while start_screen:
    screen.fill(FADED_BACKGROUND_COLOR)

    # Display game title
    title_text = font.render("Dot Avoider", True, WHITE)
    title_pos = (width // 2 - title_text.get_width() // 2, 100)
    screen.blit(title_text, title_pos)

    # Display game description
    description_lines = [
        "Avoid the red dots and survive as long as possible!",
        "Use WASD keys to move your player.",
        "Gain 1 point for every second you stay alive.",
        "Gain bonus points for being close to red dots.",
        "Level increases every 20 seconds, adding new dots.",
        "Enemy speed increases every 15 levels.",
        "Press any key to start the game."
    ]
    for i, line in enumerate(description_lines):
        line_text = font.render(line, True, WHITE)
        line_pos = (width // 2 - line_text.get_width() // 2, 200 + i * 40)
        screen.blit(line_text, line_pos)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_screen = False
            running = False
        if event.type == pygame.KEYDOWN:
            start_screen = False

while running:
    # Set the start time and last point time after the start screen
    start_time = pygame.time.get_ticks()
    last_point_time = start_time
    last_level_time = start_time
    countdown_start_time = start_time

    game_over = False

    # Spawn initial enemy dots
    spawn_initial_enemies()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
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
            # Display countdown timer above the player's starting location
            countdown_text = font.render(f"Countdown: {countdown_time}", True, BLACK)
            countdown_pos = (width // 2 - countdown_text.get_width() // 2, 50)  # Adjust the vertical position as needed
            screen.blit(countdown_text, countdown_pos)

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
                    game_over = True

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

    # Game over screen
    player_name = ""
    selected_option = 0

    while game_over:
        screen.fill(FADED_BACKGROUND_COLOR)

        # Display game over text
        game_over_text = font.render("Game Over", True, WHITE)
        game_over_pos = (width // 2 - game_over_text.get_width() // 2, 100)
        screen.blit(game_over_text, game_over_pos)

        # Display score and level
        score_text = font.render(f"Score: {points}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        score_pos = (width // 2 - score_text.get_width() // 2, 200)
        level_pos = (width // 2 - level_text.get_width() // 2, 240)
        screen.blit(score_text, score_pos)
        screen.blit(level_text, level_pos)

        # Check if the player beat their previous score
        if points > best_score:
            best_score = points
            new_best_text = font.render("New Best!", True, WHITE)
            new_best_pos = (width // 2 - new_best_text.get_width() // 2, 280)
            screen.blit(new_best_text, new_best_pos)

        # Display name input prompt
        name_prompt = font.render("Enter your name (max 20 characters):", True, WHITE)
        name_prompt_pos = (width // 2 - name_prompt.get_width() // 2, 320)
        screen.blit(name_prompt, name_prompt_pos)

        # Display input box
        input_box_width = 400
        input_box_height = 40
        input_box_pos = (width // 2 - input_box_width // 2, 360)
        pygame.draw.rect(screen, INPUT_BOX_COLOR, (input_box_pos[0], input_box_pos[1], input_box_width, input_box_height), 2)

        # Display player name
        name_text = font.render(player_name, True, WHITE)
        name_text_pos = (input_box_pos[0] + 10, input_box_pos[1] + 5)
        screen.blit(name_text, name_text_pos)

        # Display send score and cancel options
        send_text = font.render("Send Score", True, WHITE)
        cancel_text = font.render("Cancel", True, WHITE)
        send_pos = (width // 2 - send_text.get_width() // 2, 420)
        cancel_pos = (width // 2 - cancel_text.get_width() // 2, 460)

        if selected_option == 0:
            pygame.draw.rect(screen, WHITE, (send_pos[0] - 10, send_pos[1] - 5, send_text.get_width() + 20, send_text.get_height() + 10), 2)
        else:
            pygame.draw.rect(screen, WHITE, (cancel_pos[0] - 10, cancel_pos[1] - 5, cancel_text.get_width() + 20, cancel_text.get_height() + 10), 2)

        screen.blit(send_text, send_pos)
        screen.blit(cancel_text, cancel_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = False
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        # Send score to Discord webhook
                        payload = {
                            "content": f"New score submitted!\nName: {player_name}\nScore: {points}\nLevel: {level}"
                        }
                        requests.post(webhook_url, json=payload)
                    game_over = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % 2
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % 2
                else:
                    if len(player_name) < 20:
                        player_name += event.unicode

    # Try again or quit screen
    selected_option = 0
    while not game_over:
        screen.fill(FADED_BACKGROUND_COLOR)

        # Display options
        try_again_text = font.render("Try Again", True, WHITE)
        quit_text = font.render("Quit", True, WHITE)
        try_again_pos = (width // 2 - try_again_text.get_width() // 2, height // 2 - 50)
        quit_pos = (width // 2 - quit_text.get_width() // 2, height // 2 + 50)

        if selected_option == 0:
            pygame.draw.rect(screen, WHITE, (try_again_pos[0] - 10, try_again_pos[1] - 5, try_again_text.get_width() + 20, try_again_text.get_height() + 10), 2)
        else:
            pygame.draw.rect(screen, WHITE, (quit_pos[0] - 10, quit_pos[1] - 5, quit_text.get_width() + 20, quit_text.get_height() + 10), 2)

        screen.blit(try_again_text, try_again_pos)
        screen.blit(quit_text, quit_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        # Reset game variables
                        points = 0
                        level = 1
                        enemy_pos = []
                        enemy_vel = []
                        player_pos = [width // 2, height // 2]
                        enemy_speed_factor = 1.0  # Reset enemy speed factor

                        # Spawn initial enemy dots
                        spawn_initial_enemies()

                        game_over = True
                    else:
                        game_over = True
                        running = False
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % 2
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % 2

# Wait for a moment before closing the window
pygame.time.delay(1000)  # Delay for 1 second (1000 milliseconds)

pygame.quit()
