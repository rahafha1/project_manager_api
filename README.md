# 🧩 Task Management API with Role-Based Access Control (Django + DRF)

This project is a RESTful API for managing projects and tasks using Django Rest Framework, with strict role-based permissions (Admin - Manager - Member).

---

## ⚙️ Main Features:

- ✅ **JWT Authentication** for secure login and access.
- 🛡️ **Role-based Access Control**:
  - Only the **Project Manager** can update/delete the project or create tasks.
  - Only the **Project Manager** or the **Assigned Member** can update/delete a task.
  - **Project Members** can view only tasks within their projects.
  - Both **Project Manager** and **Assigned Member** can create tasks within their projects.
- 📁 **Data Models**:
  - **Project**: Represents a project with a manager.
  - **Task**: A task linked to a project and assigned to a user.
  - **ProjectMember**: Connects users to projects as members.

---

## 🏗️ Data Models Overview:

- `Project`: name, description, manager.
- `Task`: title, description, status (`todo`, `in_progress`, `done`), due date, project, assigned user.
- `ProjectMember`: a many-to-many link between projects and users.

---

## 🔐 Authentication & Permissions:

- JWT authentication:
  - `POST /api/token/` to obtain token.
  - `Authorization: Bearer <token>` required for protected endpoints.
- Custom permissions:
  - `IsProjectManager`: manages access to projects.
  - `IsTaskManagerOrAssignee`: restricts task actions.
  - `IsAdminOrManager`: extra control if expanded in the future.

---

## 🔎 Filtering & Search:

- Task filtering supports:
  - By status: `/tasks/?status=todo`
  - By due date: `/tasks/?due_date=2025-06-01`
  - By project: `/tasks/?project=1`
  - By assigned user: `/tasks/?assigned_to=3`
- Keyword search in:
  - Task title: `/tasks/?search=meeting`
  - Task description: `/tasks/?search=important details`

---

## ✅ Unit Tests

Comprehensive test cases included to verify:

- Project and task creation by authorized roles (managers and assigned members).
- Permission enforcement by role.
- Update/delete access restrictions.
- Project visibility based on membership.
- Filtering and searching tasks by title and description.
- Access denial without token.

---

## 🚀 Getting Started (Optional)

- git clone <https://github.com/rahafha1/project_manager_api>
- cd <your path>
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py runserver




## POSTMAN tests :

- 1- REGISTER:
examples:
5 users, 1 admin ,2 manager
- METHOD :POST
- http://127.0.0.1:8000/api/register/
- MEMBERS :
- Body → raw → JSON:
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "Pass123!"
}

{
  "username": "user2",
  "email": "user2@example.com",
  "password": "Password456"
}


{
  "username": "user3",
  "email": "user3@example.com",
  "password": "MyPass789"
}

{
  "username": "user4",
  "email": "user4@example.com",
  "password": "User4Pass"
}

{
  "username": "user5",
  "email": "user5@example.com",
  "password": "User5Pass123"
}


- send!
- ADMIN :
- create superuser from terminal : python manage.py createsuperuser  ,
- example:
{
  "username": "adminuser",
  "email": "admin@example.com",
  "password": "AdminPass!2025"
}

- MANAGER :
- whenever you create project ,  you are the MANAGER !

- right now all the projects have the admin as there manager otherwise you need to login as a member 
- then copy paste the token then change the url to 
- METHOD :POST-> http://127.0.0.1:8000/api/projects/
- then : Body → raw → JSON:
{
  "name": " project8 ",
  "description": "888888"
}
- and in this way the member becomes the manager of this task because he created it !
- NOW ->example:
- user1 IS MANAGER  :
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "Pass123!"
}
-  PROJECTS THAT THIS USER IS MANAGER IN THEM :
{
  "name": "roro1 project  ",
  "description": "roro1 "
}
{
  "name": "roro1 project 2  ",
  "description": "roro1 "
}
{
  "name": "roro1 project 3  ",
  "description": "roro1 "
}
- TO KNOW ANY USER ID ->
- http://localhost:8000/admin -> USER -> CHANGE ->
- IN JSON YOU WILL HANDLE IDS OR IN CHROME YOU WILL HANDLE INTERFACES EASIER 
- POSTMAN:
- user1  HAS THE ID=  (8,9,10) FOR His 3 PROJECTS 
- ((user1 ID=1 ))AS A USER AND MANAGER IS 
- user1 ((PROJECT ID=8)) THE MEMBERS ARE (( user3 ID=3  ,user5 ID=5  ,user4 ID=4 ))

- 2- LOGIN :

- METHOD :POST ->
- http://127.0.0.1:8000/api/login/

- Body → raw → JSON:
{
  "username": "user1",
  "password": "Pass123!"
}


- access : EXample
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ4NTI5MjAzLCJpYXQiOjE3NDg1MjU2MDMsImp0aSI6ImE5MzE1NTg1YWM3NzRjOTU5ODMyMTQ4YWI4M2FjMTZmIiwidXNlcl9pZCI6MX0.EVq8Pktt6OsQd7CtFP9MYOVTz5OxU5FrPADBn2I2hkI

- 3- REFRESH TOKEN:

- METHOD :POST ->
- http://127.0.0.1:8000/api/token/refresh/


- 4- ADD PROJECTS :
- METHOD :POST->
- http://127.0.0.1:8000/api/projects/

- Body → raw → JSON:


