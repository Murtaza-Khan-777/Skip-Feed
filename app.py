
from flask import Flask, render_template, request, redirect, url_for, session, flash
from brain import * 
app = Flask(__name__)
app.secret_key = "dsa_project_secret_key"


# INITIALIZE SERVER & SKIP LISTS

print("Spinning up server and loading Skip Lists...")
user_base, posts_base = load_server()

# FLASK ROUTES

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login_route'))

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_id = login(username, password, user_base)
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_route():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_id = signup(email, username, password, user_base)
        print(f"New User ID Generated: {user_id}")
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Signup failed. User might already exist.")
            
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_route'))
    
    uid = session['user_id']
    view_type = request.args.get('view', 'friends')

    posts = load_feed(uid, view_type, posts_base, user_base)
    raw_requests = show_pending(uid, user_base)
    raw_friends = get_accepted_friends(uid, user_base)
    # get all the freinds
    hydrated_friends = []
    for fid in raw_friends:
        fname = search(fid, user_base, 0, 1) # O(log n) lookup
        hydrated_friends.append({
            'user_id': fid, 
            'username': fname if fname else "Unknown"
        })
        
    # get all the requests Do the same for pending friend requests
    hydrated_requests = []
    for req_id in raw_requests:
        rname = search(req_id, user_base, 0, 1)
        hydrated_requests.append({
            'user_id': req_id, 
            'username': rname if rname else "Unknown"
        })
    
    return render_template('home.html', 
                           posts=posts, 
                           requests=hydrated_requests, # Pass the hydrated list
                           friends_list=hydrated_friends, # Pass the hydrated list
                           friends_ids=raw_friends,
                           username=session['username'],
                           current_view=view_type)

@app.route('/add_post', methods=['POST'])
def add_post():
    if 'user_id' in session:
        content = request.form.get('content')
        if content:
            # PASSED IN: posts_base
            create_post(content, session['user_id'], posts_base)
    return redirect(url_for('home'))

@app.route('/accept/<int:friend_id>', methods=['POST'])
def accept_friend(friend_id):
    # PASSED IN: user_base
    accept_request(session['user_id'], friend_id, user_base)
    return redirect(url_for('home'))

@app.route('/decline/<int:friend_id>', methods=['POST'])
def decline_friend(friend_id):
    # PASSED IN: user_base
    delete_request(session['user_id'], friend_id, user_base)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_route'))

@app.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    if 'user_id' in session:
        if session['user_id'] != friend_id:
            # PASSED IN: user_base
            send_request(session['user_id'], friend_id, user_base)
            flash("Friend request sent!")
    return redirect(url_for('home'))

@app.route('/like/<int:post_id>', methods=['POST'])
def handle_like(post_id):
    if 'user_id' in session:
        last_view = request.form.get('current_view', 'friends')
        # PASSED IN: posts_base
        like_post(session['user_id'], post_id, posts_base)
    return redirect(url_for('home', view=last_view))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)