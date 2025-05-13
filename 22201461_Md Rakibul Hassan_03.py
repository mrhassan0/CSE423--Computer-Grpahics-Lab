from OpenGL.GL import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Global variables
GRID_LENGTH = 600
player_pos = [0, 0, 0]
gun_angle = 0
bullets = []
enemies = []
camera_mode = 0  # 0: third-person, 1: first-person
camera_angle = 0
camera_height = 500
camera_distance = 500
cheat_mode = False
cheat_movement_mode = 0  # 0: no auto movement, 1: forward, 2: backward
automatic_gun_following = False
life = 5  # Adjusted initial life to match restart value
missed_bullets = 0
# life = math.inf 
# missed_bullets = -math.inf
score = 0
game_over = False
time = 0
last_shot_time = 0
fovY = 120
# Constants
PLAYER_SPEED = 5
CHEAT_MOVEMENT_SPEED = 2
ROTATION_SPEED = 5
BULLET_SPEED = 10
BULLET_COOLDOWN = 0.5
ENEMY_SPEED = 0.2
ENEMY_BASE_SIZE = 20
ENEMY_AMPLITUDE = 5
EYE_HEIGHT = 100
WALL_HEIGHT = 100
PLAYER_HALF_WIDTH_X = 20  # Half of player's width in x (40/2)
PLAYER_HALF_WIDTH_Y = 10  # Half of player's width in y (20/2)

def init_enemies():
    global enemies
    enemies = []
    for _ in range(5):
        while True:
            ex = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            ey = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            if math.hypot(ex, ey) > 100:
                break
        phase = random.uniform(0, 2 * math.pi)
        enemies.append([ex, ey, 0, phase])

init_enemies()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1), scale=1.0):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)
    glRasterPos2f(0, 0)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid():
    glBegin(GL_QUADS)
    for i in range(-10, 10):
        for j in range(-10, 10):
            if (i + j) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.8, 0.6, 0.8)
            glVertex3f(i * 60, j * 60, 0)
            glVertex3f((i + 1) * 60, j * 60, 0)
            glVertex3f((i + 1) * 60, (j + 1) * 60, 0)
            glVertex3f(i * 60, (j + 1) * 60, 0)
    glEnd()

