#import LR1
import json
import re
import tkinter
from tkinter import *

CLASSES_OF_TOKENS = ['W', 'I', 'O', 'R', 'N', 'C']

def is_identifier(token):
    return re.match(r'^I\d+$', inverse_tokens[token])

def get_priority(token):
    if token in ['(', 'for', 'if', 'while', '[', 'АЭМ', 'Ф', '{']:
        return 0
    if token in [')', ',', ':', 'else', ']']:
        return 1
    if token == '=' or token == '<-':
        return 2
    if token == '|':
        return 3
    if token == '&':
        return 4
    if token == '!':
        return 5
    if token in ['!=', '<', '<=', '==', '>', '>=']:
        return 6
    if token == '+' or token == '-':
        return 7
    if token in ['*', '^', '/', '%%']:
        return 8
    if token in ['}', 'function','return', 'print',]:
        return 9
    return -1

# лексемы (код-значение)
tokens = {}

# файлы, содержащие все таблицы лексем
for token_class in CLASSES_OF_TOKENS:
    with open('%s.json' % token_class, 'r') as read_file:
        data = json.load(read_file)
        tokens.update(data)

# лексемы (значение-код)
inverse_tokens = {val: key for key, val in tokens.items()}

# файл, содержащий последовательность кодов лексем входной программы
f = open('tokens.txt', 'r')
inp_seq = f.read()
f.close()

regexp = '[' + '|'.join(CLASSES_OF_TOKENS) + ']' + '\d+'
match = re.findall(regexp, inp_seq)

t = [tokens[i] for i in match]

i = 0
stack = []
out_seq = ''
aem_count = proc_num = proc_level = operand_count = 1
func_count = tag_count = proc_num = if_count = while_count = \
             begin_count = end_count = bracket_count = 0
