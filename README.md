# Food Waste Reduction App

## Project Overview

This project aims to develop a mobile application that tackles food waste and food insecurity in NYC. It connects businesses, restaurants, and individuals with surplus food to users in need, promoting a more sustainable and equitable food system.

### Problem Statement

- Food Waste: Businesses discard substantial amounts of surplus food daily, contributing to environmental and economic burdens.
- Food Insecurity: Many individuals and families, particularly in NYC's homeless population, face food shortages and limited access to healthy meals.

### Target Users

- Business Owners: Restaurants, delis, and grocery stores with surplus food to donate or sell at discounted prices.
- Food Insecure Individuals: People seeking affordable or free food.
- Community Organizations: Groups that coordinate food drives or manage community fridges.
- General Users: Individuals offering extra food from events or looking for discounted food options.

### Vision Statement

Our vision is to create a platform that fosters a strong community network by connecting surplus food sources with those in need. By facilitating food donation, reduced prices, and efficient food access, we strive to:

- Reduce food waste and its associated environmental and economic impacts.
- Combat food insecurity by providing access to nutritious food for underserved communities.
- Promote sustainability within the food system by encouraging resourcefulness and reducing waste.
- Cultivate a culture of community care by enabling businesses, individuals, and organizations to contribute to a more equitable and food-secure society.

### Key Features

- Food Donations: Businesses/Restaurants/Users can list surplus food for donation
- Real-time food availability dashboard: Users can browse offerings from nearby businesses and individuals in real-time.
- Location-based search: Find nearby donation locations and discounted food options.
- Seamless communication: Users can coordinate food pickups or ask questions through messaging between the person picking up and the vendor or donor, not between donors or receivers.
- User Reviews and Ratings: Recipients can leave reviews and ratings for businesses and organizations, sharing their experiences to guide future users.
- Maps Integration: Locate nearby donation sites and community fridges with integrated Google Maps/similar maps for easy navigation.

## Getting started with Development

### Project Structure

```
.
├── .github/ # GitHub workflows and settings
├── system_design_docs/ # System design documentation
├── README.md # This file
├── src/ # Django application root
│ ├── manage.py # Django management script
│ └── myproject/ # Main Django project folder
├── static/ # Static files (CSS, JS, images)
├── templates/ # HTML templates for front-end
└── venv/ # Virtual environment files
```

### Prerequisites

- Python 3.x
- pip (Python package installer)
- Virtualenv (optional but recommended)

### Setup Instructions

1. Clone the repository

   ```bash
   git clone https://github.com/gcivil-nyu-org/wed-fall24-team5
   cd wed-fall24-team5
   ```

2. Set up the virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations

   ```bash
   python src/manage.py migrate
   ```

5. Run development server

   ```bash
   python src/manage.py runserver
   ```

## Development

### Branches

- Branches must be named as follows in order for a pull request with that branch to be accepted: `branch-type/issue-##/short-description`

  - branch-type must be one of `bugfix`, `feature`, `hotfix`, `chore`, `release`, `test`, `doc`, or `refactor`

### Pull Requests

- Ensure your branch follows the appropriate naming conventions (above)
- While only one review is required, aim for two reviews.
- Do not resolve conversations you did not create. All conversations should be resolved before merging
  - If your change after opening the Pull Request greatly modified your code, you should request a re-review
- All tests and lints should pass before merging
- Only the developer who opened the Pull Request should merge the Pull Request
- Always use `Squash and merge` to keep the commit history clean
- Delete branch after merging to keep the branch tree clean

## Linting

This project uses `pylint` for linting and formatting Python files and `djlint` for HTML templates. To run linting locally:

```bash
pylint src/
djlint src/templates/
```

## Running tests

- More information will come as tests and coverage are added

## Deployment

- This application is set up for deployment using AWS Elastic Beanstalk. Detailed deployment instructions will be added when the application is ready for deployment.
