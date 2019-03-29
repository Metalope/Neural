import numpy as np
import random
import json
import math

neuron_decay=0.9
maxneuronsperunit=64
maxaxonsperunit=128
maxunits=10

binary_io=True
bitsize=8

runtime=20
testsize=20


class neuron:
    id=-1
    myunit=-1
    active=False

    can_mutate=True

    threshold=999
    amount=0
    decay=neuron_decay

    downstream_axons=[]
    upstream_axons=[]

    def __init__(self,id,threshold):
        self.id=id
        self.threshold=threshold

    def check(self):
        global units
        if self.amount>=self.threshold and self.active:
            for x in self.downstream_axons:
                if x>-1:
                    units[self.myunit].axons[x].fire()
        self.amount=self.amount*self.decay




class axon:
    id=-1
    myunit=-1
    active=False
    fireamount=0

    upstream_neuron=-1
    downstream_neuron=-1


    def __init__(self,id):
        self.id=id

    def fire(self):
        global units
        units[self.myunit].neurons[self.downstream_neuron].amount=units[self.myunit].neurons[self.downstream_neuron].amount+self.fireamount
        #print "AXON "+str(self.id)+" IS FIRING WITH "+str(self.fireamount)
        return True


class unit:
    id=-1
    active=False
    active_neurons=0
    active_axons=0

    input_neurons=[]
    output_neurons=[]

    neurons=[neuron(i,999) for i in range(maxneuronsperunit)]
    axons=[axon(i) for i in range(maxaxonsperunit)]

    def __init__(self,id):
        self.id=id

    def add_neuron(self,threshold):
        a=0
        b=-1
        while a<maxneuronsperunit:
            if self.neurons[a].active==False:
                b=a
                self.active_neurons=self.active_neurons+1
                a=maxneuronsperunit
            a=a+1

        self.neurons[b].active=True
        self.neurons[b].myunit=self.id
        self.neurons[b].threshold=threshold
        return b

    def add_n_neurons(self,n,threshold):
        a=0
        while a<n:
            self.add_neuron(threshold)
            a=a+1

    def remove_neuron(self,n):
        if self.neurons[n].active==True:
            self.neurons[n].active=False
            self.neurons[n].amount=0
            self.neurons[n].threshold=999
            self.active_neurons=self.active_neurons-1

    def connect(self,a,b,amount):
        if self.neurons[a].active and self.neurons[b].active:

            c=0
            d=0
            while c<maxaxonsperunit:
                if self.axons[c].active==False:
                   d=c
                   c=maxaxonsperunit
                c=c+1

            self.neurons[a].downstream_axons.append(d)
            self.neurons[b].upstream_axons.append(d)
            self.axons[d].active=True
            self.axons[d].fireamount=amount
            self.axons[d].myunit=self.id
            self.axons[d].downstream_neuron=b
            self.axons[d].upstream_neuron=a
            return True

        else:
            return False

    def cycle(self,inputs):
        a=0
        outputs=[]

        #RESET ALL NEURONS BETWEEN CYCLES
        for x in self.neurons:
            x.amount=0

        while a<runtime:
            b=0

            c=0
            while c<len(self.input_neurons) and c<len(inputs):
                self.neurons[self.input_neurons[c]].amount=inputs[c]
                c=c+1


            while b<maxneuronsperunit:
                if self.neurons[b].active:
                    self.neurons[b].check()
                b=b+1
            #print "RUN CYCLE "+str(a)
            a=a+1


    def print_neurons(self):
        a=0
        while a<maxneuronsperunit:
            if self.neurons[a].active:
                print "NEURON "+str(a)+"   AMT: "+str(self.neurons[a].amount)+" / "+str(self.neurons[a].threshold)
            a=a+1
        print "INPUTS"
        for x in self.input_neurons:
            print str(x)
        print ""
        print "OUTPUTS"
        for y in self.output_neurons:
            print str(y)

    def designate_io(self,ins,outs):
        a=0
        b=0
        while b<ins and a<maxneuronsperunit:
            if self.neurons[a].active:
                self.neurons[a].can_mutate=False
                self.neurons[a].decay=1

                if binary_io:
                    self.neurons[a].threshold=1 #IO are BINARY

                self.input_neurons.append(a)
                b=b+1
            a=a+1
        c=0
        d=a
        while c<outs and d<maxneuronsperunit:
            if self.neurons[d].active:
                self.neurons[d].can_mutate=False
                self.neurons[d].decay=1
                if binary_io:
                    self.neurons[d].threshold=1
                self.output_neurons.append(d)
                c=c+1
            d=d+1
        if c==ins and b==outs:
            return True
        else:
            return False

    def remove_axon(self,n):
        if self.axons[n].active:
            self.axons[n].active=False
            self.axons[n].id=-1
            self.axons[n].fireamount=0

            u=self.axons[n].upstream_neuron
            d=self.axons[n].downstream_neuron
            self.axons[n].upstream_neuron=-1
            self.axons[n].downstream_neuron=-1

            if self.neurons[u].active:
                a=0
                while a<len(self.neurons[u].downstream_axons):
                    if self.neurons[u].downstream_axons[a]==n:
                        self.neurons[u].downstream_axons[a]=-1
                    a=a+1

            if self.neurons[d].active:
                b=0
                while b<len(self.neurons[d].upstream_axons):
                    if self.neurons[d].upstream_axons[b]==n:
                        self.neurons[d].upstream_axons[b]=-1
                    b=b+1

    def change_axon_destination(self,a,d):
        if self.axons[a].active:
            b=self.axons[a].downstream_neuron
            h=0
            while h<len(self.neurons[b].upstream_axons):
                if self.neurons[b].upstream_axons[h]==a:
                    self.neurons[b].upstream_axons[h]=-1

                h=h+1
            self.neurons[b].upstream_axons.append(a)
            self.axons[a].downstream_neuron=d

    def change_axon_source(self,a,s):
        if self.axons[a].active:
            b=self.axons[a].upstream_neuron
            h=0
            while h<len(self.neurons[b].downstream_axons):
                if self.neurons[b].downstream_axons[h]==a:
                    self.neurons[b].downstream_axons[h]=-1
                h=h+1
            self.axons[a].upstream_neuron=s
            self.neurons[b].downstream_axons.append(a)


    def change_threshold(self,n,r):
        if self.neurons[n].active:
            self.neurons[n].threshold=r
            return True
        else:
            return False

    def change_fireamount(self,a,r):
        if self.axons[a].active:
            self.axons[a].fireamount=r
            return True
        else:
            return False

    def change_decay(self,n,r):
        if self.neurons[n].active:
            self.neurons[n].decay=r
            return True
        else:
            return False

    def mutate(self):
        choice=random.randint(0,100)
        #print choice

        if choice<10:  #add neuron
            self.add_neuron(1)

        elif choice<20:  # remove neuron
            ok=True
            found=False
            a=0
            while ok:
                if self.neurons[a].active:
                   ok=False
                   found=True
                elif a==maxneuronsperunit:
                    ok=False
                a=a+1

            if found:
                self.remove_neuron(a)
                #print "removed "+str(a)

        elif choice<30: #add connection
            ok=True
            fireamount=random.randint(0,4)
            fro=-1
            to=-1
            a=0
            while ok and a<maxneuronsperunit:
                f=random.randint(0,maxneuronsperunit-1)
                if self.neurons[f].active:
                   fro=f
                   ok=False
                a=a+1
            ok=True
            b=0
            while ok and b<maxneuronsperunit:
                t=random.randint(0,maxneuronsperunit-1)
                if self.neurons[t].active:
                    to=t
                    ok=False
                b=b+1
            if to>-1 and fro > -1:
                self.connect(fro,to,fireamount)
                #print "connected "+str(fro)+" to "+str(to)+" for "+str(fireamount)

        elif choice<40:  #remove connection
            ok=True
            a=0
            while ok:
                h=random.randint(0,maxaxonsperunit-1)
                if self.axons[h].active:
                   ok=False
                   #self.remove_axon(h)
                 #  print "removed "+str(a)
                a=a+1
                if a>1000:
                    ok=False

        elif choice<50: #change threshold   WORKS
            ok=True
            changeamt=(random.random()-0.5)*2
            while ok:
                a=random.randint(0,maxneuronsperunit-1)
                if self.neurons[a].active:
                    self.neurons[a].threshold=self.neurons[a].threshold+changeamt
                 #   print "changed threshold for "+str(a)+ " by "+str(changeamt)
                    ok=False
                a=a+1
        elif choice<60: #change fireamount
            ok=True
            a=0
            while ok and a<len(self.axons):
                changeamt=(random.randint(-5,5))/10
                if self.axons[a].active:
                    ok=False
                    self.axons[a].fireamount=self.axons[a].fireamount+changeamt
                #    print "changed fireamount "+str(a)+" by "+str(changeamt)
                a=a+1

        elif choice<70: # change axon source
            a=0
            b=0
            kk=True
            while kk:
                towhere=random.randint(0,maxneuronsperunit-1)
                if self.neurons[towhere].active:
                    kk=False
                b=b+1
                if b>100:
                    kk=False
            ok=True
            if b>100:
                ok=False

            while ok and a<len(self.axons):
                if self.axons[a].active:
                    self.change_axon_source(a,towhere)
                #    print "changed axon source to "+str(towhere)+" for "+str(a)
                    ok=False
                a=a+1

        elif choice<80: # change axon destination
            a=0
            b=0
            kk=True
            while kk:
                towhere=random.randint(0,maxneuronsperunit-1)
                if self.neurons[towhere].active:
                    kk=False
                b=b+1
                if b>100:
                    kk=False
            ok=True
            if b>100:
                ok=False

            while ok and a<len(self.axons):
                if self.axons[a].active:
                    self.change_axon_destination(a,towhere)
                  #  print "changed axon destination to "+str(towhere)+" for "+str(a)
                    ok=False
                a=a+1

        elif choice<90: # change decay
            ok=True
            a=0
            changeamt=(random.random()-0.5)
            while ok and a<maxneuronsperunit:
                if self.neurons[a].active:
                    self.neurons[a].decay=self.neurons[a].decay+changeamt
                   # print "changed decay for "+str(a)+ " by "+str(changeamt)
                    ok=False
                a=a+1

    def mutate_n(self,n):
        a=0
        while a<n:
            self.mutate()
            a=a+1

    def read_outputs(self):
        #OUTPUTS IN BINARY
        outputs=[]
        a=0
        while a<len(self.output_neurons):
            n=self.output_neurons[a]
            if self.neurons[n].active and self.neurons[n].amount>=self.neurons[n].threshold:
                outputs.append(1)
            else:
                outputs.append(0)
            a=a+1
        return outputs

    def read_inputs(self):
        inputs=[]
        a=0
        while a<len(self.input_neurons):
            n=self.input_neurons[a]
            if self.neurons[n].active:
                inputs.append(self.neurons[n].amount)
            else:
                inputs.append(0)
            a=a+1
        return inputs



