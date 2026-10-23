from faker import Faker

from app import app
from extensions import db
from models import Note, User

fake = Faker()


def seed():
    with app.app_context():
        Note.query.delete()
        User.query.delete()
        db.session.commit()

        users = []
        for idx in range(1, 4):
            user = User(username=f"user{idx}")
            user.set_password("password123")
            users.append(user)

        db.session.add_all(users)
        db.session.commit()

        notes = []
        for user in users:
            for _ in range(8):
                notes.append(
                    Note(
                        title=fake.sentence(nb_words=4),
                        content=fake.paragraph(nb_sentences=3),
                        mood=fake.random_element(elements=("focused", "tired", "happy", "neutral")),
                        user_id=user.id,
                    )
                )

        db.session.add_all(notes)
        db.session.commit()

        print("Database seeded successfully")


if __name__ == "__main__":
    seed()
