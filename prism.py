import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_mail import Message
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Kvarsha%4058@localhost/student_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'eB_6Q3eFZG*^4@PnKf5h7#8PbZjT9&Qv'

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        id_number = request.form['id_number']
        ssc_details = request.form['password']

        query = text("SELECT * FROM students_data WHERE ID_NUMBER = :id_number AND SSC_DETAILS = :ssc_details;")
        result = db.session.execute(query, {'id_number': id_number, 'ssc_details': ssc_details}).fetchone()

        if result:
            return redirect(url_for('index'))
        else:
            flash('Invalid ID Number or SSC Details')
            return redirect(url_for('student'))
    return render_template('student.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/guide')
def guide():
    guides = [
        {'name': 'Dr. Ratna Kumari. Ch', 'image': 'ratna mam.jpg', 'faculty_id': 1},
        {'name': 'Dr. Penugonda Ravi Kumar', 'image': 'ravi sir.jpg', 'faculty_id': 2},
        {'name': 'Mr. N. Satyanandaram', 'image': 'satya sir.jpg', 'faculty_id': 3},
        {'name': 'C. Suneetha', 'image': 'suneetha mam.jpg', 'faculty_id': 10},
        {'name': 'Mr. M Muni babu', 'image': 'muni sir.jpg', 'faculty_id': 8},
        {'name': 'Mr. K Vinod Kumar', 'image': 'vinod sir.jpg', 'faculty_id': 4},
        {'name': 'Mr. A Mahendra', 'image': 'mahendra sir.jpg', 'faculty_id': 5},
        {'name': 'Ms. P Udayasree', 'image': 'udaya mam.jpg', 'faculty_id': 7},
        {'name': 'Mr. P. Santhosh kumar', 'image': 'santhosh sir.jpg', 'faculty_id': 9},
        {'name': 'E. Susmitha', 'image': None, 'faculty_id': 6},
        {'name': 'S. Rajeswari', 'image': None, 'faculty_id': 11},
        {'name': 'V. Sravani', 'image': None, 'faculty_id': 12},
        {'name': 'R. Sreenivasulu', 'image': 'srinu sir.png', 'faculty_id': 13},
        {'name': 'K. Haribabu', 'image': None, 'faculty_id': 14},
        {'name': 'G. Swapna', 'image': None, 'faculty_id': 15}
    ]
    return render_template('guide.html', guides=guides)

# Route to get students under a specific guide
@app.route('/students/<int:faculty_id>')
def students(faculty_id):
    query = text("""
    SELECT students_data.STUDENT_NAME, students_data.ID_NUMBER, students_data.EMAIL_ID, students_data.project_title
    FROM students_data
    JOIN guide ON students_data.ID_NUMBER = guide.reg_id
    WHERE guide.faculty_id = :faculty_id
    """)
    result = db.session.execute(query, {'faculty_id': faculty_id})
    students = result.fetchall()
    students = [dict(STUDENT_NAME=row[0], ID_NUMBER=row[1], EMAIL_ID=row[2], project_title=row[3]) for row in students]
    return render_template('students.html', students=students)
    result = db.session.execute(query, {'faculty_id': faculty_id}).fetchall()
    return render_template('students.html', students=result)


@app.route('/profile/<int:faculty_id>')
def profile(faculty_id):
    query = text("SELECT * FROM faculty WHERE faculty_id = :faculty_id")
    faculty = db.session.execute(query, {'faculty_id': faculty_id}).fetchone()
    return render_template('profile.html', faculty=faculty)

@app.route('/project_checker', methods=['GET', 'POST'])
def project_checker():
    results = None
    message = None 
    
    if request.method == 'POST':
        project_title = request.form['project_title']
        query = text("""
        SELECT students_data.STUDENT_NAME, students_data.ID_NUMBER, students_data.SECTION_NAME, 
               students_data.EMAIL_ID, students_data.project_title, guide.guide_name
        FROM students_data
        JOIN guide ON students_data.ID_NUMBER = guide.reg_id
        WHERE students_data.project_title LIKE :project_title
        """)
        result = db.session.execute(query, {'project_title': f"%{project_title}%"})
        results = []
        for row in result.mappings():
            results.append({
                'STUDENT_NAME': row['STUDENT_NAME'],
                'ID_NUMBER': row['ID_NUMBER'],
                'SECTION_NAME': row['SECTION_NAME'],
                'EMAIL_ID': row['EMAIL_ID'],
                'project_title': row['project_title'],
                'guide_name': row['guide_name']
            })
        if not results:
            message = "No projects found matching the title."
        print("Results:", results)
        print("Message:", message)

    return render_template('project_checker.html', results=results, message=message)

@app.route('/student_profile/<string:id_number>')
def student_profile(id_number):
    query = text("""
    SELECT students_data.STUDENT_NAME, students_data.ID_NUMBER, students_data.SECTION_NAME, 
           students_data.EMAIL_ID, guide.guide_name
    FROM students_data
    JOIN guide ON students_data.ID_NUMBER = guide.reg_id
    WHERE students_data.ID_NUMBER = :id_number
    """)
    
    student = db.session.execute(query, {'id_number': id_number}).fetchone()
    
    if student:
        return render_template('profstudent.html', student=student)
    else:
        flash('Student not found.')
        return redirect(url_for('students'))