is_if = is_while = is_description_var = False
while i < len(t):
    p = get_priority(t[i])
    if p == -1:
        if t[i] != '\n':
            out_seq += t[i] + ' '
    else:
        if t[i] == '[':
            aem_count += 1
            stack.append(str(aem_count) + ' АЭМ')
        elif t[i] == ']':
            while not(re.match(r'^\d+ АЭМ$', stack[-1])):
                out_seq += stack.pop() + ' '
            out_seq += stack.pop() + ' '
            aem_count = 1
        elif t[i] == '(':
            if is_identifier(t[i - 1]):
                if t[i + 1] != ')':
                    func_count += 1
                stack.append(str(func_count) + ' Ф')
            else:
                stack.append(t[i])
            bracket_count += 1
        elif t[i] == ')':
            while stack[-1] != '(' and not(re.match(r'^\d+ Ф$', stack[-1])):
                out_seq += stack.pop() + ' '
            if re.match(r'^\d+ Ф$', stack[-1]):
                stack.append(str(func_count + 1) + ' Ф')
                func_count = 0
            stack.pop()
            bracket_count -= 1
            if bracket_count == 0:
                if is_if:
                    while stack[-1] != 'if':
                        out_seq += stack.pop() + ' '
                    tag_count += 1
                    stack[-1] += ' М' + str(tag_count)
                    out_seq += 'М' + str(tag_count) + ' УПЛ '
                    is_if = False
                if is_while:
                    while not(re.match(r'^while М\d+$', stack[-1])):
                        out_seq += stack.pop() + ' '
                    tag_count += 1
                    out_seq += 'М' + str(tag_count) + ' УПЛ '
                    stack[-1] += ' М' + str(tag_count)
                    is_while = False
        elif t[i] == ',':
            while not(re.match(r'^\d+ АЭМ$', stack[-1])) and \
                  not(re.match(r'^\d+ Ф$', stack[-1])) and \
                  not(re.match(r'^var', stack[-1])):
                out_seq += stack.pop() + ' '
            if re.match(r'^\d+ АЭМ$', stack[-1]):
                aem_count += 1
                stack.append(str(aem_count) + ' АЭМ')
            if re.match(r'^\d+ Ф$', stack[-1]):
                func_count += 1
                stack.append(str(func_count) + ' Ф')
            if re.match(r'^var', stack[-1]):
                operand_count += 1
        elif t[i] == 'goto':
            out_seq += t[i + 1] + ' БП '
            i += 2
        elif t[i] == 'if':
            stack.append(t[i])
            if_count += 1
            bracket_count = 0
            is_if = True
        elif t[i] == 'else':
            while not(re.match(r'^if М\d+$', stack[-1])):
                out_seq += stack.pop() + ' '
            stack.pop()
            tag_count += 1
            stack.append('if М' + str(tag_count))
            out_seq += 'М' + str(tag_count) + ' БП М' + str(tag_count - 1) + ' : '
        elif t[i] == 'while':
            tag_count += 1
            stack.append(t[i] + ' М' + str(tag_count))
            out_seq += 'М' + str(tag_count) + ' : '
            while_count += 1
            bracket_count = 0
            is_while = True
        elif t[i] == 'for':
            j = i + 2
            bracket_count = 1
            a = []
            # while t[j] != ';'
            a.append(t[j])
            j += 1
            if t[j] == '(':
                bracket_count += 1
            elif t[j] == ')':
                bracket_count -= 1
            j += 1

            b = []
            # while t[j] != ';':
            b.append(t[j])
            j += 1
            if t[j] == '(':
                bracket_count += 1
            elif t[j] == ')':
                bracket_count -= 1
            j += 1
            c = []
            while bracket_count != 0:
                c.append(t[j])
                j += 1
                if t[j] == '(':
                    bracket_count += 1
                elif t[j] == ')':
                    bracket_count -= 1
            j += 1
            d = []
            while t[j] != ';' and t[j] != '{':
                d.append(t[j])
                j += 1
            if t[j] == '{':
                j += 1
                bracket_count = 1
                d = ['{']
                while bracket_count != 0:
                    d.append(t[j])
                    j += 1
                    if t[j] == '{':
                        bracket_count += 1
                    elif t[j] == '}':
                        bracket_count -= 1
                d.append('}')
            j += 1
            t = t[:i] + a + [';', '\n', 'while', '('] + b + [')', '{', '\n'] + d + \
                ['\n'] + c + [';', '\n', '}'] + t[j:]
            i -= 1
        elif t[i] == 'var':
            stack.append(t[i] + ' ' + str(proc_num) + ' ' + str(proc_level))
            operand_count = 1
            is_description_var = True
        elif t[i] == 'sub':
            proc_num += 1
            stack.append('PROC ' + str(proc_num) + ' ' + str(proc_level))
        elif t[i] == '{':
            if len(stack) > 0 and re.match(r'^PROC', stack[-1]):
                num = re.findall(r'\d+', stack[-1])
                stack.pop()
                out_seq += '0 Ф ' + str(num[0]) + ' ' + str(num[1]) + ' НП '
                stack.append('PROC ' + str(proc_num) + ' ' + str(proc_level))
            begin_count += 1
            proc_level = begin_count - end_count + 1
            stack.append(t[i])
        elif t[i] == '}':
            end_count += 1
            proc_level = begin_count - end_count + 1
            while stack[-1] != '{':
                out_seq += stack.pop() + ' '
            stack.pop()
            if len(stack) > 0 and re.match(r'^PROC', stack[-1]):
                stack.pop()
                out_seq += 'КП '
            if if_count > 0 and re.match(r'^if М\d+$', stack[-1]):
                tag = re.search('М\d+', stack[-1]).group(0)
                j = i + 1
                while j < len(t) and t[j] == '\n':
                    j += 1
                if j >= len(t) or t[j] != 'else':
                    stack.pop()
                    out_seq += tag + ' : '
                    if_count -= 1
            if while_count > 0 and re.match(r'^while М\d+ М\d+$', stack[-1]):
                tag = re.findall('М\d+', stack[-1])
                stack.pop()
                out_seq += tag[0] + ' БП ' + tag[1] + ' : '
                while_count -= 1
        elif t[i] == ';':
            if len(stack) > 0 and re.match(r'^PROC', stack[-1]):
                num = re.findall(r'\d+', stack[-1])
                stack.pop()
                out_seq += str(num[0]) + ' ' + str(num[1]) + ' НП '
            elif len(stack) > 0 and stack[-1] == 'end':
                stack.pop()
                out_seq += 'КП '
            elif is_description_var:
                while not(re.match(r'^var', stack[-1])):
                    out_seq += stack.pop() + ' '
                proc_num, proc_level = re.findall('\d+', stack[-1])
                stack.pop()
                out_seq += str(operand_count) + ' ' + proc_num + ' ' + proc_level + \
                           ' КО '
                is_description_var = False
            elif if_count > 0 or while_count > 0:
                while not(len(stack) > 0 and stack[-1] == '{') and \
                      not(if_count > 0 and re.match(r'^if М\d+$', stack[-1])) and \
                      not(while_count > 0 and re.match(r'^while М\d+ М\d+$', stack[-1])):
                    out_seq += stack.pop() + ' '
                if if_count > 0 and re.match(r'^if М\d+$', stack[-1]):
                    tag = re.search('М\d+', stack[-1]).group(0)
                    j = i + 1
                    while t[j] == '\n':
                        j += 1
                    if t[j] != 'else':
                        stack.pop()
                    out_seq += tag + ' : '
                    if_count -= 1
                if while_count > 0 and re.match(r'^while М\d+ М\d+$', stack[-1]):
                    tag = re.findall('М\d+', stack[-1])
                    out_seq += tag[0] + ' БП ' + tag[1] + ' : '
                    while_count -= 1
            else:
                while len(stack) > 0 and stack[-1] != '{':
                    out_seq += stack.pop() + ' '
        else:
            while len(stack) > 0 and get_priority(stack[-1]) >= p:
                out_seq += stack.pop() + ' '
            stack.append(t[i])
    i += 1

