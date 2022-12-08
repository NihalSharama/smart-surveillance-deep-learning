import tkinter as tk
from tkinter import filedialog, Text
from utils import predict_on_realtime, send_sms_to_auth_sinch
import requests
from constants import *

# constants
SEQUENCE_LENGTH = 50

root = tk.Tk()
root.title("Smart Surveillance Camera")
root.geometry("450x600")
root.config(bg='#263D42')

# variables
name_var = tk.StringVar()
mobile_var = tk.StringVar()
location_var = tk.StringVar()
isCameraStarting = tk.BooleanVar()

with open('user_config.txt', 'r') as f:
    config = f.read().split('|')

    name_var.set(config[0])
    mobile_var.set(config[1])
    location_var.set(config[2])


def sub_config_btn():
    name = name_var.get()
    mobile = mobile_var.get()
    location = location_var.get()

    with open('user_config.txt', 'w') as f:

        f.write(name + '|')
        f.write(mobile + '|')
        f.write(location + '|')

    sinch_url = f'{API_URL}/alert/register_user/'

    body = {
        "user_name": name,
        "user_mobile": mobile,
        "user_location": location,
    }

    r = requests.post(sinch_url, json=body)

    if r.status_code == 200:
        print('Registered Successfully!')


def start_surveillance():
    isCameraStarting.set(True)
    predict_on_realtime('realtime_predictions.mp4', SEQUENCE_LENGTH)


title = tk.Label(root, text='Smart Surveillance Camera ', font=(
    'calibre', 16, 'bold'), bg='#263D42', fg='white')


name_label = tk.Label(root, text='Your Name', font=(
    'calibre', 10, 'bold'), bg='#263D42', fg='white')
name_entry = tk.Entry(root, textvariable=name_var,
                      font=('calibre', 10, 'normal'))

mobile_label = tk.Label(root, text='Your Mobile', font=(
    'calibre', 10, 'bold'),  bg='#263D42', fg='white')
mobile_entry = tk.Entry(root, textvariable=mobile_var,
                        font=('calibre', 10, 'normal'),)

location_label = tk.Label(root, text='Your Location', font=(
    'calibre', 10, 'bold'),  bg='#263D42', fg='white')
location_entry = tk.Entry(root, textvariable=location_var,
                          font=('calibre', 10, 'normal'))

subConfigBtn = tk.Button(root, text='Submit',  padx=10,
                         pady=5, fg='white', bg='#42b2c2', command=sub_config_btn, )

startSurveillance = tk.Button(
    root, text='Start Surveillance', padx=10, pady=8, fg='white', bg='#263D42', command=start_surveillance, )
cameraStarted = tk.Label(root, text='Camera Starting.....', font=(
    'calibre', 10, 'bold'), bg='#263D42', fg='red')

title.grid(row=0, column=1, pady=(20, 40))
name_label.grid(row=1, column=0, pady=2)
name_entry.grid(row=1, column=1, pady=2)
mobile_label.grid(row=2, column=0, pady=2)
mobile_entry.grid(row=2, column=1, pady=2)
location_label.grid(row=3, column=0, pady=2)
location_entry.grid(row=3, column=1, pady=2)

subConfigBtn.grid(row=4, column=0, pady=10)
startSurveillance.grid(row=5, column=1, pady=(50, 0))


root.mainloop()
