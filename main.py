from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
from pyngrok import ngrok
from functools import wraps
from db.posts import createPost, getAllPosts, getPostById, deletePostById
from db.clients import getUserById, getUserByEmail, createUser
from db.chats import getChatById, getChatsWithClientById, createChat, getChatBetweenClients
from db.messages import getMessagesByChatId, createMessage
import datetime
import os
import uuid

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static',

)

# session
app.permanent_session_lifetime = datetime.timedelta(days=7)
app.secret_key = 'super secret key'

# uploads
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = '/uploads'
UPLOAD_FOLDER = APP_ROOT + UPLOAD_FOLD
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def login_required(f):
    @wraps(f)
    def check_permissions(*args, **kwargs):
        client_id = session.get("id")
        if client_id is None:
            return redirect(url_for('sign_in'))
        return f(*args, **kwargs)
    return check_permissions


@app.route('/', methods=["GET", "POST"])
@login_required
def feed():
    posts = getAllPosts()
    for i in range(len(posts)):
        posts[i].update({"client_email": getUserById(posts[i]["client_id"])["email"]})

    if request.method == "POST":
        text = request.form["text"]
        file = request.files["file"]
        print(text)
        if len(text) == 0 and file.filename == '':
            return render_template("feed.html", posts=posts, form_post_error="Post can't be empty")
        filename = str(uuid.uuid4())
        date_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        createPost(text, filename, date_time, session["id"])
        return redirect(url_for('feed'))
    return render_template("feed.html", posts=posts)


@app.route('/chatlist/')
@login_required
def chat_list():
    client_id = session["id"]
    chats = getChatsWithClientById(client_id)
    for i in range(len(chats)):
        if chats[i]["first_client_id"] == client_id:
            chats[i].update({"chat_with": getUserById(chats[i]["second_client_id"])["email"]})
        elif chats[i]["second_client_id"] == client_id:
            chats[i].update({"chat_with": getUserById(chats[i]["first_client_id"])["email"]})
    return render_template("chatList.html", chats=chats)


@app.route('/chatlist/find_with/<client_id>')
def chat_find(client_id):
    current_client_id = session["id"]
    chat = getChatBetweenClients(int(client_id), current_client_id)
    if chat:
        return redirect(url_for('chat', chat_id=chat["id"]))
    else:
        chat_id = createChat(current_client_id, int(client_id))
        return redirect(url_for('chat', chat_id=chat_id))


@app.route('/chatlist/<chat_id>', methods=["GET", "POST"])
@login_required
def chat(chat_id):
    if request.method == "POST":
        text = request.form["text"]
        date_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        createMessage(text, date_time, int(chat_id), session["id"])
    messages = getMessagesByChatId(int(chat_id))
    for i in range(len(messages)):
        messages[i].update({"sender_email": getUserById(messages[i]["sender_id"])["email"]})
    return render_template("chat.html", messages=messages)


@app.route('/post/delete/<post_id>', methods=["POST"])
@login_required
def post_delete(post_id):
    if request.method == "POST":
        post = getPostById(post_id)
        if post["client_id"] == session["id"]:
            deletePostById(post_id)
            return redirect(url_for('feed'))


@app.route('/auth/signin', methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_from_db = getUserByEmail(email)
        if user_from_db and user_from_db["password"] == password:
            session["id"] = user_from_db["id"]
            return redirect(url_for('feed'))
        else:
            return render_template("signIn.html", error="Not completed")
    elif request.method == "GET":
        return render_template("signIn.html")


@app.route('/auth/signup', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        again_password = request.form["again_password"]
        if password != again_password:
            return render_template("signUp.html", error="Passwords are not the same")
        user_from_db = getUserByEmail(email)
        if not user_from_db:
            createUser(email, password)
            created_user = getUserByEmail(email)
            session["id"] = created_user["id"]
            return redirect(url_for('feed'))
        else:
            return render_template("signUp.html", error="There's user with this email")
    elif request.method == "GET":
        return render_template("signUp.html")


@app.route('/auth/logout')
def log_out():
    session["id"] = None
    return redirect(url_for('sign_in'))


@app.route('/profile/<client_id>', methods=["GET", "POST"])
@login_required
def profile(client_id):
    client_id = int(client_id)
    client = getUserById(client_id)
    client_email = client["email"]
    client_about = client["about"]
    return render_template("profile.html", client_id=client_id, client_email=client_email, client_about=client_about)


ngrok.set_auth_token("37vEMXYcl0YQCjTmbePQHAJivz3_3VveMBS8a9PDpMZbwsPxA")
public_url = ngrok.connect(5000)
print(f" * ngrok tunnel available at: {public_url}")
app.run(host='0.0.0.0', port=5000)
