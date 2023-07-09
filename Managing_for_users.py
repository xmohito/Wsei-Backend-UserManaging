import psycopg2
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Resource
from UserModel import user_model, api
from DbConn import conn_to_db
from passlib.hash import pbkdf2_sha256
import psycopg2.extras

# Create Flask app````
app = Flask(__name__)
api.init_app(app)
CORS(app)
@api.route('/api/add-user')
class UserResource(Resource):
    @api.expect(user_model)
    def post(self):
        req_data = request.get_json()
        firstname=req_data.get("first_name")
        lastname=req_data.get("last_name")
        username=req_data.get("username")
        password=req_data.get("password")
        password_hash=pbkdf2_sha256.hash(password)
        userrole=req_data.get("role")

        try:
            # Create a cursor object to interact with the database
            conn=conn_to_db()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(
                "SELECT * from users where username = %s",(username,)
            )
            usercheck=cursor.fetchone()
            if usercheck:
                return {"success": False, "msg": "This username already exists."}
            # Execute the INSERT statement
            cursor.execute(
                "INSERT INTO users (first_name, last_name, username, password) VALUES (%s, %s, %s, %s) RETURNING id",
                (firstname, lastname, username, password_hash,)
            )
            

            # Get the generated user ID
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "SELECT id from roles WHERE role = %s",(userrole,)
            )
            role_id=cursor.fetchone()
            if not role_id:
                return {"success": False, "msg": "This role doesn't exists."}
            
            # Assign the selected role to the user
            cursor.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, role_id)
            )

            # Commit the transaction
            conn.commit()

            return {'message': 'User added successfully'}, 201

        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            return {'message': 'Error adding user: {}'.format(error)}, 500

        finally:
            # Close the cursor
            cursor.close()
            conn.close()

@api.route('/api/delete-user')
class DeleteUser(Resource):
    def post():
        try:
            # Create a cursor object to interact with the database
            conn=conn_to_db()
            cursor = conn.cursor()
            req_data = request.get_json()
            user_id=req_data.get("id_user")

            cursor.execute(
                "SELECT * from users WHERE id =%s",(user_id,)
            )
            userexistcheck=cursor.fetchone()
            if not userexistcheck:
                return {"success": False, "msg": "This username doesn't exists."}
            # Execute the DELETE statement
            cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

            # Commit the transaction
            conn.commit()

            return {'message': 'User deleted successfully'}, 200

        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            return {'message': 'Error deleting user: {}'.format(error)}, 500
        

        finally:
            # Close the cursor
            cursor.close()
            conn.close()
            
@api.route('/api/list-users')
class UserList(Resource):
    def get():
        try:
            # Create a cursor object to interact with the database
            conn=conn_to_db()
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
            conn.close()



if __name__ == '__main__':
    app.run()