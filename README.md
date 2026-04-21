# 📚 Student Performance Tracker
**BTech CS-II | Python Programming Project**

---

## 🚀 How to Run

### Step 1 — Install libraries
```bash
pip install pymongo pandas matplotlib numpy
```

### Step 2 — Install & start MongoDB
- Download from: https://www.mongodb.com/try/download/community
- **Windows**: starts automatically after install
- **Mac**: `brew services start mongodb-community`
- **Linux**: `sudo systemctl start mongod`

### Step 3 — Run the app
```bash
python main.py
```

---

## 📁 Files
```
student_tracker/
├── main.py        ← Run this! Contains all 4 tabs
├── database.py    ← MongoDB connection & CRUD
├── analytics.py   ← NumPy + Pandas calculations
├── charts.py      ← Matplotlib chart functions
└── requirements.txt
```

## 🛠 Technologies
| Tech | Where used |
|------|-----------|
| Tkinter | All 4 tabs, forms, buttons, tables |
| Pandas | Leaderboard table, CSV export |
| Matplotlib | Bar, Line, Pie, Radar charts |
| NumPy | Averages, percentiles |
| MongoDB | Stores students + marks (CRUD) |
