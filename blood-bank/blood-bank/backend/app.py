from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_PATH = "bloodbank.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        last_donated TEXT,
        registered_on TEXT DEFAULT (date('now'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        units REAL NOT NULL,
        donation_date TEXT NOT NULL,
        camp TEXT,
        status TEXT DEFAULT 'Available',
        FOREIGN KEY (donor_id) REFERENCES donors(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        age INTEGER,
        blood_group TEXT NOT NULL,
        units REAL NOT NULL,
        hospital TEXT NOT NULL,
        contact TEXT NOT NULL,
        reason TEXT,
        request_date TEXT NOT NULL,
        status TEXT DEFAULT 'Pending'
    )''')

    conn.commit()
    conn.close()
    print("Blood bank DB initialized!")

# ─── DONORS ──────────────────────────────────────────────

@app.route('/donors', methods=['GET'])
def get_donors():
    conn = get_db()
    donors = conn.execute('SELECT * FROM donors ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(d) for d in donors])

@app.route('/donors', methods=['POST'])
def add_donor():
    d = request.json
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO donors (name,age,gender,blood_group,phone,email,address,last_donated) VALUES (?,?,?,?,?,?,?,?)',
            (d['name'], d['age'], d['gender'], d['blood_group'], d['phone'],
             d.get('email',''), d.get('address',''), d.get('last_donated',''))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Donor registered!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/donors/<int:did>', methods=['DELETE'])
def delete_donor(did):
    conn = get_db()
    conn.execute('DELETE FROM donations WHERE donor_id=?', (did,))
    conn.execute('DELETE FROM donors WHERE id=?', (did,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Donor deleted!"})

# ─── DONATIONS ───────────────────────────────────────────

@app.route('/donations', methods=['GET'])
def get_donations():
    conn = get_db()
    rows = conn.execute('''
        SELECT dn.*, d.name as donor_name, d.phone
        FROM donations dn JOIN donors d ON dn.donor_id = d.id
        ORDER BY dn.id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/donations', methods=['POST'])
def add_donation():
    d = request.json
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO donations (donor_id,blood_group,units,donation_date,camp,status) VALUES (?,?,?,?,?,?)',
            (d['donor_id'], d['blood_group'], d['units'], d['donation_date'],
             d.get('camp',''), d.get('status','Available'))
        )
        conn.execute('UPDATE donors SET last_donated=? WHERE id=?', (d['donation_date'], d['donor_id']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Donation recorded!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/donations/<int:did>', methods=['DELETE'])
def delete_donation(did):
    conn = get_db()
    conn.execute('DELETE FROM donations WHERE id=?', (did,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Donation deleted!"})

# ─── REQUESTS ────────────────────────────────────────────

@app.route('/requests', methods=['GET'])
def get_requests():
    conn = get_db()
    rows = conn.execute('SELECT * FROM requests ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/requests', methods=['POST'])
def add_request():
    d = request.json
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO requests (patient_name,age,blood_group,units,hospital,contact,reason,request_date,status) VALUES (?,?,?,?,?,?,?,?,?)',
            (d['patient_name'], d.get('age',0), d['blood_group'], d['units'],
             d['hospital'], d['contact'], d.get('reason',''), d['request_date'], d.get('status','Pending'))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Request submitted!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/requests/<int:rid>', methods=['PATCH'])
def update_request(rid):
    d = request.json
    conn = get_db()
    conn.execute('UPDATE requests SET status=? WHERE id=?', (d['status'], rid))
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated!"})

@app.route('/requests/<int:rid>', methods=['DELETE'])
def delete_request(rid):
    conn = get_db()
    conn.execute('DELETE FROM requests WHERE id=?', (rid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Request deleted!"})

# ─── BLOOD STOCK ─────────────────────────────────────────

@app.route('/stock', methods=['GET'])
def get_stock():
    conn = get_db()
    rows = conn.execute('''
        SELECT blood_group, SUM(units) as total_units, COUNT(*) as donations
        FROM donations WHERE status='Available'
        GROUP BY blood_group
    ''').fetchall()
    conn.close()
    groups = ['A+','A-','B+','B-','AB+','AB-','O+','O-']
    stock = {g: {"units": 0, "donations": 0} for g in groups}
    for r in rows:
        if r['blood_group'] in stock:
            stock[r['blood_group']] = {"units": r['total_units'], "donations": r['donations']}
    return jsonify(stock)

# ─── STATS ───────────────────────────────────────────────

@app.route('/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    total_donors = conn.execute('SELECT COUNT(*) as c FROM donors').fetchone()['c']
    total_units = conn.execute("SELECT COALESCE(SUM(units),0) as s FROM donations WHERE status='Available'").fetchone()['s']
    pending_requests = conn.execute("SELECT COUNT(*) as c FROM requests WHERE status='Pending'").fetchone()['c']
    total_donations = conn.execute('SELECT COUNT(*) as c FROM donations').fetchone()['c']
    conn.close()
    return jsonify({
        "total_donors": total_donors,
        "available_units": total_units,
        "pending_requests": pending_requests,
        "total_donations": total_donations
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
