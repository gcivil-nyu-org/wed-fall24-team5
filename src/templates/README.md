# Templates Directory

This directory is used to store the HTML templates for the Django application. Templates are rendered by Django’s template engine.

## Usage

- Place HTML files directly in this folder or organize them in subdirectories
- Django will search for templates in this directory to render the views of application.
- You can extend the base template in other templates to maintain consistent layout across the site.

```jinja
{% extends 'base.html' %}
```

## Structure:

```
templates/
├── base.html # Base template used across multiple pages
├── index.html # Example home page template
└── account/
  └── login.html # Template for login page
```
