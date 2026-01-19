
import reflex as rx
import sqlmodel
from database.users import Users
from rxconfig import config

def check_users():
    print("Checking Users table...")
    with rx.session() as session:
        users = session.exec(sqlmodel.select(Users)).all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"User ID: {user.id}, Member ID: {user.member_id}, Email: {user.email_cache}, Supabase ID: {user.supabase_user_id}")

if __name__ == "__main__":
    check_users()
