# Food Waste Management and Donation Platform
## BCA Final-Year Project – Implementation Plan

**Project type:** Web Application  
**Recommended complexity:** Simple / Intermediate  
**Estimated development time:** 14 days  
**Estimated student-project cost:** ₹0–₹1,500 (depending on optional hosting and domain)

---

## 1. Project Overview

The Food Waste Management and Donation Platform connects food donors with NGOs or charitable organizations so that excess food can be offered for collection instead of being wasted.

**Objective:** Provide a common platform where restaurants, hotels, marriage halls and individuals can list excess food, and registered NGOs can view and request available donations.

### Simple application workflow

1. A food donor registers and logs in.
2. The donor posts details of available excess food.
3. NGOs log in and view available donations.
4. An NGO submits a request for a donation.
5. The donor accepts or rejects the request.
6. If accepted, the NGO collects the food.
7. The donor marks the handover as completed.

Keep the first version limited to three user roles, a straightforward donation workflow and an admin dashboard.

---

## 2. User Roles

| Role | Responsibilities |
|---|---|
| Admin | Manage users and monitor donations |
| Food Donor | Add and manage food donations; review NGO requests |
| NGO | View available food and request donations |

---

## 3. Functional Modules

### Module 1: User Registration and Login

- Register as a Food Donor or NGO.
- Login using email and password.
- Logout.
- Admin login.
- Basic profile management.
- Restrict pages based on user role.

### Module 2: Food Donation Management

Food donors can create a donation by entering:

- Food name.
- Food category (Vegetarian / Non-Vegetarian).
- Quantity.
- Food preparation date and time.
- Available-until date and time.
- Pickup location.
- Description.
- Food image (optional).

Donors can also:

- View their donations.
- Edit donation details.
- Cancel donations.
- View requests received for their donations.

### Module 3: NGO Donation Management

NGOs can:

- View all available food donations.
- Search donations by food category.
- View donation details.
- Request available food.
- View their requested donations.
- Cancel a request before it is accepted.

### Module 4: Donation Request Management

This is the main business workflow:

1. NGO submits a request for a donation.
2. Donor views the request.
3. Donor accepts or rejects it.
4. If accepted, the NGO collects the food.
5. Donor marks the donation as completed.

Suggested donation statuses:

| Status | Meaning |
|---|---|
| Available | Donation is open for requests |
| Requested | At least one NGO has submitted a request |
| Accepted | Donor accepted one request |
| Rejected | A request was rejected |
| Completed | Food handover completed |
| Cancelled | Donation cancelled |

**Implementation note:** Keep request status separate from donation status. For example, a request can be `Pending`, `Accepted`, `Rejected` or `Cancelled`, while a donation can be `Available`, `Reserved`, `Completed` or `Cancelled`.

### Module 5: Admin Dashboard

Admin can:

- View total registered donors.
- View total registered NGOs.
- View total food donations.
- View pending requests.
- View completed donations.
- Manage users.
- Monitor donation records.

### Module 6: Reports

Keep reporting simple:

- Total food donated.
- Total donations completed.
- Pending donations.
- Category-wise donation statistics.
- Monthly donation report.

---

## 4. Recommended Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| UI framework | Bootstrap 5 |
| Backend | Python Flask |
| Database | MySQL |
| Database connectivity | Flask-SQLAlchemy |
| Authentication | Flask sessions |
| Password security | Werkzeug password hashing |
| Charts | Chart.js |
| Image upload | Local server storage |
| Development IDE | Visual Studio Code |
| Version control | Git / GitHub |

**Why Flask?** Flask is lightweight, requires relatively little configuration and is suitable for a small academic web application.

---

## 5. Database Design

Start with five main tables. This is sufficient for the initial implementation.

### Table 1: `users`

Stores all registered users, including admins.

