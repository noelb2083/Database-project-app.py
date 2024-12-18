from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbproject_owner:cBY71pZlSeCb@ep-green-moon-a5ukl2ph.us-east-2.aws.neon.tech/dbproject?sslmode=require'

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(255), unique=False)
    credit_hours = db.Column(db.Integer)

class Club(db.Model):
    __tablename__ = 'club'
    club_id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)

class Event(db.Model):
    __tablename__ = 'event'
    event_id = db.Column(db.Integer, primary_key=True, unique=True)
    event_Name = db.Column(db.String(255), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id', ondelete='CASCADE'))
    event_Type = db.Column(db.String(255), nullable=False)
    event_Length = db.Column(db.Interval, nullable=False)
    Recurring = db.Column(db.Boolean, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=True)
    Location = db.Column(db.String(255), nullable=False)
    Completed = db.Column(db.Boolean, nullable = False)
    event_DateTime = db.Column(db.DateTime, nullable=False)
    recurrence_interval = db.Column(db.Integer)
    recurrence_days = db.Column(db.String(200))
    recurrence_interval = db.Column(db.DateTime)

class Faculty(db.Model):
    __tablename__ = 'faculty'
    faculty_id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(255), nullable=False)

class Membership(db.Model):
    __tablename__ = 'membership'
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id', ondelete='CASCADE'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id', ondelete='CASCADE'), primary_key=True)

class Attends(db.Model):
    __tablename__='attends'
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id', ondelete='CASCADE'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id', ondelete='CASCADE'), primary_key=True)


# detects models and creates tables for them (if they don't exist)
with app.app_context():
    db.create_all()

# CREATE: Add a new student
@app.route('/create_student')
def create_student():
    new_student = Student(student_id=15, name='Tristan Dugray', year='Senior', credit_hours=39)
    
    db.session.add(new_student)
    db.session.commit()
    return f"Student {new_student.name} created successfully with ID {new_student.student_id}!"

# READ: Retrieve all students
@app.route('/read_students')
def read_students():
    students = Student.query.all()  # Fetch all students
    if not students:
        return "No students found."
    return "<br>".join([f"ID: {student.student_id}, Name: {student.name}, Year: {student.year}, Credit Hours: {student.credit_hours}" for student in students])

# UPDATE: Update a specific student 
@app.route('/update_student')
def update_student():
    student = Student.query.get(4)  
    if not student:
        return "Student not found."

    # update data
    student.name = 'Alice Smith'
    student.year = 'Junior'
    student.credit_hours = 35
    
    db.session.commit()
    return f"Student ID {student.student_id} updated successfully to Name: {student.name}, Year: {student.year}, Credit Hours: {student.credit_hours}."

# DELETE: Delete a specific student 
@app.route('/delete_student')
def delete_student():
    student = Student.query.get(15) 
    if not student:
        return "Student not found."
    
    db.session.delete(student)
    db.session.commit()
    return f"Student ID {student.student_id} deleted successfully!"

@app.route('/event_attendance/<int:event_id>')
def event_attendance(event_id):
    # Query the event info and join with attendance
    event = db.session.query(Event).filter_by(event_id=event_id).first()
    if not event:
        return f"No event found with ID {event_id}."

    attendance = db.session.query(
        Student.student_id, 
        Student.name
    ).join(
        Attends, Student.student_id == Attends.student_id
    ).filter(
        Attends.event_id == event_id
    ).all()

    # Count attendees
    total_attendance = len(attendance)

    # Format the result
    if not attendance:
        return f"No students are attending the event '{event.event_Name}'."

    result = [f"Event: {event.event_Name} ({total_attendance} attendees)"]
    for student_id, student_name in attendance:
        result.append(f"Student ID: {student_id}, Name: {student_name}")

    return "<br>".join(result)


