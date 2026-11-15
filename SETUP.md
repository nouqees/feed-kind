# Setup Guide (Step by Step)

Follow these steps in order on a fresh computer. Each step tells you exactly what to type.

## Step 1: Install Python

Make sure Python 3.9 or newer is installed. Check with:

```
python3 --version
```

## Step 2: Open the project folder

```
cd food_waste_management
```
(Use the actual folder name where you placed the project.)

## Step 3: Create a virtual environment

A virtual environment keeps this project's packages separate from the rest of your computer.

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

```
python3 -m venv venv  (optional)
```

```
venv\Scripts\activate
```

You'll know it worked when you see `(venv)` at the start of your terminal line.

## Step 4: Install the required packages

```
pip install -r requirements.txt
```

## Step 5: Create your `.env` file

```
cp .env.example .env
```
(Windows: `copy .env.example .env`)

Open `.env` in a text editor and set a `SECRET_KEY` (any random text works).
Leave the MySQL settings for now — they're covered in the next phase of this guide.

## Step 6: Run the app

```
python3 app.py
```

Open your browser at **http://127.0.0.1:5000/** — you should see the home page.

Press `Ctrl+C` in the terminal to stop the server before continuing.

## Step 7: Install MySQL

Install MySQL Server if you don't already have it (e.g. MySQL Community Server,
XAMPP, or MAMP). Make sure you know the root password you set during install.

## Step 8: Create the database and a dedicated user

Log into MySQL:

```
mysql -u root -p
```

Then run these SQL commands (replace `your-password-here` with your own password):

```sql
CREATE DATABASE food_waste_db;
CREATE USER 'food_waste_user'@'localhost' IDENTIFIED BY 'your-password-here';
GRANT ALL PRIVILEGES ON food_waste_db.* TO 'food_waste_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Step 9: Update your `.env` file

Open `.env` again and fill in:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=food_waste_user
MYSQL_PASSWORD=your-password-here
MYSQL_DATABASE=food_waste_db
```

## Step 10: Create the tables

With your virtual environment still active (you should see `(venv)`):

```
flask --app app init-db
```

This reads the models and creates all 5 tables (`users`, `food_categories`,
`food_donations`, `donation_requests`, `donation_history`) in `food_waste_db`.

(`database/schema.sql` contains the same tables written out as plain SQL, in
case you ever want to create them by hand instead.)

## Step 11: Add demo data

```
flask --app app seed
```

This creates:
- Two food categories: **Vegetarian** and **Non-Vegetarian**
- One admin account: **admin@foodwaste.local / Admin@123**

## Step 12: Run the app and test login

```
python3 app.py
```

Open **http://127.0.0.1:5000/auth/register** and create one **Food Donor** account
and one **NGO** account for testing. Then try logging in as:

- The admin account created in Step 11
- Your new Donor account
- Your new NGO account

Each should land on its own dashboard, and trying to open another role's
dashboard URL directly (e.g. an NGO visiting `/admin/dashboard`) should be blocked.

## Step 13: Try the donor features

Log in with your Donor account and:

1. Go to **Add Donation** and create a food donation (try uploading a `.jpg`/`.png` image).
2. Check **My Donations** — your new donation should show status **Available**.
3. Click **Edit** and change a detail — it should save.
4. Click **Cancel** on a donation — it should move to status **Cancelled**, and Edit should
   no longer be available for it.
5. Click **Requests** next to a donation — it lists any NGO requests received, with
   Accept/Reject actions once there's at least one.

## Step 14: Try the NGO features

Log in with your NGO account and:

1. Go to **Available Donations** — you should see the donation the donor added earlier
   (filter it by category to confirm the dropdown works).
2. Click **View Details**, then submit a request with a quantity and an optional message.
3. Go to **My Requests** — your request should show status **Pending**.
4. Try requesting the same donation again — it should say you already requested it.
5. Cancel the pending request — it should disappear from being "blocked" and you could
   request that same donation again.
6. Log back in as the Donor and open **Requests** next to that donation — the NGO's
   request should now be visible there with Accept/Reject buttons.

## Step 15: Try the full request workflow

With the Donor and a couple of NGO accounts from before:

1. Have two different NGOs request the same donation.
2. As the Donor, open **Requests** for that donation — you'll see both as **Pending**.
3. Click **Accept** on one — it becomes **Accepted**, and the other automatically becomes
   **Rejected**. The donation's status changes to **Reserved**, and it disappears from the
   NGOs' **Available Donations** list.
4. On the same page, use **Mark Handover as Completed** (optionally add remarks) — the
   donation status becomes **Completed**.
5. Log in as the accepted NGO and check **My Requests** — the Donation Status column should
   now show **Completed**.

## Step 16: Try the admin features

Log in with the admin account (**admin@foodwaste.local / Admin@123**) and:

1. Check the **Dashboard** — summary cards (donors, NGOs, total/pending/completed donations)
   and two charts: donations by category, and donations added per month.
2. Go to **Manage Users** — filter by Donor/NGO, then **Deactivate** a test account.
   Log out and try logging into that account — it should be blocked. Reactivate it
   from the admin panel to undo this.
3. Go to **Donation Records** — every donation from every donor, filterable by status.
4. Go to **Request Records** — every NGO request across the whole platform.

## Troubleshooting

**`Can't connect to MySQL server on 'localhost'`**
MySQL isn't running, or your `.env` credentials don't match what you created in Step 8.
Confirm MySQL is running, then double-check `MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE`.

**`Access denied for user ...`**
The password in `.env` doesn't match the password you set when you ran `CREATE USER` in
Step 8. Either re-run that step with a password you're sure of, or update `.env` to match.

**`ModuleNotFoundError: No module named 'flask'` (or similar)**
Your virtual environment isn't active. Run the activate command from Step 3 again —
you should see `(venv)` at the start of your terminal prompt.

**Changes to a file don't show up in the browser**
Stop the server (`Ctrl+C`) and run `python3 app.py` again.

**I want to start over with a clean database**
Log into MySQL (`mysql -u root -p`) and run `DROP DATABASE food_waste_db;`, then repeat
Steps 8, 10 and 11.

## Known limitations (by design, for this project's scope)

- No CSRF tokens on forms — acceptable for a single-student academic demo, but would be
  needed (e.g. via Flask-WTF) before any real-world deployment.
- No automatic background job expires old donations — expiry is enforced by checking
  `available_until` against the current time whenever a page is loaded or a request is
  submitted, so expired donations simply stop being requestable without needing a
  scheduled task.
- The Flask development server (`python3 app.py`) is fine for this project's demo and
  viva, but is not meant for production use — that's an intentional Werkzeug warning you
  will see in the terminal, not a bug.

## Project Deliverables Checklist

- [x] Fully functional web application (Flask + MySQL + Bootstrap 5 + Chart.js)
- [x] MySQL database and SQL schema (`database/schema.sql`, also auto-created via `flask init-db`)
- [x] Admin, Donor and NGO demo accounts (`flask seed` creates the admin; register Donor/NGO via the UI)
- [x] Project source code (this folder)
- [ ] Database relationship diagram (ER diagram) — draw from the tables described in `food_waste_management_implementation_plan.md` Section 5
- [ ] System architecture diagram — draw from the folder structure and Flask app factory pattern used here
- [ ] Software Requirement Specification (SRS) — write from the implementation plan's functional modules
- [x] Test cases and testing results — see the full testing checklist below
- [ ] Project report — write up using this SETUP.md and the implementation plan as source material
- [ ] Screenshots and final project presentation — capture from your own running instance

## Final Testing Checklist (from the implementation plan)

All of these were verified during development with automated tests; re-confirm manually
once your own MySQL setup is running:

- [x] Donor registration and login
- [x] NGO registration and login
- [x] Admin login
- [x] Donor can add a food donation
- [x] Donor can edit and cancel a donation
- [x] NGO can view available donations
- [x] NGO can submit a donation request
- [x] Donor can accept or reject requests
- [x] Accepted donation becomes unavailable to other NGOs
- [x] Completed donation appears in donation history
- [x] Expired donations cannot be requested
- [x] Admin can view users and donations
- [x] Unauthorized users cannot access restricted pages
- [x] Uploaded images and form inputs are validated