while len(stack) > 0:
    out_seq += stack.pop() + ' '

#файл, содержащий обратную польскую запись
f = open('reverse_polish_entry.txt', 'w', encoding='ANSI')
f.write(out_seq)
f.close()

# действие после нажатия на кнопку
def rpn():
    label4 = tkinter.Label(window, text='Обратная польская запись', font=("Arial", 10), foreground="white",background="#574f4f")
    label4.place(x=475, y=400, width=245, height=45)
    rpn_text = open('reverse_polish_entry_1.txt',encoding='ANSI').readlines()
    rpn_text = ''.join(rpn_text)
    textline1 = Text(window, height=10, width=95)
    textline1.insert(1.0, rpn_text)
    textline1.place(x=245, y=470)


# создание окна интерфейса
window = tkinter.Tk()
window.geometry('1300x700')
window.title("Reverse polish interface")
window.configure(bg='#6e6e6e')

# расположение всех необходимых текстовых окошек, лэйблов
label2 = tkinter.Label(window, text='Программа на входном языке',font=("Arial", 10),foreground="white", background="#574f4f")
label2.place(x=165, y=50, width=200, height=50)

text = open('R.txt',encoding='utf-8').readlines()
text=''.join(text)
textline=Text(window,height=10, width=60)
textline.insert(1.0,text)
textline.place(x=10, y=125)

label3 = tkinter.Label(window, text='Коды лексем входной программы', font=("Arial", 10), foreground="white",
                       background="#574f4f")
label3.place(x=855, y=50, width=245, height=45)

token_text = open('tokens.txt', encoding='utf-8').readlines()
token_text = ''.join(token_text)
textline = Text(window, height=10, width=60)
textline.insert(1.0, token_text)
textline.place(x=725, y=125)

button = tkinter.Button(window, text='Перевести в ОПЗ', bg='#6a8bcc',command=rpn)
button.place(x=500, y=300, width=190, height=70)

window.mainloop()
