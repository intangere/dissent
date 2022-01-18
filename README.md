# Dissent

An intermediate language that outputs valid Dis code.  

### What is Dis?
Dis is a mitigated variant of Malbolge. Consequently and sadly, the interest in Dis by the community seems to be low.

### Features
- Shift (>) and Subtract (|) automatically calculates, moves internal d pointer, and inserts the instructions to set the d pointer where you need it
- JUMP (^) has an internal code pointer so placeholder values are no longer needed
- Special operators to make life easier
  - Move d to a location >= 33 via a goto like operation
  - Validate d is where you want it to be after an operation
  - Set values used for operations manually
  - Macro operator to store operations under a name
- Randomize generated placeholders for partial program obfuscation via `--fill-random`
- Set placeholders to pipes via `--fill-lines`
- Sets placeholders to no-ops by default

### Why should I use this?
Writing in Dis is extremely annoying. Feel free to try it.

### What does this not do?
You still need to chain the | and > operators together and figure out what values you need to produce the values you want :) This still requires a decent amount of thought to produce something useful but does simplify the process. 

### Future?
I may write a standard library with macros that inserts the values you want at certain memory locations which would make writing programs incredibly simpler. 

## Operators 

|  OP | Description | Dis Equivalent  | 
| ------------ | ------------ | ------------ |
|   SET_D | Sets the data pointer to the value stored at d  | *  |
|  SET int, int | Set a value in memory at integer 1 to the value of integer 2. Should only be used to setup the memory you need for subsequent operations. Integer 2 is only allowed to be one of Dis operators  | Setting placeholder values by hand  directly in code|
|  EXIT |  Insert a exclamation point at the current location in memory. If it is read, the program will exit  | !  |
| SHIFT [int]  |  Shift the value at d to the right by 1 at the current data pointer d. If a integer is specified > 33, the assembler will insert code to jump to that memory location and insert the > operator. The pointer a is also set to the shifted value. |  >  |
|  SUB [int] |  Trinary subtraction without borrow between pointer a and data pointer d. As with SHIFT, the assembler will jump the data pointer to the integer given, then execute the subtraction. |  &#124;  |
| JUMP  | Set code pointer c to the value pointed to by data pointer d. The internal code pointer is adjusted so placeholder values are automatically handled and should not be manually inserted.  | ^  |
|  IS_D int | Validates that the data pointer d is at the exepcted location otherwise an error is thrown  | None  |
|  IS_A int | Validates that the pointer a is the value we expect it to be otherwise an error is thrown  | None  |
| A_OUT | Output the pointer a to stdout | { |
| IN | Get one character from stdin and store it in a | } |
| MACRO [name] [code body] END_MACRO| Create a set of code that can be called by name | None |
| ; [comment here] | Everything after the semi-colon is a comment and is ignored | (comment here)|

### Examples
See `examples/`  

### Usage
Format: `python3 dissent.py <file name> --[options]`  
Example: `python3 dissent.py examples/999.code --fill-random`

### References
Dis https://lutter.cc/dis/

### Notes
- GOTO operator does not support jumping to locations below 34, although this is intended
 - This is easily proven through the use of IS_D. `IS_D 33` and below will always fail
- Make sure to define your data that operations need at the start of the program. Otherwise you will encounter undefined behavior due to the partial execution
 
### Problems
- IS_A does not work as partial code execution would have to take place
- Macros do not take arguments yet
