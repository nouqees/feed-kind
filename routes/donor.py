import os
import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from extensions import db
from models.user import User
from models.category import FoodCategory
from models.donation import FoodDonation
from models.request import DonationRequest
from models.history import DonationHistory
from utils.decorators import role_required, current_user_id
from utils.validators import allowed_file

donor_bp = Blueprint("donor", __name__, url_prefix="/donor")

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


def _save_image(file_storage):
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename, current_app.config["ALLOWED_IMAGE_EXTENSIONS"]):
        raise ValueError("Only JPG, JPEG and PNG images are allowed.")

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name))
    return unique_name


def _parse_donation_form(form):
    errors = []
    food_name = form.get("food_name", "").strip()
    category_id = form.get("category_id", "")
    quantity = form.get("quantity", "").strip()
    pickup_location = form.get("pickup_location", "").strip()
    description = form.get("description", "").strip()
    prepared_at_raw = form.get("prepared_at", "")
    available_until_raw = form.get("available_until", "")

    if not food_name:
        errors.append("Food name is required.")
    if not quantity:
        errors.append("Quantity is required.")
    if not pickup_location:
        errors.append("Pickup location is required.")

    category = FoodCategory.query.get(category_id) if category_id else None
    if not category:
        errors.append("Select a valid food category.")

    prepared_at = available_until = None
    try:
        prepared_at = datetime.strptime(prepared_at_raw, DATETIME_FORMAT)
    except ValueError:
        errors.append("Enter a valid food preparation date and time.")
    try:
        available_until = datetime.strptime(available_until_raw, DATETIME_FORMAT)
    except ValueError:
        errors.append("Enter a valid availability deadline.")

    if prepared_at and available_until:
        if available_until <= prepared_at:
            errors.append("Availability deadline must be after the preparation time.")
        if available_until <= datetime.now():
            errors.append("Availability deadline must be in the future.")

    return {
        "food_name": food_name,
        "category_id": category.id if category else None,
        "quantity": quantity,
        "pickup_location": pickup_location,
        "description": description,
        "prepared_at": prepared_at,
        "available_until": available_until,
    }, errors


@donor_bp.route("/dashboard")
@role_required(User.ROLE_DONOR)
def dashboard():
    donor_id = current_user_id()
    donations = FoodDonation.query.filter_by(donor_id=donor_id).all()

    summary = {
        "total": len(donations),
        "available": sum(1 for d in donations if d.status == FoodDonation.STATUS_AVAILABLE),
        "reserved": sum(1 for d in donations if d.status == FoodDonation.STATUS_RESERVED),
        "completed": sum(1 for d in donations if d.status == FoodDonation.STATUS_COMPLETED),
        "cancelled": sum(1 for d in donations if d.status == FoodDonation.STATUS_CANCELLED),
    }
    pending_requests = (
        DonationRequest.query.join(FoodDonation)
        .filter(FoodDonation.donor_id == donor_id, DonationRequest.status == DonationRequest.STATUS_PENDING)
        .count()
    )
    recent_donations = sorted(donations, key=lambda d: d.created_at, reverse=True)[:5]

    return render_template(
        "donor/dashboard.html",
        summary=summary,
        pending_requests=pending_requests,
        recent_donations=recent_donations,
    )


@donor_bp.route("/donations")
@role_required(User.ROLE_DONOR)
def donations():
    donor_id = current_user_id()
    all_donations = (
        FoodDonation.query.filter_by(donor_id=donor_id)
        .order_by(FoodDonation.created_at.desc())
        .all()
    )
    return render_template("donor/donations.html", donations=all_donations)


@donor_bp.route("/donations/add", methods=["GET", "POST"])
@role_required(User.ROLE_DONOR)
def add_donation():
    categories = FoodCategory.query.order_by(FoodCategory.category_name).all()

    if request.method == "POST":
        data, errors = _parse_donation_form(request.form)

        image_name = None
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            try:
                image_name = _save_image(image_file)
            except ValueError as exc:
                errors.append(str(exc))

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("donor/add_donation.html", categories=categories, form=request.form)

        donation = FoodDonation(
            donor_id=current_user_id(),
            food_name=data["food_name"],
            category_id=data["category_id"],
            quantity=data["quantity"],
            prepared_at=data["prepared_at"],
            available_until=data["available_until"],
            pickup_location=data["pickup_location"],
            description=data["description"],
            image_path=image_name,
            status=FoodDonation.STATUS_AVAILABLE,
        )
        db.session.add(donation)
        db.session.commit()

        flash("Donation added successfully.", "success")
        return redirect(url_for("donor.donations"))

    return render_template("donor/add_donation.html", categories=categories, form={})


@donor_bp.route("/donations/<int:donation_id>/edit", methods=["GET", "POST"])
@role_required(User.ROLE_DONOR)
def edit_donation(donation_id):
    donation = FoodDonation.query.get_or_404(donation_id)

    if donation.donor_id != current_user_id():
        flash("You do not have access to that donation.", "error")
        return redirect(url_for("donor.donations"))

    if donation.status != FoodDonation.STATUS_AVAILABLE:
        flash("Only donations that are still Available can be edited.", "error")
        return redirect(url_for("donor.donations"))

    categories = FoodCategory.query.order_by(FoodCategory.category_name).all()

    if request.method == "POST":
        data, errors = _parse_donation_form(request.form)

        image_name = donation.image_path
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            try:
                image_name = _save_image(image_file)
            except ValueError as exc:
                errors.append(str(exc))

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "donor/edit_donation.html", donation=donation, categories=categories, form=request.form
            )

        donation.food_name = data["food_name"]
        donation.category_id = data["category_id"]
        donation.quantity = data["quantity"]
        donation.prepared_at = data["prepared_at"]
        donation.available_until = data["available_until"]
        donation.pickup_location = data["pickup_location"]
        donation.description = data["description"]
        donation.image_path = image_name
        db.session.commit()

        flash("Donation updated successfully.", "success")
        return redirect(url_for("donor.donations"))

    form = {
        "food_name": donation.food_name,
        "category_id": str(donation.category_id),
        "quantity": donation.quantity,
        "pickup_location": donation.pickup_location,
        "description": donation.description or "",
        "prepared_at": donation.prepared_at.strftime(DATETIME_FORMAT),
        "available_until": donation.available_until.strftime(DATETIME_FORMAT),
    }
    return render_template("donor/edit_donation.html", donation=donation, categories=categories, form=form)


