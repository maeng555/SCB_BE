import requests
url = 'http://127.0.0.1:8000/api/auth'

response = requests.post(url,data={'username':'admin','password':'123123'})
print(response.text)

myToken = response.json() #중요
token = myToken['token']

header ={'Authorization' : 'Token '+token}
response=requests.get('http://127.0.0.1:8000/api/student_list',headers=header)
print(response.text)