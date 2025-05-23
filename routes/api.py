from flask import Blueprint, flash, jsonify, request, session

from models import Note, Project, Todo, User
from utils import login_required

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/v1/session-debug", methods=["GET"])
def session_debug():
    """Debug endpoint to check session status"""
    return jsonify(
        {
            "user_id": session.get("user_id"),
            "user_public_id": session.get("user_public_id"),
            "display_name": session.get("display_name"),
            "username": session.get("username"),
            "is_logged_in": bool(session.get("user_id")),
        }
    )


@api_bp.route("/v1/todos-from-project/<string:public_id>", methods=["GET"])
@login_required
def get_todos_from_project(public_id):
    project = Project.get_by_public_id(public_id)
    if not project:
        flash("Project not found", "error")
        return jsonify({"error": "Project not found"}), 404
    todos = Todo.get_all_filter(project_id=project.id, is_deleted=False)
    return jsonify([todo.to_dict() for todo in todos])


@api_bp.route("/v1/notes-from-project/<string:public_id>", methods=["GET"])
@login_required
def get_notes_from_project(public_id):
    project = Project.get_by_public_id(public_id)
    if not project:
        flash("Project not found", "error")
        return jsonify({"error": "Project not found"}), 404
    notes = Note.get_all_filter(project_id=project.id, is_deleted=False)
    return jsonify([note.to_dict() for note in notes])


@api_bp.route("/v1/user-from-pid/<string:public_id>", methods=["GET"])
@login_required
def get_user_from_pid(public_id):
    user = User.get_by_field("public_id", public_id)
    if not user:
        flash("User not found", "error")
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.get_user_dict())


@api_bp.route("/v1/user-projects/<string:public_id>", methods=["GET"])
@login_required
def projects_of_user(public_id):
    user = User.get_by_field("public_id", public_id)
    if not user:
        flash("User not found!", "error")
        return jsonify({"error": "User not found"}), 404

    projects = [Project.to_dict(project) for project in user.projects]
    for project in projects:
        project.pop("owner_id", None)
    return jsonify(projects)


@api_bp.route("/v1/create-project", methods=["POST"])
@login_required
def create_project():
    """Create a new project - requires authentication via session"""
    data = request.get_json()
    print(data)
    if not data:
        flash("No data provided", "error")
        return jsonify({"error": "No data provided"}), 400
    if not data.get("name"):
        flash("Name is required", "error")
        return jsonify({"error": "Name is required"}), 400

    name = data.get("name")
    description = data.get("description")
    print(name, description)

    try:
        project = Project.create(
            name=name,
            description=description,
            owner_id=session.get("user_id"),
        )
        flash("Project created successfully", "success")
        return jsonify(
            {
                "message": "Project created successfully",
                "project": Project.to_dict(project),
            }
        ), 201
    except Exception as e:
        print(e)
        print("Error creating project")
        flash("Error creating project", "error")
        return jsonify({"error": str(e)}), 500
