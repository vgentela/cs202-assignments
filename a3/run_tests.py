import os
import traceback
import sys
import subprocess
from compiler import run_compiler
from rvar_parser import parse_rvar
from interpreter import eval_rvar
from cs202_support import eval_x86

# Pass the --run-gcc option to this file to run your compiled files in hardware
# You must compile the runtime first and place it in the parent directory

run_gcc = False
if len(sys.argv) == 2 and sys.argv[1] == '--run-gcc':
    run_gcc = True

for file_name in sorted(os.listdir('tests')):
    if file_name.endswith('.rvar'):
        with open('tests/' + file_name) as f:
            print(f'Testing program {file_name}...')

            try:
                program = f.read()
                ast = parse_rvar(program)
                interpreter_result = eval_rvar(ast)
            
                x86_program = run_compiler(program, logging=False)
                emu = eval_x86.X86Emulator(logging=False)
                x86_output = emu.eval_program(x86_program)

                if len(x86_output) == 1 and x86_output[0] == interpreter_result:
                    print('Test passed')
                else:
                    print('Test failed! **************************************************')
                    print('Interpreter result:', interpreter_result)
                    print('Compiled x86 result:', x86_output)

                if run_gcc:
                    asm_file_name = 'tests/' + file_name + '.s'
                    with open(asm_file_name, 'w') as output_file:
                        output_file.write(x86_program)
                    
                    # run gcc to compile the binary
                    gcc_result = subprocess.run(["gcc", "-g", "../runtime.o", asm_file_name],
                                                text=True, capture_output=True)
                    print('GCC output:', gcc_result.stdout)

                    # run the binary
                    binary_result = subprocess.run(["./a.out"], text=True, capture_output=True)
                    print('Binary output:', binary_result.stdout)

                    if binary_result.stdout == str(interpreter_result):
                        print('Binary test passed')
                    else:
                        print('Binary test failed! ************************************************')
                        print('Interpreter result:', interpreter_result)
                        print('Binary x86 result:', binary_result.stdout)

                    os.remove(asm_file_name)
                    os.remove('a.out')

                print()

            except:
                print('Test failed with error! **************************************************')
                traceback.print_exception(*sys.exc_info())
