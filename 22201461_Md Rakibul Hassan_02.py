from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import sys, random, time

# Window dimensions
WIN_W, WIN_H = 800, 600

# Game object sizes
diamond_w, diamond_h = 20, 20
catcher_w, catcher_h = 80, 20

# Initial state and game variables position
catcher_x = WIN_W // 2
catcher_y = 50
catcher_color = (1.0, 1.0, 1.0)
diamond_x = random.randint(diamond_w // 2, WIN_W - diamond_w // 2) #diamond random position
diamond_y = float(WIN_H - diamond_h // 2)
diamond_color = (1.0, 0.0, 1.0)
score = 0
speed = 100.0         # pixels per second
acceleration = 10.0    # speed increase per second
state = 'playing'     # 'playing', 'paused', 'over'

# Delta time tracking
t_last = time.time()

# Button definitions: (center_x, center_y, half_width, half_height)
btn_size = 30
btn_left   = (60, WIN_H - 60, btn_size, btn_size)
btn_middle = (WIN_W // 2, WIN_H - 60, btn_size, btn_size)
btn_right  = (WIN_W - 60, WIN_H - 60, btn_size, btn_size)

# ---------------------------------------------------
# Midpoint line drawing helpers (8-zone algorithm)
def findZone(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    adx, ady = abs(dx), abs(dy)
    if adx >= ady:
        if dx >= 0 and dy >= 0: return 0
        if dx >= 0 and dy <  0: return 7
        if dx <  0 and dy >= 0: return 3
        return 4
    else:
        if dx >= 0 and dy >= 0: return 1
        if dx >= 0 and dy <  0: return 6
        if dx <  0 and dy >= 0: return 2
        return 5

def toZone0(x, y, zone):
    mapping = {
        0: ( x,  y),
        1: ( y,  x),
        2: ( y, -x),
        3: (-x,  y),
        4: (-x, -y),
        5: (-y, -x),
        6: (-y,  x),
        7: ( x, -y)
    }
    return mapping[zone]

def fromZone0(x, y, zone):
    inv = {
        0: ( x,  y),
        1: ( y,  x),
        2: (-y,  x),
        3: (-x,  y),
        4: (-x, -y),
        5: (-y, -x),
        6: ( y, -x),
        7: ( x, -y)
    }
    return inv[zone]

def drawLine(x1, y1, x2, y2): #USING DESCRIBED ALGORITHM
    zone = findZone(x1, y1, x2, y2)
    x1z, y1z = toZone0(x1, y1, zone)
    x2z, y2z = toZone0(x2, y2, zone)
    if x1z > x2z:
        x1z, x2z = x2z, x1z
        y1z, y2z = y2z, y1z
    dx, dy = x2z - x1z, y2z - y1z
    d = 2 * dy - dx
    incE  = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = x1z, y1z

    #drawing starts

    glBegin(GL_POINTS)
    while x <= x2z:
        xr, yr = fromZone0(x, y, zone)
        glVertex2i(int(xr), int(yr))
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        x += 1
    glEnd()
# ---------------------------------------------------

# Render bitmap text (score)
def drawText(x, y, text, color=(1.0,1.0,1.0)):
    glColor3f(*color)
    glRasterPos2i(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

# ---------------------------------------------------
# Draw diamond using four midpoint lines
def drawDiamond(x, y):
    cx, cy = int(round(x)), int(round(y))
    hw, hh = diamond_w // 2, diamond_h // 2
    # The 5 points define a closed diamond (last equals first)
    pts = [(cx, cy+hh), (cx+hw, cy), (cx, cy-hh), (cx-hw, cy), (cx, cy+hh)]
    for i in range(4):
        drawLine(*pts[i], *pts[i+1])

# Draw catcher using four midpoint lines (rectangular shape)
def drawCatcher():
    # full half‑width & half‑height of the *top* edge
    hw = catcher_w // 2
    hh = catcher_h // 2

    # make the *bottom* half‑width inset by the vertical drop (hh),
    # so the sides sit at a 45° angle
    bottom_hw = max(0, hw - hh)

    # build the trapezoid
    pts = [
        (catcher_x - hw,       catcher_y + hh),  # top‑left
        (catcher_x + hw,       catcher_y + hh),  # top‑right
        (catcher_x + bottom_hw, catcher_y - hh), # bottom‑right
        (catcher_x - bottom_hw, catcher_y - hh), # bottom‑left
        (catcher_x - hw,       catcher_y + hh)   # close the loop
    ]

    glColor3f(*catcher_color)
    for i in range(4):
        drawLine(*pts[i], *pts[i+1])

# ---------------------------------------------------
# Draw control buttons (all with midpoint lines)
def drawButtons():
    # Restart button: teal left arrow
    glColor3f(0.0, 0.8, 0.8)
    cx, cy, hw, hh = btn_left
    arrow = [(cx-hw, cy), (cx+hw, cy+hh), (cx+hw, cy-hh), (cx-hw, cy)]
    for i in range(3):
        drawLine(*arrow[i], *arrow[i+1])
    # Play/Pause button: amber icon
    glColor3f(1.0, 0.6, 0.0)
    cx, cy, hw, hh = btn_middle
    if state == 'playing':
        # Pause icon: two vertical bars
        gap = hw // 2
        for dx in (-gap, gap // 2):
            bar = [
                (cx+dx, cy-hh),
                (cx+dx, cy+hh),
                (cx+dx+gap//2, cy+hh),
                (cx+dx+gap//2, cy-hh),
                (cx+dx, cy-hh)
            ]
            for i in range(4):
                drawLine(*bar[i], *bar[i+1])
    else:
        # Play icon: triangle
        tri = [(cx-hw, cy-hh), (cx+hw, cy), (cx-hw, cy+hh), (cx-hw, cy-hh)]
        for i in range(3):
            drawLine(*tri[i], *tri[i+1])

    # Quit button: red cross
    glColor3f(0.8, 0.0, 0.0)
    cx, cy, hw, hh = btn_right
    drawLine(cx-hw, cy-hh, cx+hw, cy+hh)
    drawLine(cx-hw, cy+hh, cx+hw, cy-hh)
# ---------------------------------------------------

# Collision detection (AABB) # b1 = diamond
def hasCollided(b1, b2):
    return (b1['x'] < b2['x'] + b2['w'] and
            b1['x'] + b1['w'] > b2['x'] and
            b1['y'] < b2['y'] + b2['h'] and
            b1['y'] + b1['h'] > b2['y'])

# horizontal :
# b1.left < b2.right → b1['x'] < b2['x'] + b2['w']
# b1.right > b2.left → b1['x'] + b1['w'] > b2['x']

# vertical:
# b1.top < b2.bottom → b1['y'] < b2['y'] + b2['h']
# b1.bottom > b2.top → b1['y'] + b1['h'] > b2['y']

# ---------------------------------------------------
# Reset diamond: new random horizontal position and bright color
def resetDiamond():
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(diamond_w // 2, WIN_W - diamond_w // 2)
    diamond_y = float(WIN_H - diamond_h // 2)
    diamond_color = (random.uniform(0.5, 1.0),
                     random.uniform(0.5, 1.0),
                     random.uniform(0.5, 1.0))

# Restart game: reset score, speed, state, diamond, and catcher color.
def restartGame():
    global score, speed, state, catcher_color
    print("Starting Over")
    score = 0
    speed = 100.0
    state = 'playing'
    catcher_color = (1.0, 1.0, 1.0)
    resetDiamond()
    print("Score reset to 0.")

# ---------------------------------------------------
# Mouse click callback for buttons
def mouseClick(btn, st, x, y):
    global state
    if st != GLUT_DOWN:
        return
    y = WIN_H - y  # Convert mouse y-coordinate to OpenGL system
    for name, b in [('left', btn_left), ('mid', btn_middle), ('right', btn_right)]:
        cx, cy, hw, hh = b
        if cx-hw <= x <= cx+hw and cy-hh <= y <= cy+hh:
            if name == 'left':
                restartGame()
            elif name == 'mid' and state in ('playing', 'paused'):
                state = 'paused' if state == 'playing' else 'playing'
                print("Toggled state:", state)
            elif name == 'right':
                print("Goodbye. Your score was:", score)
                glutLeaveMainLoop()
            break

# ---------------------------------------------------
# Special keys for moving the catcher
def specialKey(key, x, y):
    global catcher_x
    if state != 'playing':
        return
    if key == GLUT_KEY_LEFT:
        catcher_x = max(catcher_w // 2, catcher_x - 20)
    elif key == GLUT_KEY_RIGHT:
        catcher_x = min(WIN_W - catcher_w // 2, catcher_x + 20)

# ---------------------------------------------------
# Update game state each frame # GAME RESULT GENERATING
def update(): 
    global diamond_y, t_last, score, speed, catcher_color, state
    now = time.time()
    dt = now - t_last
    t_last = now
    if state == 'playing':
        diamond_y -= speed * dt
        speed += acceleration * dt
        b1 = {'x': diamond_x - diamond_w//2, 'y': diamond_y - diamond_h//2, 'w': diamond_w, 'h': diamond_h}
        b2 = {'x': catcher_x - catcher_w//2, 'y': catcher_y - catcher_h//2, 'w': catcher_w, 'h': catcher_h}
        if hasCollided(b1, b2):
            score += 1
            print("Score:", score)
            resetDiamond()
        elif diamond_y < 0: # IF DIAMOND GONE OUTSIDE THE window
            state = 'over'
            catcher_color = (1.0, 0.0, 0.0)
            print("Game Over. Your final score was:", score)
    glutPostRedisplay()

# ---------------------------------------------------
# Display callback: clear screen and draw all objects
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(*diamond_color)
    drawDiamond(diamond_x, diamond_y)
    glColor3f(*catcher_color)
    drawCatcher()
    drawButtons()
    drawText(10, WIN_H-20, f"Score: {score}")
    if state == 'over':
        msg = "Game Over!"
        w = len(msg) * 9
        drawText((WIN_W - w)//2, WIN_H//2, msg, color=(1, 0, 0))
    glutSwapBuffers()

# ---------------------------------------------------
# Reshape callback: adjust viewport and projection
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)

# ---------------------------------------------------
# Main: set up GLUT and enter the main loop
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds!")
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutSpecialFunc(specialKey)
    glutMouseFunc(mouseClick)
    glutIdleFunc(update)
    glutMainLoop()

if __name__ == "__main__":
    main()
