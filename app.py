import os
import time
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
from gradio_client import Client as GradioClient, file
from confidential import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, PARENT_FOLDER_ID
import requests
from PIL import Image
from io import BytesIO
import os
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import threading


gradio_client = GradioClient('Nymbo/Virtual-Try-On')
app = Flask(__name__)
user_data = {}


@app.route('/whatsapp', methods = ['POST'])
def whatsapp():
    sender_id = request.form.get('From')  
    incoming_msg = request.form.get('Body')  
    media_url = request.form.get('MediaUrl0')  
    num_media = int(request.form.get('NumMedia'))  
    response = MessagingResponse()
    if num_media > 0 and sender_id:
        if sender_id not in user_data:
            user_data[sender_id] = {}
        if 'human_image' not in user_data[sender_id]:
            user_data[sender_id]['human_image'] = media_url 
            response.message('Person image received. Now, please upload the garment image you want to try-on.')
        elif 'garment_image' not in user_data[sender_id]:
            user_data[sender_id]['garment_image'] = media_url  
            response.message('Garment image received. The try-on result is being processed. Please give us around a minute.')
            threading.Thread(target = handle_try_on, args = (sender_id, user_data[sender_id]['human_image'], media_url)).start()
            user_data.pop(sender_id, None)
        else:
            response.message('You have already uploaded both images. Please wait for the result.')
    else:
        response.message('Welcome to Virtual Try-On. To proceed please upload a person image first.')
    return str(response)


def handle_try_on(sender_id, human_image_url, garment_image_url):
    human_image_path = download_image(human_image_url)
    garment_image_path = download_image(garment_image_url)
    result = process_virtual_try_on(human_image_path, garment_image_path)
    if result:
        public_result = upload_photo(result)
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        media_response = twilio_client.messages.create(
            body = 'Here is your try-on result',
            from_ = TWILIO_WHATSAPP_NUMBER,
            to = sender_id,
            media_url = [public_result] 
        )


def download_image(image_url):
    try:
        session = requests.Session()
        response = session.get(image_url, auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            if not os.path.exists('images'):
                os.makedirs('images')
            filename = Path(image_url).name + '.jpg'
            save_path = os.path.join('images', filename)
            image.save(save_path)
            print(f'Image successfully saved to {save_path}')
        else:
            print(f'Failed to retrieve the image. Status code: {response.status_code}')
    except Exception as e:
        print(f'An error occurred: {e}')
    return save_path         


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "service_account.json"


def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)
    return creds


def upload_photo(file_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials = creds)
    file_metadata = {
        'name': 'Hello',
        'parents': [PARENT_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype = 'image/png')  
    file = service.files().create(
        body = file_metadata,
        media_body = media,
        fields = 'id'  
    ).execute()
    permission = {
        'role': 'reader',
        'type': 'anyone'  
    }
    service.permissions().create(
        fileId = file.get('id'),
        body = permission
    ).execute()
    file_link = f"https://drive.google.com/uc?id={file.get('id')}"
    return file_link


def process_virtual_try_on(human_image, garment_image):
    try:
        result = gradio_client.predict(
            dict = {'background': file(human_image), 'layers': [], 'composite': None},
            garm_img = file(garment_image),
            garment_des = 'Hello!!',
            is_checked = True,
            is_checked_crop = False,
            denoise_steps = 30,
            seed = 42,
            api_name = '/tryon'
        )
        print(result[0])
        return result[0]  
    except Exception as e:
        print(f'Error in Gradio API: {e}')
        return None


if __name__ == '__main__':
    os.makedirs('images', exist_ok = True)
    app.run(port = 10000, debug = True)