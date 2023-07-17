# Wsei-Backend-UserManaging

curl command for check:
user list:
curl http://localhost:5000/api/list-users

add users:
admin
curl -X POST -H "Content-Type: application/json" -d "{\"first_name\": \"Alice\", \"last_name\": \"Smith\", \"username\": \"alicesmith\", \"password\": \"pass123\", \"role\": \"admin\"}" http://localhost:5000/api/add-user

uczen
curl -X POST -H "Content-Type: application/json" -d "{\"first_name\": \"Jan\", \"last_name\": \"Kowalski\", \"username\": \"jkowalski\", \"password\": \"pass123\", \"role\": \"uczen\"}" http://localhost:5000/api/add-user

wykladowca
curl -X POST -H "Content-Type: application/json" -d "{\"first_name\": \"Anna\", \"last_name\": \"Nowak\", \"username\": \"anowak\", \"password\": \"pass123\", \"role\": \"wykladowca\"}" http://localhost:5000/api/add-user

delete user:
curl -X POST -H "Content-Type: application/json" -d "{\"id_user\": [id number]}" http://localhost:5000/api/delete-user
