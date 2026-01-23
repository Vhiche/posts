from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from pyngrok import ngrok
from functools import wraps
from db.posts import createPost, getAllPosts, getPostById, deletePostById
from db.clients import getUserById, getUserByEmail, createUser, getUserByUsername, editUser
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
socketio = SocketIO(app)


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


@socketio.on("join_chat")
def join_chat(data):
    join_room(data["chat_id"])


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
        posts[i].update({"client_username": getUserById(posts[i]["client_id"])["username"]})

    if request.method == "POST":
        text = request.form["text"]
        file = request.files["file"]
        print(text)
        if len(text) == 0 and file.filename == '':
            return render_template("feed.html", posts=posts, form_post_error="Post can't be empty")
        filename = str(uuid.uuid4()) + '.' + str(file.filename).split('.')[-1]
        date_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        if file.filename != '':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = ''
        post_id = createPost(text, filename, date_time, session["id"])
        user = getUserById(session["id"])
        socketio.emit("new_post", {
            "id": post_id,
            "text": text,
            "filename": filename,
            "datetime": date_time,
            "client_id": session["id"],
            "client_username": user["username"]
        })
        return redirect(url_for('feed'))
    return render_template("feed.html", posts=posts)


@app.route('/chatlist/')
@login_required
def chat_list():
    client_id = session["id"]
    chats = getChatsWithClientById(client_id)
    for i in range(len(chats)):
        if chats[i]["first_client_id"] == client_id:
            chats[i].update({"chat_with": getUserById(chats[i]["second_client_id"])["username"]})
        elif chats[i]["second_client_id"] == client_id:
            chats[i].update({"chat_with": getUserById(chats[i]["first_client_id"])["username"]})
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


@app.route('/chatlist/<chat_id>')
@login_required
def chat(chat_id):
    messages = getMessagesByChatId(int(chat_id))
    for i in range(len(messages)):
        messages[i].update({"sender_username": getUserById(messages[i]["sender_id"])["username"]})
    return render_template("chat.html", messages=messages, chat_id=chat_id)


@socketio.on("sendMessage")
@login_required
def handle_message(data):
    text = data["text"]
    chat_id = int(data["chat_id"])
    sender_id = session["id"]
    date_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M")
    createMessage(text, date_time, chat_id, sender_id)
    user = getUserById(sender_id)
    emit("new_message", {
        "text": text,
        "email": user["email"],
        "time": date_time,
        "sender_id": sender_id
    }, to=str(chat_id))


@app.route('/post/delete/<post_id>', methods=["POST"])
@login_required
def post_delete(post_id):
    if request.method == "POST":
        post = getPostById(post_id)
        if post["client_id"] == session["id"]:
            deletePostById(post_id)
            socketio.emit("post_deleted", {
                "post_id": post_id
            })
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
        username = request.form["username"]
        password = request.form["password"]
        again_password = request.form["again_password"]
        if password != again_password:
            return render_template("signUp.html", error="Passwords are not the same")
        user_from_db_email = getUserByEmail(email)
        if not user_from_db_email:
            user_from_db_name = getUserByUsername(email)
            if not user_from_db_name:
                createUser(email, password, username)
                created_user = getUserByEmail(email)
                session["id"] = created_user["id"]
                return redirect(url_for('feed'))
            else:
                return render_template("signUp.html", error="There's user with this username")
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
    client_username = client["username"]
    client_email = client["email"]
    client_about = client["about"]
    return render_template("profile.html", client_id=client_id, client_username=client_username,
                           client_email=client_email, client_about=client_about)


@app.route('/profile/edit', methods=["GET", "POST"])
@login_required
def edit_profile():
    client = getUserById(session["id"])
    client_username = client["username"]
    client_email = client["email"]
    client_about = client["about"]
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        about = request.form["about"]
        user_from_db_email = getUserByEmail(email)
        if not user_from_db_email or email == client_email:
            user_from_db_name = getUserByUsername(email)
            if not user_from_db_name or username == client_username:
                editUser(session["id"], email, username, about)
                return redirect(url_for('profile', client_id=session["id"]))
            else:
                return render_template("editProfile.html", error="There's user with this username", client_username=client_username,
                           client_email=client_email, client_about=client_about)
        else:
            return render_template("editProfile.html", error="There's user with this email", client_username=client_username,
                           client_email=client_email, client_about=client_about)
    elif request.method == "GET":
        return render_template("editProfile.html", client_username=client_username,
                           client_email=client_email, client_about=client_about)


if __name__ == "__main__":
    ngrok.set_auth_token("38dB4HpbLJAgzX10EwAiZg0WjBI_5yUsDvyWS7d4ZQ41U6NzY")
    try:
        ngrok.kill()
    except:
        pass
    try:
        public_url = ngrok.connect("5000")
        print(f" * ngrok tunnel available at: {public_url}")
    except Exception as e:
        print(f"ngrok error: {e}")
        print("Running without ngrok tunnel")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