def draw_walls():
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.3, 0.5)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glEnd()

    glColor3f(0.2, 0.4, 0.8)
    glPushMatrix()
    glPushMatrix()
    glTranslatef(-GRID_LENGTH, 0, WALL_HEIGHT + 5)
    glScalef(10, 2 * GRID_LENGTH, 10)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(GRID_LENGTH, 0, WALL_HEIGHT + 5)
    glScalef(10, 2 * GRID_LENGTH, 10)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, WALL_HEIGHT + 5)
    glScalef(2 * GRID_LENGTH, 10, 10)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, WALL_HEIGHT + 5)
    glScalef(2 * GRID_LENGTH, 10, 10)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    glColor3f(0.5, 0.3, 0.5)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH + 100, GRID_LENGTH, WALL_HEIGHT + 15)
    glScalef(50, 50, 20)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(GRID_LENGTH - 100, GRID_LENGTH, WALL_HEIGHT + 15)
    glScalef(50, 50, 20)
    glutSolidCube(1)
    glPopMatrix()

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    if game_over:
        glRotatef(90, 1, 0, 0)
    glRotatef(gun_angle, 0, 0, 1)

    if camera_mode == 0:
          # Body (cuboid)
     glColor3f(0.5, 0.5, 1)
     glPushMatrix()
     glTranslatef(0, 0, 40)  # Center of body at z=40 (height 80)
     glScalef(40, 20, 80)  # Width 40, Depth 20, Height 80
     glutSolidCube(1)
     glPopMatrix()

    # Head (sphere)
     glColor3f(1, 0.8, 0.6)
     glPushMatrix()
     glTranslatef(0, 0, 100)  # At top of body (40 + 80/2 + 20 = 100)
     gluSphere(gluNewQuadric(), 20, 10, 10)
     glPopMatrix()

    # Right Arm (cuboid)
     glColor3f(0.5, 0.5, 1)
     glPushMatrix()
     glTranslatef(25, 0, 70)  # Shoulder position (right edge of body, z=70)
     glRotatef(-30, 0, 1, 0)  # Angle slightly downward
     glScalef(10, 10, 30)  # Thin and long arm
     glutSolidCube(1)
     glPopMatrix()

    # Left Arm (cuboid)
     glPushMatrix()
     glTranslatef(-25, 0, 70)  # Shoulder position (left edge of body, z=70)
     glScalef(10, 10, 30)  # Same size as right arm, vertical
     glutSolidCube(1)
     glPopMatrix()

    # Gun (cylinder)
     glColor3f(0.2, 0.2, 0.2)
     glPushMatrix()
     glTranslatef(25, 0, 55)  # End of right arm (z=70 - 30/2 = 55)
     glRotatef(90, 0, 1, 0)  # Align along x-axis
     gluCylinder(gluNewQuadric(), 5, 5, 60, 10, 10)
     glPopMatrix()

    # Right Leg (cuboid)
     glColor3f(0.5, 0.5, 1)
     glPushMatrix()
     glTranslatef(15, 0, 20)  # Bottom of body, shifted right
     glRotatef(-15, 0, 1, 0)  # Angle outward
     glScalef(10, 10, 40)  # Thin and long leg
     glutSolidCube(1)
     glPopMatrix()

    # Left Leg (cuboid)
     glPushMatrix()
     glTranslatef(-15, 0, 20)  # Bottom of body, shifted left
     glRotatef(15, 0, 1, 0)  # Angle outward
     glScalef(10, 10, 40)  # Same size as right leg
     glutSolidCube(1)
     glPopMatrix()


    # First-person guns (unchanged)
    if camera_mode == 1:
        # Central gun
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(25, 0, 55)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 60, 10, 10)
        glPopMatrix()

        # Left additional gun
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(35, 0, 55)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 60, 10, 10)
        glPopMatrix()

        # Right additional gun
        glPushMatrix()
        glTranslatef(15, 0, 55)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 60, 10, 10)
        glPopMatrix()

    glPopMatrix()


def draw_enemy(ex, ey, ez, phase):
    bottom_radius = ENEMY_BASE_SIZE + ENEMY_AMPLITUDE * math.sin(time + phase)
    top_radius = 10

    glPushMatrix()
    glTranslatef(ex, ey, ez)

    glColor3f(1, 0, 0)
    gluSphere(gluNewQuadric(), bottom_radius, 10, 10)

    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, bottom_radius + top_radius)
    gluSphere(gluNewQuadric(), top_radius, 10, 10)
    glPopMatrix()

    glPopMatrix()
    return bottom_radius  # Return the current radius for collision detection

def draw_bullet(bx, by, bz):
    glPushMatrix()
    glTranslatef(bx, by, bz)
    glColor3f(0, 0, 0)
    glutSolidCube(10)
    glPopMatrix()

