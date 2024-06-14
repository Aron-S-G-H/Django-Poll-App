<h1 align="center">🌟 Django Poll App 🌟</h1>

<p align="center">Django poll app is a full featured polling app. You have to register in this app to show the polls and to vote. If you already voted you can not vote again. Only the owner of a poll can add poll , edit poll, update poll, delete poll , add choice, update choice, delete choice and end a poll. If a poll is ended it can not be voted. Ended poll only shows user the final result of the poll. There is a search option for polls. Also user can filter polls by name, publish date, and by number of voted. Pagination will work even after applying filter.</p>

---
<p>Parent repository: <a href="https://github.com/devmahmud/Django-Poll-App">Django-Poll-App</a> by devmahmud</p>

---

## What has changed ? 🤔
- Using Poetry instead of pip
- Dockerizing the project
- Adding extensive tests to check views and URLs
- Adding the ability to log in with Instagram and GitHub (Facebook, Linkedin and Google already exists)
- Converting all function-based views to class-based views
- Some code clean up
- Better README file

## 🛠 Installation
1. **Clone the repository**

   `git clone https://github.com/Aron-S-G-H/Django-Poll-App.git`

   then...

   `cd Django-Poll_app`

2. **Create and activate a virtual environment**

   `python3 -m venv venv` or `virtualenv venv`

   then...

   `source venv/bin/activate`

3. **Install dependencies**

   `pip install -r requirements.txt poetry`

   then...

   `poetry install`

4. **Setup DB**

   `python manage.py makemigrations` then `python manage.py migrate`

5. **Create superuser for admin panel**

   `python manage.py createsuperuser`

6. **Create some dummy text**

   `python manage.py shell` then `import seeder` then `seeder.seed_all(5)`

   Here 5 is a number of entry. You can use it as your own

7. **Start the app**

   `python manage.py runserver`

## 🔧 Configuring OAuth login
<details>
<summary>Obtaining OAuth Client ID for Google</summary>

1. **Go to the Google Cloud Console:**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/).
   - Sign in with your Google account.

2. **Create a new project:**
   - Click on the project dropdown menu at the top of the page.
   - Click on "New Project" and follow the prompts to create a new project.

3. **Enable the Google Identity service:**
   - In the Google Cloud Console, navigate to "APIs & Services" > "Dashboard."
   - Click on "Enable APIs and Services."
   - Search for "Google Identity" or "Google+ API" and enable it for your project.

4. **Create OAuth consent screen:**
   - In the Google Cloud Console, navigate to "APIs & Services" > "OAuth consent screen."
   - Fill in the required fields (like application name, user support email, etc.).
   - Add scopes (permissions) your application requires.
   - Save the consent screen information.

5. **Create OAuth credentials:**
   - In the Google Cloud Console, navigate to "APIs & Services" > "Credentials."
   - Click on "Create Credentials" > "OAuth client ID."
   - Select "Web application" as the application type.
   - Enter a name for your OAuth client.
   - Add authorized redirect URIs : `http://127.0.0.1:8000/complete/google-oauth2/`
   - Click "Create."

6. **Copy the client ID and client secret:**
   - Once the OAuth client is created, you'll see your client ID and client secret.
   - Copy these values and update the following variables in settings.py

        ```
        SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'
        SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'
        ```

For detailed instructions, refer to Google's documentation on [OAuth 2.0](https://developers.google.com/identity/protocols/oauth2).
</details>

<details>
  <summary>Obtaining OAuth Client ID for LinkedIn</summary>

  ### Step 1: Create a LinkedIn App
  1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/) and sign in.
  2. Click on "Create App" and fill in the required details, such as the app name, description, and logo.
  3. In the "Authorized Redirect URLs" section, add the callback URL for your Django app. This URL will be like `http://127.0.0.1:8000/complete/linkedin/`.
  4. Save the changes and note down the Client ID and Client Secret provided by LinkedIn.

  ### Step 2: Configure Django Settings
  
    1. Update the following settings to your settings file, replacing `'your-linkedin-client-id'` and `'your-linkedin-client-secret'` with your actual LinkedIn app credentials:
     ```python
     SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = 'your-client-id'
     SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = 'your-client-secret'
     ```
</details>

## 🚀 Run with Docker
---
<h4 align="center">⚠️ Ensure that you have Docker installed before you proceed</h4>

---
1. clone the repository : `https://github.com/devmahmud/Django-Poll-App.git`
2. go to the directory : `cd Django-Poll-App`
3. create an image : `docker build -t pollsapp:latest --no-cache .`
4. run a container : `docker run --name pollsapp -p 8000:8000 -d pollsapp:latest`
5. Then go to http://127.0.0.1:8000 in your browser
### if you want to create some dummy text data follow the step below
1. after you run a container : `docker exec -it pollsapp bash`
2. `python manage.py shell`
3. `import seeder`
4. create 5 dummy texts data : `seeder.seed_all(5)`
### if you want to create super user
1. after you run a container : `docker exec -it pollsapp bash`
2. `python manage.py createsuperuser`
#### for OAuth login , before you create an image, update the following settings in your Dockerfile
```python
   ENV GOOGLE_OAUTH2_KEY=your_client_id
   ENV GOOGLE_OAUTH2_SECRET=your_client_secret
   
   ENV LINKEDIN_OAUTH2_KEY=your_client_id
   ENV LINKEDIN_OAUTH2_SECRET=your_client_secret
   
   ENV FACEBOOK_OAUTH2_KEY=your_client_id
   ENV FACEBOOK_OAUTH2_SECRET=your_client_secret
   
   ENV INSTAGRAM_OAUTH2_KEY=your_client_id
   ENV INSTAGRAM_OAUTH2_SECRET=your_client_secret
   
   ENV GITHUB_KEY=your_client_id
   ENV GITHUB_SECRET=your_client_secret
 ```

## 📷 Project snapshot
<h3>Home page</h3>
<div align="center">
    <img src="https://github.com/Aron-S-G-H/Django-Poll-App/blob/master/static/img/pic.png" width="100%"</img> 
</div>

<h3>Login Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51409509-36c8a000-1b8c-11e9-845a-65b49262aa53.png" width="100%"</img> 
</div>

<h3>Registration Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51409562-5cee4000-1b8c-11e9-82f6-1aa2df159528.png" width="100%"</img> 
</div>

<h3>Poll List Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51409728-d423d400-1b8c-11e9-8903-4c08ba64512e.png" width="100%"</img> 
</div>

<h3>Poll Add Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51409796-fe759180-1b8c-11e9-941b-c1202956cca4.png" width="100%"</img> 
</div>

<h3>Polling page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51409843-1e0cba00-1b8d-11e9-9109-cceb79a6a623.png" width="100%"</img> 
</div>

<h3>Poll Result Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51409932-60ce9200-1b8d-11e9-9c83-c59ba498ca8b.png" width="100%"</img> 
</div>

<h3>Poll Edit Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51410008-92dff400-1b8d-11e9-8172-c228e4b60e28.png" width="100%"</img> 
</div>

<h3>Choice Update Delete Page</h3>
<div align="center">
    <img src="https://user-images.githubusercontent.com/19981097/51410442-dc7d0e80-1b8e-11e9-8f8e-18e6d7bb70fb.png" width="100%"</img> 
</div>

<h2>Author</h2>
<blockquote>
  Aron Sadegh<br>
  Email: aronesadegh@gmail.com
</blockquote>
