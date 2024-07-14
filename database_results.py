import sqlite3
import fpdf
import json
import tabulate
import textwrap
import subprocess

DATABASE_NAME = 'calculator.db'

# from https://stackoverflow.com/questions/10112244/convert-plain-text-to-pdf-in-python
def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = fpdf.FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    create_calculations_table_query = '''
    CREATE TABLE IF NOT EXISTS calculations (
        operand1 TEXT NOT NULL,
        operand2 TEXT NOT NULL,
        operator TEXT NOT NULL,
        result TEXT NOT NULL,
        date DATE NOT NULL
        );'''

    cursor.execute(create_calculations_table_query)

    create_user_details_table_query = '''
    CREATE TABLE IF NOT EXISTS user_details (
        email TEXT PRIMARY KEY NOT NULL,
        password TEXT NOT NULL
    );
    '''

    cursor.execute(create_user_details_table_query)

    conn.commit()
    conn.close()

def print_results():
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.execute('select * from calculations')
    res = [dict(operand1=row[0], operand2=row[1], operator=row[2], result=row[3], date=row[4]) for row in cur.fetchall()]
    conn.close()

    for result in res:
        print(result)

def print_user_details():
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.execute('select * from user_details')
    res = [dict(email=row[0], password=row[1]) for row in cur.fetchall()]
    conn.close()

    for result in res:
        print(result)

def export_to_pdf(date=''):
    pdf = fpdf.FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    conn = sqlite3.connect(DATABASE_NAME)

    if not date:
        cur = conn.execute('select * from calculations')
    else:
        cur = conn.execute("SELECT * FROM calculations WHERE DATE(date) = ?", (target_date,))
    res = [dict(operand1=row[0], operand2=row[1], operator=row[2], result=row[3], date=row[4]) for row in cur.fetchall()]
    conn.close()

    if not res:
        print("No history found for the selected date.")
        return
    
    header = res[0].keys()
    rows =  [x.values() for x in res]
    # print(tabulate.tabulate(rows, header, tablefmt='grid', numalign="left"))

    text_to_pdf(tabulate.tabulate(rows, header, tablefmt='grid', numalign="left"), "calculator_history.pdf")
    subprocess.call(["xdg-open", "calculator_history.pdf"])
    print("History exported to pdf successfully!")

def main():
    # create_tables()
    # print_results()
    export_to_pdf()
    # print_user_details()

if __name__ == '__main__':
    main()