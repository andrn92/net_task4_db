import psycopg2
from info import password


def create_db(conn):

    commands = (
        """
        CREATE TABLE clients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(40) NOT NULL,
            surname VARCHAR(40) NOT NULL,
            email VARCHAR(40) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE phones (
            id SERIAL PRIMARY KEY,
            number VARCHAR(40) NOT NULL,
            client_id INTEGER NOT NULL REFERENCES clients(id)
        )
        """
        )
    
    cur = conn.cursor()
    
    for command in commands:
        cur.execute(command)
    cur.close()
    conn.commit()

def drop_tables(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE phones; DROP TABLE clients;")
    cur.close()

def add_client(conn, first_name:str, last_name:str, email:str, numbers=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO clients(name, surname, email) VALUES(%s, %s, %s);", (first_name, last_name, email))
    cur.execute("SELECT id FROM clients WHERE email=%s;", (email, ))
    client_id = cur.fetchone()[0]
    run = True
    while run:
        if type(numbers) == list:
            for number in numbers:
                cur.execute("INSERT INTO phones(number, client_id) VALUES(%s, %s);", (number, client_id))
                run = False
        elif type(numbers) == str:
            number = numbers
            cur.execute("INSERT INTO phones(number, client_id) VALUES(%s, %s);", (number, client_id))
            run = False
        elif numbers == None:
            number = '------'
            cur.execute("INSERT INTO phones(number, client_id) VALUES(%s, %s);", (number, client_id))
            run = False
        else:
            numbers = input('Enter the correct phone number: ')

    return client_id

def add_phone(conn, client_id:int, number:str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM phones WHERE client_id=%s and number='------';", (client_id, ))
    phone_id = cur.fetchone()
    if phone_id != None:
        phone_id = phone_id[0]
    run = True
    while run:
        if phone_id and type(number) == str:
            cur.execute("UPDATE phones SET number=%s WHERE client_id=%s;", (number, client_id))
            run = False
        elif phone_id == None and type(number) == str:
            cur.execute("INSERT INTO phones(number, client_id) VALUES(%s, %s);", (number, client_id))
            run = False
        else:
            number = input('Enter the correct phone number: ')

    cur.close()
    conn.commit()

def change_client(conn, client_id:int, first_name=None, last_name=None, email=None, numbers=None):
    cur = conn.cursor()
    cur.execute("SELECT id FROM phones WHERE client_id = %s and number ='------';", (client_id, ))
    phone_id = cur.fetchone()
    if phone_id != None:
        phone_id = phone_id[0]
    if first_name:
        cur.execute("UPDATE clients SET name=%s WHERE id=%s;", (first_name, client_id))
    if last_name:
        cur.execute("UPDATE clients SET surname=%s WHERE id=%s;", (last_name, client_id))
    if email:
        cur.execute("UPDATE clients SET email=%s WHERE id=%s;", (email, client_id))
    run = True
    while run:
        if phone_id:
            if type(numbers) == list:
                cur.execute("UPDATE phones SET number=%s WHERE id=%s;", (numbers[0], phone_id))
                for number in numbers[1:]:
                    cur.execute("INSERT INTO phones(number, client_id) VALUES(%s, %s);", (number, client_id))
                run = False
            elif type(numbers) == str:
                number = numbers
                cur.execute("UPDATE phones SET number=%s WHERE client_id=%s;", (number, client_id))
                run = False
            elif type(numbers) not in [list, str, None]:
                numbers = input('Enter the correct phone number: ')
        else:
            if type(numbers) == list:
                cur.execute("UPDATE phones SET number=%s WHERE client_id=%s;", (numbers[0], client_id))
                for number in numbers[1:]:
                    cur.execute("INSERT INTO phones(number, client_id) VALUES(%s, %s);", (number, client_id))
                run = False
            elif type(numbers) == str:
                cur.execute("SELECT count(id) FROM phones WHERE client_id =%s;", (client_id, ))
                if cur.fetchone()[0] > 1:
                    cur.execute("SELECT min(id) FROM phones WHERE client_id =%s;", (client_id, ))
                    phone_id = cur.fetchone()[0]
                    number = numbers
                    cur.execute("UPDATE phones SET number=%s WHERE id=%s;", (number, phone_id))
                else:
                    number = numbers
                    cur.execute("UPDATE phones SET number=%s WHERE client_id=%s;", (number, client_id))
                run = False
            elif type(numbers) not in [list, str, None]:
                numbers = input('Enter the correct phone number: ')

    cur.close()
    conn.commit()

def delete_phone(conn, client_id:int, number:str):
    cur = conn.cursor()
    cur.execute("DELETE FROM phones WHERE number=%s and client_id=%s;", (number, client_id, ))
    cur.close()
    conn.commit()

def delete_client(conn, client_id:int):
    cur = conn.cursor()
    cur.execute("DELETE FROM phones WHERE client_id=%s;", (client_id, ))
    cur.execute("DELETE FROM clients WHERE id=%s;", (client_id, ))
    cur.close()
    conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, number=None):
    cur = conn.cursor()
    cur.execute("SELECT c.name, c.surname, c.email FROM clients AS c JOIN phones AS p ON c.id = p.client_id WHERE c.name=%s and c.surname=%s and c.email=%s and p.number=%s;", (first_name, last_name, email, number, ))
    res = cur.fetchone()
    if res:
        return "Client exists."
    else:
        return "Client doesn't exists."

config = {'database': 'clients_db', 'user': 'postgres', 'password': password}


if __name__ == '__main__':
    with psycopg2.connect(**config) as conn:
        drop_tables(conn)
        create_db(conn)
        client_id = add_client(conn, 'Bob', 'Marshal', 'bobmarsh@gmail.com', '555')
        change_client(conn, client_id, 'Alex', 'Small', 'alexsmall@gmail.com', '111')
        res = find_client(conn, 'Alex', 'Small', 'alexsmall@gmail.com', '111')
        print(res)
        add_phone(conn, client_id, '222')
        delete_phone(conn, client_id, '222')
        delete_client(conn, client_id)
        res = find_client(conn, 'Alex', 'Small', 'alexsmall@gmail.com', '111')
        print(res)
        
    conn.close()








        
