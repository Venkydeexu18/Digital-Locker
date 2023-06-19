from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

instance_path = os.path.join(app.root_path, 'instance')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "database.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')

uploads_dir = app.config['UPLOAD_FOLDER']
education_dir = os.path.join(uploads_dir, 'education')
health_dir = os.path.join(uploads_dir, 'health')
service_dir = os.path.join(uploads_dir, 'service')
transport_dir = os.path.join(uploads_dir, 'transport')

os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(education_dir, exist_ok=True)
os.makedirs(health_dir, exist_ok=True)
os.makedirs(service_dir, exist_ok=True)
os.makedirs(transport_dir, exist_ok=True)

db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(20))
    education_documents = db.relationship('EducationDocument', backref='user', lazy=True)
    health_documents = db.relationship('HealthDocument', backref='user', lazy=True)
    service_documents = db.relationship('ServiceDocument', backref='user', lazy=True)
    transport_documents = db.relationship('TransportDocument', backref='user', lazy=True)


class EducationDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)


class HealthDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)


class ServiceDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)


class TransportDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    username = session.get('username')
    name = session.get('name')
    return render_template('home.html', name=name,username=username)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('registration.html', error=error)

        new_user = User(username=username, name = name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        session['name'] = name
        return redirect(url_for('home'))

    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                session['username'] = username
                return redirect(url_for('home'))
            else:
                error = "Invalid password. Please try again."
        else:
            error = "Username is not registered with us. Please try again."

    return render_template('login.html', error=error)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            error = "Passwords do not match. Please try again."
            return render_template('forgot_password.html', error=error)

        user = User.query.filter_by(username=username).first()

        if user:
            user.password = password
            db.session.commit()
            return redirect(url_for('login'))
        else:
            error = "User not found. Please try again."
            return render_template('forgot_password.html', error=error)

    return render_template('forgot_password.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


def save_uploaded_file(file):
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None
    
@app.route('/education', methods=['GET', 'POST'])
def education():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        document = request.files['document']

        if document:
            filename = secure_filename(document.filename)
            file_path = os.path.join(education_dir, filename)
            document.save(file_path)

            username = session['username']

            user = User.query.filter_by(username=username).first()
            if user:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    new_document = EducationDocument(user_id=username, filename=filename, data=file_data)
                    db.session.add(new_document)
                    db.session.commit()
                flash('File uploaded successfully!', 'success')
            else:
                flash('User not found', 'danger')
        else:
            flash('No file selected', 'danger')

    documents = EducationDocument.query.filter_by(user_id=session['username']).all()
    return render_template('education.html', documents=documents)

@app.route('/service', methods=['GET', 'POST'])
def service():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        document = request.files['document']

        if document:
            filename = secure_filename(document.filename)
            file_path = os.path.join(service_dir, filename)
            document.save(file_path)

            username = session['username']

            user = User.query.filter_by(username=username).first()
            if user:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    new_document = ServiceDocument(user_id=username, filename=filename, data=file_data)
                    db.session.add(new_document)
                    db.session.commit()
                flash('File uploaded successfully!', 'success')
            else:
                flash('User not found', 'danger')
        else:
            flash('No file selected', 'danger')

    documents = ServiceDocument.query.filter_by(user_id=session['username']).all()
    return render_template('service.html', documents=documents)

@app.route('/transport', methods=['GET', 'POST'])
def transport():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        document = request.files['document']

        if document:
            filename = secure_filename(document.filename)
            file_path = os.path.join(transport_dir, filename)
            document.save(file_path)

            username = session['username']

            user = User.query.filter_by(username=username).first()
            if user:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    new_document = TransportDocument(user_id=username, filename=filename, data=file_data)
                    db.session.add(new_document)
                    db.session.commit()
                flash('File uploaded successfully!', 'success')
            else:
                flash('User not found', 'danger')
        else:
            flash('No file selected', 'danger')

    documents = TransportDocument.query.filter_by(user_id=session['username']).all()
    return render_template('transport.html', documents=documents)

@app.route('/health', methods=['GET', 'POST'])
def health():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        document = request.files['document']

        if document:
            filename = secure_filename(document.filename)
            file_path = os.path.join(health_dir, filename)
            document.save(file_path)

            username = session['username']

            user = User.query.filter_by(username=username).first()
            if user:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    new_document = HealthDocument(user_id=username, filename=filename, data=file_data)
                    db.session.add(new_document)
                    db.session.commit()
                flash('File uploaded successfully!', 'success')
            else:
                flash('User not found', 'danger')
        else:
            flash('No file selected', 'danger')

    documents = HealthDocument.query.filter_by(user_id=session['username']).all()
    return render_template('health.html', documents=documents)


@app.route('/view_documents')
def view_documents():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()

        if user:
            education_documents = EducationDocument.query.filter_by(user_id=username).all()
            health_documents = HealthDocument.query.filter_by(user_id=username).all()
            service_documents = ServiceDocument.query.filter_by(user_id=username).all()
            transport_documents = TransportDocument.query.filter_by(user_id=username).all()

            return render_template('view_documents.html', education_documents=education_documents,
                                   health_documents=health_documents, service_documents=service_documents,
                                   transport_documents=transport_documents)

    return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload():
    if 'username' in session:
        username = session['username']
        document = request.files['document']

        if document:
            filename = secure_filename(document.filename)
            file_data = document.read()

            user = User.query.filter_by(username=username).first()
            if user:
                new_document = Document(user_id=username, filename=filename, data=file_data)
                db.session.add(new_document)
                db.session.commit()

    return redirect(url_for('health'))


@app.route('/serve_document/<int:document_id>')
def serve_document(document_id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()

        if user:
            document = None
            document_type = None
            document = HealthDocument.query.filter_by(id=document_id, user_id=username).first()
            if document:
                document_type = 'health'
            if not document:
                document = EducationDocument.query.filter_by(id=document_id, user_id=username).first()
                if document:
                    document_type = 'education'
            if not document:
                document = ServiceDocument.query.filter_by(id=document_id, user_id=username).first()
                if document:
                    document_type = 'service'
            if not document:
                document = TransportDocument.query.filter_by(id=document_id, user_id=username).first()
                if document:
                    document_type = 'transport'

            if document:
                document_folder = os.path.join(app.config['UPLOAD_FOLDER'], document_type)
                return send_from_directory(document_folder, document.filename, as_attachment=True)

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)