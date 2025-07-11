from datetime import datetime
from models import db
from models.ticket import Ticket
from models.project import Project

def open_ticket(project, creator, title, description, ttype):
    if creator.id != project.owner_id and \
       not project.members.filter_by(id=creator.id).first():
        return None, "Permission denied"

    ticket = Ticket(
        title=title,
        description=description,
        type=ttype,
        project_id=project.id,
        creator_id=creator.id,
        created_at=datetime.utcnow()
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket, None

def review_ticket(ticket_id, accept, reviewer):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return None, "Ticket not found"
    project = ticket.project
    if reviewer.id != project.owner_id:
        return None, "Only project owner can review"
    ticket.status = 'accepted' if accept else 'rejected'
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    return ticket, None