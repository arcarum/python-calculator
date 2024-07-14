import tkinter as tk
from tkinter import font as tkFont
import datetime
import sqlite3
import hashlib
from email_validator import validate_email, EmailNotValidError
import database_results
import customtkinter as ctk

DATABASE_NAME = 'calculator.db'

OPERATORS = ['+', '-', '÷', '×']
equal_btn_pressed = False # overwrite the current results with the new number pressed after equal has been pressed 

def build_buttons(root, display_field):
    '''
    Create buttons for the calculator display 
    Buttons 0-9,
    Operators (+,-,/,*),
    AC (Clears Display),
    Equal (Displays Output),
    On (Turns on calculator),
    Export to pdf
    '''
    button_config = {
        'font': tkFont.Font(family='Arial', size=20),
        'relief': 'flat',
        'bg': '#eceff4',
        'width': 3,
        'height': 2
    }

    operator_button_config = {
        **button_config,
        'bg': '#88c0d0'
    }
    
    buttons_list = []
    font = tkFont.Font(family='Arial', size=20)

    # 0-9 buttons
    row = 4
    col = 0
    for i in range(10):
        buttons_list.append(tk.Button(root, text=i, command=lambda i=i: display_numbers_pressed(i, display_field), **button_config))
        buttons_list[-1].grid(row=row,column=col)

        # properly place the numbers in their respective cells on the grid
        if col == 2 or i == 0:
            row -= 1
            col = -1
        col += 1

    # operators Buttons
    row = 4
    col = 2
    operator_buttons_list = []
    for operator in OPERATORS:
        operator_buttons_list.append(tk.Button(root, text=f'{operator}', command=lambda op=operator: display_operator_and_calculate(op,display_field), **operator_button_config))
        operator_buttons_list[-1].grid(row=row,column=col)

        # properly place the operators in their respective cells on the grid
        col = col if col == 3 else col + 1
        row = row - 1 if operator != '+' else row

    # AC (clear display)
    button_clear = tk.Button(root, text='AC', command=lambda: display('0', display_field), **button_config)
    button_clear.grid(row=1,column=3)
    button_clear.configure(bg = '#a3be8c')

    # equal
    button_equal = tk.Button(root, text='=', command=lambda: calculate_and_display(display_field.get(), display_field), **button_config)
    button_equal.grid(row=4,column=1)
    button_equal.configure(bg = '#ebcb8b')

    # power on
    button_on = tk.Button(root, text='ON', command=lambda: power_on(display_field), **button_config)
    button_on.grid(row=0,column=3)
    button_on.configure(bg = '#e5e9f0')

    set_keybinds(root, display_field)

def set_keybinds(root, display_field):

    numpad_keys = [
        '<KP_Insert>',
        '<KP_End>',
        '<KP_Down>',
        '<KP_Next>',
        '<KP_Left>',
        '<KP_Begin>',
        '<KP_Right>',
        '<KP_Home>',
        '<KP_Up>',
        '<KP_Prior>'
    ]
    
    for key, i in zip(numpad_keys, range(10)):
        root.bind(i, lambda i=i: display_numbers_pressed(i.char, display_field))
        root.bind(key, lambda event, num=i: display_numbers_pressed(num, display_field))

    key_names = [
        '<KP_Add>',
        '<KP_Subtract>',
        '<KP_Divide>',
        '<KP_Multiply>'
    ]

    for operator, i in zip(OPERATORS, key_names):
        if operator == '÷':
            root.bind("/", lambda event: display_operator_and_calculate('÷', display_field))
            root.bind(i, lambda event: display_operator_and_calculate('÷', display_field))
        elif operator == '×':
            root.bind('*', lambda event: display_operator_and_calculate('×', display_field))
            root.bind(i, lambda event: display_operator_and_calculate('×', display_field))
        else:
            root.bind(operator, lambda op=operator: display_operator_and_calculate(op.char, display_field))
            root.bind(i, lambda op=operator: display_operator_and_calculate(op.char, display_field))
    
    # equal
    root.bind('<Return>', lambda event: calculate_and_display(display_field.get(), display_field))
    root.bind('<KP_Enter>', lambda event: calculate_and_display(display_field.get(), display_field))

def build_display_field(root):
    '''
    Create the display field
    '''
    font = tkFont.Font(family='Arial', size=15, weight=tkFont.BOLD)
    display_field = tk.Entry(root, font=font, bd=2, relief='solid')
    display_field.grid(row=0, columnspan=3)
    display_field.configure(state='disabled')
    return display_field

def display_numbers_pressed(number, display_field):
    '''
    Display the numbers the user presses in the display field
    '''
    global equal_btn_pressed

    if display_field['state'] == 'disabled':
        return

    current_output = display_field.get()

    if current_output and len(current_output) == 1 and current_output[0] == '0':
        current_output = ''

    if not current_output:
        current_output = number
    elif current_output[-1] in OPERATORS:
        current_output = current_output + f' {number}'
    elif current_output == 'ERROR':
        current_output = number
        equal_btn_pressed = False
    elif equal_btn_pressed:
        current_output = number
        equal_btn_pressed = False
    else:
        current_output = current_output + f'{number}'

    display(current_output, display_field)

