import sys
from random import choice

"""
Very rough implementation. I will make it elegant later
"""

operators = { 'EXCLAMATION' : ord('!'),
              'ASTERISK': ord('*'),
              'UNDERSCORE': ord('_'),
              'PIPE': ord('|'),
              'RCHEVRON': ord('>'),
              'CARET': ord('^'),
              'LBRACE': ord('{'),
              'RBRACE': ord('}') }

DEBUG = False

class Assembler():
    def __init__(self):
        self.a = 0
        self.d = 0
        self.c = 0
        self.mem = [0] * 59049
        self.ignore_ptrs = [] #Rename this, memory locations that will be modified
        #meaning they cannot be relied on for jumps in loops or persistent data
        self.queue = [] #Queue of instructions for partial execution (not done)

    def goto(self, loc):
        if self.d != loc:

           log('INFO', 'Need to insert instructions for GOTO')
           log('INFO', 'd=%s, required=%s' % (self.d, loc))

           #The ignore_ptrs condition isnt exactly right. (May be correct now)
           #Why does "or d in ignore_ptrs" wrk and not "and not d in ignore_ptrs"
           #while self.d in self.ignore_ptrs:
           #while (self.mem[self.d] != 0) or self.d in self.ignore_ptrs or (self.mem[self.d] != operators['EXCLAMATION']):
           while (self.mem[self.d] != 0 and self.mem[self.d] != operators['EXCLAMATION']) or self.d in self.ignore_ptrs:
               #print(self.c, self.mem[self.d], self.ignore_ptrs)
               #self.mem[self.c] = operators['UNDERSCORE']
               self.c+=1
               self.d+=1

           self.mem[self.d] = operators['EXCLAMATION']
           self.mem[self.c] = operators['ASTERISK']
           #ignore_ptrs.append(d)
           self.d = self.mem[self.d]
           self.d += 1
           self.c += 1

           while self.d < loc:
              self.mem[self.c] = operators['UNDERSCORE']
              self.d += 1
              self.c += 1
        else:
            log('INFO|GOTO', 'd is already at %s. Ignoring' % loc)

    def lookup(self, ptr):
        """If a pointer adjustment needs to be made"""
        return ptr

    def assemble(self, program):

       for i, instruction in enumerate(program):
           op = instruction[0]
           args = instruction[1]
           original_d = self.d

           if op == 'SET':
              self.mem[args[0]] = args[1]
              continue
           if op == 'SET_C':
              self.c = args[0]
              continue
           if op == 'SET_D':
              self.mem[self.c] = operators['ASTERISK']
              self.d = self.mem[self.d] #not self.mem[self.c]
           if op == 'A_OUT':
              self.mem[self.c] = operators['LBRACE']
           if op == 'SUB': #This fill method is completely wrong if less than d
              if len(args) == 0:
                 args = [self.d]
              else:
                 args[0] = self.lookup(args[0])
              self.goto(args[0]) #this should be good
              self.ignore_ptrs.append(self.d)
              self.mem[self.c] = operators['PIPE']

           if op == 'SHIFT':
              if len(args) == 0:
                 args = [self.d]
              else:
                 args[0] = self.lookup(args[0])
              self.goto(args[0]) #This should be good
              self.ignore_ptrs.append(args[0]) #self.d
              self.mem[self.c] = operators['RCHEVRON']
              self.queue.append('shift')
              #a = shift(mem[d+1])
           if op == 'ISWAP': #Inefficent way to put d into a, shift 10 times
              if len(args) == 0:
                 args = [self.d]
              else:
                 args[0] = self.lookup(args[0])
              for _ in range(10):
                  self.goto(args[0]) #This should be good
                  self.ignore_ptrs.append(self.d)
                  self.mem[self.c] = operators['RCHEVRON']
                  self.queue.append('shift')
                  self.c += 1
                  self.d += 1
              continue
           if op == 'GOTO_D':
              if len(args) == 0:
                 args = [self.d]
              else:
                 args[0] = self.lookup(args[0])
              self.goto(args[0])
              continue
           if op == 'EXIT':
              self.mem[self.c] = operators['EXCLAMATION']
           if op == 'JUMP':
              self.mem[self.c] = operators['CARET']
              #self.c += 1
              #self.d += 1 #This really is supposed to be increased. big bug
              self.c = self.mem[self.d]
              #if self.mem[self.c-1] == 0: #Index is off by 1 so fixes a problem with obfscation
              #   self.mem[self.c-1] = operators['UNDERSCORE'] #This may be fake news actually
           if op == 'IN':
              self.mem[self.c] = operators['RBRACE']
           if op == 'NOOP':
              self.mem[self.c] = operators['UNDERSCORE']
           if op == 'IS_D':
              if self.lookup(self.d) != self.lookup(args[0]):
                 log('ERROR', 'Validation failed. d=%s not %s' % (self.lookup(self.d), args[0]))
                 sys.exit(1)
              continue
           if op == 'IS_C':
              if self.lookup(self.c) != self.lookup(args[0]):
                 log('ERROR', 'Validation failed. c=%s not %s' % (self.lookup(self.c), args[0]))
                 sys.exit(1)
              continue
           if op == 'IS_A':
              if self.a != args[0]:
                 log('ERROR', 'IS_A broken!. Validation failed. a=%s not %s' % (self.a, args[0]))
                 sys.exit(1)
              continue

           self.c += 1
           self.d += 1

           while len(self.queue) > 0:
              oper = self.queue.pop()
              if oper == 'shift':
                 self.a = shift(self.mem[self.d])
       return self.mem

