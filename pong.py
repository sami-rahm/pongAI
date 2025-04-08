import pygame 
import random
import math
pygame.init()


class neural_network:
    def __init__(self,inp,h,o):#initialise network
        self.inputs=[1 for _ in range(inp)]
        self.hidden=[[[1,random.uniform(-0.5,0.5)] for _ in range(h[i])] for i in range(len(h))]#neuron value,bias
        self.outputs=[[1,random.uniform(-0.5,0.5)] for _ in range(o) ]
        self.weights=[]

        self.weights.append([[random.uniform(-0.5,0.5) for i in range(h[0])] for _ in range(inp)])

        for i in range(len(h)-1):
            self.weights.append([[random.uniform(-0.5,0.5) for n in range(h[i+1])] for w in range(h[i])])

        self.weights.append([[random.uniform(-0.5,0.5) for i in range(o)] for _ in range(h[-1])]) 
       
        #layer indexing is [layer][source neuron][target neuron]
   
    def softsign(self,n):#scaled softsign 
        return n/(1+abs(n*2))*2
    def leakyrelu(self,n):
        if n>0:
            return n
        else:
            return n*0.01
 
    def forward(self,inputvalues):#forward propagation- calculates outputs
        if len(inputvalues)!=len(self.inputs):
            raise ValueError("input size doesnt match input network size")
        self.inputs=inputvalues
        for h in range(len(self.hidden[0])):#iterating through neurons in hidden layer 0
            nsum=0#sum of all input neurons * weight connected to it
            for n in range(len(self.inputs)):#iterating through input neurons
                nsum+=self.inputs[n]*self.weights[0][n][h]
            nsum=self.leakyrelu(nsum+self.hidden[0][h][1])#adds the bias then applies leaky relu activation
            self.hidden[0][h][0]=nsum
        if len(self.hidden)!=1:
            for layer in range(len(self.hidden)-1):
                for h in range(len(self.hidden[layer+1])):
                    nsum=0
                    for n in range(len(self.hidden[layer])):
                        nsum+=self.hidden[layer][n][0]*self.weights[layer+1][n][h]
                    nsum=self.leakyrelu(nsum+self.hidden[layer+1][h][1])
                    self.hidden[layer+1][h][0]=nsum
        output_values=[0 for i in range(len(self.outputs))]
        for o in range(len(self.outputs)):#calculate output layer
            nsum=0
            for n in range(len(self.hidden[-1])):
                nsum+=self.hidden[-1][n][0]*self.weights[-1][n][o]
            nsum=self.softsign(nsum+self.outputs[o][1])
            self.outputs[o][0]=nsum
            output_values[o]=nsum
        return output_values
    
    def modifyby_evolution(self,mutation_rate):#random modifies weights and biases
        for w in range(len(self.weights)):
            for i in range(len(self.weights[w])):
                for j in range(len(self.weights[w][i])):
                    if random.uniform(0,1)<mutation_rate:
                        self.weights[w][i][j]+=random.uniform(-1,1)*mutation_rate # if mutation rate is higher it will also mutate by a higher amount
        for h in range(len(self.hidden)):
            for i in range(len(self.hidden[h])):
                if random.uniform(0,1)<mutation_rate:
                    self.hidden[h][i][1]+=random.uniform(-1,1)*mutation_rate
        for o in range(len(self.outputs)):
            if random.uniform(0,1)<mutation_rate:
                self.outputs[o][1]+=random.uniform(-1,1)*   mutation_rate

    def copy(self):
            new_net = neural_network(len(self.inputs), [len(h) for h in self.hidden], len(self.outputs))
            # Copy weights
            for l in range(len(self.weights)):
                for i in range(len(self.weights[l])):
                    for j in range(len(self.weights[l][i])):
                        new_net.weights[l][i][j] = self.weights[l][i][j]
            # Copy biases
            for l in range(len(self.hidden)):
                for i in range(len(self.hidden[l])):
                    new_net.hidden[l][i][1] = self.hidden[l][i][1]
            for i in range(len(self.outputs)):
                new_net.outputs[i][1] = self.outputs[i][1]
            return new_net