@app.route('/student_events/<int:student_id>')
def student_events(student_id):
    # Query the student info
    student = db.session.query(Student).filter_by(student_id=student_id).first()
    if not student:
        return f"No student found with ID {student_id}."

    # Query events the student is attending
    events = db.session.query(
        Event.event_id,
        Event.event_Name,
        Event.event_DateTime,
        Event.Location,
        Event.event_Type
    ).join(
        Attends, Event.event_id == Attends.event_id
    ).filter(
        Attends.student_id == student_id
    ).all()

    # Format results
    if not events:
        return f"Student {student.name} is not attending any events."

    result = [f"Student: {student.name} (ID: {student.student_id})"]
    for event_ID, event_Name, event_DateTime, Location, event_Type in events:
        result.append(f"Event ID: {event_id}, Name: {event_Name}, DateTime: {event_DateTime}, Location: {Location}, Type: {event_Type}")

    return "<br>".join(result)

from datetime import datetime, timedelta

@app.route('/common_availability/<int:student1_id>/<int:student2_id>/<date>')
def common_availability(student1_id, student2_id, date):
    """
    Find common availability for two students on a specific day.

    :param student1_id: ID of the first student.
    :param student2_id: ID of the second student.
    :param date: The date to check availability (format: YYYY-MM-DD).
    """
    # Define the start and end of the day
    try:
        day_start = datetime.strptime(date, "%Y-%m-%d")
        day_end = day_start + timedelta(days=1)
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

    # Query from datetime import datetime, timedelta
    student1_busy = db.session.query(
        Event.event_DateTime,
        Event.event_Length
    ).join(
        Attends, Event.event_ID == Attends.event_ID
    ).filter(
        Attends.student_id == student1_id,
        Event.event_DateTime.between(day_start, day_end)
    ).all()

    # Query the busy times for student 2
    student2_busy = db.session.query(
        Event.event_DateTime,
        Event.event_Length
    ).join(
        Attends, Event.event_ID == Attends.event_ID
    ).filter(
        Attends.student_id == student2_id,
        Event.event_DateTime.between(day_start, day_end)
    ).all()

    # Combine busy times
    busy_times = []
    for event in student1_busy + student2_busy:
        event_start = event.event_DateTime
        # Directly use event.event_Length if it's already a timedelta
        event_end = event.event_DateTime + event.event_Length if isinstance(event.event_Length, timedelta) else event.event_DateTime + timedelta(minutes=event.event_Length)
        busy_times.append((event_start, event_end))

    # Merge overlapping busy intervals
    busy_times.sort()
    merged_busy_times = []
    for start, end in busy_times:
        if not merged_busy_times or merged_busy_times[-1][1] < start:
            merged_busy_times.append((start, end))
        else:
            merged_busy_times[-1] = (merged_busy_times[-1][0], max(merged_busy_times[-1][1], end))

    # Find free intervals between the busy times
    free_times = []
    current_time = day_start
    for start, end in merged_busy_times:
        if current_time < start:
            free_times.append((current_time, start))
        current_time = max(current_time, end)
    if current_time < day_end:
        free_times.append((current_time, day_end))

    # Format free intervals
    if not free_times:
        return f"No common availability for students {student1_id} and {student2_id} on {date}."

    result = [f"Common availability for students {student1_id} and {student2_id} on {date}:"]
    for start, end in free_times:
        result.append(f" - {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")

    return "<br>".join(result)

@app.route('/add_membership/<int:student_id>/<int:club_id>')
def add_membership(student_id, club_id):
    # Check if the student and club exist
    student = Student.query.get(student_id)
    club = Club.query.get(club_id)

    if not student or not club:
        return "Student or Club not found!"

    # Create the membership
    new_membership = Membership(student_id=student_id, club_id=club_id)
    db.session.add(new_membership)

    # Get all events for the club
    events = Event.query.filter_by(club_id=club_id).all()

    # Add each event to the Attends table for the student
    for event in events:
        # Check if the attendance already exists to avoid duplicates
        existing_attendance = Attends.query.filter_by(student_id=student_id, event_id=event.event_id).first()
        if not existing_attendance:
            new_attendance = Attends(student_id=student_id, event_id=event.event_id)
            db.session.add(new_attendance)

    # Commit the changes to the database
    db.session.commit()

    return f"Membership added for student {student_id} in club {club_id}. Events added to attendance."



