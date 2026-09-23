#Get Employees Data from API
#this ApiUser has no PERMISSION:"empapp.view_detail_employee" 

import requests

get_url = "http://127.0.0.1:8000/api/EmployeeModelViewSet/2/"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg1MDU2Mjg3LCJpYXQiOjE3ODUwNTU5ODcsImp0aSI6ImJjMDYyMzcwMmU2NjQ3MWQ4YzRjNDkzOGZiYWMxMTBjIiwidXNlcl9pZCI6IjUifQ.lqGr1E7iYuYjgTBh0lh7nRIGIWd4xapnUgF_pgQSR4A"
headers = {
    "Authorization":f"Bearer {access_token}"
}

response = requests.get(get_url, headers=headers)
print(response)
print(response.history)
print(response.url)
print(response.text)
print(response.json)