class ball:
    def __init__(self, x, y, radius,colour,speed):
        self.x = x # X coordinate of the ball
        self.y = y # Y coordinate of the ball
        self.radius = radius # Radius of the ball
        self.speed=speed
        theta=random.uniform(-0.5,0.5)#generate an angle between 30,-30 excluding angles between 10 and -10
        if theta<0 and theta>-0.2:theta-=0.2
        if theta>0 and theta<0.2:theta+=0.2
        rnd=random.choice((-1,1))
        self.vel_x=math.cos(theta)*self.speed*rnd
        self.vel_y=math.sin(theta)*self.speed*rnd
        self.iscollided=False
        self.colour=colour
      

    def draw(self, win): # Draws the ball on the window
        pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius) # Draws a circle with a red color

    def collisioncheck(self, p):
        # Check if the ball's x-coordinate overlaps with the paddle's x-coordinate
        if self.x - self.radius < p.x + p.width and self.x + self.radius > p.x:
            # Check if the ball's y-coordinate is within the paddle's height
            if self.y + self.radius > p.y and self.y - self.radius < p.y + p.height:
                self.iscollided = True
                # Move ball to proper position based on which paddle it hit
                if p.isenemy:
                    self.x = p.x - self.radius-1  # Place ball at left edge of enemy paddle
                else:
                    self.x = p.x + p.width + self.radius+1  # Place ball at right edge of player paddle
              
                p.score += 2
                p.computefitness(p.score)
                #print("collision")
        
    def move(self,p):
        
        if self.y+self.radius>500 or self.y-self.radius<0:
    
            rand=random.uniform(0.99,1.01)
            self.vel_y*=-rand
            self.vel_x/=rand
        if self.iscollided:
            self.x+=1
            rand=random.uniform(0.99,1.01)
            self.vel_x*=-rand#prevent ball from repeating patterns
            self.vel_y/=rand
            self.iscollided=False
        self.x+=self.vel_x
        self.y+=self.vel_y
    def reset(self):
        self.x=400
        self.y=250
        theta=random.uniform(-0.5,0.5)#generate an angle between 30,-30 excluding angles between 10 and -10
        if theta<0 and theta>-0.2:theta-=0.2
        if theta>0 and theta<0.2:theta+=0.2
        rnd=random.choice((-1,1))
        self.vel_x=math.cos(theta)*self.speed*rnd
        self.vel_y=math.sin(theta)*self.speed*rnd
        self.iscollided=False
       
             
class player:
    def __init__(self, x, y, width, height,colour,isenemy): # Initializes the player with the given x and y coordinates and width and height
        self.x = x # X coordinate of the player
        self.y = y # Y coordinate of the player
        self.width = width # Width of the player
        self.height = height # Height of the player
        self.net=neural_network(6,[18,10],1)#initialise network
        self.fitness=0
        self.mutationrate=1.01
        self.vel=0
        self.score=0
        self.points=0
        self.gen=0
        self.predictedval=0
        self.colour=colour
        self.isenemy=isenemy
        self.iselite=False
        self.pointstowin=3

    def draw(self, win): # Draws the player on the window
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.height)) # Draws a rectangle with a red color
    def move(self,speed,b,opp,movementthreshold,g):
        self.gainedpoint=False
        b.gainedgen=False
        self.iselite=False
        if b.x+b.radius<0 :#if ball hits player wall
            if self.isenemy:
                self.points+=1
                self.score+=0.5
                self.computefitness(self.score)
              
                #print("enemy gained point",self.score)
            else:#if the player lost the ball half their score and reward based on distance to ball, give the enemy a point
                self.score*=0.9
                sc=self.computescore(b)
               
                self.score+=sc
                print("player score",sc)
                self.computefitness(self.score)
                opp.points+=1
                opp.score+=0.5
                opp.computefitness(opp.score)
            self.y=250-self.height/2
            opp.y=250-opp.height/2   
            b.reset()
            #print('ball hit player wall')
            if self.points>=self.pointstowin or opp.points>=opp.pointstowin:
                self.reset(g)
                opp.reset(g)
                self.gen+=1
                opp.gen+=1
               # print("new generation",self.gen,opp.gen)

        if b.x+b.radius>800 :#if ball hits enemy wall
            if self.isenemy:
                self.score*=0.9
                sc=self.computescore(b)
               
                self.score+=sc
                #print("enemy score",self.score)
                self.computefitness(self.score)
                
                opp.points+=1
                opp.score+=0.5
                opp.computefitness(opp.score)
               
              
            else:#if the enemy lost the ball half their score and reward based on distance to ball, give the enemy a point
                self.points+=1
                self.score+=0.5
                self.computefitness(self.score)
                
                #print("enemy gained point",self.score)
            #print('ball hit enemy wall')
            self.y=250-self.height/2
            opp.y=250-opp.height/2
            b.reset()
            if self.points>=self.pointstowin or opp.points>=opp.pointstowin:
                self.reset(g)
                opp.reset(g)
                self.gen+=1
                opp.gen+=1
                #print("new generation",self.gen,opp.gen)
       
        #region predicted movement- takes inputs and feeds them into the network   
        if self.y<0:
 
            self.computefitness(self.score)
            self.y+=speed
        if self.y>500-self.height:
         
            self.computefitness(self.score)
            self.y-=speed
        self.predictedval=self.net.forward([self.y/500,b.y/500,b.x/800,b.vel_x/speed,b.vel_y/speed,opp.y/500])[0]
        if self.predictedval>movementthreshold:
            self.vel=speed
        elif self.predictedval<movementthreshold and self.predictedval>-movementthreshold:
            self.vel=0
        elif self.predictedval<-movementthreshold:
            self.vel=-speed
        self.y+=self.vel
        self.score+=0.0005/self.pointstowin
        self.computefitness(self.score)
        #endregion
       

    def computefitness(self,score):
        self.fitness=score/(10+score)
    def computescore(self,b):
        return 2/(1+abs(self.y-self.height/2-b.y)/10) #rewards for being close to the ball
    def reset(self,g):
        self.y=250-self.height/2
        self.vel=0
        self.score=0
        self.points=0
        if not self.iselite:
            self.mutate(g)
            self.fitness=0
        
    def mutate(self,g):
        rnd=random.uniform(0,1)
        if rnd<0.5 :    
            self.mutationrate=(1.01-self.fitness)/4
            self.net.modifyby_evolution(self.mutationrate)
            print("mutation happened",self.mutationrate)
        elif rnd<0.9:
            if not self.isenemy:
                elites=sorted(range(g.population),key=lambda x: g.players[x].fitness,reverse=True)[:g.elitesn]
                self.net=random.choice([g.players[i].net.copy() for i in elites])#copy elite network
            if self.isenemy:
                elites=sorted(range(g.population),key=lambda x: g.enemies[x].fitness,reverse=True)[:g.elitesn]
                self.net=random.choice([g.enemies[i].net.copy() for i in elites])
            
            self.mutationrate=(1.01-self.fitness)/5
            self.net.modifyby_evolution(self.mutationrate)
            print("elite copy",self.mutationrate)
        else:
            self.net=neural_network(6,[18,10],1)#initialise network
            self.mutationrate=(1.01-self.fitness)/4
            print("reset network",self.mutationrate)
        
           

