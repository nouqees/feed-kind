from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash

from extensions import db
from models.user import User
from models.category import FoodCategory
from models.donation import FoodDonation
from models.request import DonationRequest
from utils.decorators import role_required, current_user_id

ngo_bp = Blueprint("ngo", __name__, url_prefix="/ngo")

ACTIVE_REQUEST_STATUSES = (DonationRequest.STATUS_PENDING, DonationRequest.STATUS_ACCEPTED)


def _available_donations_query():
    return FoodDonation.query.filter(
        FoodDonation.status == FoodDonation.STATUS_AVAILABLE,
        FoodDonation.available_until > datetime.now(),
    )


@ngo_bp.route("/dashboard")
@role_required(User.ROLE_NGO)
def dashboard():
    ngo_id = current_user_id()

    available_count = _available_donations_query().count()
    my_requests = DonationRequest.query.filter_by(ngo_id=ngo_id).all()
    pending_count = sum(1 for r in my_requests if r.status == DonationRequest.STATUS_PENDING)
    accepted_count = sum(1 for r in my_requests if r.status == DonationRequest.STATUS_ACCEPTED)

    recent_available = (
        _available_donations_query().order_by(FoodDonation.created_at.desc()).limit(5).all()
    )

    return render_template(
        "ngo/dashboard.html",
        available_count=available_count,
        pending_count=pending_count,
        accepted_count=accepted_count,
        recent_available=recent_available,
    )


@ngo_bp.route("/donations")
@role_required(User.ROLE_NGO)
def available_donations():
    category_id = request.args.get("category_id", "")

    query = _available_donations_query()
    if category_id:
        query = query.filter(FoodDonation.category_id == category_id)

    listing = query.order_by(FoodDonation.available_until.asc()).all()
    categories = FoodCategory.query.order_by(FoodCategory.category_name).all()

    return render_template(
        "ngo/available_donations.html",
        donations=listing,
        categories=categories,
        selected_category=category_id,
    )


@ngo_bp.route("/donations/<int:donation_id>")
@role_required(User.ROLE_NGO)
def donation_detail(donation_id):
    donation = FoodDonation.query.get_or_404(donation_id)

    is_expired = donation.available_until <= datetime.now()
    existing_request = (
        DonationRequest.query.filter_by(donation_id=donation.id, ngo_id=current_user_id())
        .filter(DonationRequest.status.in_(ACTIVE_REQUEST_STATUSES))
        .first()
    )
    can_request = (
        donation.status == FoodDonation.STATUS_AVAILABLE and not is_expired and not existing_request
    )

    return render_template(
        "ngo/donation_detail.html",
        donation=donation,
        is_expired=is_expired,
        can_request=can_request,
        existing_request=existing_request,
    )


@ngo_bp.route("/donations/<int:donation_id>/request", methods=["POST"])
@role_required(User.ROLE_NGO)
def request_donation(donation_id):
    donation = FoodDonation.query.get_or_404(donation_id)
    ngo_id = current_user_id()

    if donation.status != FoodDonation.STATUS_AVAILABLE or donation.available_until <= datetime.now():
        flash("This donation is no longer available to request.", "error")
        return redirect(url_for("ngo.donation_detail", donation_id=donation.id))

    existing_request = (
        DonationRequest.query.filter_by(donation_id=donation.id, ngo_id=ngo_id)
        .filter(DonationRequest.status.in_(ACTIVE_REQUEST_STATUSES))
        .first()
    )
    if existing_request:
        flash("You have already requested this donation.", "error")
        return redirect(url_for("ngo.donation_detail", donation_id=donation.id))

    requested_quantity = request.form.get("requested_quantity", "").strip()
    message = request.form.get("message", "").strip()

    if not requested_quantity:
        flash("Enter the quantity you are requesting.", "error")
        return redirect(url_for("ngo.donation_detail", donation_id=donation.id))

    donation_request = DonationRequest(
        donation_id=donation.id,
        ngo_id=ngo_id,
        requested_quantity=requested_quantity,
        message=message,
        status=DonationRequest.STATUS_PENDING,
    )
    db.session.add(donation_request)
    db.session.commit()

    flash("Request submitted. The donor will review it shortly.", "success")
    return redirect(url_for("ngo.my_requests"))


@ngo_bp.route("/requests")
@role_required(User.ROLE_NGO)
def my_requests():
    ngo_id = current_user_id()
    requests_list = (
        DonationRequest.query.filter_by(ngo_id=ngo_id)
        .order_by(DonationRequest.requested_at.desc())
        .all()
    )
    return render_template("ngo/requests.html", requests=requests_list)


@ngo_bp.route("/requests/<int:request_id>/cancel", methods=["POST"])
@role_required(User.ROLE_NGO)
def cancel_request(request_id):
    donation_request = DonationRequest.query.get_or_404(request_id)

    if donation_request.ngo_id != current_user_id():
        flash("You do not have access to that request.", "error")
        return redirect(url_for("ngo.my_requests"))

    if donation_request.status != DonationRequest.STATUS_PENDING:
        flash("Only pending requests can be cancelled.", "error")
        return redirect(url_for("ngo.my_requests"))

    donation_request.status = DonationRequest.STATUS_CANCELLED
    db.session.commit()

    flash("Request cancelled.", "success")
    return redirect(url_for("ngo.my_requests"))
