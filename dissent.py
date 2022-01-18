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

    #print(program)
    return program, macros

if __name__ == '__main__':
   if len(sys.argv) < 2:
      log('ERROR', 'Filename missing')
      sys.exit(1)

   if '--debug' in sys.argv:
      DEBUG = True

   mem = [0] * 59049
   ignore_ptrs = [] #memory locations that will be modified
   #meaning they cannot be relied on for jumps in loops or persistent data


   program = []
   macros = []

   with open(sys.argv[1],'r') as f:
      instructions = f.readlines()

   program, macros = parse_program(instructions)

   #print(macros)

   c = 0
   d = 0
   a = 0

   queue = []

   for i, instruction in enumerate(program):
       op = instruction[0]
       args = instruction[1]
       if op == 'SET':
          set(mem, args[0], args[1])
          continue
       if op == 'SET_C':
          c = args[0]
          continue
       if op == 'SET_D':
          mem[c] = operators['ASTERISK']
          d = mem[c]
       if op == 'A_OUT':
          mem[c] = operators['LBRACE']
       if op == 'SUB': #This fill method is completely wrong if less than d
          if len(args) == 0:
             args = [d]

          if d != args[0]:
             log('INFO', 'Need to insert instructions for sub')
             log('INFO', 'd=%s, required=%s' % (d, args[0]))
             if args[0] < d:
                while d < args[0]:
                    mem[c] = operators['UNDERSCORE']
                    c += 1
                    d += 1
             else:
                mem[c] = operators['ASTERISK']
                c += 1
                d = 33
                while d < args[0]:
                    mem[c] = operators['UNDERSCORE']
                    d += 1
                    c += 1
          mem[c] = operators['PIPE']

       """
       We could  do like
       d = 42, required = 33,
       while d != 0, noop, then insert ! at the first 0, then * it
       """
       if op == 'SHIFT':
          if len(args) == 0:
             args = [d]

          if d != args[0]:

             log('INFO', 'Need to insert instructions for shift')
             log('INFO', 'd=%s, required=%s' % (d, args[0]))

             while mem[d] != 0 and mem[d] != operators['EXCLAMATION'] or d in ignore_ptrs:
                 mem[c] = operators['UNDERSCORE']
                 c+=1
                 d+=1

             mem[d] = operators['EXCLAMATION']
             mem[c] = operators['ASTERISK']

             d = mem[d]
             d += 1
             c += 1

             while d < args[0]:
                mem[c] = operators['UNDERSCORE']
                d += 1
                c += 1

             ignore_ptrs.append(d)
             mem[c] = operators['RCHEVRON']
          else:
              log('INFO', 'd is equal for shift')
              mem[c] = operators['RCHEVRON']
          queue.append('shift')
          #a = shift(mem[d+1])
       if op == 'GOTO_D':
          if len(args) == 0:
             args = [d]

          if d != args[0]:

             log('INFO', 'Need to insert instructions for GOTO')
             log('INFO', 'd=%s, required=%s' % (d, args[0]))

             #The ignore_ptrs condition isnt exactly right. (May be correct now)
             while mem[d] != 0 and mem[d] != operators['EXCLAMATION'] and d not in ignore_ptrs:
                 mem[c] = operators['UNDERSCORE']
                 c+=1
                 d+=1

             mem[d] = operators['EXCLAMATION']
             mem[c] = operators['ASTERISK']
             #ignore_ptrs.append(d)
             d = mem[d]
             d += 1
             c += 1

             while d < args[0]:
                mem[c] = operators['UNDERSCORE']
                d += 1
                c += 1
             continue
          else:
              log('INFO|GOTO', 'd is already at %s. Ignoring' % args[0])
              continue
              #mem[c] = operators['RCHEVRON']
       if op == 'EXIT':
          mem[c] = operators['EXCLAMATION']
       if op == 'JUMP':
          mem[c] = operators['CARET']
          c = mem[d]
          if mem[c-1] == 0: #Index is off by 1 so fixes a problem with obfscation
             mem[c-1] = operators['UNDERSCORE']
       if op == 'IN':
          mem[c] = operators['RBRACE']
       if op == 'NOOP':
          mem[c] = operators['UNDERSCORE']
       if op == 'IS_D':
          if d != args[0]:
             log('ERROR', 'Validation failed. d=%s not %s' % (d, args[0]))
             sys.exit(1)
          continue
       if op == 'IS_A':
          if a != args[0]:
             log('ERROR|IS_A broken', 'Validation failed. a=%s not %s' % (a, args[0]))
             sys.exit(1)
          continue
       c += 1
       d += 1

       while len(queue) > 0:
          oper = queue.pop()
          if oper == 'shift':
             a = shift(mem[d])


   if '--fill-lines' in sys.argv:
      mem = fill_noops(mem, op=operators['PIPE'])
   elif '--fill-random' in sys.argv:
      mem = fill_random(mem)
   else:
      mem = fill_noops(mem)

   print(mem_to_program(mem))
