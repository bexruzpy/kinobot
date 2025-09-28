import psycopg2

class PostgreSQLController:
    def __init__(self, db_name, user, password, host='localhost', port=5432):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None
        # Jadval yaratamiz (agar kerak bo‘lsa)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kinolar (
            id SERIAL PRIMARY KEY,
            name VARCHAR(500),
            file_id VARCHAR(500)
        )
        """
        self.connect()
        try:
            self.execute(create_table_query)
        except:
            pass

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("✅ Ulanish muvaffaqiyatli!")
        except Exception as e:
            print("❌ Ulanishda xatolik:", e)

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("✅ So‘rov bajarildi")
        except Exception as e:
            self.connection.rollback()
            print("❌ So‘rovda xatolik:", e)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("🔒 Ulanish yopildi.")
    
    # INSERT metodi
    def add_kino(self, name, file_id):
        insert_query = """
        INSERT INTO kinolar (name, file_id)
        VALUES (%s, %s)
        RETURNING id
        """
        try:
            self.cursor.execute(insert_query, (name, file_id))
            self.connection.commit()
            kino_id = self.cursor.fetchone()[0]
            print(f"✅ Kino qo‘shildi. ID: {kino_id}")
            return kino_id
        except Exception as e:
            self.connection.rollback()
            print("❌ Kino qo‘shishda xatolik:", e)
            return None


    # DELETE metodi
    def delete_kino_by_id(self, kino_id):
        delete_query = """
        DELETE FROM kinolar
        WHERE id = %s
        """
        self.execute(delete_query, (kino_id,))

    # Barcha kinolarni ko‘rish
    def get_all_kinos(self):
        select_query = "SELECT * FROM kinolar"
        self.execute(select_query)
        return self.fetchall()

    # Bitta kino olish (ID orqali)
    def get_kino_by_id(self, kino_id):
        select_query = "SELECT * FROM kinolar WHERE id = %s"
        self.execute(select_query, (kino_id,))
        return self.fetchone()
    # Yangilash metodi
    def update_kino(self, old_kino_id, new_name, new_id):
        update_query = """
        UPDATE kinolar
        SET name = %s, id = %s
        WHERE id = %s
        """
        self.execute(update_query, (new_name, new_id, old_kino_id))
