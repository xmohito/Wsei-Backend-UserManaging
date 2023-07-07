from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="back",
    user="postgres",
    password="123",
    port=5432
)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Create Flask-RestX API
api = Api(app, version='1.0', title='User API', description='API for managing users')

# Define user model
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'role': fields.String(required=True, description='User role (student/lecturer)')
})

class UserResource(Resource):
    @api.expect(user_model)
    def post(self):
        user_data = api.payload

        try:
            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # Execute the INSERT statement
            cursor.execute(
                "INSERT INTO users (first_name, last_name, username, password) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_data['first_name'], user_data['last_name'], user_data['username'], user_data['password'])
            )

            # Get the generated user ID
            user_id = cursor.fetchone()[0]

            # Get the role ID based on the selected role
            if user_data['role'] == 'student':
                role_id = 1  # Assuming 'student' role has ID 1 in the roles table
            elif user_data['role'] == 'lecturer':
                role_id = 2  # Assuming 'lecturer' role has ID 2 in the roles table
            else:
                return {'message': 'Invalid role'}, 400

            # Assign the selected role to the user
            cursor.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, role_id)
            )

            # Commit the transaction
            conn.commit()

            return {'message': 'User added successfully'}, 201

        except (Exception, psycopg2.Error) as error:
            return {'message': 'Error adding user: {}'.format(error)}, 500

        finally:
            # Close the cursor
            cursor.close()

    @api.param('user_id', 'User ID', type='integer', required=True)
    def delete(self, user_id):
        try:
            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # Execute the DELETE statement
            cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

            # Commit the transaction
            conn.commit()

            return {'message': 'User deleted successfully'}, 200

        except (Exception, psycopg2.Error) as error:
            return {'message': 'Error deleting user: {}'.format(error)}, 500

        finally:
            # Close the cursor
            cursor.close()

    def get(self):
        try:
            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # Execute the SELECT statement to retrieve all users with their roles
            cursor.execute("""
                SELECT u.id, u.first_name, u.last_name, u.username, r.role
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
            """)

            # Fetch all rows from the cursor
            rows = cursor.fetchall()

            # Transform rows into a list of dictionaries
            users = []
            for row in rows:
                user = {
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'username': row[3],
                    'role': row[4]
                }
                users.append(user)

            return {'users': users}, 200

        except (Exception, psycopg2.Error) as error:
            return {'message': 'Error retrieving users: {}'.format(error)}, 500

        finally:
            # Close the cursor
            cursor.close()

# Add resource to the API
api.add_resource(UserResource, '/users')

if __name__ == '__main__':
    app.run()