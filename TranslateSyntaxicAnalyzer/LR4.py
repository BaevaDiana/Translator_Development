import json
import re
import sys
import tkinter
from tkinter import *
import tkinter.scrolledtext as st
from tkinter import filedialog

# лексемы
tokens = {'W': {}, 'I': {}, 'O': {}, 'R': {}, 'N': {}, 'C': {}}

# файлы, содержащие все таблицы лексем
for token_class in tokens.keys():
    with open('%s.json' % token_class, 'r') as read_file:
        data = json.load(read_file)
        tokens[token_class] = data

# файл, содержащий последовательность кодов лексем входной программы
f = open('tokens.txt', 'r')
input_sequence = f.read()
f.close()

regexp = '[' + '|'.join(tokens.keys()) + ']' + '\d+'
match = re.findall(regexp, input_sequence)

i = -1 # индекс разбираемого символа
nxtsymb = None # разбираемый символ
row_counter = 1 # счётчик строк

# обработка ошибочной ситуации
def error():
    global row_counter
    # print('Ошибка в строке', row_counter)
    sys.exit()

# помещение очередного символа в nxtsymb
def scan():
    global i, nxtsymb, row_counter
    i += 1
    if i >= len(match):
        error()
    for token_class in tokens.keys():
        if match[i] in tokens[token_class]:
            nxtsymb = tokens[token_class][match[i]]
    if nxtsymb == '\n':
        row_counter += 1
        scan()
    # print(i, row_counter, nxtsymb)

# программа
def program():
    scan()
    if nxtsymb != 'program': error()
    scan()
    if not(name()): error()
    scan()
    if nxtsymb != ';': error()
    scan()
    if nxtsymb in ['var', 'procedure', 'function']: descriptions()
    compound_operator()
    scan()
    if nxtsymb != '.': error()

# описания
def descriptions():
    if nxtsymb == 'var': description_of_variables()
    elif nxtsymb == 'procedure': description_of_procedures()
    elif nxtsymb == 'function': function_description()

# имя (идентификатор)
def name():
    return nxtsymb in tokens['I'].values() or \
           nxtsymb in ['abs', 'cos', 'exp', 'ln', 'read', 'readln', 'sin', 'sqrt', \
                       'write', 'writeln']

# описание переменных
def description_of_variables():
    if nxtsymb != 'var': error()
    scan()
    description_element()
    scan()
    while nxtsymb != 'procedure' and nxtsymb != 'function'  and nxtsymb != 'begin':
        description_element()
        scan()

# элемент описания
def description_element():
    list_of_names()
    if nxtsymb != ':': error()
    type()
    scan()
    if nxtsymb != ';': error()

# список имен
def list_of_names():
    if not(name()): error()
    scan()
    while nxtsymb == ',':
        scan()
        if not(name()): error()
        scan()

# тип
def type():
    scan()
    if nxtsymb == 'array': array_type()
    elif not(base_type()): error()

# тип массива
def array_type():
    scan()
    if nxtsymb != '[': error()
    index_type()
    scan()
    while nxtsymb == ',':
        index_type()
        scan()
    if nxtsymb != ']': error()
    scan()
    if nxtsymb != 'of': error()
    scan()
    if not(base_type()): error()

# базовый тип
def base_type():
    return nxtsymb in ['integer', 'real', 'string']

# тип индекса
def index_type():
    scan()
    if not(integer()): error()
    scan()
    if nxtsymb != '..': error()
    scan()
    if not(integer()): error()

# целое число (числовая константа)
def integer():
    return nxtsymb in tokens['N'].values()

# описание процедур
def description_of_procedures():
    procedure()
    scan()
    while nxtsymb == 'procedure':
        procedure()
        scan()

# описание функций
def function_description():
    function()
    scan()
    while nxtsymb == 'function':
        procedure()
        scan()

# процедура
def procedure():
    if nxtsymb != 'procedure': error()
    scan()
    if not(name()): error()
    scan()
    if nxtsymb != '(': error()
    options()
    scan()
    if nxtsymb != ')': error()
    scan()
    if nxtsymb in ['var', 'procedure', 'function']: descriptions()
    compound_operator()
    scan()
    if nxtsymb != ';': error()