def keyboardListener(key, x, y):
    global player_pos, gun_angle, cheat_mode, cheat_movement_mode, automatic_gun_following, game_over, life, score, missed_bullets, last_shot_time
    if game_over and key == b'r':
        player_pos = [0, 0, 0]
        gun_angle = 0
        bullets.clear()
        init_enemies()
        life = 5
        score = 0
        missed_bullets = 0
        game_over = False
        cheat_mode = False
        cheat_movement_mode = 0
        last_shot_time = 0
        print(f"Game Restarted: Life = {life}, Score = {score}, Bullets Missed = {missed_bullets}")
    elif not game_over:
        if cheat_mode:
            if key == b'w':
                cheat_movement_mode = 1
            elif key == b's':
                cheat_movement_mode = 2
            elif key == b'a':
                gun_angle += ROTATION_SPEED
            elif key == b'd':
                gun_angle -= ROTATION_SPEED
            elif key == b'c':
                cheat_mode = not cheat_mode
                cheat_movement_mode = 0
            elif key == b'v':
                automatic_gun_following = not automatic_gun_following
            elif key == b'w' or key == b's':
                # Update player position in cheat mode
                new_x = player_pos[0]
                new_y = player_pos[1]
                if cheat_movement_mode == 1:
                    new_x += CHEAT_MOVEMENT_SPEED * math.cos(math.radians(gun_angle))
                    new_y += CHEAT_MOVEMENT_SPEED * math.sin(math.radians(gun_angle))
                elif cheat_movement_mode == 2:
                    new_x -= CHEAT_MOVEMENT_SPEED * math.cos(math.radians(gun_angle))
                    new_y -= CHEAT_MOVEMENT_SPEED * math.sin(math.radians(gun_angle))
                # Clamp position to keep player fully within boundaries
                player_pos[0] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_X, min(GRID_LENGTH - PLAYER_HALF_WIDTH_X, new_x))
                player_pos[1] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_Y, min(GRID_LENGTH - PLAYER_HALF_WIDTH_Y, new_y))
                player_pos[2] = 0
        else:
            if key == b'w':
                player_pos[0] += PLAYER_SPEED * math.cos(math.radians(gun_angle))
                player_pos[1] += PLAYER_SPEED * math.sin(math.radians(gun_angle))
                player_pos[0] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_X, min(GRID_LENGTH - PLAYER_HALF_WIDTH_X, player_pos[0]))
                player_pos[1] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_Y, min(GRID_LENGTH - PLAYER_HALF_WIDTH_Y, player_pos[1]))
                player_pos[2] = 0
            elif key == b's':
                player_pos[0] -= PLAYER_SPEED * math.cos(math.radians(gun_angle))
                player_pos[1] -= PLAYER_SPEED * math.sin(math.radians(gun_angle))
                player_pos[0] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_X, min(GRID_LENGTH - PLAYER_HALF_WIDTH_X, player_pos[0]))
                player_pos[1] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_Y, min(GRID_LENGTH - PLAYER_HALF_WIDTH_Y, player_pos[1]))
                player_pos[2] = 0
            elif key == b'a':
                gun_angle += ROTATION_SPEED
            elif key == b'd':
                gun_angle -= ROTATION_SPEED
            elif key == b'c':
                cheat_mode = not cheat_mode
                cheat_movement_mode = 0
            elif key == b'v':
                automatic_gun_following = not automatic_gun_following

def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    if key == GLUT_KEY_UP:
        camera_height += 10
    elif key == GLUT_KEY_DOWN:
        camera_height = max(10, camera_height - 10)
    elif key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5

def mouseListener(button, state, x, y):
    global camera_mode
    if not game_over and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        direction = [math.cos(math.radians(gun_angle)), math.sin(math.radians(gun_angle)), 0]
        bullets.append([player_pos[0], player_pos[1], player_pos[2], direction[0], direction[1], direction[2]])
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode == 0:
        cx = camera_distance * math.cos(math.radians(camera_angle))
        cy = camera_distance * math.sin(math.radians(camera_angle))
        cz = camera_height
        gluLookAt(cx, cy, cz, player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)
    else:
        cx = player_pos[0]
        cy = player_pos[1]
        cz = player_pos[2] + EYE_HEIGHT
        if cheat_mode and automatic_gun_following:
            # In cheat mode with automatic gun following, align camera with gun_angle
            lx = cx + math.cos(math.radians(gun_angle))
            ly = cy + math.sin(math.radians(gun_angle))
            lz = cz
        else:
            # Normal first-person view, use gun_angle as before
            lx = cx + math.cos(math.radians(gun_angle))
            ly = cy + math.sin(math.radians(gun_angle))
            lz = cz
        gluLookAt(cx, cy, cz, lx, ly, lz, 0, 0, 1)

