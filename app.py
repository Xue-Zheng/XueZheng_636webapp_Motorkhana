from flask import Flask, flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect
#test
app = Flask(__name__)
app.secret_key = 'QQQWWWEEE123123'

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return redirect(url_for('overall'))

@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("SELECT * FROM driver INNER JOIN car WHERE driver.car = car.car_num ;")
    driverList = connection.fetchall()

    return render_template("driverlist.html", driver_list = driverList)    

@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM driver INNER JOIN car WHERE driver.car = car.car_num;")
    driverList = connection.fetchall()
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList, driver_list=driverList)

@app.route("/graph")
def showgraph():
    connection = getCursor()
    overall_list, driverList = get_overall_all()
    bestDriverList = []
    resultsList = []
    for i in range(len(overall_list)):
        if i >= 5:
            break
        item = overall_list[i]
        bestDriverList.append(str(item[0]) + ' ' +  item[1])
        resultsList.append(item[-2])

    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)

def get_overall(runList):
    run_bests = []
    for i in range(len(runList)):
        if i % 2 == 1:
            run_this = runList[i]
            run_last = runList[i - 1]
            if run_this[-1] is None and run_last[-1] is None:
                run_bests.append([run_this[0], 'dnf'])
            elif run_this[-1] is None and run_last[-1] is not None:
                run_bests.append([run_last[0], run_last[-1]])
            elif run_this[-1] is not None and run_last[-1] is None:
                run_bests.append([run_this[0], run_this[-1]])
            else:
                if run_this[-1] <= run_last[-1]:
                    run_bests.append([run_this[0], run_this[-1]])
                else:
                    run_bests.append([run_last[0], run_last[-1]])

    overall_result = 0
    for run in run_bests:
        if run[-1] == 'dnf':
            overall_result = 'NQ'
            break
        else:
            overall_result += run[-1]
    if overall_result != 'NQ':
        overall_result = round(overall_result, 2)

    return run_bests, overall_result

@app.route('/run_list/<int:driver_id>')
def run_list(driver_id):
    connection = getCursor()
    connection.execute("SELECT * FROM driver ;")
    driverList = connection.fetchall()
    connection = getCursor()
    connection.execute("SELECT driver.driver_id, driver.first_name, driver.surname, car.model, car.drive_class FROM driver INNER JOIN car WHERE driver.car = car.car_num AND driver.driver_id = %s;", (driver_id,) )
    driver_info = connection.fetchone()
    connection = getCursor()
    connection.execute("SELECT course.name, run_num, seconds, cones, wd FROM run INNER JOIN course WHERE dr_id=%s AND run.crs_id=course.course_id ORDER BY crs_id, run_num;", (driver_id,))
    runList = connection.fetchall()
    for i in range(len(runList)):
        run = runList[i]
        run = list(run)
        total = run[-3]
        if total is None:
            pass
        else:
            if run[-2] is not None:
                total += 5 * run[-2]
            if run[-1] is not None:
                total += 10 * run[-1]
        if run[-2] is None:
            run[-2] = 0
        run.append(total)
        runList[i] = tuple(run)

    run_bests, overall_result = get_overall(runList)

    return render_template("runlist.html", run_list = runList, run_best_list = run_bests, overall_result=overall_result, driver_info=driver_info, driver_list=driverList)


def custom_sort(item):
    element = item[-2]

    if element == "NQ":
        return float('inf')
    else:
        return element

def get_overall_all():
    overall_list = []
    connection = getCursor()
    connection.execute("SELECT * FROM driver ;")
    driverList = connection.fetchall()
    for driver in driverList:
        driver_id = driver[0]
        driver_name = driver[1] + ' ' + driver[2]
        if driver[4] is not None and driver[4] <= 16:
            driver_name += ' (J)'
        connection = getCursor()
        connection.execute(
            "SELECT course.name, run_num, seconds, cones, wd FROM run INNER JOIN course WHERE dr_id=%s AND run.crs_id=course.course_id ORDER BY crs_id, run_num;",
            (driver_id,))
        runList = connection.fetchall()
        for i in range(len(runList)):
            run = runList[i]
            run = list(run)
            total = run[-3]
            if total is None:
                pass
            else:
                if run[-2] is not None:
                    total += 5 * run[-2]
                if run[-1] is not None:
                    total += 10 * run[-1]
            if run[-2] is None:
                run[-2] = 0
            run.append(total)
            runList[i] = tuple(run)
        run_bests, overall_result = get_overall(runList)
        car_id = driver[-1]
        connection = getCursor()
        connection.execute(
            "SELECT model FROM car WHERE car_num=%s;",
            (car_id,))
        car_name = connection.fetchone()[0]
        overall_list.append([driver_id, driver_name, car_name, run_bests, overall_result, None])
        overall_list = sorted(overall_list, key=custom_sort)
        for i in range(len(overall_list)):
            if i == 0:
                overall_list[i][-1] = '🏆'
            elif i <= 4:
                overall_list[i][-1] = '💵'
            else:
                overall_list[i][-1] = ''

    return overall_list, driverList

@app.route("/overall")
def overall():
    overall_list, driverList = get_overall_all()
    return render_template("overall.html", overall_list = overall_list, driver_list=driverList)

