from app import app, db
from app import Officer  # Ensure this import matches your setup

# Sample officer credentials (plain text passwords)
officers = [
    {'username': 'officer1', 'password_hash': 'password123'},  # Replace with actual plain text password
    {'username': 'officer2', 'password_hash': 'password456'}   # Replace with actual plain text password
]

with app.app_context():
    for officer_data in officers:
        officer = Officer(username=officer_data['username'], password_hash=officer_data['password_hash'])
        db.session.add(officer)
    db.session.commit()

print("Officers inserted successfully.")
