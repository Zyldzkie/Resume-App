from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# Configure MySQL Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/resumes_db'  # Adjust to your database name and credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a Resume Model (Table)
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    template = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)

    def __init__(self, title, template, name=None):
        self.title = title
        self.template = template
        self.name = name

# Create the database and table if it doesn’t exist
with app.app_context():
    db.create_all()

# Route to display the list of resumes
@app.route('/')
def index():
    resumes = Resume.query.all()  # Fetch all resumes from the database
    return render_template('index.html', resumes=resumes)

# Route to add a new resume via POST (HTML form)
@app.route('/add_resume', methods=['POST'])
def add_resume():
    title = request.form['title']
    template = request.form['template']
    name = request.form['name']
    new_resume = Resume(title=title, template=template, name=name)

    db.session.add(new_resume)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/resumes', methods=['POST'])
def api_add_resume():
    data = request.json
    title = data.get('title')
    template = data.get('template')
    name = data.get('name')  # This will be None initially

    if not title or not template:
        return jsonify({"error": "Title and template are required"}), 400

    new_resume = Resume(title=title, template=template, name=name)
    db.session.add(new_resume)
    db.session.commit()

    return jsonify({
        "id": new_resume.id,
        "title": new_resume.title,
        "template": new_resume.template,
        "name": new_resume.name
    }), 201


@app.route('/api/resumes/<int:id>/update_name', methods=['PATCH'])
def update_resume_name(id):
    data = request.json
    name = data.get('name')

    resume = Resume.query.get(id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    resume.name = name
    db.session.commit()

    return jsonify({
        "id": resume.id,
        "title": resume.title,
        "template": resume.template,
        "name": resume.name
    })


# Route to delete a resume
@app.route('/delete_resume/<int:id>')
def delete_resume(id):
    resume = Resume.query.get(id)
    db.session.delete(resume)
    db.session.commit()
    return redirect(url_for('index'))

# API Route to get all resumes in JSON format
@app.route('/api/resumes', methods=['GET'])
def get_resumes():
    try:
        resumes = Resume.query.all()
        resume_list = [{"id": resume.id, "title": resume.title, "template": resume.template, "name": resume.name} for resume in resumes]
        return jsonify(resume_list)
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving resumes"}), 500

if __name__ == "__main__":
    app.run(debug=True)
