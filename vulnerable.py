from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)

# ✅ Use a persistent database file instead of memory
DATABASE = "users.db"

# ✅ Function to create a connection to the database
def connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Initialize Database (Only if the table doesn’t exist)
def init_db():
    conn = connection()
    cursor = conn.cursor()
    
    # ✅ Create table only if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    
    # ✅ Check if table is empty before inserting default users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES ('john', 'admin123')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('kant', 'password')")
        conn.commit()

    conn.close()

# ✅ Function to fetch all users from the database
def get_users():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# ✅ Call init_db() to ensure the database and users exist
init_db()

# ✅ Vulnerable Login Route (Allows SQL Injection)
@app.route("/", methods=['GET', 'POST'])
def login():
    message = ""
    users_before = get_users()  

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = connection()
        cursor = conn.cursor()

        # vulnearbility
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print("Executing Query:", query)  # ✅ Debugging output
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            message = f"Welcome, {user['username']}! (Login Successful)"
        else:
            message = "Login failed. Invalid credentials."

    users_after = get_users()  # Fetch users after login attempt

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQL Injection - Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding: 50px;
            }
            h1 { color: #333; margin-bottom: 20px; }
            .login-container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                display: inline-block;
                text-align: center;
                width: 300px;
            }
            .input-field {
                width: 90%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
            }
            .login-button {
                width: 100%;
                padding: 10px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: 0.3s;
            }
            .login-button:hover {
                background-color: #0056b3;
            }
            .table-container {
                margin-top: 20px;
                display: inline-block;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                text-align: left;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #007BFF;
                color: white;
            }
        </style>
    </head>
    <body>

        <h1>SQL Injection Demo - Login</h1>

        <div class="login-container">
            <form method="POST">
                <input type="text" name="username" class="input-field" placeholder="Enter Username" required>
                <input type="password" name="password" class="input-field" placeholder="Enter Password" required>
                <button type="submit" class="login-button">Login</button>
            </form>
        </div>

        <p><b>{{ message }}</b></p>

        <div class="table-container">
            <h2>Users Table (Before Login Attempt)</h2>
            {% if users_before %}
                <table>
                    <tr><th>ID</th><th>Username</th><th>Password</th></tr>
                    {% for user in users_before %}
                        <tr>
                            <td>{{ user['id'] }}</td>
                            <td>{{ user['username'] }}</td>
                            <td>{{ user['password'] }}</td>
                        </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p><b>The table is empty! SQL Injection may have deleted all users.</b></p>
            {% endif %}
        </div>

        <div class="table-container">
            <h2>Users Table (After Login Attempt)</h2>
            {% if users_after %}
                <table>
                    <tr><th>ID</th><th>Username</th><th>Password</th></tr>
                    {% for user in users_after %}
                        <tr>
                            <td>{{ user['id'] }}</td>
                            <td>{{ user['username'] }}</td>
                            <td>{{ user['password'] }}</td>
                        </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p><b>The table is empty! SQL Injection may have deleted all users.</b></p>
            {% endif %}
        </div>

        <h3>Try SQL Injection:</h3>
        <p>Username: <b>' OR '1'='1</b></p>
        <p>Password: <b>anything</b> (Bypasses authentication!)</p>
        <p>OR</p>
        <p>Username: <b>'; DELETE FROM users --</b></p>
        <p>Password: <b>anything</b> (Deletes all users!)</p>

    </body>
    </html>
    """, message=message, users_before=users_before, users_after=users_after)

if __name__ == "__main__":
    app.run(debug=True)
