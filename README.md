# Attendance-System
This project is build to record attendance from a csv file and store it in an excel file.

It is a flask-based web app developed to record attendance as present(1) or absent(0) from the csv input file and store it as output in an excel file. It first gets maximum duration of class, then in accordance with the minimum percentage of presence given it marks the presence of each student. It then compares the names of student in input to that of output and marks the present in output sheet with respective name.

Please install the follwing libraries:
- flask
- flask-sqlalchemy
- datetime
- pathlib
- pandas
- numpy

#### Note: 
This project is assumed to work with the record maintained from the google meet chrome extension(https://chrome.google.com/webstore/detail/google-meet-attendance-li/appcnhiefcidclcdjeahgklghghihfok?hl=en).