def idle():
    global time, bullets, enemies, life, score, missed_bullets, game_over, gun_angle, player_pos, last_shot_time
    if not game_over:
        time += 0.01
        # Update bullets
        i = 0
        while i < len(bullets):
            b = bullets[i]
            b[0] += BULLET_SPEED * b[3]
            b[1] += BULLET_SPEED * b[4]
            b[2] += BULLET_SPEED * b[5]
            if abs(b[0]) > GRID_LENGTH or abs(b[1]) > GRID_LENGTH:
                bullets.pop(i)
                missed_bullets += 1
                print(f"Bullet Missed! Total Missed: {missed_bullets}")
                if missed_bullets >= 10:
                    game_over = True
                    print("Game Over: Missed 10 bullets!")
            else:
                i += 1
        # Update enemies and collisions
        for e in enemies[:]:
            dx = player_pos[0] - e[0]
            dy = player_pos[1] - e[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                e[0] += ENEMY_SPEED * dx / dist
                e[1] += ENEMY_SPEED * dy / dist
                e[0] = max(-GRID_LENGTH, min(GRID_LENGTH, e[0]))
                e[1] = max(-GRID_LENGTH, min(GRID_LENGTH, e[1]))
                e[2] = 0
            # Calculate the current enemy radius for collision detection
            current_radius = ENEMY_BASE_SIZE + ENEMY_AMPLITUDE * math.sin(time + e[3])
            if dist < 30:
                life -= 1
                print(f"Enemy Touched Player! Life Remaining: {life}")
                if life <= 0:
                    game_over = True
                    print("Game Over: Life reached zero!")
                enemies.remove(e)
                while True:
                    ex = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                    ey = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                    if math.hypot(ex - player_pos[0], ey - player_pos[1]) > 100:
                        break
                enemies.append([ex, ey, 0, random.uniform(0, 2 * math.pi)])
            for b in bullets[:]:
                if math.hypot(b[0] - e[0], b[1] - e[1]) < current_radius + 5:
                    bullets.remove(b)
                    enemies.remove(e)
                    score += 1
                    print(f"Enemy Hit! Score: {score}")
                    while True:
                        ex = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                        ey = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                        if math.hypot(ex - player_pos[0], ey - player_pos[1]) > 100:
                            break
                    enemies.append([ex, ey, 0, random.uniform(0, 2 * math.pi)])
                    break
        # Cheat mode
        if cheat_mode:
            gun_angle += 0.5
            gun_dir = [math.cos(math.radians(gun_angle)), math.sin(math.radians(gun_angle))]
            for e in enemies:
                dx = e[0] - player_pos[0]
                dy = e[1] - player_pos[1]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    enemy_dir = [dx / dist, dy / dist]
                    dot = gun_dir[0] * enemy_dir[0] + gun_dir[1] * enemy_dir[1]
                    if dot > 0.996 and (time - last_shot_time) >= BULLET_COOLDOWN:
                        bullets.append([player_pos[0], player_pos[1], player_pos[2], gun_dir[0], gun_dir[1], 0])
                        last_shot_time = time
                        break
            if cheat_movement_mode == 1:
                player_pos[0] += CHEAT_MOVEMENT_SPEED * math.cos(math.radians(gun_angle))
                player_pos[1] += CHEAT_MOVEMENT_SPEED * math.sin(math.radians(gun_angle))
                player_pos[0] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_X, min(GRID_LENGTH - PLAYER_HALF_WIDTH_X, player_pos[0]))
                player_pos[1] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_Y, min(GRID_LENGTH - PLAYER_HALF_WIDTH_Y, player_pos[1]))
                player_pos[2] = 0
            elif cheat_movement_mode == 2:
                player_pos[0] -= CHEAT_MOVEMENT_SPEED * math.cos(math.radians(gun_angle))
                player_pos[1] -= CHEAT_MOVEMENT_SPEED * math.sin(math.radians(gun_angle))
                player_pos[0] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_X, min(GRID_LENGTH - PLAYER_HALF_WIDTH_X, player_pos[0]))
                player_pos[1] = max(-GRID_LENGTH + PLAYER_HALF_WIDTH_Y, min(GRID_LENGTH - PLAYER_HALF_WIDTH_Y, player_pos[1]))
                player_pos[2] = 0
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_grid()
    draw_walls()
    draw_player()
    for e in enemies:
        draw_enemy(e[0], e[1], e[2], e[3])
    for b in bullets:
        draw_bullet(b[0], b[1], b[2])
    draw_text(10, 770, f"Player Life Remaining: {life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {missed_bullets}")
    if game_over:
        draw_text(400, 400, "Game Over", GLUT_BITMAP_HELVETICA_18, color=(0, 0, 0), scale=3.0)
        draw_text(350, 360, "To Press R We Can Restart the Game", GLUT_BITMAP_HELVETICA_18, color=(0, 0, 0), scale=3.0)
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for correct rendering
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()