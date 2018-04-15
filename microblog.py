from app import create_app, db, cli #import the Flask object called app from our app package ("Folder"). "cli" - run scripts to create, update and compile new languages
from app.models import User, Post

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context(): #Make items available in the "flask shell" .
    return {'db': db, 'User': User, 'Post': Post}