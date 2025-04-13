import requests
from bs4 import BeautifulSoup

def check_dashboard():
    """
    Check if student names are showing in the admin dashboard
    """
    # Create a session to handle cookies
    session = requests.Session()

    # Login first
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status code: {login_response.status_code}")

    # Make a request to the admin dashboard using the session
    response = session.get('http://127.0.0.1:5000/admin/dashboard')

    # Print the status code
    print(f"Status code: {response.status_code}")

    # Save the HTML content to a file
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("HTML content saved to dashboard.html")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Print all h5 elements to find the correct one
    print("All h5 elements:")
    for h5 in soup.find_all('h5'):
        print(f"- {h5.text.strip()}")

    # Find the recent attendance table
    recent_attendance_heading = soup.find('h5', string=lambda text: 'Recent Attendance' in text if text else False)
    if recent_attendance_heading:
        recent_attendance_table = recent_attendance_heading.find_parent('div').find_parent('div').find('table')
    else:
        print("Recent Attendance heading not found")
        recent_attendance_table = None

    # Print the table rows
    if recent_attendance_table:
        rows = recent_attendance_table.find_all('tr')
        for row in rows[1:]:  # Skip the header row
            cells = row.find_all('td')
            if cells:
                student_name = cells[0].text.strip()
                course_name = cells[1].text.strip()
                date = cells[2].text.strip()
                status = cells[3].text.strip()
                marked_by = cells[4].text.strip()
                time = cells[5].text.strip()

                print(f"Student: {student_name}, Course: {course_name}, Date: {date}, Status: {status}, Marked By: {marked_by}, Time: {time}")
    else:
        print("Recent attendance table not found")

if __name__ == "__main__":
    check_dashboard()
