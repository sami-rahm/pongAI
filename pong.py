import pygame 
import random
import math
import time
pygame.init()


class neural_network:
    def __init__(self,inp,h,o):#initialise network
        self.inputs=[1 for _ in range(inp)]
        lim=math.sqrt(2/(inp+o))#limit for weights and biases
        self.hidden=[[[1,random.uniform(-lim,lim)] for _ in range(h[i])] for i in range(len(h))]#neuron value,bias
        self.outputs=[[1,random.uniform(-lim,lim)] for _ in range(o) ]
        self.weights=[]

        self.weights.append([[random.uniform(-lim,lim) for i in range(h[0])] for _ in range(inp)])

        for i in range(len(h)-1):
            self.weights.append([[random.uniform(-lim,lim) for n in range(h[i+1])] for w in range(h[i])])

        self.weights.append([[random.uniform(-lim,lim) for i in range(o)] for _ in range(h[-1])]) 
       
        #layer indexing is [layer][source neuron][target neuron]
   
    def softsign(self,n):#scaled softsign 
        return n/(1+abs(n*2))+0.5
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
        theta=random.uniform(-0.7,0.7)#generate an angle between 35,-35 excluding angles between 10 and -10
        if theta<0 and theta>-0.2:theta-=0.2
        if theta>0 and theta<0.2:theta+=0.2
        rnd=random.choice((-1,1))
        self.vel_x=self.qcos(theta)*self.speed*rnd
        self.vel_y=self.qsin(theta)*self.speed*rnd
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
              
                reward=p.computescore(self)+1
                #if reward>2.999:
                    #print("reward",reward)
                p.score+=reward
                p.computefitness(p.score)
                #print("collision")
        
    def move(self,bounceerror):
        if self.y+self.radius>500:
            self.y=499-self.radius
            self.vel_y*=-1
            angle=math.atan2(self.vel_y,self.vel_x)
            rand=random.uniform(angle-bounceerror,angle+bounceerror)
            self.vel_y=self.speed*math.sin(rand)
            self.vel_x=self.speed*math.cos(rand)
        elif self.y-self.radius<0:
            self.y=1+self.radius
            self.vel_y*=-1
            angle=math.atan2(self.vel_y,self.vel_x)
            rand=random.uniform(angle-bounceerror,angle+bounceerror)
            self.vel_y=self.speed*math.sin(rand)
            self.vel_x=self.speed*math.cos(rand)
        if self.iscollided:
            ratio=abs(self.vel_y/self.vel_x) #also known as tangent
            #uses trig values of 40 and 15 deg to maintain the total normalised velocity to be one 
            if ratio>1:#if gradient is too steep (greater than 45 degrees) then it will be 40 degress
                rx= 1 if self.vel_x<0 else -1
                ry=-1 if self.vel_y<0 else 1
                self.vel_x=self.speed*rx*0.765
                self.vel_y=self.speed*ry*0.644
                
            elif ratio<0.0875:#if gradient is too shallow (less than 5 degrees) then it will be 10 degrees
                rx= 1 if self.vel_x<0 else -1
                ry=-1 if self.vel_y<0 else 1
                self.vel_x=self.speed*rx*0.985
                self.vel_y=self.speed*ry*0.174
            else:
                self.vel_x*=-1
                angle=math.atan2(self.vel_y,self.vel_x)
                rand=random.uniform(angle-bounceerror,angle+bounceerror)
                self.vel_y=self.speed*math.sin(rand)
                self.vel_x=self.speed*math.cos(rand)
            self.iscollided=False
        self.x+=self.vel_x
        self.y+=self.vel_y
       
    def reset(self):
        self.x=400
        self.y=250
        theta=random.uniform(-0.7,0.7)#generate an angle between 35,-35 excluding angles between 10 and -10
        if theta<0 and theta>-0.2:theta-=0.2
        if theta>0 and theta<0.2:theta+=0.2
        rnd=random.choice((-1,1))
        self.vel_x=self.qcos(theta)*self.speed*rnd
        self.vel_y=self.qsin(theta)*self.speed*rnd
        self.iscollided=False
    def qsin(self,theta):   
        if theta==0:
            return 0  
        pi=3.1416
        n=theta%pi
        x=pi-n
        ans= 16*n*x/(5*pi*pi-4*n*x)
        if (theta//pi)%2==0:
            return ans
        else:
            return -ans
    def qcos(self,theta):
        pi=3.1416
        return self.qsin(theta+pi/2)
    def qtan(self,theta):
        return self.qsin(theta)/self.qcos(theta)
    def qatan(self,theta):#probably no point of these approximations since python is slow
        halfpi=1.5708
        fa=(halfpi*theta)/(1+abs(theta))
        if theta<5 and theta>-5:
            return fa
        sa=theta*(45+theta**2)/(45+9*theta**2)
       
        
        return (fa+sa)/2
      
             
class player:
    def __init__(self, x, y, width, height,colour,isenemy): # Initializes the player with the given x and y coordinates and width and height
        self.x = x # X coordinate of the player
        self.y = y # Y coordinate of the player
        self.width = width # Width of the player
        self.height = height # Height of the player
        self.net=neural_network(6,[16,10],3)#initialise network
        self.fitness=0
        self.mutationrate=0.4
        self.vel=0
        self.score=0
        self.points=0
        self.gen=0
        self.predictedvals=[None]
        self.colour=colour
        self.isenemy=isenemy
        self.iselite=False
        self.pointstowin=3

    def draw(self, win): # Draws the player on the window
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.height)) # Draws a rectangle with a red color
    def move(self,speed,b,opp,g):
       
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
                self.score*=0.7
                sc=self.computescore(b)
               
                self.score+=sc
                #print("player score",sc)
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
                self.score*=0.7
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
       
       
        if self.y<0: 
            self.y+=speed
        if self.y>500-self.height: 
            self.y-=speed
        #region predicted movement- takes inputs and feeds them into the network   
        self.predictedvals=self.net.forward([self.y/500,b.y/500,b.x/800,b.vel_x/speed,b.vel_y/speed,opp.y/500])
        upsignal=self.predictedvals[0]
        staysignal=self.predictedvals[1]
        downsignal=self.predictedvals[2]
        if upsignal>staysignal and upsignal>downsignal:
            self.vel=-speed
        elif downsignal>upsignal and downsignal>staysignal:
            self.vel=speed
        else:
            self.vel=0
           
        
        self.y+=self.vel
        self.score+=0.001/self.pointstowin
        self.computefitness(self.score)
        #endregion
       
    def geneticcrossover(self,other):#crossover between two players
        new_net=neural_network(len(self.net.inputs), [len(h) for h in self.net.hidden], len(self.net.outputs))
        for l in range(len(self.net.weights)):
            for i in range(len(self.net.weights[l])):
                for j in range(len(self.net.weights[l][i])):
                    if random.uniform(0,1)<0.5:
                        new_net.weights[l][i][j] = self.net.weights[l][i][j]
                    else:
                        new_net.weights[l][i][j] = other.weights[l][i][j]
        for l in range(len(self.net.hidden)):
            for i in range(len(self.net.hidden[l])):
                if random.uniform(0,1)<0.5:
                    new_net.hidden[l][i][1] = self.net.hidden[l][i][1]
                else:
                    new_net.hidden[l][i][1] = other.hidden[l][i][1]
        for i in range(len(self.net.outputs)):
            if random.uniform(0,1)<0.5:
                new_net.outputs[i][1] = self.net.outputs[i][1]
            else:
                new_net.outputs[i][1] = other.outputs[i][1]
        return new_net


    def computefitness(self,score):
        if score<12:
            self.fitness=score*0.03
        elif score<26:
            self.fitness=score*0.01+0.24
        elif score<70:
            self.fitness=score*0.005+0.37
        elif score<200:
            self.fitness=score*0.001+0.65
        elif score<500:
            self.fitness=score*0.0002+0.81
        elif score<1400:
            self.fitness=score*0.00005+0.885
        elif score<2900:
            self.fitness=score*0.00003+0.913
        else:
            self.fitness=1.0
    def computescore(self,b):
        return 2/(1+abs(self.y+self.height/2-b.y)/(self.height/4)) #rewards for being close to the ball
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
        if rnd<0.7 :    
            self.mutationrate=(1.01-self.fitness)/4
            self.net.modifyby_evolution(self.mutationrate)
            #print("mutation happened",self.mutationrate)
        elif rnd<0.74:
            efitness=0
            if not self.isenemy:
                elites=sorted(range(g.population),key=lambda x: g.players[x].fitness,reverse=True)[:g.elitesn]
                ei1=random.choice([i for i in elites])
                ei2=random.choice([i for i in elites])
                efitness=(g.players[ei1].fitness+g.players[ei2].fitness)/2
                self.net=g.players[ei1].geneticcrossover(g.players[ei2].net.copy()).copy()#mix elite genes
            if self.isenemy:
                elites=sorted(range(g.population),key=lambda x: g.enemies[x].fitness,reverse=True)[:g.elitesn]
                ei1=random.choice([i for i in elites])
                ei2=random.choice([i for i in elites])
                efitness=(g.enemies[ei1].fitness+g.enemies[ei2].fitness)/2
                self.net=g.enemies[ei1].geneticcrossover(g.enemies[ei2].net.copy()).copy()#mix elite genes
            if random.random()<0.7:
                self.mutationrate=(1.01-efitness)/5
                self.net.modifyby_evolution(self.mutationrate)
            #print("elite crossover",self.mutationrate)
        elif rnd<0.9:
             if not self.isenemy:
                elites=sorted(range(g.population),key=lambda x: g.players[x].fitness,reverse=True)[:g.elitesn]
                eliteindex=random.choice([i for i in elites])
                self.net=g.players[eliteindex].net.copy()
                if random.random()<0.5:
                    self.mutationrate=(1.01-g.players[eliteindex].fitness)/5
                    self.net.modifyby_evolution(self.mutationrate)
             if self.isenemy:
                elites=sorted(range(g.population),key=lambda x: g.enemies[x].fitness,reverse=True)[:g.elitesn]
                eliteindex=random.choice([i for i in elites])
                self.net=g.enemies[eliteindex].net.copy()
                if random.random()<0.5:
                    self.mutationrate=(1.01-g.enemies[eliteindex].fitness)/5
                    self.net.modifyby_evolution(self.mutationrate)

        else:
            self.net=neural_network(6,[16,10],3)#initialise network
            self.mutationrate=(1.01-self.fitness)/4
            #print("reset network",self.mutationrate)
        
           

