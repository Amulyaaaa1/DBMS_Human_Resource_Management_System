from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
import os
from functools import wraps
app = Flask(__name__)

# Set the secret key for sessions and flash messages
app.secret_key = os.urandom(24)  # Generate a random secret key (24 bytes)


# MySQL connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234abcd",  # Replace with your MySQL password
        database="HRMprjt"  # Ensure this matches your database name
    )

# def execute_query(query, params=None, fetchall=False):
#     db = get_db_connection()
#     with db.cursor(dictionary=True) as cursor:
#         cursor.execute(query, params or ())
#         if fetchall:
#             return cursor.fetchall()
#         db.commit()
#     db.close()

def execute_query(query, params=None, fetchall=False, fetchone=False):
    db = get_db_connection()
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(query, params or ())
        if fetchone:
            return cursor.fetchone()  # Fetch a single result
        elif fetchall:
            return cursor.fetchall()   # Fetch all results
        db.commit()
    db.close()
    print(f"Executing query: {query}")



# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submission for adding employee data
@app.route('/submit', methods=['POST'])
def submit():
    emp_name = request.form['empName']
    query = "INSERT INTO Employee (firstname) VALUES (%s)"
    execute_query(query, (emp_name,))
    return redirect('/')

# Route to fetch and display data from the Employee table
@app.route('/view_employees', methods=['POST'])
def view_employees():
    employees = execute_query("SELECT * FROM Employee", fetchall=True)
    return render_template('index.html', employees=employees)

# Route to view salary details
@app.route('/view_salary', methods=['POST'])
def view_salary():
    salaries = execute_query("SELECT * FROM Salary", fetchall=True)
    return render_template('index.html', salaries=salaries)

# Route to view growth assessments
@app.route('/view_assessments', methods=['POST'])
def view_assessments():
    assessments = execute_query("SELECT * FROM GrowthAssessment", fetchall=True)
    return render_template('index.html', assessments=assessments)

# Route to view employee achievements
@app.route('/view_achievements', methods=['POST'])
def view_achievements():
    achievements = execute_query("SELECT * FROM EmployeeAchievements", fetchall=True)
    return render_template('index.html', achievements=achievements)

@app.route('/search_employee', methods=['POST'])
def search_employee():
    emp_name = request.form['empName']
    query = "SELECT * FROM Employee WHERE firstname LIKE %s OR lastname LIKE %s"
    employee = execute_query(query, (f"%{emp_name}%", f"%{emp_name}%"), fetchall=True)
    return render_template('index.html', employee=employee)

# Route for salary page
@app.route('/salary', methods=['GET'])
def salary_page():
    return render_template('salary.html')

# Route to filter employees by salary grade
@app.route('/filter_salary_grade', methods=['POST'])
def filter_salary_grade():
    grade = request.form.get('grade')
    query = """
        SELECT e.empid, e.firstname, e.lastname, s.salgrade, s.salary, s.sal_bonus
        FROM Employee e
        JOIN Salary s ON e.empid = s.empid
        WHERE s.salgrade = %s
    """
    filtered_employees = execute_query(query, (grade,), fetchall=True)
    return render_template('salary.html', filtered_employees=filtered_employees, selected_grade=grade)

# Function to get all employees
def get_all_employees():
    return execute_query("SELECT * FROM Employee", fetchall=True)

# Route to display the Employee Info page
@app.route('/employee-info', methods=['GET', 'POST'])
def employee_info():
    employees = get_all_employees()
    return render_template('empinfo.html', employees=employees)

# # Route to insert a new employee
# @app.route('/insert_employee', methods=['POST'])
# def insert_employee():
#     firstname = request.form['firstname']
#     lastname = request.form['lastname']
#     contributions = request.form['contributions']
#     starofthemonth = request.form.get('starofthemonth') == 'true'
#     no_of_yrs_at_comp = int(request.form['no_of_yrs_at_comp'])
#     achievements = request.form['achievements']

#     query = """
#         INSERT INTO Employee (firstname, lastname, contributions, starofthemonth, no_of_yrs_at_comp, achievements)
#         VALUES (%s, %s, %s, %s, %s, %s)
#     """
#     execute_query(query, (firstname, lastname, contributions, starofthemonth, no_of_yrs_at_comp, achievements))
    
#     return redirect(url_for('employee_info'))

