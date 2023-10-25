
# Blog-App
## Description
This is a Blogging site developed with Python and the Flask microframework. It allows users to create profiles about themselves, follow other users whose posts they like, comment on posts and edit their own posts. It is embedded with RESTful API allowing users to create, edit and delete posts or commands.
## Installation
Install the project with 
```bash
  $ git clone https://github.com/Ian-Musima/flask-blog.git
  $ python -m venv env
  $ source env/Scripts/activate
  $ ./init.sh
  $ flask run
```
## Usage/Examples
To use the API create an access token with:
```bash
$ curl -H "Content-Type: application/json" -d
'{"username":"user1","password":"password"}' http://localhost:5000/auth/api
```
Use the token to access API-protected resources, as follows:
```bash
export
ACCESS="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyOGZjMDNkOC0xY2MyLT
QwZDQtODJlMS0xMGQ0Mjc2YTk1ZjciLCJleHAiOjE1MzIwMTg4NDMsImZyZXNoIjpmYWxzZSwia
WF0IjoxNTMyMDE3OTQzLCJ0eXBlIjoiYWNjZXNzIiwibmJmIjoxNTMyMDE3OTQzLCJpZGVudGl0
eSI6InVzZXIxIn0.Cs-ANWq0I2M2XMrZpQof-_cX0gsKE7U4UG1t1rB0UoY"
```
To access all the posts on a particular page:
```bash
$ curl -H "Authorization: Bearer $ACCESS"
"http://localhost:5000/api/post?page=2"
```
To access posts of a particular user:
```bash
$ curl -H "Authorization: Bearer $ACCESS"
"http://localhost:5000/api/post?user=user1"
```
To create a new post:
```bash
$ curl -X POST -H "Authorization: Bearer $ACCESS" -H "Content-Type:
application/json" -d '{"title":"Example Title", "text":"Example text"}'
"http://localhost:5000/api/post"
```
To edit a particular post:
```bash
$ curl -X PUT -H "Authorization: Bearer $ACCESS" -H "Content-Type:
application/json" \
 -d '{"title": "Modified From REST", "text": "this is from REST",
"tags": ["tag1","tag2"]}' \
http://localhost:5000/api/post/5
```
To delete a particular post:
```bash
$ curl -X DELETE -H "Authorization: Bearer $ACCESS"
http://localhost:5000/api/post/102
```
To get a comment to a particular post:
```bash
$ curl -H "Authorization: Bearer $ACCESS" "http://localhost:5000/api/comment/300"
```
To get all the comments at a particular page:
```bash
$ curl -H "Authorization: Bearer $ACCESS" "http://localhost:5000/api/comment?page=1"
```
To edit a particular comment:
```bash
$ curl -X PUT -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" -d '{"name":"user_poster", "text":"Modified from RESTAPI"}' "http://localhost:5000/api/comment/315"
```
To create a new comment on a post:
```bash
$ curl -X POST -H "Authorization: Bearer $ACCESS" -H "Content-Type:
application/json" \
 -d '{"name": "user_poster", "text": "this is from RESTAPI"}' 'http://localhost:5000/api/post/5/comments'
```
To delete a particular comment:
```bash
$ curl -X DELETE -H "Authorization: Bearer $ACCESS" "http://localhost:5000/api/comment/315"
```
## Running Tests
To run tests, run the test server in different terminal with the following command:
```bash
  $ python run_test_server.py
```
Then, run the command:
```bash
  $ python -m unittest discover
```

## Acknowledgements
The following resources were used:

- [Mastering Flask Web Development](https://www.packtpub.com/product/mastering-flask-web-development-second-edition/9781788995405)
 - [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
