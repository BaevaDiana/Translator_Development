import json
import re
import tkinter
from tkinter import *

CLASSES_OF_TOKENS = ['W', 'I', 'O', 'R', 'N', 'C']

def is_identifier(token):
    return ((token in inverse_tokens) and re.match(r'^I\d+$', inverse_tokens[token])) or token in ['abs', 'cos', 'exp', 'ln', 'read', 'readln', 'sin', 'sqrt', 'write', 'writeln'] or re.match(r'^М\d+$', token)

def is_constant(token):
    return ((token in inverse_tokens) and re.match(r'^C\d+$', inverse_tokens[token])) or ((token in inverse_tokens) and re.match(r'^N\d+$', inverse_tokens[token])) or token.isdigit()

def is_operation(token):
    return (token in inverse_tokens) and re.match(r'^O\d+$', inverse_tokens[token])

# лексемы (код-значение)
tokens = {}

# файлы, содержащие все таблицы лексем
for token_class in CLASSES_OF_TOKENS:
    with open('%s.json' % token_class, 'r') as read_file:
        data = json.load(read_file)
        if token_class == 'C':
            for k in data.keys():
                data[k] = re.sub(r"'([^']*)'", r'"\1"', data[k])
        tokens.update(data)

# лексемы (значение-код)
inverse_tokens = {val: key for key, val in tokens.items()}

replace = { 'scan': 'cin', 'print': 'cout', 'integer': 'integer', 'function':'function', '<-': '=', '||': '||', '&&': '&&', '!=': '!=', '=': '=', '/': '/', '%%': '%', '!': '!'}
# файл, содержащий обратную польскую запись
f = open('reverse_polish_entry.txt', 'r')
inp_seq = f.read()
inp_seq = re.sub(r"'([^']*)'", r'"\1"', inp_seq)
f.close()

t = re.findall(r'(?:\"[^\"]*\")|(?:[^ ]+)', inp_seq)

i = 0
stack = []
out_seq = ''
is_func = False
variable = {}
while i < len(t):
    if is_func == True and not(is_identifier(t[i])):
        out_seq += '() {\n'
        is_func = False
    if is_identifier(t[i]) or is_constant(t[i]):
        stack.append(replace[t[i]] if t[i] in replace else t[i])
    elif t[i] == 'НП':
        arg1 = int(stack.pop())
        stack.pop()
        #arg2 = stack.pop()
        if arg1 == 1:
            out_seq += f'void main'
        else:
            out_seq += f'void {arg2}'
        is_func = True
    elif t[i] == 'КП':
        out_seq += '}'
    elif t[i] in ['integer']:
        k = int(stack.pop())
        a = []
        while k != 0:
            a.append(stack.pop())
            k -= 1
        a.reverse()
        out_seq += replace[t[i]] + ' ' + ', '.join(a) + ';\n'
        for j in a:
            variable[j] = replace[t[i]]
    elif t[i] == 'КО':
        stack.pop()
        stack.pop()
    elif t[i] == 'УПЛ':
        arg1 = stack.pop()
        arg2 = stack.pop()
        out_seq += f'if (!({arg2})) goto {arg1};\n'
    elif t[i] == 'БП':
        arg1 = stack.pop()
        out_seq += f'goto {arg1};\n'
    elif t[i] == ':':
        arg1 = stack.pop()
        out_seq += f'{arg1}: '
    elif is_operation(t[i]):
        if t[i] == ':=':
            arg1 = stack.pop()
            arg2 = stack.pop()
            out_seq += f'{arg2} = {arg1};\n'
        else:
            operation = replace[t[i]] if t[i] in replace else t[i]
            arg1 = stack.pop()
            # if t[i] != 'not':
            #     #arg2 = stack.pop()
            #     #stack.append(f'({arg2} {operation} {arg1})')
            # else:
            stack.append(f'({operation}{arg1})')
    elif t[i] == 'АЭМ':
        k = int(stack.pop())
        a = []
        while k != 0:
            a.append(stack.pop())
            k -= 1
        a.reverse()
        out_seq += a[0] + '[' + ']['.join(a[1:]) + ']'
    elif t[i] == 'Ф':
        try:
            k = int(stack.pop()) + 1
        except ValueError:
            k = 0
        a = []
        while k != 0:
            a.append(stack.pop())
            k -= 1
        a.reverse()
        if len(a) > 0 and a[0] == 'scan':
            b = []
            for j in a[1:]:
                if variable[j] == 'int':
                    b.append('%d')
                elif variable[j] == 'double':
                    b.append('%f')
            out_seq += a[0] + '("' + ' '.join(b) + '", ' + ', '.join(map(lambda x: '&' + x, a[1:])) + ');\n'
        elif len(out_seq)>0 and len(a)>0:
            out_seq += a[0] + '(' + ', '.join(a[1:]) + ');\n'
    i += 1