class game:
    def __init__(self,width,height, population, ptw,speed,elitesn,bounceError,win): 
        colours=[(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for i in range(population)]
        self.players=[player(30, 250-height/2, width, height,colours[i],False) for i in range(population)] # Creates a player object
        self.enemies=[player(780-width, 250-height/2, width, height,colours[i],True) for i in range(population)] # Creates the enemies object
        self.balls=[ball(400, 250, 15,colours[i],speed) for i in range(population)] # Creates the ball object
        self.elitesn=elitesn
        self.population=population
        self.ptw=ptw
        self.speed=speed
        self.win=win
        self.bounceError=bounceError
       
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
    def maxfitness(self):#find max fitness of all players
        plindex=max(range(self.population),key=lambda x: self.players[x].fitness)
        enindex=max(range(self.population),key=lambda x: self.enemies[x].fitness)
        return self.players[plindex].fitness,self.enemies[enindex].fitness,self.players[plindex].gen,self.enemies[enindex].gen
      
    def run(self,txt,txt2):
        for p in range(self.population):#apply movement
            self.players[p].move(self.speed,self.balls[p],self.enemies[p],self)
            self.enemies[p].move(self.speed,self.balls[p],self.players[p],self)
            self.balls[p].move(self.bounceError)
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
#width height population points to win speed number of elites  window
inp=input("enter 1 for default values or 0 for custom values")

if inp=="1":
    width=31
    height=200
    population=50
    ptw=2
    speed=60
    elitesn=5
    bounceError=0.1#radians where 0.1 is 6 deg
    fps=165

else:
    width=int(input("width "))
    height=int(input("height "))
    population=int(input("population "))
    ptw=int(input("points to win "))
    speed=float(input("speed "))
    elitesn=int(input("no of elites "))
    bounceError=float(input("bounce error in radians "))#radians where 0.1 is 6 deg
    fps=int(input("fps "))
delay=int(1000/fps)
game1=game(width,height,population,ptw,speed,elitesn,bounceError,win) # Creates the game object with the given player and ball
i=0
run = True # This is a boolean variable that will be used to run the game loop
while run:
    t=time.time()
    pygame.time.delay(delay) # This will delay the game the given amount of milliseconds 0.013 seconds or 75fps
    win.fill((23, 24, 33))
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:
            run = False  # Ends the game loop

    game1.run(txt,txt2)
    if i%100==0:
        fps=int(1/(time.time()-t))
    if i%1000==0:
        pf,ef,pg,eg=game1.maxfitness()
        print("player fitness",f'{pf:.2f}',"enemy fitness",f'{ef:.2f}',"player gen",pg,"enemy gen",eg)
        #print("max fitness",game1.maxfitness())
    txt=font.render("fps: "+str(fps),1,(255,255,255)) # Renders the text with the given font and color
    win.blit(txt,(0,0)) # Blits the text on the window
  
    pygame.display.update()
    i+=1

pygame.quit()  # If we exit the loop this will execute and close our game
#endregion