@app.route('/insert_employee', methods=['POST'])
def insert_employee():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    contributions = request.form['contributions']
    starofthemonth = request.form.get('starofthemonth') == 'true'
    no_of_yrs_at_comp = int(request.form['no_of_yrs_at_comp'])
    achievements = request.form['achievements']  # This is still necessary for the EmployeeAchievements table

    # Insert the employee into the Employee table
    query = """
        INSERT INTO Employee (firstname, lastname, contributions, starofthemonth, no_of_yrs_at_comp)
        VALUES (%s, %s, %s, %s, %s)
    """
    execute_query(query, (firstname, lastname, contributions, starofthemonth, no_of_yrs_at_comp))
    
    # Get the last inserted employee id
    empid = get_last_inserted_empid()  # You'll need to create this function

    # Insert achievements into EmployeeAchievements table
    for achievement in achievements.splitlines():  # Assuming achievements are provided as multiple lines
        achievement = achievement.strip()  # Clean up whitespace
        if achievement:  # Only insert if there's something
            insert_achievement(empid, achievement)

    return redirect(url_for('employee_info'))

def insert_achievement(empid, achievement):
    query = """
        INSERT INTO EmployeeAchievements (empid, achievement)
        VALUES (%s, %s)
    """
    execute_query(query, (empid, achievement))


# # Route to update an existing employee
# @app.route('/update_employee', methods=['POST'])
# def update_employee():
#     empid = int(request.form['update_empid'])
#     firstname = request.form['update_firstname']
#     lastname = request.form['update_lastname']
#     contributions = request.form['update_contributions']
#     starofthemonth = request.form.get('update_starofthemonth') == 'true'
#     no_of_yrs_at_comp = int(request.form['update_no_of_yrs_at_comp'])
#     achievements = request.form['update_achievements']

#     query = """
#         UPDATE Employee SET firstname=%s, lastname=%s, contributions=%s, starofthemonth=%s,
#         no_of_yrs_at_comp=%s, achievements=%s WHERE empid=%s
#     """
#     execute_query(query, (firstname, lastname, contributions, starofthemonth, no_of_yrs_at_comp, achievements, empid))

#     return redirect(url_for('employee_info'))

@app.route('/update_employee', methods=['POST'])
def update_employee():
    empid = int(request.form['update_empid'])
    firstname = request.form['update_firstname']
    lastname = request.form['update_lastname']
    contributions = request.form['update_contributions']
    starofthemonth = request.form.get('update_starofthemonth') == 'true'
    no_of_yrs_at_comp = int(request.form['update_no_of_yrs_at_comp'])
    achievements = request.form['update_achievements']  # Assuming multiple achievements for update

    # Update the employee in the Employee table
    query = """
        UPDATE Employee SET firstname=%s, lastname=%s, contributions=%s, starofthemonth=%s,
        no_of_yrs_at_comp=%s WHERE empid=%s
    """
    execute_query(query, (firstname, lastname, contributions, starofthemonth, no_of_yrs_at_comp, empid))

    # Clear existing achievements for the employee if needed (optional)
    execute_query("DELETE FROM EmployeeAchievements WHERE empid=%s", (empid,))

    # Insert new achievements
    for achievement in achievements.splitlines():
        achievement = achievement.strip()
        if achievement:
            insert_achievement(empid, achievement)

    return redirect(url_for('employee_info'))

def get_last_inserted_empid():
    """Get the last inserted employee ID."""
    result = execute_query("SELECT LAST_INSERT_ID()", fetchone=True)
    return result[0] if result else None


# Route to delete an employee
@app.route('/delete_employee', methods=['POST'])
def delete_employee():
    empid = int(request.form['delete_empid'])
    execute_query("DELETE FROM Employee WHERE empid=%s", (empid,))
    return redirect(url_for('employee_info'))

# Route to get the average salary
@app.route('/average_salary', methods=['GET'])
def average_salary():
    avg_salary = execute_query("SELECT calculate_average_salary()", fetchall=True)
    return f'Average salary of employees: {avg_salary[0][0]}' if avg_salary else 'No salary data available.'




@app.route('/add_emp_record', methods=['POST'])
def add_emp_record():
    medical_leave = int(request.form['medical_leave'])
    vacation = int(request.form['vacation'])
    record_num = request.form['record_num']

    # Input validation
    if medical_leave > 30:
        flash("Medical leave days cannot exceed 30.", 'error')
        return redirect(url_for('get_emp_records'))

    # SQL query to add the record
    query = "INSERT INTO EmpRecords (MedicalLeave, Vacation, recordnum) VALUES (%s, %s, %s)"
    params = (medical_leave, vacation, record_num)

    add_result = execute_query(query, params)  # Execute query and capture any error

    # If there's an error message from the query
    if add_result:
        flash(add_result, 'error')  # Use flash to display the error message
        return redirect(url_for('get_emp_records'))  # Redirect to the records page
    
    # If successful
    flash("Record added successfully!", 'success')
    return redirect(url_for('get_emp_records'))  # Redirect to the records page

