from dataclasses import dataclass

import pygame

pygame.init()

screen = pygame.display.set_mode((1000, 500))
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
SCORE_POS = (10, 10)

GAME_OVER = "GAME OVER"
GAME_OVER_POS = (400, 200)
START_OVER = "Do you want to start over? Y/N"
START_OVER_POS = (250, 300)


@dataclass
class Sprite:
    position: tuple
    velocity: tuple = (0, 0)
    acceleration: tuple = (0, 0)


PLAYER_RADIUS = 25
PLAYER_COLOR = (255, 0, 0)
PLAYER_INITIAL_POS = (300, 475)
player = Sprite(PLAYER_INITIAL_POS)
PLAYER_JUMP_VELOCITY = (0, -300)
GRAVITY = (0, 9.81)

enemies = []
ENEMY_COLOR = (0, 0, 225)
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 80
ENEMY_INITIAL_POS = (900, 420)
ENEMY_INITIAL_VELOCITY = (-140, 0)
ENEMY_VELOCITY_INCREMENT = (-10, 0)

GENERATE_ENEMY, APPEAR_INTERVAL = pygame.USEREVENT + 1, 3 * 1000
pygame.time.set_timer(GENERATE_ENEMY, APPEAR_INTERVAL)

INCREASE_ENEMY_VELOCITY, INCREMENT_INTERVAL = pygame.USEREVENT + 2, 1 * 1000
pygame.time.set_timer(INCREASE_ENEMY_VELOCITY, INCREMENT_INTERVAL)


def add_tuple(a, b):
    x = a[0] + b[0]
    y = a[1] + b[1]
    return (x, y)


def subtract_tuple(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return (x, y)


def times_tuple_constant(t, c):
    x = t[0] * c
    y = t[1] * c
    return (x, y)


def update_player(t_elapse):
    # update position
    diff = times_tuple_constant(player.velocity, t_elapse)
    diff = add_tuple(diff, times_tuple_constant(player.acceleration, t_elapse ** 2 / 2))
    player.position = add_tuple(player.position, diff)

    # update velocity
    player.velocity = add_tuple(player.velocity, times_tuple_constant(player.acceleration, t_elapse))

    # update acceleration
    if player.position[1] < PLAYER_INITIAL_POS[1]:
        # if the player is jumping
        player.acceleration = add_tuple(player.acceleration, GRAVITY)
    if player.position[1] > PLAYER_INITIAL_POS[1]:
        # if the player is below ground
        player.position = PLAYER_INITIAL_POS
        player.acceleration = (0, 0)
        player.velocity = (0, 0)


def update_enemies(t_elapse):
    for enemy in enemies:
        enemy.position = add_tuple(enemy.position, times_tuple_constant(enemy.velocity, t_elapse))


def draw_player():
    pygame.draw.circle(screen, PLAYER_COLOR, player.position, PLAYER_RADIUS)


def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, enemy.position + (ENEMY_WIDTH, ENEMY_HEIGHT))


def is_collide(e, p):
    if player.position[1] + PLAYER_RADIUS > e.position[1]:
        if p.position[0] - PLAYER_RADIUS <= e.position[0] <= p.position[0] + PLAYER_RADIUS:
            return True
        if p.position[0] - PLAYER_RADIUS <= e.position[0] + ENEMY_WIDTH <= p.position[0] + PLAYER_RADIUS:
            return True
    return False


def check_enemies_player_collision():
    for enemy in enemies:
        if is_collide(enemy, player):
            return True
    return False


def is_player_in_air():
    return player.position[1] < PLAYER_INITIAL_POS[1]


def remove_jumped_over_enemies():
    global score_value
    for enemy in enemies:
        if player.position[0] - PLAYER_RADIUS > enemy.position[0] + ENEMY_WIDTH and not is_player_in_air():
            enemies.remove(enemy)
            score_value += 1


def show_score():
    global score_value
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, SCORE_POS)


def wait_in_ms(time):
    t_cur = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t_cur < time:
        continue


def should_continue_game():
    game_over = font.render(GAME_OVER, True, (255, 255, 255))
    screen.blit(game_over, GAME_OVER_POS)
    start_over = font.render(START_OVER, True, (255, 255, 255))
    screen.blit(start_over, START_OVER_POS)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP and event.key == pygame.K_y:
                return True
            elif event.type == pygame.KEYUP and event.key == pygame.K_n:
                return False
        wait_in_ms(500)


running = True
t_pre = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if not is_player_in_air():
                player.velocity = add_tuple(player.velocity, PLAYER_JUMP_VELOCITY)
        if event.type == GENERATE_ENEMY:
            enemies.append(Sprite(ENEMY_INITIAL_POS, ENEMY_INITIAL_VELOCITY))
        if event.type == INCREASE_ENEMY_VELOCITY:
            ENEMY_INITIAL_VELOCITY = add_tuple(ENEMY_INITIAL_VELOCITY, ENEMY_VELOCITY_INCREMENT)
            for enemy in enemies:
                enemy.velocity = add_tuple(enemy.velocity, ENEMY_VELOCITY_INCREMENT)
            print(enemies)
    remove_jumped_over_enemies()

    screen.fill((0, 0, 0))
    t_cur = pygame.time.get_ticks()
    update_enemies((t_cur - t_pre) * 10 ** -3)
    update_player((t_cur - t_pre) * 10 ** -3)
    show_score()
    draw_player()
    draw_enemies()
    pygame.display.update()
    t_pre = t_cur
    if check_enemies_player_collision():
        if should_continue_game():
            enemies.clear()
            score_value = 0
            ENEMY_INITIAL_VELOCITY = (-140, 0)
        else:
            running = False
