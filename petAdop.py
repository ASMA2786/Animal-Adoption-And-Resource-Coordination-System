from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'pet_adoption.db'

# ---------- DATABASE ----------
def init_db():
    with sqlite3.connect(DB_NAME) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS Pet (
            PetID INTEGER PRIMARY KEY,
            PetName TEXT,
            Breed TEXT,
            Age INTEGER,
            HealthStatus TEXT
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS Adopter (
            AdopterID INTEGER PRIMARY KEY,
            FirstName TEXT,
            LastName TEXT,
            Contact TEXT,
            Address TEXT,
            City TEXT,
            State TEXT,
            Country TEXT
        )""")

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template_string(base_html, content="<h3>Welcome to the Pet Adoption System 🐾</h3>")

# --- PETS CRUD ---
@app.route('/pets')
def pets():
    con = sqlite3.connect(DB_NAME)
    pets = con.execute("SELECT * FROM Pet").fetchall()
    return render_template_string(base_html, content=render_template_string(pets_html, pets=pets))

@app.route('/add_pet', methods=['POST'])
def add_pet():
    con = sqlite3.connect(DB_NAME)
    con.execute("INSERT INTO Pet VALUES (?, ?, ?, ?, ?)", (
        request.form['PetID'],
        request.form['PetName'],
        request.form['Breed'],
        request.form['Age'],
        request.form['HealthStatus']
    ))
    con.commit()
    return redirect('/pets')

@app.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    con = sqlite3.connect(DB_NAME)
    if request.method == 'POST':
        con.execute("""UPDATE Pet SET PetName=?, Breed=?, Age=?, HealthStatus=? WHERE PetID=?""", (
            request.form['PetName'],
            request.form['Breed'],
            request.form['Age'],
            request.form['HealthStatus'],
            pet_id
        ))
        con.commit()
        return redirect('/pets')
    pet = con.execute("SELECT * FROM Pet WHERE PetID=?", (pet_id,)).fetchone()
    return render_template_string(base_html, content=render_template_string(edit_pet_html, pet=pet))

@app.route('/delete_pet/<int:pet_id>')
def delete_pet(pet_id):
    con = sqlite3.connect(DB_NAME)
    con.execute("DELETE FROM Pet WHERE PetID=?", (pet_id,))
    con.commit()
    return redirect('/pets')

# --- ADOPTERS CRUD ---
@app.route('/adopters')
def adopters():
    con = sqlite3.connect(DB_NAME)
    adopters = con.execute("SELECT * FROM Adopter").fetchall()
    return render_template_string(base_html, content=render_template_string(adopters_html, adopters=adopters))

@app.route('/add_adopter', methods=['POST'])
def add_adopter():
    con = sqlite3.connect(DB_NAME)
    con.execute("INSERT INTO Adopter VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
        request.form['AdopterID'],
        request.form['FirstName'],
        request.form['LastName'],
        request.form['Contact'],
        request.form['Address'],
        request.form['City'],
        request.form['State'],
        request.form['Country']
    ))
    con.commit()
    return redirect('/adopters')

@app.route('/edit_adopter/<int:adopter_id>', methods=['GET', 'POST'])
def edit_adopter(adopter_id):
    con = sqlite3.connect(DB_NAME)
    if request.method == 'POST':
        con.execute("""UPDATE Adopter SET FirstName=?, LastName=?, Contact=?, Address=?, City=?, State=?, Country=? WHERE AdopterID=?""", (
            request.form['FirstName'],
            request.form['LastName'],
            request.form['Contact'],
            request.form['Address'],
            request.form['City'],
            request.form['State'],
            request.form['Country'],
            adopter_id
        ))
        con.commit()
        return redirect('/adopters')
    adopter = con.execute("SELECT * FROM Adopter WHERE AdopterID=?", (adopter_id,)).fetchone()
    return render_template_string(base_html, content=render_template_string(edit_adopter_html, adopter=adopter))

@app.route('/delete_adopter/<int:adopter_id>')
def delete_adopter(adopter_id):
    con = sqlite3.connect(DB_NAME)
    con.execute("DELETE FROM Adopter WHERE AdopterID=?", (adopter_id,))
    con.commit()
    return redirect('/adopters')

# ---------- TEMPLATES ----------
base_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Pet Adoption</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
<div class="container mt-4">
  <h2>🐶 Pet Adoption System</h2>
  <nav class="mb-3">
    <a href="/" class="btn btn-primary">Home</a>
    <a href="/pets" class="btn btn-success">Pets</a>
    <a href="/adopters" class="btn btn-warning">Adopters</a>
  </nav>
  {{ content|safe }}
</div>
</body>
</html>
"""

pets_html = """
<h4>All Pets</h4>
<table class="table table-bordered">
<tr><th>ID</th><th>Name</th><th>Breed</th><th>Age</th><th>Health</th><th>Actions</th></tr>
{% for p in pets %}
<tr>
<td>{{p[0]}}</td><td>{{p[1]}}</td><td>{{p[2]}}</td><td>{{p[3]}}</td><td>{{p[4]}}</td>
<td>
  <a href="/edit_pet/{{p[0]}}" class="btn btn-sm btn-info">Edit</a>
  <a href="/delete_pet/{{p[0]}}" class="btn btn-sm btn-danger">Delete</a>
</td>
</tr>
{% endfor %}
</table>

<h5>Add New Pet</h5>
<form method="POST" action="/add_pet">
  <input name="PetID" class="form-control" placeholder="ID" required><br>
  <input name="PetName" class="form-control" placeholder="Name"><br>
  <input name="Breed" class="form-control" placeholder="Breed"><br>
  <input name="Age" class="form-control" type="number" placeholder="Age"><br>
  <input name="HealthStatus" class="form-control" placeholder="Health"><br>
  <button class="btn btn-primary">Add Pet</button>
</form>
"""

edit_pet_html = """
<h4>Edit Pet</h4>
<form method="POST">
  <input name="PetName" class="form-control" value="{{pet[1]}}"><br>
  <input name="Breed" class="form-control" value="{{pet[2]}}"><br>
  <input name="Age" class="form-control" type="number" value="{{pet[3]}}"><br>
  <input name="HealthStatus" class="form-control" value="{{pet[4]}}"><br>
  <button class="btn btn-success">Update Pet</button>
</form>
"""

adopters_html = """
<h4>All Adopters</h4>
<table class="table table-bordered">
<tr><th>ID</th><th>Name</th><th>Contact</th><th>City</th><th>Actions</th></tr>
{% for a in adopters %}
<tr>
<td>{{a[0]}}</td><td>{{a[1]}} {{a[2]}}</td><td>{{a[3]}}</td><td>{{a[5]}}</td>
<td>
  <a href="/edit_adopter/{{a[0]}}" class="btn btn-sm btn-info">Edit</a>
  <a href="/delete_adopter/{{a[0]}}" class="btn btn-sm btn-danger">Delete</a>
</td>
</tr>
{% endfor %}
</table>

<h5>Add New Adopter</h5>
<form method="POST" action="/add_adopter">
  <input name="AdopterID" class="form-control" placeholder="ID"><br>
  <input name="FirstName" class="form-control" placeholder="First Name"><br>
  <input name="LastName" class="form-control" placeholder="Last Name"><br>
  <input name="Contact" class="form-control" placeholder="Contact"><br>
  <input name="Address" class="form-control" placeholder="Address"><br>
  <input name="City" class="form-control" placeholder="City"><br>
  <input name="State" class="form-control" placeholder="State"><br>
  <input name="Country" class="form-control" placeholder="Country"><br>
  <button class="btn btn-warning">Add Adopter</button>
</form>
"""

edit_adopter_html = """
<h4>Edit Adopter</h4>
<form method="POST">
  <input name="FirstName" class="form-control" value="{{adopter[1]}}"><br>
  <input name="LastName" class="form-control" value="{{adopter[2]}}"><br>
  <input name="Contact" class="form-control" value="{{adopter[3]}}"><br>
  <input name="Address" class="form-control" value="{{adopter[4]}}"><br>
  <input name="City" class="form-control" value="{{adopter[5]}}"><br>
  <input name="State" class="form-control" value="{{adopter[6]}}"><br>
  <input name="Country" class="form-control" value="{{adopter[7]}}"><br>
  <button class="btn btn-success">Update Adopter</button>
</form>
"""

# ---------- MAIN ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
