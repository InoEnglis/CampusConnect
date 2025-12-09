-----------------------------------------Campus Connect---------------------------------------
Just some random social media website that's created using python(django), CSS, HTML, some bootstrap, Tailwind and Allauth_UI.

Requirements
To completely run the project, you'll need:

1. Python 3.11

2. Django 6.0+

3. Redis (for WebSockets and Celery tasks)

PostgreSQL (optional you can use the default databse of django which is sqlite--Avoid using it in production)

-------Installation----------
Clone the repository

1. git clone https://github.com/YourUsername/CampusConnect.git
2. cd to the project
3. Create a virtual environment
   python -m venv venv
   Activate the virtual environment
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Create a .env file (or set them in your system) with:

DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
REDIS_URL=redis://127.0.0.1:6379/0

Apply migrations
  (python manage.py migrate)

------To run the project-------
1. Create a superuser
python manage.py createsuperuser

2. Run the development server
type in your terminal: python manage.py runserver
----NOTE:----
use daphne to use websocket features:
type in your terminal:  daphne -p 8000 (project's name).asgi:application.
The system might get laggy because daphne is not meant to serve media files and i recommend using nginx for it. (you can do it locally)

3. Start Redis (if not running, media uploads will not work)
redis-server


Features
1. User authentication and profiles
2. Create, edit, and delete posts
3.Commenting and file uploads (images, video, documents)
4.Groups with privacy settings and join requests
5.Real-time chat using WebSockets(not working for now)
6.Admin panel with user and content moderation
7.Feedback system
8. Personalization of feed (You might not feel this if u have few users).

Addtional NOTE:

If u signup using google it wont work.
if u sign up using gmail it will send a confirmation mail to your email and if u cant find it, check spam.
and always create ur virtual environment.
