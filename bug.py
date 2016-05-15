__author__ = 'nacho'

import copy
import logging
import numpy
import pickle
from constants import *

logger=logging.getLogger('bugs')


class bug:
    def __init__(self,id=''):
        self.id=id
        self.age=0
        self._memory=[None]*NBLOCKS
        # Init the memory blocks
        self._memory[STACK]=[0]*MAX_MEM
        self._memory[CODE]=[0]*MAX_MEM
        self._memory[HEAP]=[0]*MAX_MEM
        # Init the registers
        self._registers=[0]*NREGS
        # 1-Stack pointer. Points to the head (top empty position) of the stack
        # 2-Program pointer. Points to the next instruction to be executed (or parameter to be read)
        self._registers[ENER]=INITENERGY
        self._registers[MATU]=ENERGY
        self._registers[OFFS]=OFFSPRING
        self._registers[DIET]=HERB
        self._registers[SHRE]=SHARENERGY

        self.last_executed=""



    def copy(self,energy):
        """
        :param energy:
        :return: An exact copy of the parent with the energy set
        """
        b=copy.deepcopy(self)
        self._registers[ENER]=energy
        b._registers[ENER]=energy
        return b

    def offspring(self):
        """
        Creates as much identical copies as in the OFFS register
        :return: A list with the offspring
        """
        l=[]
        n=self._registers[OFFS]
        logger.debug(self.id+' offspringing '+str(n))
        if n>0:
            energy=self._registers[ENER]/(n+1)
            for i in range(0,n):
                a=self.copy(energy)
                a.age=0
                l.append(a)
            self._registers[ENER]=energy
        # Because offspringing also has a
        self._registers[ENER]-=1
        return l

    def _incPC(self,value=1):
        """
        PC points to the next instruction to execute.
        Increments the PC in value. If reaches MAX_MEM goes to the beginning
        :param value:
        :return:
        """
        pc=self._registers[CODE]
        pc+=value
        if pc>=MAX_MEM:
            pc-=MAX_MEM
        elif pc<0:
            pc+=MAX_MEM
        self._registers[CODE]=pc

    def PC(self):
        """

        :return: the value of the CODE register (Program Counter)
        """
        pc=self._registers[CODE]
        if pc<0:
            pc+=MAX_MEM
            self._registers[CODE]=pc
        elif pc>=MAX_MEM:
            pc = pc % MAX_MEM
            self._registers[CODE]=pc
        return pc

    def _push(self,S,value):
        """
        Pushes value (int) in the stack S

        :return:
        """
        id=self._registers[S]
        if id<0:
            id+=MAX_MEM
        elif id>=MAX_MEM:
            id-=MAX_MEM
        self._memory[S][id]=value
        id+=1
        if id>=MAX_MEM:
            id-=MAX_MEM
        self._registers[S]=id

    def push(self,value):
        """
        Pushes value to the stack S
        :param value: value to push
        :return:
        """
        self._push(STACK,value)

    def _pop(self,S):
        """
        Pops the value from the stack S
        :return:
        The popped value (int)
        """
        id=self._registers[S]
        if id<=0:
            id+=MAX_MEM
        elif id>MAX_MEM:
            id-=MAX_MEM
        id-=1
        v=self._memory[S][id]
        self._registers[S]=id

        return v

    def pop(self):
        """
        Pops the value on the top of the general stack
        :return: the value
        """
        v=self._pop(STACK)
        return v


    def _set(self,address,value):
        """
        Sets a memory address to the given value
        :param address: The memory address.
        The memory block index is address/MAX_MEM. The cell index is address%MAX_MEM
        :param value: The value to set (int)
        :return:
        """
        (block,cell)=self._decode_address(address)
        self._memory[block][cell]=value


    def _get(self,address):
        """
        Gets the value in a memory address
        :param address: The memory address to get.
        The memory block index is address/MAX_MEM. The cell index is address%MAX_MEM
        :return: The value (int)
        """
        (block,cell)=self._decode_address(address)
        v=self._memory[block][cell]
        return v

    def _getp(self,address):
        """
        Gets the value of the memory address stored in address (pointer)
        :param address:
        :return: The value of the memory address pointed by the content of address
        """
        (block,cell)=self._decode_address(address)
        p=self._memory[block][cell]
        (block,cell)=self._decode_address(p)
        v=self._memory[block][cell]
        return v


    def _dump_memory(self,index):
        """
        Dumps to stdout a memory block
        :param index: The index of the memory block
        :return:
        """
        cont=0
        while cont<MAX_MEM:
            v=self._memory[index][cont]
            if v!=None:
                print cont,': ',self._memory[index][cont]
            cont+=1


    def _decode_address(self,address):
        """
        Decodes a memory address in block_index and cell
        :param address:
        :return:
        """
        if address<(NBLOCKS*MAX_MEM):
            return (address/MAX_MEM,address%MAX_MEM)
        else:
            return 0


    def _opcode_NOP(self):
        """
        Does nothing
        :return:
        """
        self.last_executed="NOP"
        pass

    def _opcode_PUSH(self):
        """
        Microinstructions to execute PUSH code:
        :return:
        """
        pc=self.PC()
        v=self._memory[CODE][pc]
        self._incPC()
        self._push(STACK,v)
        self.last_executed="PUSH "+str(v)

    def _opcode_JMF(self):
        pc=self.PC()
        v=self._memory[CODE][pc]
        self._incPC(v)
        self.last_executed="JFM "+str(v)

    def _opcode_JMB(self):
        pc=self.PC()
        v=self._memory[CODE][pc]
        self._incPC(-v)
        self.last_executed="JMB "+str(v)

    def _opcode_JZ(self):
        pc=self.PC()
        address=self._memory[CODE][pc]
        self._incPC()
        v=self._pop(STACK)
        if v==0:
            address = address % MAX_MEM
            self._memory[CODE][pc]=address
        self.last_executed="JZ "+str(v)

    def _opcode_JNZ(self):
        pc=self.PC()
        address=self._memory[CODE][pc]
        self._incPC()
        v=self._pop(STACK)
        if v!=0:
            address = address % MAX_MEM
            self._memory[CODE][pc]=address
        self.last_executed="JNZ "+str(v)

    def _opcode_RST(self):
        self._registers[CODE]=0
        self.last_executed="RST"

    def _opcode_MOV(self):
        self._registers[COMM]=OPS.index('MOV')
        self.last_executed="MOV"

    def _opcode_MOVA(self):
        self._registers[COMM]=OPS.index('MOVA')
        self.last_executed="MOVA"

    def _opcode_SRFD(self):
        self._registers[COMM]=OPS.index('SRFD')
        self.last_executed="SRFD"

    def _opcode_SRBG(self):
        self._registers[COMM]=OPS.index('SRBG')
        self.last_executed="SRBG"

    def _opcode_ATK(self):
        self._registers[COMM]=OPS.index('ATK')
        self.last_executed="ATK"

    def _opcode_SHR(self):
        self._registers[SHRE]=OPS.index('SHR')
        self.last_executed="SHR"

    def _opcode_ADD(self):
        v1=self._pop(STACK)
        v2=self._pop(STACK)
        self._push(STACK,v1+v2)
        self.last_executed="ADD"

    def _opcode_MUL(self):
        v1=self._pop(STACK)
        v2=self._pop(STACK)
        self._push(STACK,v1*v2)
        self.last_executed="MUL"

    def _opcode_DIV(self):
        v1=self._pop(STACK)
        v2=self._pop(STACK)
        if v2!=0:
            self._push(STACK,v1/v2)
        self.last_executed="DIV"

    def _opcode_ST(self):
        """
        Reads a register. Normalizes the register.
        Pushes the value of register to the stack.
        :return:
        """
        pc=self.PC()
        reg=self._memory[CODE][pc]
        self._incPC()
        reg = reg % NREGS
        v=self._registers[reg]
        self._push(STACK,v)
        self.last_executed="ST "+str(v)

    def _opcode_LD(self):
        """
        Reads a register. Normalizes the register.
        Loads in the register the head of the stack
        :return:
        """
        pc=self.PC()
        reg=self._memory[CODE][pc]
        self._incPC()
        reg= reg % NREGS
        v=self._pop(STACK)
        self._registers[reg]=v
        self.last_executed="LD "+str(v)

    def _opcode_STM(self):
        """
        Reads an address of the heap.
        Copy to that address the value in the stack.
        :return:
        """
        pc=self.PC()
        address=self._memory[CODE][pc]
        self._incPC()
        address = address % MAX_MEM
        v=self._memory[HEAP][address]
        self._push(STACK,v)
        self.last_executed="STM "+str(v)

    def _opcode_LDM(self):
        """
        Reads an address of the heap.
        Copy the value in the stack to that address
        :return:
        """
        pc=self.PC()
        address=self._memory[CODE][pc]
        self._incPC()
        address = address % MAX_MEM
        v=self._pop(STACK)
        self._memory[HEAP][address]=v
        self.last_executed="LDM "+str(v)

    def _opcode_STP(self):
        """
        Reads a register. Looks the value in the heap pointed by the register
        Pushes to stack
        :return:
        """
        pc=self.PC()
        reg=self._memory[CODE][pc]
        self._incPC()
        reg= reg % NREGS
        pointer=self._registers[reg]
        pointer = pointer % MAX_MEM
        v=self._memory[HEAP][pointer]
        self._push(STACK,v)
        self.last_executed="STP "+str(v)


    def _opcode_LDP(self):
        """
        Reads a register. Copies the stack to the heap address pointed by register
        :return:
        """
        pc=self.PC()
        reg=self._memory[CODE][pc]
        self._incPC()
        reg= reg % NREGS
        pointer=self._registers[reg]
        pointer = pointer % MAX_MEM
        v=self._pop(STACK)
        self._memory[HEAP][pointer]=v
        self.last_executed="LDP "+str(v)



    def compile(self,list):
        """
        Converts a list representing a program to opcodes and loads it in CODE memory
        :param list: One code or parameter in each position
        :return:
        """
        id=0
        for i in list:
            try:
                v=int(i)
            except:
                try:
                    v=OPS.index(i)
                except:
                    v=OPS.index('NOP')
            self._memory[CODE][id]=v
            id+=1

    def decompile(self):
        """
        Dumps the CODE memory to a readable format
        :return:
        """
        l=[]
        i=0
        while i<MAX_MEM:
            v=self._memory[CODE][i]
            try:
                s=OPS[v]
            except IndexError:
                s='NOP'
            if (s in ('PUSH','JMF','JMB','ST','LD','LDM','STM','LDP','STP','JZ','JNZ')) and (i<(MAX_MEM-1)):
                i+=1
                v=self._memory[CODE][i]
                s=s+' '+str(v)
            l.append(s)
            i+=1
        return l


    def step(self):
        """
        Executes the instruction the PC points to.
        Decreases energy
        :return:
        """
        pc=self.PC()
        op=self._memory[CODE][pc]
        try:
            op=OPS[op]
        except:
            pass
        self._incPC()

        oper={
            'RST':    self._opcode_RST,
            'NOP':    self._opcode_NOP,
            'PUSH':   self._opcode_PUSH,
            'ST':     self._opcode_ST,
            'LD':     self._opcode_LD,
            'STM':    self._opcode_STM,
            'LDM':    self._opcode_LDM,
            'STP':    self._opcode_STP,
            'LDP':    self._opcode_LDP,
            'MOV':    self._opcode_MOV,
            'MOVA':   self._opcode_MOVA,
            'SRFD':   self._opcode_SRFD,
            'SRBG':   self._opcode_SRBG,
            'ATK':    self._opcode_ATK,
            'SHR':    self._opcode_SHR,
            'ADD':    self._opcode_ADD,
            'MUL':    self._opcode_MUL,
            'DIV':    self._opcode_DIV,
            'JMF':    self._opcode_JMF,
            'JMB':    self._opcode_JMB,
            'JZ':     self._opcode_JZ,
            'JNZ':    self._opcode_JNZ,
        }.get(op,self._opcode_NOP)
        oper()
        #self.last_executed=str(op)
        #logger.debug(self.id+'('+str(self._registers[ENER])+') '+str(op))
        logger.debug(self.id+'('+str(self._registers[ENER])+') '+self.last_executed)
        self._registers[ENER]-=1
        # Age is controlled by the world
        #self.age+=1

    def readcomm(self):
        """
        Reads the content of the communications register
        After reading, sets it to zero
        :return: the value of the communications register
        """
        v=self._registers[COMM]
        self._registers[COMM]=0
        return v

    def mutate(self,listmut):
        """
        Modifies a random amount (-delta,delta) a list of memory addresses
        :param listmut: a list of memory addresses to mutate
        :return:
        """
        for i in listmut:
            delta=numpy.random.randint(-DELTA,DELTA+1)
            if i<NREGS:
                # register
                self._registers[i]+=delta
            else:
                i=i-NREGS
                block=i/MAX_MEM
                offset=i%MAX_MEM
                self._memory[block][offset]+=delta


    def dead(self):
        """

        :return: true if the bug has no energy left
        """
        return self._registers[ENER]==0

    def mature(self):
        """
        If the bug's energy is above the max it is mature to procreate
        :return: true if the energy is above the max
        """
        return self._registers[ENER]>=self._registers[MATU]

    def energy(self):
        """

        :return: Bug's current amount of energy
        """
        return self._registers[ENER]

    def sharing_quote(self):
        """
        :return: the energy share quota of the bug
        """
        return self._registers[SHRE]/100

    def feed(self,value):
        """
        Adds value to the bug's energy
        :param value: energy to add
        :return:
        """
        self._registers[ENER]+=value
        if self._registers[ENER]<0:
            self._registers[ENER]=0

    def kill(self):
        """
        Sets the energy of the bug to zero
        :return: the former energy value
        """
        v=self._registers[ENER]
        self._registers[ENER]=0
        return v

    def size(self):
        """

        :return: the bug's total memory addresses including registers
        """
        return (NBLOCKS*MAX_MEM)+NREGS

    def diet(self):
        return self._registers[DIET]

    def dump(self):
        a='Id: '+str(self.id)+'\n'
        a+='Age: '+str(self.age)+'\n'
        a+='=============\n'
        l=self.decompile()
        for i in l:
            a+=i
            a+='\n'
        a+='\n'
        return a

    def save(self,file):
        """
        saves a bug to the file
        :param file:
        :return:
        """
        pickle.dump(self,file)

    def load(self,file):
        """
        Loads a bug from a file
        :param file:
        :return: the bug
        """
        a=pickle.load(file)
        return a




