import pygame 
import random
import network
pygame.init()

class ball:
    def __init__(self, x, y, radius):
        self.x = x # X coordinate of the ball
        self.y = y # Y coordinate of the ball
        self.radius = radius # Radius of the ball
        self.vel_x = random.choice((-0.5,0.5)) # Velocity in the x direction
        self.vel_y =random.choice((-0.2,0.2)) # Velocity in the y direction

    def draw(self, win): # Draws the ball on the window
        pygame.draw.circle(win, (176, 176, 176), (self.x, self.y), self.radius) # Draws a circle with a red color
class player:
    def __init__(self, x, y, width, height): # Initializes the player with the given x and y coordinates and width and height
        self.x = x # X coordinate of the player
        self.y = y # Y coordinate of the player
        self.width = width # Width of the player
        self.height = height # Height of the player
        self.net=network.neural_network(2,[5,5],1)#initialise network

    def draw(self, win): # Draws the player on the window
        pygame.draw.rect(win, (45, 95, 156), (self.x, self.y, self.width, self.height)) # Draws a rectangle with a red color
    def move(self,vel):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.y - vel > 0: # If the up arrow key is pressed and the player is not at the top edge of the window
            self.y -= vel
        if keys[pygame.K_DOWN] and self.y + vel < 500 - self.height: # If the down arrow key is pressed and the player is not at the bottom edge of the window
            self.y += vel
        
win=pygame.display.set_mode((800,500))
pygame.display.set_caption("Pong Game")
points=0
ball1 = ball(400, 250, 20) # Creates a ball object with x=400, y=250 and radius=10
player1 = player(20, 250, 20, 150) 
pygame.font.init() # you have to call this at the start, 
my_font = pygame.font.SysFont('freesansbold', 100)
text_surface = my_font.render('0', False, (114, 224, 92))
run = True # This is a boolean variable that will be used to run the game loop
while run:
    pygame.time.delay(1) # This will delay the game the given amount of milliseconds. In our casee 0.1 seconds will be the delay
    win.fill((37, 21, 46))
    for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
        if event.type == pygame.QUIT: # Checks if the red button in the corner of the window is clicked
            run = False  # Ends the game loop
   
    if ball1.x + ball1.radius >= 800 : # If the ball hits the left or right wall
        ball1.vel_x *= -1 # Reverse the velocity in the x direction
    if ball1.y + ball1.radius >= 500 or ball1.y - ball1.radius <= 0: # If the ball hits the top or bottom wall
        ball1.vel_y *= -1
    # Reverse the velocity in the y direction
    if ball1.x-ball1.radius<player1.x+player1.width and ball1.y>player1.y and ball1.y<player1.y+player1.height: 
        ball1.x+=1
        print("Collision")
        ball1.vel_x*=-1
    if ball1.x - ball1.radius <=0:
        print("point")
        points+=1
        text_surface = my_font.render(str(points), False, (114, 224, 92))
        if points>=5:
            run=False
        ball1.x=400
        ball1.y=250
        ball1.vel_x=random.choice((-0.5,0.5))
        ball1.vel_y=random.choice((-0.2,0.2))
    ball1.x += ball1.vel_x # Updates the x coordinate of the ball by adding the velocity in the x direction
    ball1.y += ball1.vel_y # Updates the y coordinate of the ball by adding the velocity in the y direction
    player1.move(0.5) # Moves the player by 5 pixels  
    player1.draw(win) # Draws the player on the window
    ball1.draw(win)
    win.blit(text_surface, (390, 0)) # Draws the text on the window
    pygame.display.update()


pygame.quit()  # If we exit the loop this will execute and close our game
