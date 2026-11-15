from collections import Counter
from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash

from extensions import db
from models.user import User
from models.category import FoodCategory
from models.donation import FoodDonation
from models.request import DonationRequest
from utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

DONATION_STATUSES = (
    FoodDonation.STATUS_AVAILABLE,
    FoodDonation.STATUS_RESERVED,
    FoodDonation.STATUS_COMPLETED,
    FoodDonation.STATUS_CANCELLED,
)


def _last_n_months(n=6):
    today = date.today()
    year, month = today.year, today.month
    months = []
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


@admin_bp.route("/dashboard")
@role_required(User.ROLE_ADMIN)
def dashboard():
    total_donors = User.query.filter_by(role=User.ROLE_DONOR).count()
    total_ngos = User.query.filter_by(role=User.ROLE_NGO).count()
    total_donations = FoodDonation.query.count()
    pending_requests = DonationRequest.query.filter_by(status=DonationRequest.STATUS_PENDING).count()
    completed_donations = FoodDonation.query.filter_by(status=FoodDonation.STATUS_COMPLETED).count()

    categories = FoodCategory.query.order_by(FoodCategory.id).all()
    category_labels = [c.category_name for c in categories]
    category_counts = [FoodDonation.query.filter_by(category_id=c.id).count() for c in categories]

    months = _last_n_months(6)
    created_dates = [row[0] for row in FoodDonation.query.with_entities(FoodDonation.created_at).all()]
    month_counter = Counter((dt.year, dt.month) for dt in created_dates)
    month_labels = [date(year, month, 1).strftime("%b %Y") for (year, month) in months]
    month_counts = [month_counter.get(key, 0) for key in months]

    return render_template(
        "admin/dashboard.html",
        total_donors=total_donors,
        total_ngos=total_ngos,
        total_donations=total_donations,
        pending_requests=pending_requests,
        completed_donations=completed_donations,
        category_labels=category_labels,
        category_counts=category_counts,
        month_labels=month_labels,
        month_counts=month_counts,
    )


@admin_bp.route("/users")
@role_required(User.ROLE_ADMIN)
def users():
    role_filter = request.args.get("role", "")
    query = User.query.filter(User.role != User.ROLE_ADMIN)
    if role_filter in (User.ROLE_DONOR, User.ROLE_NGO):
        query = query.filter_by(role=role_filter)
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users, role_filter=role_filter)


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@role_required(User.ROLE_ADMIN)
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == User.ROLE_ADMIN:
        flash("Admin accounts cannot be deactivated.", "error")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()

    flash(f"{user.name} has been {'activated' if user.is_active else 'deactivated'}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/donations")
@role_required(User.ROLE_ADMIN)
def donations():
    status_filter = request.args.get("status", "")
    query = FoodDonation.query
    if status_filter in DONATION_STATUSES:
        query = query.filter_by(status=status_filter)
    all_donations = query.order_by(FoodDonation.created_at.desc()).all()
    return render_template(
        "admin/donations.html",
        donations=all_donations,
        status_filter=status_filter,
        statuses=DONATION_STATUSES,
    )


@admin_bp.route("/requests")
@role_required(User.ROLE_ADMIN)
def requests_list():
    all_requests = DonationRequest.query.order_by(DonationRequest.requested_at.desc()).all()
    return render_template("admin/requests.html", requests=all_requests)
