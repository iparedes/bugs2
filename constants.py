__author__ = 'nacho'


# *************** BUG CONSTANTS ***************
# Index of memory blocks and pointer registers
HEAP=0
STACK=1
CODE=2
# Index of other registers
COMM=3
ENER=4
OFFS=5
DIET=6
SHRE=7


# Number of registers. The three registers are block pointers (stack, code, heap)
NREGS=10
# Number of memory blocks
NBLOCKS=3
# Size of memory blocks
MAX_MEM=100

# Max Energy
ENERGY=100
# Init Energy
INITENERGY=50
# Percentage of energy to share
SHARENERGY=50
# Number of descendants
OFFSPRING=2
# Max size of the mutation
DELTA=3

# Diet Type
HERB=0
CARN=1
# OMNI has to be the last one
OMNI=2


OPS=['RST', # Resets the PC
     'NOP',  # NO Operation
     'PUSH', # PUSH n ; Pushes n into the STACK
     'ST', # ST Reg ; Copy value of register to stack
     'LD', # LD Reg ; Copy value of stack to register
     'STM', # STM Address ; Copy value in stack to heap address
     'LDM', # LDM Address ; Copy value in heap address to stack
     'STP', # STP Reg ; Copy value pointed by register to stack
     'LDP', # LDP Reg ; Copy value in stack to memory address pointed by register
     'MOV', # Sets the COMM register to MOV
     'MOVA', # Sets the COMM register to MOV AWAY
     'SRFD', # Sets the COMM register to SEARCH FOOD. Pushes direction to the stack
     'SREY', # Sets the COMM register to SEARCH ENEMY. Pushes direction to the stack
     'ATK', # Attacks one bug in the same location
     'SHR', # Shares energy with bus in the same location
     'ADD', # Adds the two numbers in the stack. Stores the result in the stack
     'MUL', # Multiplies the two numbers in the stack. Stores the result in the stack
     'DIV', # Pops A, Pops B, Divides A into B. If B is zero does nothing
     'JMF', # JMF n ; Jumps the PC forward n memory addresses
     'JMB', # JMB n ; Jumps the PC backward n memory addresses
     'JZ' , # JZ address ; Jumps to the address in the CODE memory if stack is zero
     'JNZ' , # JNZ address ; Jumps to the address in the CODE memory if stack is not zero
]

# *************** WORLD CONSTANTS ***************

# side of the world
#BOARDSIZE=50
BOARDSIZE=200

# Food per cell
FOODPACK=10

# Index in the sowratevalues of initial sowrate
SOWRATE=4

MUTRATE=1 # percentage
STDDEV=10 # percentage


# *************** GUI CONSTANTS ***************

# Dimensions of the map (<=Boardsize)
TILESWIDTH=50
TILESHEIGHT=50
TILESIZE=10
MAPWIDTH=TILESWIDTH*TILESIZE
MAPHEIGHT=TILESHEIGHT*TILESIZE
MARGIN=4

HSCROLLHEIGHT=20
CONTROLWIDTH=200
CONTROLHEIGHT=MAPHEIGHT+HSCROLLHEIGHT



WINWIDTH=MAPWIDTH+CONTROLWIDTH
WINHEIGHT=MAPHEIGHT+HSCROLLHEIGHT


CONSOLEHEIGHT=150
INFOWIDTH=75

RED=(255,0,0)
ORANGE=(255,165,0)
YELLOW=(255,255,0)
GREEN=(0,205,0)
BROWN=(153,76,0)
WHITE=(255,255,255)
PINK=(250,20,147)
BLACK=(0,0,0)

HERBCOLOR=YELLOW
CARNCOLOR=BLACK
OMNICOLOR=PINK