@app.route('/projects/<string:reg_id>')
def get_projects(reg_id):
    query = text("""
    SELECT DISTINCT 
        CASE 
            WHEN PROJECT_TITLE IS NULL OR PROJECT_TITLE = '' THEN 'No projects found'
            ELSE PROJECT_TITLE
        END AS PROJECT_TITLE
    FROM students_data
    WHERE ID_NUMBER = :reg_id
    """)
    result = db.session.execute(query, {'reg_id': reg_id}).fetchall()
    
    projects = [row[0] for row in result]

    # Check if the only result is "No projects found"
    if projects and projects[0] == 'No projects found':
        return jsonify({'message': 'No projects found'}), 404
    
    return jsonify({'projects': projects})


@app.route('/faculty_login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if password == 'rkv@cse':
            query = text("SELECT * FROM guide WHERE guide_name = :username")
            guide = db.session.execute(query, {'username': username}).fetchone()

            if guide:
                session['faculty_id'] = guide.faculty_id 
                session['faculty_name'] = guide.guide_name  
                return redirect(url_for('index1'))
            else:
                flash('Invalid username', 'error')
        else:
            flash('Invalid password', 'error')
        
        return redirect(url_for('faculty_login'))

    # GET request: Fetch all guides to display in the form
    query = text("SELECT DISTINCT guide_name FROM guide")
    result = db.session.execute(query).fetchall()
    guides = [{'name': row[0]} for row in result]

    return render_template('faculty_login.html', guides=guides)


@app.route('/logout')
def logout():
    return render_template('home.html')

@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/manage_proposals')
def manage_proposals():
    faculty_id = session.get('faculty_id')
    if not faculty_id:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('faculty_login'))

    # Fetch proposals for the logged-in guide
    query = text("SELECT * FROM projects WHERE guide_id = :guide_id")
    proposals = db.session.execute(query, {'guide_id': faculty_id}).fetchall()

    return render_template('manage_proposals.html', proposals=proposals)


@app.route('/propose_project', methods=['GET', 'POST'])
def propose_project():
    # Fetch guide names from the database
    query = text("SELECT distinct guide_name FROM guide")
    guides = [guide[0] for guide in db.session.execute(query).fetchall()]

    if request.method == 'POST':
        id_number = request.form['id_number']
        name = request.form['name']
        section = request.form['section']
        guide_name = request.form['guide_name']
        project_title = request.form['project_title']
        project_description = request.form['project_description']

        # Get the guide's faculty ID from the guide_name
        query = text("SELECT faculty_id FROM guide WHERE guide_name = :guide_name")
        result = db.session.execute(query, {'guide_name': guide_name}).fetchone()
        guide_id = result[0] if result else None

        if not guide_id:
            flash('Guide not found', 'error')
            return redirect(url_for('propose_project'))  # Handle case where guide is not found

        # Insert project with the guide_id
        query = text("""
        INSERT INTO projects (id_number, name, section, guide_name, project_title, project_description, guide_id)
        VALUES (:id_number, :name, :section, :guide_name, :project_title, :project_description, :guide_id)
        """)
        db.session.execute(query, {
            'id_number': id_number,
            'name': name,
            'section': section,
            'guide_name': guide_name,
            'project_title': project_title,
            'project_description': project_description,
            'guide_id': guide_id
        })
        db.session.commit()

        flash('Project proposed successfully!', 'success')
        return redirect(url_for('propose_project'))  # Redirect after successful proposal

    # Render the form and pass the guide names to the template
    return render_template('propose_project.html', guides=guides)



from flask_mail import Message, Mail

mail = Mail(app)


# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/update_proposal/<id_number>', methods=['POST'])
def update_proposal(id_number):
    app.logger.debug(f"Received ID_NUMBER: {id_number}")
    
    try:
        # Modify the query to only select the student's name and email
        query = text("""
        SELECT STUDENT_NAME, EMAIL_ID
        FROM students_data
        WHERE ID_NUMBER = :id_number
        """)
        
        # Fetch the student's name and email
        student = db.session.execute(query, {'id_number': id_number}).fetchone()
        
        app.logger.debug(f"Query result: {student}")

        # Check if student was found
        if student is None:
            app.logger.error("Student not found")
            flash('Student not found', 'error')
            return redirect(url_for('manage_proposals'))

        # Unpack the result only if student is not None
        student_name, email_id = student
        
        app.logger.debug(f"Student name: {student_name}, Email: {email_id}")
        
        # Get the project status from the form (e.g., 'Accepted' or 'Rejected')
        status = request.form['status']
        
        # Set the subject and body based on the status
        subject = "Project Proposal Status Update"
        if status == "Accepted":
            body = f"Dear {student_name},\n\nYour project proposal has been accepted."
            flash('Project proposal accepted and email sent to student!', 'success')
        elif status == "Rejected":
            body = f"Dear {student_name},\n\nYour project proposal has been rejected."
            flash('Project proposal rejected and email sent to student!', 'error')
        else:
            body = f"Dear {student_name},\n\nYour project proposal status is pending."

      
        sender_email = "kalyanicheppali8@gmail.com"
        sender_password = "zicrbpllsuikwwbw" 
        receiver_email = email_id
        
  
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

   
        message.attach(MIMEText(body, "plain"))

        # Send the email using smtplib
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                app.logger.debug(f"Email sent to {receiver_email}")

                # Update the proposal status in the database after sending the email
                update_query = text("""
                UPDATE projects
                SET status = :status
                WHERE id_number = :id_number
                """)
                db.session.execute(update_query, {'status': status, 'id_number': id_number})
                db.session.commit()

        except Exception as e:
            app.logger.error(f"Error sending email: {str(e)}")
            flash(f'Error sending email: {str(e)}', 'error')

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        flash(f"An error occurred: {str(e)}", 'error')

    return redirect(url_for('manage_proposals'))


if __name__ == '__main__':
    app.run(debug=True)


