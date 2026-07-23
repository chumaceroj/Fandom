## Screenshots
 
<!-- Add screenshots of the site here -->
 
---
 
## Description
 
<!-- Describe what FanVerse is and what it does -->
 
## Motivation
 
<!-- Why we built this project -->
 
## Features
 
<!-- List features organized by category -->
 
## Installation
 
### Prerequisites
 
- Python 3.10 or newer
- Git
### Setup
 
```bash
git clone https://github.com/chumaceroj/FanVerse.git
cd FanVerse
pip install django
```
 
### Database Setup
 
```bash
cd Fandom
python manage.py makemigrations
python manage.py migrate
```
 
### Creating an Admin Account (Optional)
 
```bash
python manage.py createsuperuser
```
 
### Running the Server
 
```bash
python manage.py runserver
```
 
Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
 
## Usage
 
<!-- Describe how to use the site once it's running -->
 
## Project Structure
 
```
Fandom/
├── README.md
├── LICENSE
├── fandomsite/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blogs/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── context_processors.py
│   └── templates/blogs/
│       ├── base.html
│       ├── index.html
│       ├── detail.html
│       ├── comment_item.html
│       ├── profile.html
│       ├── profile_settings.html
│       ├── post_settings.html
│       ├── notifications.html
│       ├── create_blog.html
│       ├── edit_blog.html
│       ├── edit_comment.html
│       ├── edit_profile.html
│       ├── change_username.html
│       ├── delete_account.html
│       ├── login.html
│       └── register.html
└── manage.py
```
 
## Technologies
 
- Python
- Django
- HTML
## Known Limitations
 
<!-- List any known bugs or limitations -->
 
## Authors
 
- Julian Chumacero
- Lewhat Kahsay
 
## License
This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.