from flask import Blueprint, request, redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user

from models.project import Project
from models.ticket import Ticket
from controllers.ticket_controllers import open_ticket, review_ticket

ticket_bp = Blueprint("tickets", __name__, template_folder="../templates")

@ticket_bp.route("/<int:proj_id>/tickets", methods=["GET", "POST"])
@login_required
def tickets(proj_id):
    project = Project.query.get_or_404(proj_id)
    if current_user.id != project.owner_id and \
       not project.members.filter_by(id=current_user.id).first():
        abort(403)

    if request.method == "POST":
        title = request.form["title"]
        desc  = request.form.get("description")
        ttype = request.form["type"]
        ticket, err = open_ticket(project, current_user, title, desc, ttype)
        if err:
            flash(err, "danger")
        else:
            flash("Ticket opened.", "success")
        return redirect(url_for("tickets.tickets", proj_id=proj_id))

    all_t = project.tickets.order_by(Ticket.created_at.desc()).all()
    return render_template("tickets.html", project=project, tickets=all_t)

@ticket_bp.route("/<int:ticket_id>/review", methods=["POST"])
@login_required
def review(ticket_id):
    accept = request.form.get("action") == "accept"
    ticket, err = review_ticket(ticket_id, accept, current_user)
    if err:
        flash(err, "danger")
    else:
        flash(f"Ticket {ticket.status}.", "info")
    return redirect(
      url_for("tickets.tickets", proj_id=ticket.project_id)
    )