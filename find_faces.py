import face_recognition
zac_image = face_recognition.load_image_file("zac1.jpg")
navi_image = face_recognition.load_image_file("navi1.jpg")

zac_encoding = face_recognition.face_encodings(zac_image)[0]
navi_encoding = face_recognition.face_encodings(navi_image)[0]

results = face_recognition.compare_faces([biden_encoding], unknown_encoding)