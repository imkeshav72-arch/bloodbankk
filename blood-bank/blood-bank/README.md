# 🩸 Blood Bank Management System — Mini College Project

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python + Flask
- **Database**: SQLite (auto-created)

---

## 📁 Project Structure

```
blood-bank/
├── backend/
│   ├── app.py            ← Flask backend + SQLite DB
│   └── requirements.txt
├── frontend/
│   └── index.html        ← Full UI
└── README.md
```

---

## ⚙️ Setup & Run

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open `frontend/index.html` in browser.

---

## 🔗 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET/POST | `/donors` | List / Add donors |
| DELETE | `/donors/<id>` | Remove donor |
| GET/POST | `/donations` | List / Add donations |
| DELETE | `/donations/<id>` | Remove donation |
| GET/POST | `/requests` | List / Add blood requests |
| PATCH | `/requests/<id>` | Update request status |
| DELETE | `/requests/<id>` | Remove request |
| GET | `/stock` | Blood stock by group |
| GET | `/stats` | Dashboard statistics |

---

## ✨ Features
- Register donors with blood group, age, gender, contact
- Record donations and track blood stock per group
- Visual blood stock bar charts by group (A+, B+, O-, etc.)
- Submit & manage patient blood requests
- Update request status: Pending → Fulfilled / Cancelled
- Dashboard with live stats
- SQLite database (no extra setup needed)

---

## 👨‍💻 Mini College Project