@app.route("/admin")
def admin():
    connection = getCursor()
    connection.execute("SELECT d1.driver_id, d1.first_name, d1.surname, d1.date_of_birth, d1.age, d1.caregiver, d2.first_name, d2.surname FROM driver as d1 INNER JOIN driver as d2 WHERE d1.caregiver = d2.driver_id ORDER BY d1.age DESC;")
    driverList = connection.fetchall()

    search_content = request.args.get('search_content')
    if search_content is None:
        connection = getCursor()
        connection.execute("SELECT * FROM driver ;")
        driverList2 = connection.fetchall()
    else:
        connection = getCursor()
        connection.execute("SELECT * FROM driver WHERE first_name LIKE %s OR surname LIKE %s;", (f'%{search_content}%', f'%{search_content}%'))
        driverList2 = connection.fetchall()

    connection = getCursor()
    connection.execute("SELECT * FROM driver ;")
    driverList3 = connection.fetchall()

    driver_id_to_edit_runs = request.args.get('driver_id_to_edit_runs')
    if driver_id_to_edit_runs is not None:
        connection = getCursor()
        connection.execute(
            "SELECT first_name, surname FROM driver WHERE driver_id=%s;",
            (driver_id_to_edit_runs,))
        driverName = connection.fetchone()
        driverName = driverName[0] + ' ' + driverName[1]
        connection = getCursor()
        connection.execute(
            "SELECT course.name, run_num, seconds, cones, wd FROM run INNER JOIN course WHERE dr_id=%s AND run.crs_id=course.course_id ORDER BY crs_id, run_num;",
            (driver_id_to_edit_runs,))
        runList = connection.fetchall()
        for i in range(len(runList)):
            run = runList[i]
            run = list(run)
            total = run[-3]
            if total is None:
                pass
            else:
                if run[-2] is not None:
                    total += 5 * run[-2]
                if run[-1] is not None:
                    total += 10 * run[-1]
            if run[-2] is None:
                run[-2] = 0
            run.append(total)
            runList[i] = tuple(run)
    else:
        runList = []
        driverName = None

    connection = getCursor()
    connection.execute("SELECT * FROM driver ;")
    driverList4 = connection.fetchall()
    for driver in driverList4:
        if driver[-3] is not None and driver[-3] <= 16:
            driverList4.remove(driver)

    connection = getCursor()
    connection.execute("SELECT * FROM car ;")
    carList = connection.fetchall()

    return render_template("admin.html", driver_list=driverList, driver_list2=driverList2, driver_list3=driverList3, driver_list4=driverList4, run_list = runList, driver_name = driverName, driver_id_to_edit_runs = driver_id_to_edit_runs, car_list = carList)

@app.route("/edit_run", methods=['POST'])
def edit_run():
    cones = request.form.get('cones')
    wd = request.form.get('wd')
    driver_id_to_edit_runs = request.form.get('driver_id_to_edit_runs')
    run = request.form.get('run')
    course_name = request.form.get('course_name')

    connection = getCursor()
    connection.execute(
        "SELECT course_id FROM course WHERE name = %s;",
        (course_name,))
    course_id = connection.fetchone()[0]

    if cones is not None:
        connection = getCursor()
        connection.execute(
            "UPDATE run SET cones = %s WHERE dr_id=%s AND crs_id = %s AND run_num = %s;",
            (cones, driver_id_to_edit_runs, course_id, run))
    if wd is not None:
        connection = getCursor()
        connection.execute(
            "UPDATE run SET wd = %s WHERE dr_id=%s AND crs_id = %s AND run_num = %s;",
            (wd, driver_id_to_edit_runs, course_id, run))
    return redirect(url_for('admin', driver_id_to_edit_runs = driver_id_to_edit_runs))

@app.route("/add_driver", methods=['POST'])
def add_driver():
    driver_id_to_edit_runs = request.form.get('driver_id_to_edit_runs')
    if driver_id_to_edit_runs == 'None':
        driver_id_to_edit_runs = None
    first_name = request.form.get('firstName')
    surname = request.form.get('surname')
    driver_type = request.form.get('driverType')
    date_of_birth = request.form.get('dateOfBirth')
    if date_of_birth is None or len(date_of_birth) == 0:
        age = None
    else:
        birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
        current_date = datetime.now()
        age = current_date.year - birth_date.year - (
                    (current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    caregiver = request.form.get('careGiver')
    if driver_type != 'Junior':
        caregiver = None
    car = request.form.get('carList')
    if driver_type == 'Junior':
        connection = getCursor()
        connection.execute(
            "SELECT car FROM driver WHERE driver_id = %s;",
            (caregiver,))
        car = connection.fetchone()[0]
        if age is None:
            flash('Junior show enter a birthday.', 'warning')
            return redirect(url_for('admin', driver_id_to_edit_runs=driver_id_to_edit_runs))
    connection = getCursor()
    connection.execute(
        "INSERT INTO driver (first_name, surname, date_of_birth, age, caregiver, car) VALUES (%s, %s, %s, %s, %s, %s);",
        (first_name if first_name else None, surname if surname else None, date_of_birth if date_of_birth else None, age if age else None, caregiver if caregiver else None, car if car else None))
    id = connection.lastrowid
    connection = getCursor()
    connection.execute(
        "SELECT course_id FROM course;")
    courses = connection.fetchall()
    for course in courses:
        course_id = course[0]
        for i in range(1, 3):
            connection = getCursor()
            connection.execute("INSERT INTO run values (%s, %s, %s, NULL, NULL, 0)", (id, course_id, i))
    return redirect(url_for('admin', driver_id_to_edit_runs = driver_id_to_edit_runs))