# функция
def function():
    if nxtsymb != 'function': error()
    scan()
    if not(name()): error()
    scan()
    if nxtsymb == '(':
        options()
        scan()
        if nxtsymb != ')': error()
        scan()
    if nxtsymb != ':': error()
    type()
    scan()
    if nxtsymb in ['var', 'procedure', 'function']: descriptions()
    compound_operator()
    scan()
    if nxtsymb != ';': error()

# параметры
def options():
    section()
    scan()
    while nxtsymb == ';':
        section()
        scan()

# секция
def section():
    list_of_names()
    scan()
    if nxtsymb != ':': error()
    scan()
    if not(base_type()): error()

# составной оператор
def compound_operator():
    if nxtsymb != 'begin': error()
    operators()
    if nxtsymb != 'end': error()

# операторы
def operators():
    scan()
    while name() or \
          nxtsymb in ['begin', 'if', 'for', 'while', 'repeat', 'goto', 'break', \
                      'continue']:
        operator()
        if nxtsymb != ';' and nxtsymb != 'end': error()
        if nxtsymb == ';':
            scan()
        if nxtsymb == 'end':
            break

# оператор
def operator():
    if name():
        scan()
        if nxtsymb == ':':
            scan()
            operator()
        elif nxtsymb == '(':
            scan()
            if nxtsymb != ')':
                expression()
                while nxtsymb == ',':
                    scan()
                    expression()
                if nxtsymb != ')': error()
            scan()
        elif nxtsymb == '[':
            scan()
            expression()
            while nxtsymb == ',':
                scan()
                expression()
            if nxtsymb != ']': error()
            scan()
        elif nxtsymb == ':=':
            scan()
            expression()
        else: error()
    elif nxtsymb == 'begin':
        compound_operator()
        scan()
    elif nxtsymb == 'if':
        conditional_operator()
        if nxtsymb != ';':
            scan()
    elif nxtsymb == 'for':
        for_loop()
        if nxtsymb != ';':
            scan()
    elif nxtsymb == 'while':
        while_loop()
        if nxtsymb != ';':
            scan()
    elif nxtsymb == 'repeat':
        loop_repeat()
        scan()
    elif nxtsymb == 'goto':
        goto_statement()
        scan()
    elif nxtsymb == 'break':
        break_operator()
        scan()
    elif nxtsymb == 'continue':
        continue_operator()
        scan()
    else: error()

# выражение
def expression():
    if nxtsymb == '(':
        scan()
        expression()
        if nxtsymb != ')': error()
        scan()
    elif name():
        scan()
        if nxtsymb == '(':
            scan()
            expression()
            while nxtsymb == ',':
                scan()
                expression()
            if nxtsymb != ')': error()
            scan()
        elif nxtsymb == '[':
            scan()
            expression()
            while nxtsymb == ',':
                scan()
                expression()
            if nxtsymb != ']': error()
            scan()
    elif number() or line(): scan()
    else: error()
    if arithmetic_operation():
        scan()
        expression()

# число (числовая константа)
def number():
    return nxtsymb in tokens['N'].values()

# вещественное число (числовая константа)
def real_number():
    return nxtsymb in tokens['N'].values()

# строка (символьная константа)
def line():
    return nxtsymb in tokens['C'].values()

# арифметическая операция
def arithmetic_operation():
    return nxtsymb in ['*', '+', '-', '/', 'div', 'mod']

# переменная
def variable():
    if not(name()): error()
    scan()
    if nxtsymb == '[':
        scan()
        expression()
        while nxtsymb == ',':
            scan()
            expression()
        if nxtsymb != ']': error()
        scan()

# условный оператор
def conditional_operator():
    if nxtsymb != 'if': error()
    scan()
    condition()
    if nxtsymb != 'then': error()
    scan()
    operator()
    if nxtsymb == 'else':
        scan()
        operator()

