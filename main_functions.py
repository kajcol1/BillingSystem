import mysql.connector

# Funkcja łącząca się z bazą danych
def connect_to_database():
    connection = mysql.connector.connect(
        host="",
        user="",
        password="",
        database="e"
    )
    return connection




# Funkcja pobierająca listę dzieci z saldem dla danej grupy
def get_children_with_balances(group_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        Children.child_id,
        Children.first_name,
        Children.last_name,
        SUM(Payments.amount) - (21*7 - COALESCE((
            SELECT COUNT(absences_id) FROM Absences WHERE Absences.child_id = Children.child_id
        ), 0)) * MealRates.rate AS balance
    FROM
        Children
    LEFT JOIN Payments ON Children.child_id = Payments.child_id
    LEFT JOIN MealRates ON 1 = 1
    WHERE
        Children.group_id = %s
    GROUP BY
        Children.child_id,
        Children.first_name,
        Children.last_name
""", (group_id,))
    

    children = cursor.fetchall()
    connection.close()

    return children

# Funkcja zwracająca liczbę dni roboczych w danym miesiącu
def get_working_days(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    working_days = sum(1 for day in range(1, days_in_month + 1) if datetime.date(year, month, day).weekday() < 5)
    return working_days