@donor_bp.route("/donations/<int:donation_id>/cancel", methods=["POST"])
@role_required(User.ROLE_DONOR)
def cancel_donation(donation_id):
    donation = FoodDonation.query.get_or_404(donation_id)

    if donation.donor_id != current_user_id():
        flash("You do not have access to that donation.", "error")
        return redirect(url_for("donor.donations"))

    if donation.status != FoodDonation.STATUS_AVAILABLE:
        flash("Only donations that are still Available can be cancelled.", "error")
        return redirect(url_for("donor.donations"))

    donation.status = FoodDonation.STATUS_CANCELLED
    for req in donation.requests:
        if req.status == DonationRequest.STATUS_PENDING:
            req.status = DonationRequest.STATUS_CANCELLED
    db.session.commit()

    flash("Donation cancelled.", "success")
    return redirect(url_for("donor.donations"))


@donor_bp.route("/donations/<int:donation_id>/requests")
@role_required(User.ROLE_DONOR)
def donation_requests(donation_id):
    donation = FoodDonation.query.get_or_404(donation_id)

    if donation.donor_id != current_user_id():
        flash("You do not have access to that donation.", "error")
        return redirect(url_for("donor.donations"))

    requests_list = (
        DonationRequest.query.filter_by(donation_id=donation.id)
        .order_by(DonationRequest.requested_at.desc())
        .all()
    )
    return render_template("donor/donation_requests.html", donation=donation, requests=requests_list)


@donor_bp.route("/requests/<int:request_id>/accept", methods=["POST"])
@role_required(User.ROLE_DONOR)
def accept_request(request_id):
    donor_id = current_user_id()

    # Lock both rows for the rest of this transaction so a concurrent accept
    # attempt on the same donation blocks until this one commits or rolls back.
    donation_request = DonationRequest.query.filter_by(id=request_id).with_for_update().first()
    if donation_request is None:
        flash("Request not found.", "error")
        return redirect(url_for("donor.donations"))

    donation = FoodDonation.query.filter_by(id=donation_request.donation_id).with_for_update().first()

    if donation.donor_id != donor_id:
        db.session.rollback()
        flash("You do not have access to that request.", "error")
        return redirect(url_for("donor.donations"))

    if donation.status != FoodDonation.STATUS_AVAILABLE or donation_request.status != DonationRequest.STATUS_PENDING:
        db.session.rollback()
        flash("This request can no longer be accepted.", "error")
        return redirect(url_for("donor.donation_requests", donation_id=donation.id))

    donation_request.status = DonationRequest.STATUS_ACCEPTED
    donation.status = FoodDonation.STATUS_RESERVED

    DonationRequest.query.filter(
        DonationRequest.donation_id == donation.id,
        DonationRequest.id != donation_request.id,
        DonationRequest.status == DonationRequest.STATUS_PENDING,
    ).update({DonationRequest.status: DonationRequest.STATUS_REJECTED}, synchronize_session=False)

    db.session.commit()

    flash("Request accepted. Other pending requests for this donation have been rejected.", "success")
    return redirect(url_for("donor.donation_requests", donation_id=donation.id))


@donor_bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@role_required(User.ROLE_DONOR)
def reject_request(request_id):
    donation_request = DonationRequest.query.get_or_404(request_id)
    donation = FoodDonation.query.get_or_404(donation_request.donation_id)

    if donation.donor_id != current_user_id():
        flash("You do not have access to that request.", "error")
        return redirect(url_for("donor.donations"))

    if donation_request.status != DonationRequest.STATUS_PENDING:
        flash("Only pending requests can be rejected.", "error")
        return redirect(url_for("donor.donation_requests", donation_id=donation.id))

    donation_request.status = DonationRequest.STATUS_REJECTED
    db.session.commit()

    flash("Request rejected.", "success")
    return redirect(url_for("donor.donation_requests", donation_id=donation.id))


@donor_bp.route("/donations/<int:donation_id>/complete", methods=["POST"])
@role_required(User.ROLE_DONOR)
def complete_donation(donation_id):
    donation = FoodDonation.query.get_or_404(donation_id)

    if donation.donor_id != current_user_id():
        flash("You do not have access to that donation.", "error")
        return redirect(url_for("donor.donations"))

    if donation.status != FoodDonation.STATUS_RESERVED:
        flash("Only a Reserved donation (with an accepted NGO) can be marked completed.", "error")
        return redirect(url_for("donor.donations"))

    accepted_request = DonationRequest.query.filter_by(
        donation_id=donation.id, status=DonationRequest.STATUS_ACCEPTED
    ).first()
    if accepted_request is None:
        flash("No accepted request found for this donation.", "error")
        return redirect(url_for("donor.donations"))

    remarks = request.form.get("remarks", "").strip()

    donation.status = FoodDonation.STATUS_COMPLETED
    db.session.add(DonationHistory(
        donation_id=donation.id,
        request_id=accepted_request.id,
        remarks=remarks,
    ))
    db.session.commit()

    flash("Donation marked as completed.", "success")
    return redirect(url_for("donor.donations"))
