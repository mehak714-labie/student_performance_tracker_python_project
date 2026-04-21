#  database.py  —  Connects to MongoDB and handles all data
from pymongo import MongoClient
from bson import ObjectId
# --- Connect to MongoDB ---
client = MongoClient("mongodb://localhost:27017/")
db     = client["student_tracker"]
students_col = db["students"]
marks_col    = db["marks"]
SUBJECTS = ["Maths", "Physics", "Digital Electronics", "Python", "DSA"]
EXAMS    = ["Mid-1", "Mid-2", "Finals"]
# ── STUDENT FUNCTIONS ────────────────────────────────────────
def add_student(name, sap_id, batch, course):
    """Save a new student to MongoDB"""
    student = {
        "name":   name,
        "sap_id": sap_id,
        "batch":  batch,
        "course": course
    }
    students_col.insert_one(student)
def get_all_students():
    """Get list of all students, sorted A-Z by name"""
    return list(students_col.find().sort("name", 1))
def get_student(student_id):
    """Get one student by their MongoDB ID"""
    return students_col.find_one({"_id": ObjectId(student_id)})

def update_student(student_id, name, sap_id, batch, course):
    """Update an existing student's details"""
    students_col.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {"name": name, "sap_id": sap_id, "batch": batch, "course": course}}
    )

def delete_student(student_id):
    """Delete a student AND all their marks"""
    students_col.delete_one({"_id": ObjectId(student_id)})
    marks_col.delete_many({"student_id": student_id})

def search_students(query):
    """Search students by name or SAP ID"""
    return list(students_col.find({
        "$or": [
            {"name":   {"$regex": query, "$options": "i"}},
            {"sap_id": {"$regex": query, "$options": "i"}}
        ]
    }))
# ── MARKS FUNCTIONS ──────────────────────────────────────────
def save_marks(student_id, exam, marks_dict):
    """Save marks for a student. Replaces existing record for same exam."""
    marks_col.delete_one({"student_id": student_id, "exam": exam})
    marks_col.insert_one({
        "student_id": student_id,
        "exam":       exam,
        "marks":      marks_dict
    })
def get_student_marks(student_id):
    """Get all marks records for one student"""
    return list(marks_col.find({"student_id": student_id}))

def get_all_marks():
    """Get every marks record in the database"""
    return list(marks_col.find())
# ── HELPER ───────────────────────────────────────────────────
def get_grade(score):
    """Convert a number score to a letter grade"""
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"