| Column | Type | Description |
|---|---|---|
| id | INT (PK) | User ID |
| name | VARCHAR | User name |
| email | VARCHAR | Login email; unique |
| password_hash | VARCHAR | Hashed password |
| phone | VARCHAR | Contact number |
| address | TEXT | Address |
| role | ENUM / VARCHAR | ADMIN / DONOR / NGO |
| created_at | DATETIME | Registration date |

### Table 2: `food_donations`

Stores food donation information.

| Column | Type | Description |
|---|---|---|
| id | INT (PK) | Donation ID |
| donor_id | INT (FK) | User ID of donor |
| food_name | VARCHAR | Food name |
| category_id | INT (FK) | Food category |
| quantity | VARCHAR | Food quantity and unit |
| prepared_at | DATETIME | Preparation time |
| available_until | DATETIME | Availability deadline |
| pickup_location | TEXT | Pickup address |
| description | TEXT | Additional details |
| image_path | VARCHAR | Uploaded image path |
| status | VARCHAR | Donation status |
| created_at | DATETIME | Created date |

### Table 3: `donation_requests`

Stores requests submitted by NGOs.

| Column | Type | Description |
|---|---|---|
| id | INT (PK) | Request ID |
| donation_id | INT (FK) | Donation ID |
| ngo_id | INT (FK) | NGO user ID |
| requested_quantity | VARCHAR | Requested quantity |
| message | TEXT | Request message |
| status | VARCHAR | Pending / Accepted / Rejected / Cancelled |
| requested_at | DATETIME | Request date |

### Table 4: `donation_history`

Stores completed donation records.

| Column | Type | Description |
|---|---|---|
| id | INT (PK) | History ID |
| donation_id | INT (FK) | Donation ID |
| request_id | INT (FK) | Accepted request |
| completed_at | DATETIME | Completion date |
| remarks | TEXT | Optional remarks |

### Table 5: `food_categories`

Stores food categories.

| Column | Type | Description |
|---|---|---|
| id | INT (PK) | Category ID |
| category_name | VARCHAR | Category name |

### Database relationships and rules

- One donor can create multiple donations.
- One donation can receive multiple requests.
- One NGO can submit multiple requests.
- Only one request can be accepted for a donation in the simple version.
- When a request is accepted, the donation should no longer be available to other NGOs.
- Use a database transaction when accepting a request to prevent two NGOs from reserving the same donation.
- A completed donation should have one corresponding history record.

---

## 6. Application Screens

Keep the UI simple and responsive.

1. **Home page**
   - Project introduction.
   - How it works.
   - Login and registration links.

2. **Login and registration**
   - Common login form.
   - Donor and NGO registration.
   - Role-based access.

3. **Donor dashboard**
   - Donation summary.
   - Add donation.
   - Existing donations.
   - Incoming requests.

4. **Add food donation**
   - Food details.
   - Quantity.
   - Preparation time.
   - Availability deadline.
   - Pickup location.
   - Optional image upload.

5. **NGO dashboard**
   - Available donations.
   - Search and filter.
   - Request history.

6. **Donation details**
   - Food information.
   - Donor and pickup information.
   - Request action.

7. **Admin dashboard**
   - Summary cards.
   - User management.
   - Donation records.
   - Request records and statistics.

---

## 7. Development Plan – Phase by Phase

The following is a suggested 14-day schedule for one student working consistently.

| Phase | Duration | Tasks |
|---|---:|---|
| 1. Project setup | Day 1 | Create Flask project, configure MySQL, install dependencies, create folder structure and configure Bootstrap |
| 2. Database and authentication | Days 2–3 | Create tables, registration, login, logout, role-based access and admin account |
| 3. Food donation module | Days 4–5 | Add donation, image upload, list donations, edit and cancel donations |
| 4. NGO module | Days 6–7 | Display available food, search and filter, view details, submit requests and show request history |
| 5. Request management | Days 8–9 | Display requests to donors, accept/reject requests, update donation status and complete donations |
| 6. Admin and reports | Days 10–11 | Dashboard summary, user management, donation records and basic statistics |
| 7. Testing and finalization | Days 12–14 | Test user roles and workflows, validate inputs, fix issues and prepare documentation |