out_seq = re.sub(r'(М\d+): if \(!\((.*)\)\) goto (М\d+);(?:\n|\n((?:.|\n)+)\n)goto \1;\n\3: ', r'while \2 {\n\4\n}\n', out_seq)
out_seq = re.sub(r'if \(!\((.*)\)\) goto (М\d+);(?:\n|\n((?:.|\n)+)\n)goto (М\d+);\n\2: ((?:\n|.)+)\n?\4: ', r'if \1 {\n\3\n} else {\n\5\n}\n', out_seq)
out_seq = re.sub(r'if \(!\((.*)\)\) goto (М\d+);(?:\n|\n((?:.|\n)+)\n)\2: ', r'if \1 {\n\3\n}\n', out_seq)

c = 0
a = out_seq.split('\n')
for i in range(len(a)):
    if len(a[i]) == 0:
        continue
    if a[i][0] == '}':
        c -= 1
    a[i] = 4*c*' ' + a[i]
    if a[i][len(a[i]) - 1] == '{':
        c += 1
a = [i for i in a if len(i.strip()) > 0]
out_seq = '\n'.join(a)
out_seq = '#include <stdio.h>\n\n' + out_seq
while re.search(r'= \(([^\)]+)\);\n', out_seq):
    out_seq = re.sub(r'= \(([^\)]+)\);\n', r'= \1;\n', out_seq)

# файл, содержащий текст на выходном языке программирования
f = open('c++.txt', 'w')
f.write(out_seq)
f.close()

# действие после нажатия на кнопку
def ml():
    label4 = tkinter.Label(window, text='Программа на выходном языке', font=("Arial", 10), foreground="white",background="#574f4f")
    label4.place(x=475, y=400, width=245, height=45)
    ml_text = open('output.txt',encoding='UTF-8').readlines()
    ml_text = ''.join(ml_text)
    textline1 = Text(window, height=15, width=100)
    textline1.insert(1.0, ml_text)
    textline1.place(x=245, y=450)


# создание окна интерфейса
window = tkinter.Tk()
window.geometry('1300x700')
window.title("Translate of Reverse Polish Notation In Machine Language")
window.configure(bg='#6e6e6e')

# расположение всех необходимых текстовых окошек, лэйблов
label2 = tkinter.Label(window, text='Программа на входном языке',font=("Arial", 10),foreground="white", background="#574f4f")
label2.place(x=165, y=50, width=200, height=50)

text = open('R.txt',encoding='utf-8').readlines()
text=''.join(text)
textline=Text(window,height=10, width=60)
textline.insert(1.0,text)
textline.place(x=10, y=125)

label3 = tkinter.Label(window, text='Обратная польская запись', font=("Arial", 10), foreground="white",
                       background="#574f4f")
label3.place(x=855, y=50, width=245, height=45)

token_text = open('reverse_polish_entry.txt', encoding='ANSI').readlines()
token_text = ''.join(token_text)
textline = Text(window, height=10, width=60)
textline.insert(1.0, token_text)
textline.place(x=725, y=125)

button = tkinter.Button(window, text='Перевести в машинный язык', bg='#6a8bcc',command=ml)
button.place(x=500, y=300, width=190, height=70)

window.mainloop()
