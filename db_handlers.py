from datetime import datetime
import sqlite3


class CannotFoundFieldError(Exception): ...
class IsExistsError(Exception): ...


class Db:
    """Класс бази данних."""
    def __init__(self, file_path):
        """Створення таблиць."""
        self.base = sqlite3.connect(file_path, check_same_thread=False)
        self.cursor = self.base.cursor()
    
        self.cursor.execute('CREATE TABLE IF NOT EXISTS dishs(photo, name, description, price, add_date, id PRIMARY KEY)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS work_time(data, id)')
        self.cursor.execute('INSERT INTO work_time VALUES(?, ?)', ('12:00 - 16:00', 0))

        self.base.commit()
    
    def get_work_time(self):
        """Отримати час роботи."""
        request = 'SELECT data FROM work_time WHERE id == ?'
        data = (0,)
        return self.cursor.execute(request, data).fetchone()[0]
    
    def add_dish(self, photo, name, description, price, id):
        """Додати нове блюдо."""
        add_date = datetime.now().date()
            
        if self.cursor.execute('SELECT id FROM dishs WHERE id == ?', (id,)).fetchone():
            raise IsExistsError
    
        else:
            request = 'INSERT INTO dishs VALUES(?, ?, ?, ?, ?, ?)'
            request_data = (photo, name, description, price, add_date, id)
            self.cursor.execute(request, request_data)
            self.base.commit()

    def delete_dish(self, id):
        """Видалити блюдо."""
        request = 'DELETE FROM dishs WHERE id == ?'
        data = (id,)

        if self.cursor.execute('SELECT id FROM dishs WHERE id == ?', (id,)).fetchone():
            self.cursor.execute(request, data)
            self.base.commit()
        
        else:
            raise CannotFoundFieldError
    
    def get_dishs(self):
        """Отримати список всіх блюд."""
        request = 'SELECT * FROM dishs'
        data = self.cursor.execute(request).fetchall()
        return data
    
    def update_work_time(self, new_time):
        request = 'UPDATE work_time SET data == ? WHERE id == ?'
        data = (new_time, 0)
        self.cursor.execute(request, data)
