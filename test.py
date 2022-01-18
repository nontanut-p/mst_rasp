
import csv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth()

# Create local webserver and auto handles authentication.
gauth.LoadClientConfigFile('client_secrets.json')
drive = GoogleDrive(gauth)
upload_file_list = ['2022-1-7-17:9.png','202217-16-31.csv' ]


file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
file1.SetContentString('Hello World!') # Set content of the file from given string.
file1.Upload()



file2 = drive.CreateFile()
file2.SetContentFile(upload_file_list[0])
file2.Upload()


file2 = drive.CreateFile()
file2.SetContentFile(upload_file_list[1])
file2.Upload()