**Estimated duration: 14 days.** Allow extra time if the student is new to Flask or MySQL.

---

## 8. Suggested Project Folder Structure

```text
food_waste_management/
│
├── app.py
├── config.py
├── requirements.txt
│
├── models/
│   ├── user.py
│   ├── donation.py
│   └── request.py
│
├── routes/
│   ├── auth.py
│   ├── donor.py
│   ├── ngo.py
│   └── admin.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   │
│   ├── donor/
│   │   ├── dashboard.html
│   │   ├── add_donation.html
│   │   └── donations.html
│   │
│   ├── ngo/
│   │   ├── dashboard.html
│   │   ├── available_donations.html
│   │   └── requests.html
│   │
│   └── admin/
│       ├── dashboard.html
│       ├── users.html
│       └── donations.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
│
└── database/
    └── schema.sql
```

---

## 9. Important Business Rules

Implement these rules as part of the core functionality:

1. Only logged-in donors can create food donations.
2. Only logged-in NGOs can request donations.
3. NGOs cannot request expired or cancelled donations.
4. A donor can accept only one NGO request for each donation.
5. Once accepted, the donation should be unavailable to other NGOs.
6. Only the donor can mark the handover as completed.
7. Cancelled and completed donations should not appear in available donations.
8. Admin can view and manage all records.
9. Validate food preparation and availability dates.
10. Clearly display food preparation time and collection deadline.

**Food safety note:** The platform does not certify food as safe. Donors and recipients must follow applicable food safety requirements and independently assess whether food is suitable for donation and consumption.

---

## 10. Features Excluded from the First Version

To keep the project manageable, do not implement these initially:

- AI-based food recognition.
- Real-time GPS tracking.
- Online payment gateway.
- Complex delivery partner management.
- Live chat.
- Separate mobile application.
- SMS OTP integration.
- Automatic food quality verification.

These can be listed as future enhancements, not project dependencies.

---

## 11. Testing Checklist

Before submitting the project, test the following:

- [ ] Donor registration and login.
- [ ] NGO registration and login.
- [ ] Admin login.
- [ ] Donor can add a food donation.
- [ ] Donor can edit and cancel a donation.
- [ ] NGO can view available donations.
- [ ] NGO can submit a donation request.
- [ ] Donor can accept or reject requests.
- [ ] Accepted donation becomes unavailable to other NGOs.
- [ ] Completed donation appears in donation history.
- [ ] Expired donations cannot be requested.
- [ ] Admin can view users and donations.
- [ ] Unauthorized users cannot access restricted pages.
- [ ] Uploaded images and form inputs are validated.

---

## 12. Final Project Deliverables

At the end of development, the student should have:

1. Fully functional web application.
2. MySQL database and SQL schema.
3. Admin, Donor and NGO demo accounts.
4. Project source code.
5. Database relationship diagram (ER diagram).
6. System architecture diagram.
7. Software Requirement Specification (SRS).
8. Test cases and testing results.
9. Project report.
10. Screenshots and final project presentation.

---

## 13. Implementation Order

Follow this order to avoid building screens before the main workflow is ready.

1. **Build authentication:** Registration and login for Admin, Donor and NGO.
2. **Build food donation:** Allow donors to create and manage food listings.
3. **Build NGO functionality:** Display donations and allow NGOs to request them.
4. **Build request workflow:** Implement accept, reject and complete actions.
5. **Build admin and reports:** Add summary dashboards and basic reporting.
6. **Test and polish:** Validate the full workflow, then improve the UI and prepare documentation.

## Final Recommendation

Complete the core application first. Once it works end-to-end, improve the UI and add charts. Do not spend too much time designing dashboards before the main donation workflow is functional.

This scope is sufficient for a BCA final-year web development project without making it unnecessarily complicated.