class game:
    def __init__(self,width,height, population, ptw,speed,elitesn,movementthreshold,win): 
        colours=[(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for i in range(population)]
        self.players=[player(20, 250-height/2, width, height,colours[i],False) for i in range(population)] # Creates a player object
        self.enemies=[player(780-width, 250-height/2, width, height,colours[i],True) for i in range(population)] # Creates the enemies object
        self.balls=[ball(400, 250, 10,colours[i],speed) for i in range(population)] # Creates the ball object
        self.elitesn=elitesn
        self.population=population
        self.ptw=ptw
        self.speed=speed
        self.win=win
        self.movethreshold=movementthreshold
    def drawall(self):#draw all (unused for now)
        for i in range(len(self.players)):
            self.players[i].draw(win)
            self.enemies[i].draw(win)
            self.balls[i].draw(win)
    def findelites(self):#sort by fitness 
        plindex=sorted(range(self.population),key=lambda x: self.players[x].fitness,reverse=True)[:self.elitesn]
        enindex=sorted(range(self.population),key=lambda x: self.enemies[x].fitness,reverse=True)[:self.elitesn]
        for i in range(len(self.players)):
            if i not in plindex:
                self.players[i].iselite=False
            else:
                self.players[i].iselite=True
            if i not in enindex:
                self.enemies[i].iselite=False
            else:
                self.enemies[i].iselite=True
    def run(self,txt,txt2):
        for p in range(self.population):#apply movement
            self.players[p].move(self.speed,self.balls[p],self.enemies[p],self.movethreshold,self)
            self.enemies[p].move(self.speed,self.balls[p],self.players[p],self.movethreshold,self)
            self.balls[p].move(self.players[p])
            self.balls[p].collisioncheck(self.players[p])
            self.balls[p].collisioncheck(self.enemies[p])
        self.findelites()
        for i in range(self.population):#only render the top performing games
            if (self.players[i].fitness+self.enemies[i].fitness)/2==max((self.players[n].fitness+self.enemies[n].fitness)/2 for n in range(self.population)):
                
                self.players[i].draw(self.win)
                self.enemies[i].draw(self.win)
                self.balls[i].draw(self.win)
                txt=font.render("fitness: "+f'{self.players[i].fitness:.2f}'+' score: '+\
                f'{self.players[i].score:.2f}'+" gen:"+str(self.players[i].gen)+" iselite: "+str(self.players[i].iselite),1,(255,255,255)) # Renders the text with the given font and color
                txt2=font.render("fitness: "+f'{self.enemies[i].fitness:.2f}'+\
                ' score: '+f'{self.enemies[i].score:.2f}'+" iselite: "+str(self.enemies[i].iselite),1,(255,255,255)) # Renders the text with the given font and color
                self.win.blit(txt2,(self.enemies[i].x-300,self.enemies[i].y+self.enemies[i].height/2)) # Blits the text on the window
                self.win.blit(txt,(self.players[i].x+30,self.players[i].y+self.enemies[i].height/2)) # Blits the text on the window
                #display gen fitness
                break
                




       


#region main game loop
win=pygame.display.set_mode((800,500))
pygame.display.set_caption("Pong Game")
pygame.font.init() # Initializes the font module
font=pygame.font.SysFont('verdana', 15) # Creates a font object with the given font and size
txt=font.render(None,1,(255,255,255)) # Renders the text with the given font and color
txt2=font.render(None,1,(255,255,255)) # Renders the text with the given font and color
#width height population points to win speed number of elites movement threshold window

game1=game(20,200,20,2,30,3,0.4,win) # Creates the game object with the given player and ball
run = True # This is a boolean variable that will be used to run the game loop
while run:
    pygame.time.delay(7) # This will delay the game the given amount of milliseconds 0.013 seconds or 75fps
    win.fill((37, 21, 46))
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:
            run = False  # Ends the game loop
  
    game1.run(txt,txt2)
   
  
    pygame.display.update()


pygame.quit()  # If we exit the loop this will execute and close our game
#endregion
