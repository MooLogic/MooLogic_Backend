
# MooLogic  - Best Practices (Backend with django)

## Project Overview

This Django project is designed to be a scalable, maintainable, and collaborative application. The following guidelines are set to ensure consistency, readability, and ease of collaboration among team members.

## Table of Contents
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Coding Best Practices](#coding-best-practices)
- [Naming Conventions](#naming-conventions)
- [Function Naming Conventions](#function-naming-conventions)
- [Model Conventions](#model-conventions)
- [Testing](#testing)
- [Version Control](#version-control)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MooLogic/MooLogic_Backend.git
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations and run the server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## Project Structure

```bash
moologic/
│
├── moologic/             # Project settings and root URL configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── app_name/                 # Each Django app should have this structure
│   ├── migrations/           # Migration files
│   ├── templates/            # HTML templates
│   ├── static/               # Static files (CSS, JS, images)
│   ├── models.py             # Database models
│   ├── views.py              # View logic
│   ├── forms.py              # Django Forms
│   ├── serializers.py        # Django REST Framework serializers (if applicable)
│   ├── admin.py              # Admin site configuration
│   └── tests.py              # Unit and integration tests
│
├── manage.py
└── requirements.txt
```

---

## Coding Best Practices

1. **Follow PEP8 Guidelines**: 
   - Use meaningful variable names, with clear and concise function names.
   - Keep code modular and reusable.
   - Use 4 spaces per indentation level (never use tabs).
   - Max line length: 79 characters.

2. **DRY Principle**: Avoid duplication. If code is reused, abstract it into a function or utility.

3. **Use Django's ORM**: Always use Django’s built-in ORM methods instead of raw SQL queries for better security, readability, and maintainability.

4. **Error Handling**: Use `try-except` blocks where appropriate to handle exceptions, and log errors using Django's logging framework.

5. **Environment Variables**: Sensitive information such as API keys, database passwords, and secret keys should be stored in environment variables (e.g., using `.env` files). Never commit sensitive data to version control.

6. **Settings Management**: Split settings into multiple files (e.g., `settings/base.py`, `settings/dev.py`, `settings/prod.py`) to separate development and production environments.

7. **Use Migrations**: Always generate and run migrations after changing models. Never edit migration files manually unless necessary.

---

## Naming Conventions

1. **File Names**: 
   - Python files: lowercase with underscores (`snake_case`). For example, `views.py`, `models.py`, etc.
   - Template files: use hyphens (`kebab-case.html`). For example, `user-profile.html`.

2. **Classes**: 
   - Use `PascalCase` for class names. 
   - Example: `class UserProfile(models.Model)`.

3. **Variables and Functions**: 
   - Use `snake_case` for functions and variable names.
   - Example: `get_user_profile`.

4. **URLs**: 
   - Keep URL names meaningful, short, and related to the functionality.
   - Example: `profile_detail` instead of `view_profile`.

---

## Function Naming Conventions

1. **Views**:
   - Name view functions according to the action they perform.
   - Example: `def get_user_profile(request)`.

2. **Utility Functions**:
   - Use descriptive names that clearly state the function’s purpose.
   - Example: `def send_email_verification(user_email)`.

3. **Model Methods**:
   - Keep methods meaningful to the data they are operating on.
   - Example: `def calculate_total_price(self)` in an `Order` model.

4. **Signal Handlers**:
   - Name signal functions to indicate the model they relate to and the action.
   - Example: `def create_profile(sender, instance, created, **kwargs)`.

---

## Model Conventions

1. **Model Class Names**:
   - Use `PascalCase` for models.
   - Example: `class UserProfile(models.Model)`.

2. **Field Names**:
   - Use `snake_case` for model fields.
   - Example: `first_name = models.CharField(max_length=50)`.

3. **Meta Class**:
   - Always include a `Meta` class for custom ordering, permissions, and other metadata.
   - Example:
     ```python
     class Meta:
         ordering = ['created_at']
         verbose_name = 'User Profile'
     ```

4. **String Representation**:
   - Implement `__str__()` for each model for better readability in the admin panel and debugging.
   - Example:
     ```python
     def __str__(self):
         return f'{self.first_name} {self.last_name}'
     ```

---

## Testing

1. **Unit Tests**: 
   - Write tests for each view, model, and utility function.
   - Use Django’s built-in testing framework (`unittest` or `pytest-django`).

2. **Coverage**: Aim for at least 80% test coverage.

3. **Test Naming**:
   - Test functions should describe the functionality being tested.
   - Example: `def test_create_user_profile_successfully(self)`.

---

## Version Control

1. **Branching Strategy**:
   - Use feature branches: `feature/your-feature-name`.
   - For bug fixes: `fix/bug-description`.

2. **Commits**:
   - Keep commit messages concise and descriptive (50 characters or less for the title).
   - Example: `Fix user profile image upload bug`.

3. **Pull Requests**:
   - Ensure your branch passes all tests before submitting a pull request.
   - Add clear descriptions to explain the changes introduced.

4. **Code Review**:
   - Review pull requests for consistency with these best practices before merging.

---

## Contributing

1. **Create a new branch** for each feature or bug fix.
2. **Follow the code conventions** outlined above.
3. **Run all tests** before pushing your code.
4. **Submit a pull request** with a clear description of the changes.

---

## Contact

For questions or contributions, please contact the project team at `wondmenehdereje@gmail.com`.

---
