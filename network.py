import random
import math
import time


class neural_network:
    def __init__(self,inp,h,o):#initialise network
        self.inputs=[1 for _ in range(inp)]
        self.hidden=[[[1,0] for _ in range(h[i])] for i in range(len(h))]#neuron value,bias
        self.outputs=[[1,0] for _ in range(o) ]
        self.weights=[]

        self.weights.append([[random.uniform(0,1) for i in range(h[0])] for _ in range(inp)])

        for i in range(len(h)-1):
            self.weights.append([[random.uniform(0,1) for n in range(h[i+1])] for w in range(h[i])])

        self.weights.append([[random.uniform(0,1) for i in range(o)] for _ in range(h[-1])]) 
       
        #layer indexing is [layer][source neuron][target neuron]
       
    def sigmoid(self,n):#sigmoid activation
        return 1/(1+2.72**(-n))
    def sigmoid_derivative(self,n):#only use for values that have already been passed through sigmoid
        return n*(1-n)
    def tanh(self,n):
        e=2.72
        ex=e**n
        exn=1/ex
        return (ex-exn)/(ex+exn)
    def tanhd(self,n):#only use for values that have already been passed through tanh
        return 1-n**2
    def relu(self,n):
        return max(0,n)
    def relud(self,n):
        return 1 if n>0 else 0
    def mse(self,predval,realval):#mean squared error
        return (realval-predval)**2
    def mse_derivative(self,predval,realval):
        return 2*(predval-realval)
   
    def forward(self,inputvalues):#forward propagation- calculates outputs
        if len(inputvalues)!=len(self.inputs):
            raise ValueError("input size doesnt match input network size")
        self.inputs=inputvalues
        for h in range(len(self.hidden[0])):#iterating through neurons in hidden layer 0
            nsum=0#sum of all input neurons * weight connected to it
            for n in range(len(self.inputs)):#iterating through input neurons
                nsum+=self.inputs[n]*self.weights[0][n][h]
            nsum=self.tanh(nsum+self.hidden[0][h][1])#adds the bias then applies sigmoid activation
            self.hidden[0][h][0]=nsum
        if len(self.hidden)!=1:
            for layer in range(len(self.hidden)-1):
                for h in range(len(self.hidden[layer+1])):
                    nsum=0
                    for n in range(len(self.hidden[layer])):
                        nsum+=self.hidden[layer][n][0]*self.weights[layer+1][n][h]
                    nsum=self.tanh(nsum+self.hidden[layer+1][h][1])
                    self.hidden[layer+1][h][0]=nsum
        output_values=[0 for i in range(len(self.outputs))]
        for o in range(len(self.outputs)):#calculate output layer
            nsum=0
            for n in range(len(self.hidden[-1])):
                nsum+=self.hidden[-1][n][0]*self.weights[-1][n][o]
            nsum=nsum+self.outputs[o][1]
            self.outputs[o][0]=nsum
            output_values[o]=nsum
        return output_values
    
    def backward(self,target_values):#backpropagation one pass
        learning_rate=0.1#how quickly it converges
        inputs=self.inputs
        pred_values=self.forward(inputs)
        values_length=len(pred_values)
        if max(pred_values)>20 or min(pred_values)<-20:
            raise ValueError("values too big")
        if len(target_values)!=values_length:
            raise ValueError("target value size doesnt match predicted values size")
        errors=[self.mse(pred_values[i],target_values[i]) for i in range(values_length)]
#_______________________________________________________________________________________________________________________
        def calculategradients():
            #this is only temporary for last layer only will change soon
            error_derivatives=[self.mse_derivative(pred_values[i],target_values[i]) for i in range(values_length)]
           
            #partial derivative with respect to weights in last layer
            llayer_dx=[[0 for _ in range(len(self.outputs))]for _ in range(len(self.hidden[-1]))]
            
            #calculate partial derivatives for weights in last layer
            for i in range(len(self.hidden[-1])):
                for j in range(len(self.outputs)):
                    #indexing [hiddenneuron][output]
                    llayer_dx[i][j]=error_derivatives[j]*self.hidden[-1][i][0]
            #calculate partial derivatives for weights in hidden layers
            lweight_dx = [[[0 for _ in range(len(self.hidden[l]))]\
               for _ in range(len(self.inputs if l == 0 else self.hidden[l-1]))] for l in range(len(self.hidden))]
            lbias_dx=[[0 for _ in range(len(self.hidden[l]))]for l in range(len(self.hidden))]
            for layer in range(0,len(self.hidden)):#loop through hidden layers
                targetlayer=len(self.hidden)-layer-1#target layer(iterating backwards)
                tlayer=self.hidden[targetlayer]
                inputlayer=self.hidden[targetlayer-1] if targetlayer!=0 else self.inputs
                newerror_derivatives=[0 for _ in range(len(self.hidden[targetlayer]))]#initiate new error derivatives
                for tar in range(len(self.hidden[targetlayer])):
                    #sum of all error derivatives*weights in the layer before it(propogating backwards)
                    newerror_derivatives[tar]=sum(error_derivatives[i]*self.weights[targetlayer+1][tar][i]\
                       for i in range(len(error_derivatives)))
                    #the weights target neuron
                    targetval=self.hidden[targetlayer][tar][0]
                    #the gradient of the error with respect to the target neuron
                    grad=self.tanhd(targetval)*newerror_derivatives[tar]
                    biasgrad=grad
                    lbias_dx[targetlayer][tar]=biasgrad
                    for inp in range(len(inputlayer)):
                        #source value of the weight
                        sourceval=inputlayer[inp] if targetlayer==0 else inputlayer[inp][0]
                        #gradient of the error with respect to the weight
                        weightgrad=grad*sourceval
                     
                        lweight_dx[targetlayer][inp][tar]=weightgrad
                error_derivatives=newerror_derivatives

            return llayer_dx,error_derivatives,lweight_dx,lbias_dx
#_______________________________________________________________________________________________________________________
        gradl,gradbl,gradwh,gradbh=calculategradients()
        #perform one backwards pass on every weight in the last layer 
        for i in range(len(self.hidden[-1])):
            for j in range(len(self.outputs)):
                self.weights[-1][i][j]-=gradl[i][j]*learning_rate
        #perform one backwards pass on every bias in the last layer
        for o in range(len(self.outputs)):self.outputs[o][1]-=gradbl[o]*learning_rate
        #perform one backwards pass on every weight in the hidden layers
        for l in range(len(self.weights)-1):
            for i in range(len(self.weights[l])):
                for j in range(len(self.weights[l][i])):
                    self.weights[l][i][j]-=gradwh[l][i][j]*learning_rate
        #perform one backwards pass on every bias in the hidden layers
        for b in range(len(self.hidden)):
            for i in range(len(self.hidden[b])):
                self.hidden[b][i][1]-=gradbh[b][i]*learning_rate
    def modifyby_evolution(self,mutation_rate):
        for w in range(len(self.weights)):
            for i in range(len(self.weights[w])):
                for j in range(len(self.weights[w][i])):
                    if random.uniform(0,1)<mutation_rate:
                        self.weights[w][i][j]+=random.uniform(-1,1)*0.1
        for h in range(len(self.hidden)):
            for i in range(len(self.hidden[h])):
                if random.uniform(0,1)<mutation_rate:
                    self.hidden[h][i][1]+=random.uniform(-1,1)*0.1
        for o in range(len(self.outputs)):
            if random.uniform(0,1)<mutation_rate:
                self.outputs[o][1]+=random.uniform(-1,1)*0.1