def display_operator_and_calculate(operator, display_field):
    '''
    Display the operator after the number and calculate if there is already two operand
    '''
    global equal_btn_pressed

    if display_field['state'] == 'disabled':
        return
    
    equal_btn_pressed = False
    current_output = display_field.get()

    if not current_output:
        current_output = ''
        output = calculate(display_field, current_output=display_field.get())
        display(output, display_field)
        return

    if current_output[-1] in OPERATORS:
        current_output = f'{operator}'.join(current_output.rsplit(current_output[-1], 1))
        display(current_output, display_field)
        return
    
    current_output = current_output.strip() + f' {operator}'
    output = calculate(display_field, current_output=display_field.get())
    if output == 'ERROR':
        display(output, display_field)
    else:
        display(f'{output} {operator}', display_field)

def power_on(display_field):
    '''
    Change the display field state to readonly and display 0
    '''
    print('=== Calculator powered on ===')
    display_field.configure(state='readonly', readonlybackground='#eceff4')
    display('0', display_field)

def display(output, display_field):
    '''
    Display output
    '''
    if display_field['state'] == 'disabled':
        return

    print(f'Current Display: {output}')
    display_field.configure(state='normal')
    display_field.delete(0, 'end')
    display_field.insert(0, output)
    display_field.configure(state='readonly')

def calculate(display_field, current_output=''):
    '''
    Returns: The result of applyting the operator on the first and second operand.
    '''
    calculation = display_field.get().split(' ')

    if not calculation or len(calculation) == 1:
        return current_output

    first_operand = float(calculation[0])
    operator = calculation[1]
    second_operand = float(calculation[2])

    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '÷': lambda x, y: 'ERROR' if y == 0 else x / y,
        '×': lambda x, y: x * y
    }

    calculation = operations[operator](first_operand, second_operand)

    print(f'Operands: ({first_operand} and {second_operand}), Applying {operator}, Result = {calculation}')

    if calculation == 'ERROR':
        return 'ERROR'

    output = f'{calculation:.5f}'
    float_output = float(output)
    int_output = int(float_output)

    # store the calculation information in the database
    now = datetime.datetime.now().isoformat()
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("INSERT INTO calculations (operand1, operand2, operator, result, date) \
        VALUES (?,?,?,?,?)", [first_operand, second_operand, operator, calculation, now])
    conn.commit()
    conn.close()

    return int_output if float_output == int_output else float_output # remove decimal points if the decimal numbers are all zeros

def calculate_and_display(output, display_field):
    '''
    calls calculate and display functions
    '''
    global equal_btn_pressed

    if display_field['state'] == 'disabled':
        return
    
    if output[-1] in OPERATORS:
        display('ERROR', display_field)
        return

    output = calculate(display_field, output)
    display(output, display_field)
    equal_btn_pressed = True

def calculator_window():
    '''
    Creates the window screen for the calculator
    '''
    root = tk.Tk()
    root.configure(bg='#d8dee9')
    root.title('Calculator Project')
    root.resizable(False, False)

    col_count = 4
    row_count = 5
    for col in range(col_count):
        root.columnconfigure(col, minsize=80)

    for row in range(row_count):
        root.rowconfigure(row, minsize=80)

    display_field = build_display_field(root)
    build_buttons(root, display_field)

    root.mainloop()

def hash_password(password):
    h = hashlib.new('sha256')
    h.update(password.encode())
    return h.hexdigest()

def signup(root, email_field, password_field, information_label):
    email = email_field.get()

    is_valid_email = False
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
        is_valid_email = True
    except EmailNotValidError as e:
        pass
    
    if password_field.get() == '' or not is_valid_email:
        information_label.configure(text='Invalid email or password', text_color='red')
        return

    hashed_password = hash_password(password_field.get())
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_details WHERE email=? AND password=?", (email, hashed_password))

    row = cursor.fetchone()
    if row:
        information_label.configure(text='Account already exists', text_color='red')
    else:
        conn.execute("INSERT INTO user_details (email, password) \
            VALUES (?,?)", [email, hashed_password])
        conn.commit()

        information_label.configure(text='Signup successful!', text_color='green')
    
    conn.close()

def login(root, email_field, password_field, information_label):
    email = email_field.get()

    hashed_password = hash_password(password_field.get())

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_details WHERE email=? AND password=?", (email, hashed_password))

    row = cursor.fetchone()

    if row:
        root.destroy()
        calculator_window()
    else:
        information_label.configure(text='Email or password is incorrect', text_color='red')
    
    conn.close()

def login_window():
    '''
    Creates the window screen for the user to sign up or log in
    '''
    ctk.set_appearance_mode("light") 
    root = tk.Tk()
    root.title('Login')
    root.resizable(False, False)

    frame = ctk.CTkFrame(master=root) 
    frame.pack(pady=20,padx=40, fill='both',expand=True) 

    email_entry = ctk.CTkEntry(master=frame, placeholder_text="Email") 
    email_entry.pack(pady=12,padx=10) 
    
    password_entry = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*") 
    password_entry.pack(pady=5,padx=10) 

    information_label = label = ctk.CTkLabel(root,text='') 
    information_label.pack(pady=10,padx=10)
    
    login_button = ctk.CTkButton(master=frame, 
                        text='Login',command=lambda: login(root, email_entry, password_entry, information_label)) 
    login_button.pack(pady=12,padx=10) 

    signup_button = ctk.CTkButton(master=frame, 
                        text='Signup',command=lambda: signup(root, email_entry, password_entry, information_label)) 
    signup_button.pack(padx=10) 
    
    root.mainloop()

def main():
    database_results.create_tables()
    login_window()
    # calculator_window()

if __name__ == '__main__':
    main()