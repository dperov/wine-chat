import os
import sqlite3
import csv
import json


def load_csv_to_db(csv_file, db_file = "database.db", table_name = "wines"):
    # Открываем CSV файл и читаем его
    # Подключение к базе данных SQLite (если файла нет, он будет создан)
    # Удаление базы данных, если она существует
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Старая база данных удалена.")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    with open(csv_file, 'r', encoding='utf-8') as file:
        # Используем csv.DictReader для чтения CSV файла
        csv_reader = csv.DictReader(file)
        
        # Получаем имена столбцов из первой строки CSV файла
        columns = csv_reader.fieldnames
        
        # Создаем таблицу в SQLite, если она еще не существует
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{col} TEXT' for col in columns])})"
        cursor.execute(create_table_query)
        
        # Вставляем данные из CSV в таблицу SQLite
        for row in csv_reader:
            placeholders = ', '.join(['?' for _ in columns])
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            #print(insert_query)
            values = [row[col] for col in columns]
            #print(values)
            cursor.execute(insert_query, [row[col] for col in columns])

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


def execute_sql(query, db_file = "database.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    #print(rows)
    conn.close()
    
    result = [dict(zip(columns, row)) for row in rows]
    return result

def main():
    load_csv_to_db("data.csv")
    result = execute_sql("SELECT COUNT(*) FROM wines;")
    print(result)

if __name__ == "__main__":
    main()
else:
    script_dir = os.path.dirname(__file__)  # Получаем путь к текущему скрипту
    file_path = os.path.join(script_dir, "data.csv")

    load_csv_to_db(file_path)
    