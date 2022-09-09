from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import time
import function
import os
import click
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.filters['zip'] = zip
###
###
### for security reason, set secret key to a very random string
app.config['SECRET_KEY'] = '932ngvi3bnru3b4'
###
###
###
db = SQLAlchemy(app)
login_manager = LoginManager(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


class Credential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(60))
    client_id = db.Column(db.String(60))
    client_secret = db.Column(db.String(60))
    tenant_id = db.Column(db.String(60))
    subscription_id = db.Column(db.String(60))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.cli.command()  # registe as command
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.argument("username")
@click.argument("password")
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # set password
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # setpassword
        db.session.add(user)

    db.session.commit()  # commit to database
    click.echo('Done.')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    Credentials = Credential.query.all()
    return render_template('index.html', Credentials=Credentials)


@app.route('/account/add', methods=['GET', 'POST'])
def account_add():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need login')
            return redirect(url_for('login'))
        account = request.form.get('account')
        client_id = request.form.get('string').split("|")[0]
        client_secret = request.form.get('string').split("|")[1]
        tenant_id = request.form.get('string').split("|")[2]
        subscription_id = request.form.get('string').split("|")[3]
        if not account or not client_id or not client_secret or not tenant_id or not subscription_id:
            flash('Incorrect input')
            return redirect(url_for('index'))
        credential = Credential(account=account, client_id=client_id, client_secret=client_secret, tenant_id=tenant_id,
                                subscription_id=subscription_id)
        db.session.add(credential)
        db.session.commit()
        flash('Create account successful')
        return redirect(url_for('index'))
    Credentials = Credential.query.all()
    return render_template('account.html', Credentials=Credentials)


@app.route('/account/delete/<int:credential_id>', methods=['POST'])
def account_delete(credential_id):
    if not current_user.is_authenticated:
        flash('You need login')
        return redirect(url_for('login'))
    credential = Credential.query.get_or_404(credential_id)
    db.session.delete(credential)
    db.session.commit()
    flash('Delete account successful')
    return redirect(url_for('index'))


@app.route('/account/<int:credential_id>/vm/create', methods=['GET', 'POST'])
def create_vm(credential_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need login')
            return redirect(url_for('login'))
        credential = Credential.query.get_or_404(credential_id)
        client_id = credential.client_id
        client_secret = credential.client_secret
        tenant_id = credential.tenant_id
        subscription_id = credential.subscription_id
        tag = request.form.get('tag')
        createtime = time.strftime('%m%d-%H%M', time.localtime(time.time()))
        tag = (tag + "-" + createtime)
        location = request.form.get('location')
        size = request.form.get('size')
        os = request.form.get('os')
        set = request.form.get('set')
        custom = request.form.get('custom')
        acc = request.form.get('acc')
        disk = request.form.get('disk')
        spot = request.form.get('spot')
        username = "defaultuser"
        password = "Thisis.yourpassword1"
        credential = function.create_credential_object(tenant_id, client_id, client_secret)
        for i in range(int(set)):
            name = (tag + "-" + str(i + 1))
            function.create_resource_group(subscription_id, credential, name, location)
            threading.Thread(target=function.create_or_update_vm, args=(
            subscription_id, credential, name, location, username, password, size, os, custom, acc, disk, spot)).start()
        flash('Creating VM, Be patient')
    info = Credential.query.all()
    credential = Credential.query.get_or_404(credential_id)
    account = credential.account
    id = credential.id
    return render_template('createvm.html', account=account, id=id, Credentials=info)


@app.route('/account/<int:credential_id>/vm/delete/<string:tag>', methods=['POST'])
def delete_vm(credential_id, tag):
    if not current_user.is_authenticated:
        flash('You need login')
        return redirect(url_for('login'))
    credential = Credential.query.get_or_404(credential_id)
    client_id = credential.client_id
    client_secret = credential.client_secret
    tenant_id = credential.tenant_id
    subscription_id = credential.subscription_id
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    threading.Thread(target=function.delete_vm, args=(subscription_id, credential, tag)).start()
    flash("Deleting VM, Be patient")
    return redirect(url_for('index'))


@app.route('/account/<int:credential_id>/vm/start/<string:tag>', methods=['POST'])
def start_vm(credential_id, tag):
    if not current_user.is_authenticated:
        flash('You need login')
        return redirect(url_for('login'))
    credential = Credential.query.get_or_404(credential_id)
    client_id = credential.client_id
    client_secret = credential.client_secret
    tenant_id = credential.tenant_id
    subscription_id = credential.subscription_id
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    try:
        threading.Thread(target=function.start_vm, args=(subscription_id, credential, tag)).start()
        flash("Starting VM, Be patient")
        return redirect(url_for('index'))
    except:
        flash("Unexpected error")


@app.route('/account/<int:credential_id>/vm/stop/<string:tag>', methods=['POST'])
def stop_vm(credential_id, tag):
    if not current_user.is_authenticated:
        flash('You need login')
        return redirect(url_for('login'))
    credential = Credential.query.get_or_404(credential_id)
    client_id = credential.client_id
    client_secret = credential.client_secret
    tenant_id = credential.tenant_id
    subscription_id = credential.subscription_id
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    try:
        threading.Thread(target=function.stop_vm, args=(subscription_id, credential, tag)).start()
        flash("Stoping VM, Be patient")
        return redirect(url_for('index'))
    except:
        flash("Unexpected error")


@app.route('/account/<int:credential_id>/vm/changeip/<string:tag>', methods=['POST'])
def changeip_vm(credential_id, tag):
    if not current_user.is_authenticated:
        flash('You need login')
        return redirect(url_for('login'))
    credential = Credential.query.get_or_404(credential_id)
    client_id = credential.client_id
    client_secret = credential.client_secret
    tenant_id = credential.tenant_id
    subscription_id = credential.subscription_id
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    try:
        threading.Thread(target=function.change_ip, args=(subscription_id, credential, tag)).start()
        flash("Chaning IP, Be patient")
        return redirect(url_for('index'))
    except:
        flash("Unexpected error")


@app.route('/account/<int:credential_id>/list', methods=['GET', 'POST'])
def list(credential_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need login')
            return redirect(url_for('login'))
        credential = Credential.query.get_or_404(credential_id)
        id = credential.id
        account = credential.account
        client_id = credential.client_id
        client_secret = credential.client_secret
        tenant_id = credential.tenant_id
        subscription_id = credential.subscription_id
        credential = function.create_credential_object(tenant_id, client_id, client_secret)
        dict = function.list(subscription_id, credential)
        return render_template('list.html', dict=dict, id=id, account=account)


if __name__ == '__main__':
    app.run(port=8888, host="0.0.0.0")