def log(info, msg):
    if DEBUG or info == 'ERROR':
       print('[%s]: %s' % (info, msg))

def subtract(a, d):
  """ | """
  i = ( a // 1 % 3 - d // 1 % 3 + 3 ) % 3 * 1;
  i += ( a // 3 % 3 - d // 3 % 3 + 3 ) % 3 * 3;
  i += ( a // 9 % 3 - d // 9 % 3 + 3 ) % 3 * 9;
  i += ( a // 27 % 3 - d // 27 % 3 + 3 ) % 3 * 27;
  i += ( a // 81 % 3 - d // 81 % 3 + 3 ) % 3 * 81;
  i += ( a // 243 % 3 - d // 243 % 3 + 3 ) % 3 * 243;
  i += ( a // 729 % 3 - d // 729 % 3 + 3 ) % 3 * 729;
  i += ( a // 2187 % 3 - d // 2187 % 3 + 3 ) % 3 * 2187;
  i += ( a // 6561 % 3 - d // 6561 % 3 + 3 ) % 3 * 6561;
  i += ( a // 19683 % 3 - d // 19683 % 3 + 3 ) % 3 * 19683;
  return i

def shift(num):
    """ > """
    return num // 3 + num % 3 * 19683

def set(mem, idx, value):
    mem[idx] = value
    #self.ignore_ptrs.append(idx)

def find_program_end(mem):
    i = len(mem) - 1
    end = None
    while i > 0:
       op = mem[i]
       if op != 0:
          end = i
          break
       i -= 1

    return end

def fill_noops(mem, op=operators['UNDERSCORE']):
    end = find_program_end(mem)
    if end:
       i = 0
       while i < len(mem[0:end]):
          if mem[i] == 0:
             mem[i] = op
          i += 1
    else:
       log('ERROR', 'Could not fill noops. Program is invalid')
    return mem

def fill_random(mem):
    end = find_program_end(mem)
    if end:
       i = 0
       while i < len(mem[0:end]):
          if mem[i] == 0:
             mem[i] = choice(list(operators.values()))
          i += 1
    else:
       log('ERROR', 'Could not fill noops. Invalid program')
    return mem

def mem_to_program(mem):
    end = find_program_end(mem)
    program = ''
    i = 0
    while i < end+1:
       program += chr(mem[i])
       i += 1
    return program

def parse_program(instructions):
    program = []
    macros = {}
    macro_instructions = []
    macro_name = None
    skipping = False
    for instruction in instructions:
        instruction = instruction.strip().split(';')[0]
        op = instruction.split(' ',1)[0]

        if skipping and op == 'END_MACRO':
           #macro ended
           skipping = False
           macros[macro_name] = parse_program(macro_instructions)[0]
           macro_instructions = []
           continue

        if skipping:
           macro_instructions.append(instruction)
           continue

        if not op: #empty line
           continue

        if op == 'MACRO':
           skipping = True
           macro_name = instruction.split(' ')[1]
           #print('Macro found', macro_name)
           continue

        if op in macros:
           for inst in macros[op]:
             program.append(inst)
           continue

        args = instruction.split(op)[1].split(',')
        args = [arg.strip() for arg in args if arg.strip()]
        for i, arg in enumerate(args):
            if arg in operators:
               args[i] = operators[arg]
            elif arg.isdigit():
               args[i] = int(arg)
        program.append((op, args))

    return program, macros

if __name__ == '__main__':
   if len(sys.argv) < 2:
      log('ERROR', 'Filename missing')
      sys.exit(1)

   if '--debug' in sys.argv:
      DEBUG = True

   program = []
   macros = []

   with open(sys.argv[1],'r') as f:
      instructions = f.readlines()

   program, macros = parse_program(instructions)

   #print(macros)

   assembler = Assembler()

   mem = assembler.assemble(program)

   if '--fill-lines' in sys.argv:
      mem = fill_noops(mem, op=operators['PIPE'])
   elif '--fill-random' in sys.argv:
      mem = fill_random(mem)
   else:
      mem = fill_noops(mem)

   print(mem_to_program(mem))
