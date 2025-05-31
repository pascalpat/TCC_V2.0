import click
from werkzeug.security import generate_password_hash
from flask.cli import FlaskGroup

from app import create_app, db
from app.models.workforce_models import Worker


def create_app_cli():
    return create_app()

cli = FlaskGroup(create_app=create_app_cli)

@cli.command("create-user")
def create_user():
    """Create a new user with hashed password."""
    email = click.prompt("Email")
    name = click.prompt("Name")
    role = click.prompt(
        "Role",
        type=click.Choice([
            "admin",
            "manager",
            "superintendent",
            "foreman",
            "worker",
        ], case_sensitive=False),
    )
    password = click.prompt("Password", confirmation_prompt=False)

    worker = Worker(
        name=name,
        courriel=email,
        role=role,
        password_hash=generate_password_hash(password),
        worker_id=email,
    )
    db.session.add(worker)
    db.session.commit()
    click.echo(f"Created user {name} with role {role}")

if __name__ == "__main__":
    cli()