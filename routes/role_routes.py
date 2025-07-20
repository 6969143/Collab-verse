from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from controllers import role_controllers
from utils.decorators import admin_required, team_manager_required  # type: ignore
from models import User, Team

role_bp = Blueprint('role', __name__)

@role_bp.route('/apply/team-manager', methods=['GET', 'POST'])
@login_required
def apply_team_manager():
    """Apply for team manager role"""
    if request.method == 'POST':
        reason = request.form.get('reason')
        experience = request.form.get('experience')
        skills = request.form.get('skills')
        
        if not all([reason, experience, skills]):
            flash('Please fill in all fields', 'error')
            return render_template('apply_team_manager.html')
        
        application, error = role_controllers.create_role_application(
            applicant_id=current_user.id,
            requested_role='team_manager',
            reason=reason,
            experience=experience,
            skills=skills
        )
        
        if error:
            flash(f'Error submitting application: {error}', 'error')
        else:
            flash('Your application has been submitted successfully!', 'success')
            return redirect(url_for('main.dashboard'))
    
    return render_template('apply_team_manager.html')

@role_bp.route('/applications')
@admin_required
def view_applications():
    """View all pending role applications (admin only)"""
    applications, error = role_controllers.get_pending_role_applications()
    if error:
        flash(f'Error loading applications: {error}', 'error')
        applications = []
    
    return render_template('admin/role_applications.html', applications=applications)

@role_bp.route('/applications/<int:application_id>/review', methods=['POST'])
@admin_required
def review_application(application_id):
    """Review a role application (admin only)"""
    status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')
    
    if status not in ['approved', 'rejected']:
        flash('Invalid status', 'error')
        return redirect(url_for('role.view_applications'))
    
    application, error = role_controllers.review_role_application(
        application_id=application_id,
        admin_id=current_user.id,
        status=status,
        admin_notes=admin_notes
    )
    
    if error:
        flash(f'Error reviewing application: {error}', 'error')
    else:
        flash(f'Application {status} successfully', 'success')
    
    return redirect(url_for('role.view_applications'))

@role_bp.route('/my-applications')
@login_required
def my_applications():
    """View user's own role applications"""
    applications, error = role_controllers.get_user_role_applications(current_user.id)
    if error:
        flash(f'Error loading applications: {error}', 'error')
        applications = []
    
    return render_template('my_role_applications.html', applications=applications)

@role_bp.route('/teams')
@team_manager_required
def manage_teams():
    """Manage teams (team manager only)"""
    teams = Team.query.filter_by(manager_id=current_user.id).all()
    return render_template('team_manager/teams.html', teams=teams)

@role_bp.route('/teams/create', methods=['GET', 'POST'])
@team_manager_required
def create_team():
    """Create a new team (team manager only)"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Team name is required', 'error')
            return render_template('team_manager/create_team.html')
        
        team = Team()
        team.name = name
        team.description = description
        team.manager_id = current_user.id
        
        from models import db
        db.session.add(team)
        db.session.commit()
        
        flash('Team created successfully!', 'success')
        return redirect(url_for('role.manage_teams'))
    
    return render_template('team_manager/create_team.html')

@role_bp.route('/teams/<int:team_id>')
@team_manager_required
def team_detail(team_id):
    """View team details (team manager only)"""
    team = Team.query.get_or_404(team_id)
    
    # Ensure current user is the team manager
    if team.manager_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('team_manager/team_detail.html', team=team) 