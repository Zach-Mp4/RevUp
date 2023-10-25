from app import db, app

ctx = app.app_context()
ctx.push()

db.drop_all()
db.create_all()