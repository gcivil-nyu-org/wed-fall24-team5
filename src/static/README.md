# Static Files Directory

This directory is used to store static assets for the Django project. These assets include CSS, JavaScript files, images, fonts, and other media files that are necessary for the front-end of the application.

## Usage

- Place CSS, JavaScript, and image files in appropriate subdirectories under `static/`.
  - `static/css/` for CSS files
  - `static/js/` for JavaScript files
  - `static/images/` for image files

Django will collect all static files from this directory when running `python manage.py collectstatic` before deployment.

If you want to customize Bulma:
1. Install `sass` globally: `brew install sass/sass/sass`
2. Once you have modified the scss files, run: `sass src/static/bulma/bulma.scss src/static/bulma/css/bulma.css`

## Structure:

```
static/
├── css/
│   └── main.css
├── js/
│   └── main.js
└── images/
    └── logo.png
```