@app.route('/update_emp_record', methods=['POST'])
def update_emp_record():
    emp_record_id = request.form['emp_record_id']
    updated_medical_leave = int(request.form['updated_medical_leave'])
    updated_vacation = int(request.form['updated_vacation'])

    # Input validation
    if updated_medical_leave > 30:
        flash("Medical leave days cannot exceed 30.", 'error')
        return redirect(url_for('get_emp_records'))

    # SQL query to update the record
    query = "UPDATE EmpRecords SET MedicalLeave=%s, Vacation=%s WHERE EmpRecordID=%s"
    params = (updated_medical_leave, updated_vacation, emp_record_id)

    update_result = execute_query(query, params)  # Execute query and capture any error

    # If there's an error message from the query
    if update_result:
        flash(update_result, 'error')  # Use flash to display the error message
        return redirect(url_for('get_emp_records'))  # Redirect to the records page
    
    # If successful
    flash("Record updated successfully!", 'success')
    return redirect(url_for('get_emp_records'))  # Redirect to the records page

@app.route('/emp_records', methods=['GET'])
def get_emp_records():
    records = execute_query("SELECT * FROM EmpRecords", fetchall=True)
    return render_template('employee_records.html', emp_records=records)


# Route to get HR Department Employee Report
@app.route('/hr_department_employee_report', methods=['GET'])
def hr_department_employee_report():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Call the stored procedure
    cursor.callproc("GetHRDepartmentEmployeeReport")
    
    # Retrieve the results from the procedure
    hr_department_employee_report = []
    for result in cursor.stored_results():
        hr_department_employee_report = result.fetchall()
    
    cursor.close()
    connection.close()
    
    # Render the report in an HTML template
    return render_template('hr_department_employee_report.html', hr_department_employee_report=hr_department_employee_report)


# @app.route('/get_hr_and_department_info', methods=['POST'])
# def get_hr_and_department_info():
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     # Call the stored procedure
#     cursor.callproc("GetHRDepartmentEmployeeReport")
    
#     # Retrieve the results from the procedure
#     hr_and_department_info = []
#     for result in cursor.stored_results():
#         hr_and_department_info = result.fetchall()
    
#     cursor.close()
#     connection.close()
    
#     # Render the report in the same HTML template
#     return render_template('hr_department_employee_report.html', hr_department_employee_report=hr_and_department_info)

@app.route('/get_hr_and_department_info', methods=['POST'])
def get_hr_and_department_info():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Call the stored procedure
    cursor.callproc("GetHRDepartmentEmployeeReport")
    
    # Retrieve the results from the procedure
    hr_and_department_info = []
    for result in cursor.stored_results():
        hr_and_department_info = result.fetchall()
    
    cursor.close()
    connection.close()
    
    # Render the report in the same HTML template
    return render_template('hr_department_employee_report.html', hr_department_employee_report=hr_and_department_info, show_report=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SQL query to check user credentials
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, (username, password))
            user = cursor.fetchone()  # Fetch one user record

            if user:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))  # Redirect to home or another page
            else:
                flash('Invalid username or password.', 'danger')

        except mysql.connector.Error as err:
            flash(f'Database error: {err}', 'danger')
        finally:
            if cursor:
                cursor.close()  # Close cursor if it was created
            if db:
                db.close()  # Close the database connection

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # SQL query to insert a new user
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        
        try:
            execute_query(query, (username, password, role))  # Insert user data
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error registering user: {err}', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

# @app.route('/update_privileges')
# def privileges():
#     # Get grants for HR user
#     hr_grants_raw = execute_query("SHOW GRANTS FOR 'HR'@'localhost'", fetchall=True)

#     # Parse the privileges from the raw query result
#     hr_grants = []
    
#     if hr_grants_raw:
#         for grant in hr_grants_raw:
#             grant_statement = grant['Grants for HR@localhost']
#             # Extract the privileges from the GRANT statement (e.g., GRANT SELECT, INSERT, UPDATE ...)
#             privileges = grant_statement.split('ON')[0].replace('GRANT', '').strip()
#             hr_grants.extend(privileges.split(', '))  # Split multiple privileges by comma

