from .database import get_db_connection
from .models import User

def create_user(user):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
            cursor.execute(sql, (user.email, user.password))
        connection.commit()
    except Exception as e:
        print(f"Error creating user: {e}")
        connection.rollback()
    finally:
        connection.close()

def get_user(email):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT email, password FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            if result:
                return User(email=result[0], password=result[1])
            else:
                print(f"User with email {email} not found")
                return None
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        connection.close()

def update_user_password(email, new_password):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET password = %s WHERE email = %s"
            cursor.execute(sql, (new_password, email))
        connection.commit()
    except Exception as e:
        print(f"Error updating user password: {e}")
        connection.rollback()
    finally:
        connection.close()

def delete_user(email):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
        connection.commit()
    except Exception as e:
        print(f"Error deleting user: {e}")
        connection.rollback()
    finally:
        connection.close()

def get_all_users():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT email, password FROM users"
            cursor.execute(sql)
            results = cursor.fetchall()
            users = [User(email=result[0], password=result[1]) for result in results]
            return users
    except Exception as e:
        print(f"Error retrieving all users: {e}")
        return []
    finally:
        connection.close()