- COPY ACCESS TOKEN (((  from the admin OR any one else that is the manager ))))
 - -> THEN -> GO TO -> auth:

- bearer token : paste TOKEN here 
- then:

- Body → raw → JSON:
{
  "name": "first project ",
  "description": "test project"
}

{
  "name": "second project ",
  "description": "ss project"
}
{
  "name": "project1",
  "description": "111111"
}

{
  "name": "project2",
  "description": "222222"
}
{
  "name": "project3",
  "description": "333333"
}

{
  "name": "project4",
  "description": "444444"
}
{
  "name": "project5",
  "description": "555555"
}

- TO SEE THEM :
- METHOD :GET ->
- http://127.0.0.1:8000/projects/



- 5- ADMIN REGISTER :
- TERMINAL : python manage.py createsuperuser

  "username": "adminuser",
  "email": "admin@example.com",
  "password": "AdminPass!2025"


- 6-ADMIN CONTROL:
- the access to http://127.0.0.1:8000/admin/ is forbiden if you don't login as admin
- you have to login with admin informations .
- SO YOU LOGIN AS ADMIN :
- METHOD :POST ->
- http://127.0.0.1:8000/api/login/

- Body → raw → JSON:
{
  "username": "adminuser",
  "password": "AdminPass!2025"
}

- then copy paste his token .
- then youcan control by changing th link url and the method 

- 6- CREATE NEW PROJECT :
- POSTMAN :
- LOGIN AS ADMIN -> COPY TOKEN -> POST -> http://localhost:8000/api/projects/ 
- -> AUTH HEADER PASTE TOKEN (from whoever )->
-  Body → raw → JSON:
{
  "name": "TASK MANAGER PROJECT ",
  "description": " TASK CREATE TEST"
}
- THEN -> enter 

- 7-ADD MEMBERS TO THE PROJECT :
- FROM TERMINAL :
- python manage.py runserver
-  ->FROM CHROME or POSTMAN -> http://localhost:8000/admin/ -> LOGIN AS SUPERUSER -> 
- then from chrome :
- you open to ( core -> project_members -> +add -> chose ( project_name & members( add them one by one ))

- ADD MEMBER TO PROJECT FROM POSTMAN :


- 8-CREATE NEW TASK IN PROJECT :
- THE TASK IS ONLY FOR ONE MEMBER OF THE PROJECT
- ** (THE PROJECT HAS MAY MEMBERS THE TASK IS FOR ONE OF THEM )**
- LOGIN THE MANAGER OR THE ADMIN -> COPY PAST THE TOKEN -> 
- METHOD : POST ->
- URL :http://localhost:8000/api/tasks/
- Body -> Json :
  {
  "project": 1,
  "title": "frontend development",
  "description": "create auth form",
  "assigned_to": 2,
  "status": "todo",
  "due_date": "2025-06-01"
}


- NOTES:
- 1-THE MANAGERS SEES ALL HIS PROJECTS BY ->
- METHOD :GET ->
- http://127.0.0.1:8000/projects/
- THEN HE CAN MEMORIZE THE ID OF THE PROJECTS THAT HE WANTS LINK THEM WITH SPACIFIC TASK , AND USE IT


- 2-IN JSON YOU WILL HANDLE IDS
- 3-IN CHROME YOU WILL HANDLE INTERFACES EASIER 
- 4-TO KNOW ANY USER ID ->

- http://localhost:8000/admin -> USER -> CHANGE -> IT LOOKS ON URL IF YOU PRESSED.
- 5-IN OUR CASE :
- 6- user1  HAS THE ID=  (8,9,10) FOR His 3 PROJECTS 
- ((user1 ID=1 ))AS A USER AND MANAGER IS 
- user1 ((PROJECT ID=8)) THE MEMBERS ARE (( user3 ID=3  ,user5 ID=5  ,user4 ID=4 ))


- TRY IT NOW TO ADD NEW TASK TO PROJECT MEMBER 5 !!!

- EX :
- Body -> Json :
{
  "project": 8,
  "title": "frontend development",
  "description": "create auth form",
  "assigned_to": 5,
  "status": "todo",
  "due_date": "2025-06-01"
}



- 7-FILTERING THE RESAULTS:
- GET ->
- http://localhost:8000/api/tasks/

- COPY ACCESS TOKEN -> THEN -> GO TO -> auth:

- bearer token : paste TOKEN here

- THEN :
- http://localhost:8000/api/tasks/?status=todo
- http://localhost:8000/api/tasks/?due_date=2025-06-05
- http://localhost:8000/api/tasks/?project=1
- http://localhost:8000/api/tasks/?assigned_to=3
- OR SUMMON THEM ALL
- http://localhost:8000/api/tasks/?status=todo&assigned_to=3&project=1


- 8- SEARCH 
- ((THE USER SEARCH FOR SOME TASK THAT HE HAS ))
- FOR THE TASK TITLE OR DESCRIPTION : IN THE TASKS THAT THE USER HAS ACCESS TO IT ONLYYY 
- soooo -> login -> token -> example:
- METHOD :GET
- URL: http://127.0.0.1:8000/tasks/?search=front
- the resault is the task that contains the word "front " .

- 9- TESTS :
-  terminal : python manage.py test -> ENTER .
-  THE TESTS INCLUDES  :
-  1- access permissions 
-  2- create projects and tasks 
-  3- filtering and search .