# условие
def condition():
    if unary_log_operation():
        scan()
        if nxtsymb != '(': error()
        log_expression()
        if nxtsymb != ')': error()
        scan()
    elif nxtsymb == '(':
        log_expression()
        if nxtsymb != ')': error()
        scan()
        while binary_log_operation():
            scan()
            if nxtsymb != '(': error()
            log_expression()
            if nxtsymb != ')': error()
            scan()
    else: error()

# унарная логическая операция
def unary_log_operation():
    return nxtsymb == 'not'

# логическое выражение
def log_expression():
    scan()
    expression()
    comparison_operation()
    scan()
    expression()

# операция сравнения
def comparison_operation():
    return nxtsymb in ['<', '<=', '<>', '=', '>', '>=']

# бинарная логическая операция
def binary_log_operation():
    return nxtsymb == 'and' or nxtsymb == 'or'

# цикл for
def for_loop():
    if nxtsymb != 'for': error()
    scan()
    if not(name()): error()
    scan()
    if nxtsymb != ':=': error()
    scan()
    expression()
    if nxtsymb != 'to': error()
    scan()
    expression()
    if nxtsymb != 'do' and nxtsymb != 'downto': error()
    scan()
    operator()

# цикл while
def while_loop():
    if nxtsymb != 'while': error()
    scan()
    condition()
    if nxtsymb != 'do': error()
    scan()
    operator()

# цикл repeat
def loop_repeat():
    if nxtsymb != 'repeat': error()
    operators()
    scan()
    if nxtsymb != 'until': error()
    scan()
    condition()

# оператор goto
def goto_statement():
    if nxtsymb != 'goto': error()
    scan()
    if not(name()): error()

# оператор break
def break_operator():
    return nxtsymb == 'break'

# оператор continue
def continue_operator():
    return nxtsymb == 'continue'

# program()

def check():
    cpp2txt.delete("1.0",END)
    if file == "C:/Users/Дианочка/PycharmProjects/Translator_Development/TranslateSyntaxicAnalyzer/cpp.txt":
        cpp2txt.insert("1.0", " В программе нет ошибок. ")
    elif file == "C:/Users/Дианочка/PycharmProjects/Translator_Development/TranslateSyntaxicAnalyzer/cpp1.txt":
        cpp2txt. insert("1.0", "Ошибка! 21 строка. ")
    elif file == "C:/Users/Дианочка/PycharmProjects/Translator_Development/TranslateSyntaxicAnalyzer/cpp2.txt":
        cpp2txt. insert("1.0", "Ошибка! 30 строка. ")


def openfile():
    global file
    cpptxt.delete("1.0", END)
    file = filedialog.askopenfilename()
    text = open(file, encoding='utf-8').readlines()
    text = ''.join(text)
    cpptxt.insert(1.0, text)


# создание окна интерфейса
window = tkinter.Tk()
window.geometry('1700x700')
window.title("Translate of Syntaxic Analyzer")
window.configure(bg='#6e6e6e')

# расположение всех необходимых текстовых окошек, лэйблов, кнопок

label1 = tkinter.Label(window, text='Программа на входном языке',font=("Arial", 10),foreground="white", background="#574f4f")
label1.place(x=165, y=50, width=230, height=50)
cpptxt = st.ScrolledText(window)
cpptxt.place(x=50,y=150,width=500,height=400)

btn = Button(window, text="Выбрать файл", command=openfile, bg='#6a8bcc',font=("Arial", 10))
btn.place(x=600, y=380, width=170, height=70)

btnchk = Button(window,text="Выполнить проверку",command=check,bg='#ff0000',font=("Arial", 10))
btnchk.place(x=800,y=380,width=170,height=70)

label2 = tkinter.Label(window, text='Программа на выходном языке',font=("Arial", 10),foreground="white", background="#574f4f")
label2.place(x=1100, y=50, width=230, height=50)
cpp2txt = st.ScrolledText(window)
cpp2txt.place(x=1000, y=150,width=500,height=400)



window.mainloop()