class system:
    units=[unit(i) for i in range(maxunits)]

    def init(self, n_units):
        for i in range(0,n_units):
            self.units[i].add_n_neurons(maxneuronsperunit,1)
            self.units[i].designate_io(bitsize*2,bitsize)
            self.units[i].active=True

    def save(self):
        global data
        a=0
        data=[] #each element is a unit
        while a<maxunits:
            if self.units[a].active:

                r={'active_neurons':self.units[a].active_neurons,'active_axons':self.units[a].active_axons,'input_neurons':self.units[a].input_neurons,'output_neurons':self.units[a].output_neurons}
                r['neurons']=[]
                r['unitid']=a
                #save neuron data in each active unit
                b=0
                while b<maxneuronsperunit:
                    if self.units[a].neurons[b].active:

                        d={'can_mutate':self.units[a].neurons[b].can_mutate,'threshold':self.units[a].neurons[b].threshold,'currentamount':self.units[a].neurons[b].amount,'decay':self.units[a].neurons[b].decay}
                        d['downstream_axons']=self.units[a].neurons[b].downstream_axons
                        d['upstream_axons']=self.units[a].neurons[b].upstream_axons
                        d['neuronid']=b

                        r['neurons'].append(d)

                    b=b+1

                b=0

                r['axons']=[]

                while b<maxaxonsperunit:
                    if self.units[a].axons[b].active:
                        g={'fire_amount':self.units[a].axons[b].fireamount,'axonid':b,'upstream_neuron':self.units[a].axons[b].upstream_neuron,'downstream_neuron':self.units[a].axons[b].downstream_neuron}

                        r['axons'].append(g)

                    b=b+1

                data.append(r)

            a=a+1

        v=json.dumps(data)

        file=open('config.txt','wb')
        file.write(v)
        file.close()

    def load(self):
        global data,units
        file=open('config.txt')
        f=file.read()

        data=json.loads(f)

        a=0
        while a<len(data):
            r=data[a]['unitid']
            self.units[r].active_axons=data[a]['active_axons']
            self.units[r].active_neurons=data[a]['active_neurons']
            self.units[r].input_neurons=data[a]['input_neurons']
            self.units[r].output_neurons=data[a]['output_neurons']

            #load neuron data
            n=0
            while n<len(data[a]['neurons']):

                neuronid=data[a]['neurons'][n]['neuronid']
                self.units[r].neurons[neuronid].threshold=data[a]['neurons'][n]['threshold']
                self.units[r].neurons[neuronid].can_mutate=data[a]['neurons'][n]['can_mutate']
                self.units[r].neurons[neuronid].amount=data[a]['neurons'][n]['currentamount']
                self.units[r].neurons[neuronid].decay=data[a]['neurons'][n]['decay']
                self.units[r].neurons[neuronid].downstream_axons=data[a]['neurons'][n]['downstream_axons']
                self.units[r].neurons[neuronid].upstream_axons=data[a]['neurons'][n]['upstream_axons']
                self.units[r].neurons[neuronid].active=True
                n=n+1


            #load axon data
            g=0
            while g<len(data[a]['axons']):
                axon=data[a]['axons'][g]
                axonid=axon['axonid']

                self.units[r].axons[axonid].fire_amount=axon['fire_amount']
                self.units[r].axons[axonid].upstream_neuron=axon['upstream_neuron']
                self.units[r].axons[axonid].downstream_neuron=axon['downstream_neuron']
                self.units[r].axons[axonid].active=True
                g=g+1

            a=a+1