#     # Get grants for admin user (optional, for verification)
#     admin_grants = execute_query("SHOW GRANTS FOR 'admin'@'localhost'", fetchall=True)

#     # Pass the grants data to the template for rendering
#     return render_template('update_privileges.html', hr_grants=hr_grants, admin_grants=admin_grants)



# @app.route('/edit_hr_privileges', methods=['GET', 'POST'])
# def edit_hr_privileges():
#     if request.method == 'POST':
#         # Get the selected privileges from the form
#         privileges = request.form.getlist('privileges')  # A list of selected privileges

#         # Print the selected privileges for debugging purposes
#         print("Selected Privileges: ", privileges)

#         # If no privileges were selected, show an error
#         if not privileges:
#             flash("No privileges selected! Please select at least one privilege.", "error")
#             return redirect(url_for('edit_hr_privileges'))

#         # Convert the list into a comma-separated string
#         selected_privileges = ', '.join(privileges)
#         print(f"Selected Privileges (String): {selected_privileges}")

#         # Update the privileges for HR user (first remove previous grants and then apply new ones)
#         # Drop the old privileges
#         execute_query("REVOKE ALL PRIVILEGES ON *.* FROM 'HR'@'localhost'")

#         # Grant the new privileges
#         for priv in privileges:
#             query = f"GRANT {priv} ON HRMprjt.* TO 'HR'@'localhost'"
#             execute_query(query)

#         flash("Privileges updated successfully!", "success")
#         return redirect(url_for('privileges'))

#     # Display the form with available privileges
#     available_privileges = [
#         'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'INDEX'
#     ]
#     return render_template('edit_hr_privileges.html', available_privileges=available_privileges)


# Role-based access control decorator
def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if user is logged in and has the correct role
            if 'role' not in session or session['role'] != role:
                flash("You do not have access to this page.", 'error')
                return redirect(url_for('login'))  # Redirect to login if not authorized
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/update_privileges')
@role_required('admin')  # Only admin can access this route
def privileges():
    # Get grants for HR user
    hr_grants_raw = execute_query("SHOW GRANTS FOR 'HR'@'localhost'", fetchall=True)

    # Parse the privileges from the raw query result
    hr_grants = []
    
    if hr_grants_raw:
        for grant in hr_grants_raw:
            grant_statement = grant['Grants for HR@localhost']
            # Extract the privileges from the GRANT statement (e.g., GRANT SELECT, INSERT, UPDATE ...)
            privileges = grant_statement.split('ON')[0].replace('GRANT', '').strip()
            hr_grants.extend(privileges.split(', '))  # Split multiple privileges by comma

    # Get grants for admin user (optional, for verification)
    admin_grants = execute_query("SHOW GRANTS FOR 'admin'@'localhost'", fetchall=True)

    # Pass the grants data to the template for rendering
    return render_template('update_privileges.html', hr_grants=hr_grants, admin_grants=admin_grants)

@app.route('/edit_hr_privileges', methods=['GET', 'POST'])
@role_required('admin')  # Only admin can access this route
def edit_hr_privileges():
    if request.method == 'POST':
        # Get the selected privileges from the form
        privileges = request.form.getlist('privileges')  # A list of selected privileges

        # Print the selected privileges for debugging purposes
        print("Selected Privileges: ", privileges)

        # If no privileges were selected, show an error
        if not privileges:
            flash("No privileges selected! Please select at least one privilege.", "error")
            return redirect(url_for('edit_hr_privileges'))

        # Convert the list into a comma-separated string
        selected_privileges = ', '.join(privileges)
        print(f"Selected Privileges (String): {selected_privileges}")

        # Update the privileges for HR user (first remove previous grants and then apply new ones)
        # Drop the old privileges
        execute_query("REVOKE ALL PRIVILEGES ON *.* FROM 'HR'@'localhost'")

        # Grant the new privileges
        for priv in privileges:
            query = f"GRANT {priv} ON HRMprjt.* TO 'HR'@'localhost'"
            execute_query(query)

        flash("Privileges updated successfully!", "success")
        return redirect(url_for('privileges'))

    # Display the form with available privileges
    available_privileges = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'INDEX'
    ]
    return render_template('edit_hr_privileges.html', available_privileges=available_privileges)

# Route for the dashboard
@app.route('/dashboard')
def dashboard():
    if 'role' not in session:  # Check if user is logged in and has a role
        return redirect(url_for('login'))  # Redirect to login if no role is found in session
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)
