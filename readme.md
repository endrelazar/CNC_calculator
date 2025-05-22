# CNC Calculation Web App

A Flask-based web application for CNC machining calculations, parameter storage, and PDF/email export.

## Features

- CNC parameter calculations (drilling, milling, countersinking, etc.)
- User authentication (login/logout)
- Data storage with SQLite and SQLAlchemy
- PDF export of calculation results
- Email sending with file attachment
- Responsive Bootstrap UI

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

- **Email sending requires a `config.json` file** in the project root with your own credentials:
    ```json
    {
      "email_felado": "your_email@example.com",
      "email_jelszo": "your_email_password"
    }
    ```
    Only works with freemail.hu account.


- **User authentication requires an `.env` file** (or `ini.env`) with at least:
    ```
    USERPASS=hashed_password
    SECRET_KEY=your_secret_key
    ```

### 4. Running

```bash
flask run
```

Or with Docker (if you add a Dockerfile):

```bash
docker build -t cnc-app .
docker run -p 5000:5000 --env-file .env cnc-app
```

## Testing

```bash
pytest
```

For testing login/logout, temporarily set in `app.py`:
```python
users = {"admin": generate_password_hash("admin")}  # For testing only
```
Do not use this in production!

```

## Notes

- Do **not** commit your real `config.json` or `.env` files to version control.
- For email sending to work, you must provide valid SMTP credentials in `config.json`.

---

**For any questions or issues, please open an issue on GitHub.**