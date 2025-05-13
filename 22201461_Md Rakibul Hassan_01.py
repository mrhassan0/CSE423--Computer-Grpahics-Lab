# MD RAKIBUL HASSAN
# 22201461
# SECTION 02


#######------------------------------------Task 01----------------------------------------------------------------------------#######


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

#Window dimensions
width,height= 1100, 800
#Rain properties
total_drops=200  
#random raindrops 
raindrops= [(random.randint(300, 800), random.randint(300, 600)) for x in range(total_drops)]
rain_speed= 5    #Vertical 
rain_angle= 0    # Horizontal angle
rain_length=20  
#Day-night 
bg_color= [0.0, 0.0, 0.0]  
day_night_step=0.05         
def draw_house():
    #Roof
    glColor3f(0.5, 0.2, 0.1)  #Brown color
    glBegin(GL_TRIANGLES)
    glVertex2f(400, 400)
    glVertex2f(700, 400)
    glVertex2f(550, 600)
    glEnd()
    
    #House walls
    glColor3f(0.9, 0.8, 0.7)  #Light gray
    glBegin(GL_TRIANGLES)
    #First triangle for walls
    glVertex2f(420, 200)
    glVertex2f(680, 200)
    glVertex2f(420, 400)
    # Second triangle for walls
    glVertex2f(420, 400)
    glVertex2f(680, 400)
    glVertex2f(680, 200)
    glEnd()
    
    #oor 
    glColor3f(0.4, 0.2, 0.0)  #Dark brown
    glBegin(GL_TRIANGLES)
    glVertex2f(520, 200)
    glVertex2f(580, 200)
    glVertex2f(520, 320)
    
    glVertex2f(520, 320)
    glVertex2f(580, 320)
    glVertex2f(580, 200)
    glEnd()
    
    #Windows
    glColor3f(0.6, 0.8, 1.0)  #light blue
    #Left window
    glBegin(GL_TRIANGLES)
    glVertex2f(440, 320)
    glVertex2f(480, 320)
    glVertex2f(440, 360)
    
    glVertex2f(440, 360)
    glVertex2f(480, 360)
    glVertex2f(480, 320)
    glEnd()
    
    #Right window
    glBegin(GL_TRIANGLES)
    glVertex2f(620, 320)
    glVertex2f(660, 320)
    glVertex2f(620, 360)
    
    glVertex2f(620, 360)
    glVertex2f(660, 360)
    glVertex2f(660, 320)
    glEnd()



def draw_rain():
    glColor3f(0.0,0.0, 1.0) #blue 
    glBegin(GL_LINES)
    for i in range(total_drops):
        x,y =raindrops[i]
        #draw each raindrop as a line segment
        glVertex2f(x,y)
        glVertex2f(x+rain_angle, y-rain_length)  #diagonal line based on wind angle
    glEnd()




def update_rain(value):
    global raindrops
    new_raindrops=[]
    for x,y in raindrops:
        #update raindrop position with wind angle and speed
        x+= rain_angle
        y-= rain_speed
        #reset raindrop position when it falls below 200
        if y<200:
            y= random.randint(400, 600)
            x=random.randint(300, 800)
        new_raindrops.append((x, y))
    raindrops= new_raindrops
    glutPostRedisplay()  #Trigger redraw
    glutTimerFunc(50, update_rain,0)  #Recursive timer for animation




def keyboard(key, x, y):
    global bg_color
    #w key increases brightness 
    if key== b'w':
        if bg_color[0]< 1.0:
            # Create 3-element 
            bg_color = [min(1.0,bg_color[0]+day_night_step)]*3
    #s key decreases brightness 
    elif key== b's':
        if bg_color[0] > 0.0:
            bg_color=[max(0.0,bg_color[0]-day_night_step)]*3
    glutPostRedisplay()

def spec_keys(key, x, y):
    global rain_angle
    if key==GLUT_KEY_LEFT:
        rain_angle-= 1
    elif key== GLUT_KEY_RIGHT:
        rain_angle+= 1
    glutPostRedisplay()



def display():
    glClear(GL_COLOR_BUFFER_BIT)  # Clear screen
    glLoadIdentity()
    #set background color (uses first 3 elements of bg_color)
    glClearColor(bg_color[0], bg_color[1], bg_color[2], 1.0)
    draw_house()
    draw_rain()
    glutSwapBuffers()  
def reshape(w,h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)









# GLUT 
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  
glutInitWindowSize(width, height)
glutCreateWindow(b'House in Rainfall')  
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(spec_keys)
#start rain animation timer
glutTimerFunc(50,update_rain,0)
glLineWidth(2)  
glutMainLoop()  


#######------------------------------------Task 02----------------------------------------------------------------------------#######

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

#window dimensions
width,height=800, 600

#point properties
points=[]  
speed=2
frozen= False
blinking= False


def draw_points():
    glPointSize(5)
    glBegin(GL_POINTS)
    for x,y,dx,dy,r,g,b in points:
        if blinking and int(glutGet(GLUT_ELAPSED_TIME)/500)%2==  0:
            glColor3f(0,0, 0)  #blink to background color
        else:
            glColor3f(r, g, b)
        glVertex2f(x, y)
    glEnd()




def update_points(value):
    global points
    if not frozen:
        new_points= []
        for x,y,dx,dy,r,g,b in points:
            x += dx *speed
            y+= dy* speed
            #bounce off walls
            if x<=0 or x>=width:
                dx= -dx
            if y<=0 or y>=height:
                dy=-dy
            new_points.append((x,y,dx,dy,r,g,b))
        points=new_points
    glutPostRedisplay()
    glutTimerFunc(20,update_points,0)






def mouse(button, state, x, y):
    global blinking
    if state==GLUT_DOWN:
        if button==GLUT_RIGHT_BUTTON:
            #generate a new point with a random direction and color
            dx=random.choice([-1,1])
            dy=random.choice([-1,1])
            r,g,b = random.random(),random.random(),random.random()
            points.append((x,height-y,dx,dy,r,g,b))
        elif button ==GLUT_LEFT_BUTTON:
            blinking =not blinking  #toggle blinking


def keyboard(key,x, y):
    global frozen
    if key==b' ':
        frozen=not frozen  #toggle freeze



def special_keys(key, x, y):
    global speed
    if key==GLUT_KEY_UP:
        speed+=1  #increase speed
    elif key== GLUT_KEY_DOWN:
        speed= max(1,speed-1)  #decrease speed but not below 1


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    draw_points()
    glutSwapBuffers()
def reshape(w,h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,0,height)
    glMatrixMode(GL_MODELVIEW)





glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b'Bouncing Points')
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special_keys)
glutTimerFunc(20, update_points, 0)
glClearColor(0,0,0,1)
glutMainLoop()
