# ============================================================
#  analytics.py  —  Calculations using NumPy and Pandas
# ============================================================

import numpy as np
import pandas as pd
import database as db


def get_student_summary(student_id):
    """Calculate performance stats for one student."""
    records = db.get_student_marks(student_id)
    if not records:
        return None

    marks_by_exam = {}
    for record in records:
        marks_by_exam[record["exam"]] = record["marks"]

    # Average score per exam
    exam_averages = {}
    for exam, marks in marks_by_exam.items():
        scores = list(marks.values())
        exam_averages[exam] = round(float(np.mean(scores)), 1)

    # Average score per subject across all exams
    subject_averages = {}
    for subject in db.SUBJECTS:
        scores = [marks_by_exam[e][subject]
                  for e in marks_by_exam if subject in marks_by_exam[e]]
        subject_averages[subject] = round(float(np.mean(scores)), 1) if scores else 0

    overall = round(float(np.mean(list(subject_averages.values()))), 1)

    # Trend sorted Mid-1 → Mid-2 → Finals
    exam_order = {e: i for i, e in enumerate(db.EXAMS)}
    trend = sorted(exam_averages.items(), key=lambda x: exam_order.get(x[0], 99))

    # Alert if score dropped more than 20 points
    alert = None
    avgs = [score for _, score in trend]
    for i in range(1, len(avgs)):
        drop = avgs[i-1] - avgs[i]
        if drop > 20:
            alert = f"Score dropped {drop:.0f} pts between {trend[i-1][0]} → {trend[i][0]}"
            break

    return {
        "marks_by_exam":    marks_by_exam,
        "exam_averages":    exam_averages,
        "subject_averages": subject_averages,
        "overall":          overall,
        "grade":            db.get_grade(overall),
        "trend":            trend,
        "alert":            alert
    }


def get_class_leaderboard():
    """Build a Pandas DataFrame ranking all students by average score."""
    rows = []
    for student in db.get_all_students():
        sid     = str(student["_id"])
        summary = get_student_summary(sid)
        avg     = summary["overall"] if summary else 0
        rows.append({
            "Name":     student["name"],
            "SAP ID":   student.get("sap_id", ""),
            "Batch No": student.get("batch", ""),
            "Course":   student.get("course", ""),
            "Avg Score": avg,
            "Grade":    db.get_grade(avg)
        })

    if not rows:
        return pd.DataFrame(columns=["Name", "SAP ID", "Batch No", "Course", "Avg Score", "Grade"])

    df = pd.DataFrame(rows).sort_values("Avg Score", ascending=False)
    df = df.reset_index(drop=True)
    df.index += 1
    return df


def get_class_subject_averages():
    """Average score per subject across ALL students"""
    subject_scores = {s: [] for s in db.SUBJECTS}
    for student in db.get_all_students():
        sid     = str(student["_id"])
        summary = get_student_summary(sid)
        if not summary:
            continue
        for subject, avg in summary["subject_averages"].items():
            if avg > 0:
                subject_scores[subject].append(avg)

    return {
        subject: round(float(np.mean(scores)), 1) if scores else 0
        for subject, scores in subject_scores.items()
    }


def get_pass_fail_count():
    """Count passed (>=50) vs failed students"""
    passed = failed = 0
    for student in db.get_all_students():
        summary = get_student_summary(str(student["_id"]))
        if not summary:
            continue
        if summary["overall"] >= 50:
            passed += 1
        else:
            failed += 1
    return passed, failed


def get_at_risk_students():
    """Return list of (name, alert) for students with big score drops"""
    result = []
    for student in db.get_all_students():
        summary = get_student_summary(str(student["_id"]))
        if summary and summary["alert"]:
            result.append((student["name"], summary["alert"]))
    return result


def export_csv(filepath):
    """Save leaderboard to CSV using Pandas"""
    df = get_class_leaderboard()
    df.to_csv(filepath, index_label="Rank")
    return filepath
