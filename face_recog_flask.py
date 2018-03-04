# This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains a picture of Barack Obama.
# The result is returned as json. For example:
#
# $ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_picture_of_obama": true
# }
#
# This example is based on the Flask file upload example: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# NOTE: This example requires flask to be installed! You can install it with pip:
# $ pip3 install flask

import os
import sys
from argparse import ArgumentParser

import base64
import face_recognition
from flask import Flask, jsonify, send_file, Response, json, request, redirect, render_template, url_for
import re
from PIL import Image
import sqlite3 as sql
from io import BytesIO
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
AUDIO_FORMATS = {"ogg_vorbis": "audio/ogg",
                 "mp3": "audio/mpeg",
                 "pcm": "audio/wave; codecs=1"}

session = Session(profile_name="adminuser")
polly = session.client("polly")

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/read', methods=['GET'])
def read():
    """Handles routing for reading text (speech synthesis)"""
    # Get the parameters from the query string
    try:
        outputFormat = request.args.get('outputFormat')
        text = request.args.get('text')
        voiceId = request.args.get('voiceId')
    except TypeError:
        raise InvalidUsage("Wrong parameters", status_code=400)

    # Validate the parameters, set error flag in case of unexpected
    # values
    if len(text) == 0 or len(voiceId) == 0 or \
            outputFormat not in AUDIO_FORMATS:
        raise InvalidUsage("Wrong parameters", status_code=400)
    else:
        try:
            # Request speech synthesis
            response = polly.synthesize_speech(Text=text,
                                               VoiceId=voiceId,
                                               OutputFormat=outputFormat)
        except (BotoCoreError, ClientError) as err:
            # The service returned an error
            raise InvalidUsage(str(err), status_code=500)

        return send_file(response.get("AudioStream"),
                         AUDIO_FORMATS[outputFormat])



@app.route('/voices', methods=['GET'])
def voices():
    """Handles routing for listing available voices"""
    params = {}
    voices = []

    try:
        # Request list of available voices, if a continuation token
        # was returned by the previous call then use it to continue
        # listing
        response = polly.describe_voices(**params)
    except (BotoCoreError, ClientError) as err:
        # The service returned an error
        raise InvalidUsage(str(err), status_code=500)

    # Collect all the voices
    voices.extend(response.get("Voices", []))

    return jsonify(voices)














@app.route('/')
def home():
    return render_template('index.html')




@app.route('/up', methods=['GET', 'POST'])
def index():
    #print(request.files['file'].filename)
    #image_data = str(request.form['imgBase64'])
    image_data = request.files['file']
    image_string = base64.b64encode(image_data.read())
    #print(image_string)
    #image_64_decode = base64.decodebytes(image_string) 

    #print(image_64_decode[0:30])
    #image_data = re.sub('^data:image/.+;base64,', '', image_data)
    im = Image.open(BytesIO(base64.b64decode(image_string)))
    im.save('out2.png')
    img = Image.open("out2.png")

    
    res = detect_faces_in_image()
    #print(res)

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response


def detect_faces_in_image():
    # Pre-calculated face encoding of Obama generated with face_recognition.face_encodings(img)



    # Load the uploaded image file
    #img = face_recognition.load_image_file(file_stream)
    img = face_recognition.load_image_file("out2.png")
    # Get face encodings for any faces in the uploaded image
    if len(face_recognition.face_encodings(img)) > 0:
        unknown_face_encodings = face_recognition.face_encodings(img)[0]
    else:
        return {
            "nobody": "nobody",
            "relation": "none",
            "info": "no info"
         }
    face_found = False
    is_zac = False
    is_navi = False

    face_distances = []
    known_encodings = []
    known_names = []
    if len(unknown_face_encodings) > 0:
        face_found = True


        for filename in os.listdir("./known_people/"):
            if filename.endswith(".jpg"): 
                print(os.path.join("../", filename))

                # Load some images to compare against
                known_image = face_recognition.load_image_file(os.path.join("./known_people", filename))

                # Get the face encodings for the known images
                known_encoding = face_recognition.face_encodings(known_image)[0]
                known_encodings.append(known_encoding)
                known_names.append(filename[:-4])

        face_distances = face_recognition.face_distance(known_encodings, unknown_face_encodings)

        min_dist = 1
        name = "nobody"

        for i, face_distance in enumerate(face_distances):
            if face_distance < min_dist and face_distance < .5:
                min_dist = face_distance
                name = known_names[i]

            print("{} distance: {}".format(known_names[i], face_distance))
            print()

        con = sql.connect("hackathon.db")
        cur = con.cursor()
        print("select * from visitors where name = '{0}'".format(name))
        cur.execute("select * from visitors where name = '{}'".format(name))
        rows = cur.fetchall()


            # See if the first face in the uploaded image matches the known face of Obama


        result = {
            "name": name,
            "relation": rows[0][1],
            "info": rows[0][2]
         }
    else:
        result = {
            "nobody": "nobody",
            "relation": "none",
            "info": "no info"
         }



    # Return the result as json

    return result

cli = ArgumentParser(description='Example Flask Application')
cli.add_argument(
    "-p", "--port", type=int, metavar="PORT", dest="port", default=8000)
cli.add_argument(
    "--host", type=str, metavar="HOST", dest="host", default="localhost")
arguments = cli.parse_args()


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=5002, debug=True)


