The project is about a face login applicatioin, where real-time image is captured using webcam and it is compared with images in the database(employee_data.db). If the image matches with any of the images in the employees table in sqlite3 database, the application welcomes the person in the image, along with his/her details and image. And employee details containing name, login time, etc., of the person is written in the Attendance.csv file.  Other wise, login fails and nothing is written in the Attendance.csv file. If the same persoon's image is captured more that one time, we are redirected to the same welcome page, but there is no re-entry of the same person's details more than one time in Attendance.csv.
First run the faceApp.py in the terminal. It will show an IP address. Follow the link.
index.html opens in the browser. Click on "login now" button. An image of yours is captured.
If the image matches, we are redirected to welcome.html. Otherwise, we are redirected to not_authorized.html.
images folder contains all the images of employees.
static/images contain the images for building the website.
templates contain all the html files.
Attendance.csv is the record file where employee details are written into.
sql.ipynb is used to create the database, employees table, populate it with records and delete the records.
