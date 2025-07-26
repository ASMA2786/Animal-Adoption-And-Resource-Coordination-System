from flask import Flask, render_template_string, request, redirect
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
    CREATE TABLE IF NOT EXISTS pets (
        PetID TEXT PRIMARY KEY,
        PetName TEXT NOT NULL,
        Breed TEXT NOT NULL,
        Age INTEGER NOT NULL,
        HealthStatus TEXT NOT NULL
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS adopters (
        AdopterID TEXT PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Contact TEXT NOT NULL,
        Address TEXT NOT NULL,
        City TEXT NOT NULL,
        State TEXT NOT NULL,
        Country TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS adoptions (
        AdoptionID INTEGER PRIMARY KEY AUTOINCREMENT,
        PetID TEXT NOT NULL,
        AdopterID TEXT NOT NULL,
        AdoptionDate TEXT NOT NULL,
        FOREIGN KEY (PetID) REFERENCES pets(PetID),
        FOREIGN KEY (AdopterID) REFERENCES adopters(AdopterID)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        AdoptionID INTEGER NOT NULL,
        Amount REAL NOT NULL,
        PaymentDate TEXT NOT NULL,
        FOREIGN KEY (AdoptionID) REFERENCES adoptions(AdoptionID)
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# HTML Templates
base_html = """
<!doctype html>
<html lang="en">
<head>
    <title>Pet Adoption System</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="p-4">
    <h2>Pet Adoption Management</h2>
    <nav class="mb-4">
        <a href="/pets" class="btn btn-primary">Pets</a>
        <a href="/adopters" class="btn btn-primary">Adopters</a>
        <a href="/adoptions" class="btn btn-primary">Adoptions</a>
        <a href="/payments" class="btn btn-primary">Payments</a>
    </nav>
    <div>
        {{ content|safe }}
    </div>
</body>
</html>
"""

# --- PETS TEMPLATE ---
pets_html = """
<h4>All Pets</h4>
<table class="table table-bordered">
<tr><th>ID</th><th>Name</th><th>Breed</th><th>Age</th><th>Health</th><th>Actions</th></tr>
{% for p in pets %}
<tr>
<td>{{p[0]}}</td><td>{{p[1]}}</td><td>{{p[2]}}</td><td>{{p[3]}}</td><td>{{p[4]}}</td>
<td>
  <a href="/edit_pet/{{p[0]}}" class="btn btn-warning btn-sm">Edit</a>
  <a href="/delete_pet/{{p[0]}}" class="btn btn-danger btn-sm">Delete</a>
</td>
</tr>
{% endfor %}
</table>

<h5>Add New Pet</h5>
<form method="POST" action="/add_pet">
  <input name="PetID" class="form-control" placeholder="Pet ID" required><br>
  <input name="PetName" class="form-control" placeholder="Pet Name" required><br>
  <input name="Breed" class="form-control" placeholder="Breed" required><br>
  <input name="Age" class="form-control" type="number" placeholder="Age" required><br>
  <input name="HealthStatus" class="form-control" placeholder="Health Status" required><br>
  <button class="btn btn-success">Add Pet</button>
</form>
"""

edit_pet_html = """
<h4>Edit Pet</h4>
<form method="POST">
  <input name="PetName" class="form-control" placeholder="Pet Name" value="{{pet[1]}}" required><br>
  <input name="Breed" class="form-control" placeholder="Breed" value="{{pet[2]}}" required><br>
  <input name="Age" class="form-control" type="number" placeholder="Age" value="{{pet[3]}}" required><br>
  <input name="HealthStatus" class="form-control" placeholder="Health Status" value="{{pet[4]}}" required><br>
  <button class="btn btn-warning">Update Pet</button>
</form>
"""

# --- ADOPTERS TEMPLATE ---
adopters_html = """
<h4>All Adopters</h4>
<table class="table table-bordered">
<tr><th>ID</th><th>First Name</th><th>Last Name</th><th>Contact</th><th>City</th><th>Actions</th></tr>
{% for a in adopters %}
<tr>
<td>{{a[0]}}</td><td>{{a[1]}}</td><td>{{a[2]}}</td><td>{{a[3]}}</td><td>{{a[5]}}</td>
<td>
  <a href="/edit_adopter/{{a[0]}}" class="btn btn-warning btn-sm">Edit</a>
  <a href="/delete_adopter/{{a[0]}}" class="btn btn-danger btn-sm">Delete</a>
</td>
</tr>
{% endfor %}
</table>

<h5>Add New Adopter</h5>
<form method="POST" action="/add_adopter">
  <input name="AdopterID" class="form-control" placeholder="Adopter ID" required><br>
  <input name="FirstName" class="form-control" placeholder="First Name" required><br>
  <input name="LastName" class="form-control" placeholder="Last Name" required><br>
  <input name="Contact" class="form-control" placeholder="Contact" required><br>
  <input name="Address" class="form-control" placeholder="Address" required><br>
  <input name="City" class="form-control" placeholder="City" required><br>
  <input name="State" class="form-control" placeholder="State" required><br>
  <input name="Country" class="form-control" placeholder="Country" required><br>
  <button class="btn btn-warning">Add Adopter</button>
</form>
"""

edit_adopter_html = """
<h4>Edit Adopter</h4>
<form method="POST">
  <input name="FirstName" class="form-control" placeholder="First Name" value="{{adopter[1]}}" required><br>
  <input name="LastName" class="form-control" placeholder="Last Name" value="{{adopter[2]}}" required><br>
  <input name="Contact" class="form-control" placeholder="Contact" value="{{adopter[3]}}" required><br>
  <input name="Address" class="form-control" placeholder="Address" value="{{adopter[4]}}" required><br>
  <input name="City" class="form-control" placeholder="City" value="{{adopter[5]}}" required><br>
  <input name="State" class="form-control" placeholder="State" value="{{adopter[6]}}" required><br>
  <input name="Country" class="form-control" placeholder="Country" value="{{adopter[7]}}" required><br>
  <button class="btn btn-warning">Update Adopter</button>
</form>
"""

# --- ADOPTIONS TEMPLATE ---
adoptions_html = """
<h4>All Adoptions</h4>
<table class="table table-bordered">
<tr><th>ID</th><th>Pet ID</th><th>Adopter ID</th><th>Date</th></tr>
{% for a in adoptions %}
<tr><td>{{a[0]}}</td><td>{{a[1]}}</td><td>{{a[2]}}</td><td>{{a[3]}}</td></tr>
{% endfor %}
</table>

<h5>New Adoption</h5>
<form method="POST" action="/add_adoption">
  <input name="PetID" class="form-control" placeholder="Pet ID" required><br>
  <input name="AdopterID" class="form-control" placeholder="Adopter ID" required><br>
  <input name="AdoptionDate" class="form-control" placeholder="Adoption Date (YYYY-MM-DD)" required><br>
  <button class="btn btn-success">Add Adoption</button>
</form>
"""

# --- PAYMENTS TEMPLATE ---
payments_html = """
<h4>All Payments</h4>
<table class="table table-bordered">
<tr><th>ID</th><th>Adoption ID</th><th>Amount</th><th>Payment Date</th></tr>
{% for p in payments %}
<tr><td>{{p[0]}}</td><td>{{p[1]}}</td><td>{{p[2]}}</td><td>{{p[3]}}</td></tr>
{% endfor %}
</table>

<h5>New Payment</h5>
<form method="POST" action="/add_payment">
  <input name="AdoptionID" class="form-control" placeholder="Adoption ID" required><br>
  <input name="Amount" class="form-control" type="number" step="0.01" placeholder="Amount" required><br>
  <input name="PaymentDate" class="form-control" placeholder="Payment Date (YYYY-MM-DD)" required><br>
  <button class="btn btn-success">Add Payment</button>
</form>
"""

# ROUTES

@app.route('/')
def home():
    return redirect('/pets')

@app.route('/pets', methods=['GET'])
def pets():
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pets")
    pets = c.fetchall()
    conn.close()
    return render_template_string(base_html, content=render_template_string(pets_html, pets=pets))

@app.route('/add_pet', methods=['POST'])
def add_pet():
    data = (request.form['PetID'], request.form['PetName'], request.form['Breed'], request.form['Age'], request.form['HealthStatus'])
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("INSERT INTO pets VALUES (?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return redirect('/pets')

@app.route('/edit_pet/<PetID>', methods=['GET', 'POST'])
def edit_pet(PetID):
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = (request.form['PetName'], request.form['Breed'], request.form['Age'], request.form['HealthStatus'], PetID)
        c.execute("UPDATE pets SET PetName=?, Breed=?, Age=?, HealthStatus=? WHERE PetID=?", data)
        conn.commit()
        return redirect('/pets')
    c.execute("SELECT * FROM pets WHERE PetID=?", (PetID,))
    pet = c.fetchone()
    return render_template_string(base_html, content=render_template_string(edit_pet_html, pet=pet))

@app.route('/delete_pet/<PetID>')
def delete_pet(PetID):
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("DELETE FROM pets WHERE PetID=?", (PetID,))
    conn.commit()
    conn.close()
    return redirect('/pets')

@app.route('/adopters', methods=['GET'])
def adopters():
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("SELECT * FROM adopters")
    adopters = c.fetchall()
    conn.close()
    return render_template_string(base_html, content=render_template_string(adopters_html, adopters=adopters))

@app.route('/add_adopter', methods=['POST'])
def add_adopter():
    data = (request.form['AdopterID'], request.form['FirstName'], request.form['LastName'], request.form['Contact'],
            request.form['Address'], request.form['City'], request.form['State'], request.form['Country'])
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("INSERT INTO adopters VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return redirect('/adopters')

@app.route('/edit_adopter/<AdopterID>', methods=['GET', 'POST'])
def edit_adopter(AdopterID):
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = (request.form['FirstName'], request.form['LastName'], request.form['Contact'], request.form['Address'],
                request.form['City'], request.form['State'], request.form['Country'], AdopterID)
        c.execute("UPDATE adopters SET FirstName=?, LastName=?, Contact=?, Address=?, City=?, State=?, Country=? WHERE AdopterID=?", data)
        conn.commit()
        return redirect('/adopters')
    c.execute("SELECT * FROM adopters WHERE AdopterID=?", (AdopterID,))
    adopter = c.fetchone()
    return render_template_string(base_html, content=render_template_string(edit_adopter_html, adopter=adopter))

@app.route('/delete_adopter/<AdopterID>')
def delete_adopter(AdopterID):
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("DELETE FROM adopters WHERE AdopterID=?", (AdopterID,))
    conn.commit()
    conn.close()
    return redirect('/adopters')

@app.route('/adoptions', methods=['GET'])
def adoptions():
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("SELECT * FROM adoptions")
    adoptions = c.fetchall()
    conn.close()
    return render_template_string(base_html, content=render_template_string(adoptions_html, adoptions=adoptions))

@app.route('/add_adoption', methods=['POST'])
def add_adoption():
    data = (request.form['PetID'], request.form['AdopterID'], request.form['AdoptionDate'])
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("INSERT INTO adoptions (PetID, AdopterID, AdoptionDate) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()
    return redirect('/adoptions')

@app.route('/payments', methods=['GET'])
def payments():
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("SELECT * FROM payments")
    payments = c.fetchall()
    conn.close()
    return render_template_string(base_html, content=render_template_string(payments_html, payments=payments))

@app.route('/add_payment', methods=['POST'])
def add_payment():
    data = (request.form['AdoptionID'], request.form['Amount'], request.form['PaymentDate'])
    conn = sqlite3.connect('pet_adoption.db')
    c = conn.cursor()
    c.execute("INSERT INTO payments (AdoptionID, Amount, PaymentDate) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()
    return redirect('/payments')

if __name__ == '__main__':
    app.run(debug=True)