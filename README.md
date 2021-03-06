# Dissent

An intermediate language that outputs valid Dis code.  

### What is Dis?
Dis is a mitigated variant of Malbolge. Consequently and sadly, the interest in Dis by the community seems to be low.

````
^!_______________________________>*!*!*}!{**!_____________________________
_____________________*_________|*_________|*___>__*_________>*_______|__*_
________>*_______|__*___|__*__|{>_*_________>*_____|*_________>*_____|*___
_|___|{*______*_________>*___|__*_________>*___|{!
````

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
|  IS_D int | Validates that the data pointer d is at the expected location otherwise an error is thrown  | None  |
|  IS_C int | Validates that the code pointer c is at the expected location otherwise an error is thrown  | None  |
|  IS_A int | Validates that the pointer a is the value we expect it to be otherwise an error is thrown  | None  |
| A_OUT | Output the pointer a to stdout | { |
| IN | Get one character from stdin and store it in a | } |
| MACRO [name] [code body] END_MACRO| Create a set of code that can be called by name | None |
| ; [comment here] | Everything after the semi-colon is a comment and is ignored | (comment here)|
| ISHIFT | Inefficent operator to put the value of d into a by calling SHIFT d 10 times| i.e *__> 10 times |  

### Examples
See `examples/`  

### Usage
Format: `python3 dissent.py <file name> --[options]`  
Example: `python3 dissent.py examples/999.code --fill-random`

### Running Dis Code
You can use my interpreter at https://github.com/intangere/dis
```
python3 dis.py example.dis
```
Or you can use the original interpreter from https://lutter.cc/dis/dis.c
```
gcc dis.c
./a.out example.dis
```

### References
Dis https://lutter.cc/dis/

### Notes
- GOTO operator does not support jumping to locations below 34, although this is intended
 - This is easily proven through the use of IS_D. `IS_D 33` and below will always fail
 - If you have a 0 at some [d], you can goto that location and `SET_D` to jump the data pointer d lower than 33
- Make sure to define your data that operations need at the start of the program. Otherwise you will encounter undefined behavior due to the partial execution
- The assembler will not prevent you from writing invalid code that may get stuck looping, but by using `IS_D` and `IS_C` you can prevent the code pointer and data pointer from being at an unexpected place
 
### Tips
- The easiest way to create a "memory/data space" is to jump the code pointer further into memory so that any value under where you jump to can be modified for operations. Then make data pointer d loop constantly under that value. So you can jump c to 42 and keep d looping 33-42 or jump c to 95 and keep d looping 33-95 but more efficently 33-42+
- To put a value from d into a efficiently, pick a location in the "data space" and double subtract it to get a 0 at both [d] and a. Whenever you need the 0 in a, just shift that value since shifting 0 remains 0 and places it into a. If you need it at d just `GOTO` that cell

### Problems
- IS_A does not work as partial code execution would have to take place
- Macros do not take arguments yet
