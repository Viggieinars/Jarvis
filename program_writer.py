import os.path
import autopep8

def write_program(code):
    i = 1
    while True:
        if os.path.isfile(f'jcode{i}.py'):
            i += 1
        else:
            break
    code = code.replace('\\t', '\t').replace('\\n', '\n') 
    formatted_code = autopep8.fix_code(code)

    with open(f'jcode{i}.py', 'w') as file:
        file.write(formatted_code)

    return f'jcode{i}.py'