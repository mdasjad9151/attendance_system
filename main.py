import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import os
import mysql.connector as c
import numpy as np
import time
from datetime import datetime, date

# database connections
con = c.connect(
    # host ='locahost',
    user='root',
    passwd='Asjad#8330',
    database='finalproject'
)

cursor = con.cursor()
# video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

#  graphics rendreing
imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, employeeIds = encodeListKnownWithIds
# print(employeeIds)
print("Encode File Loaded")

modeType = 0

imgemployee = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    # print(faceCurFrame)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)
            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)
            

            if matches[matchIndex]:
                # print("Known Face Detected")
                date = date.today()
                times = datetime.now()

                empid = employeeIds[matchIndex]
                pauseTime = time.time() + 5

                date_query = "SELECT attendace_date FROM hrm_attendance WHERE emp_id = %s"
                count_query = "SELECT attendance_count FROM hrm_attendance WHERE emp_id = %s"
                cursor.execute(date_query, (empid,))
                date_result = cursor.fetchone()

                cursor.execute(count_query, (empid,))
                count_result = cursor.fetchone()

                if date_result and date_result[0] != date:
                    update_attendance_count = int(count_result[0]) + 1
                    quary = "UPDATE hrm_attendance SET attendance_time = %s, attendace_date = %s, attendance_count = %s WHERE emp_id = %s"
                    cursor.execute(quary, (times, date, update_attendance_count, empid))
                    con.commit()

                

                    modeType =  1
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                else:
                    modeType =  2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                
                # cover face area 

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                # modeType = 1
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                # print("match")
            else:
                    modeType = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                # modeType = 1
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    # print("dosnt match")

                
               

                # print(empid)

    cv2.imshow("Automated Attendance System", imgBackground)
    cv2.waitKey(1)
    modeType = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
