import sqlite3 as sq
from skiplist import SkipList, PostSkipList
import zlib
import random

def load_server():
    user_base = SkipList(15)
    posts_base = SkipList(15)
    conn = sq.connect("social_media.db")
    cursor = conn.cursor()
    # loads users and friends from data base
    cursor.execute("SELECT user_id, user_name, email, pass FROM users ORDER BY user_id ASC")
    for record in cursor.fetchall():
        uid, uname, email, password = record[0], record[1], record[2], record[3]
        
        #gets the freind status
        cursor.execute("SELECT friend_id, friend_status FROM friends WHERE user_id_1 = ?", (uid,))
        friends_list = []
        for f_row in cursor.fetchall():
            friends_list.append([f_row[0], f_row[1]]) # Standard Python List!
            
        user_base.insert([uid, uname, email, password, friends_list])
    # load posts and likes
    cursor.execute("SELECT post_id, user_id, content, likes FROM posts ORDER BY post_id ASC")
    for post in cursor.fetchall():
        pid, uid, content, likes_count = post[0], post[1], post[2], post[3]
        
        # Grab likes from the junction table
        cursor.execute("SELECT user_id FROM post_likes WHERE post_id = ?", (pid,))
        liked_by_set = set(row[0] for row in cursor.fetchall()) # Standard Python Set!
        
        posts_base.insert([pid, uid, content, likes_count, liked_by_set])
        
    conn.close()
    print("Lists loaded Skiplists ready to go!")
    return user_base, posts_base

def search(search_query, search_base, search_level=0, output_level=1):
    return search_base.search(search_query, search_level, output_level)

def show_pending(user_id, user_base):
    friends = search(user_id, user_base, 0, 4)
    pending_friends = []
    
    # Bulletproof type check
    if isinstance(friends, list):
        for friend in friends:
            # Ensure it's a valid [id, status] pair
            if isinstance(friend, list) and len(friend) >= 2:
                if friend[1] == "pending":
                    pending_friends.append(friend[0])
                
    return pending_friends

def get_accepted_friends(user_id, user_base):
    friends = search(user_id, user_base, 0, 4)
    accepted_friends = []
    
    # Bulletproof type check
    if isinstance(friends, list):
        for friend in friends:
            if isinstance(friend, list) and len(friend) >= 2:
                if friend[1] == "accepted":
                    accepted_friends.append(friend[0])
                
    return accepted_friends

def send_request(current_user_id, receiver_id, user_base):
    #Update RAM instantly using standard List append
    friends_list = search(receiver_id, user_base, 0, 4)
    if isinstance(friends_list, list):
        #Append the new relationship as a sub-list: [user_id, status]
        friends_list.append([current_user_id, "pending"])
        
    # 2. Save to SQLite (happens in the backend slowly)
    conn = sq.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO friends (user_id_1, friend_id, friend_status) VALUES (?, ?, 'pending')", (receiver_id, current_user_id))
    conn.commit()
    conn.close()

def accept_request(current_user_id, sender_id, user_base):
    #Update the Receiver's RAM list
    friends = search(current_user_id, user_base, 0, 4)
    if isinstance(friends, list):
        for current in friends:
            if current[0] == current_user_id and current[1] in ("pending", "accepted"):
                break # step incase already sent request before.
        for friend in friends:
            if isinstance(friend, list) and friend[0] == sender_id:
                friend[1] = "accepted"

    # 2. Update the Sender's RAM list to make it mutual
    sender_friends = search(sender_id, user_base, 0, 4)
    if isinstance(sender_friends, list):
        sender_friends.append([current_user_id, "accepted"])
        
    #  Update sql in the background
    conn = sq.connect("social_media.db")
    cursor = conn.cursor()
    
    # Update the original request to 'accepted'
    cursor.execute("UPDATE friends SET friend_status = 'accepted' WHERE user_id_1 = ? AND friend_id = ?", (current_user_id, sender_id))
    
    # Insert the mutual connection for the sender
    cursor.execute("INSERT OR IGNORE INTO friends (user_id_1, friend_id, friend_status) VALUES (?, ?, 'accepted')", (sender_id, current_user_id))
    
    conn.commit()
    conn.close()

def delete_request(current_user_id, sender_id, user_base):
    # 1. Update RAM Instantly
    friends = search(current_user_id, user_base, 0, 4)
    if isinstance(friends, list):
        for friend in friends:
            if isinstance(friend, list) and friend[0] == sender_id:
                friends.remove(friend) 
                break # Stop looping once we find and delete them
                
    #  Update sql in the background
    conn = sq.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM friends WHERE user_id_1 = ? AND friend_id = ?", (current_user_id, sender_id))
    conn.commit()
    conn.close()

def signup(email, username, password, user_base):
    # Collision Check (Instantly scan the bottom level of the Skip List)
    current = user_base.header.forward[0]
    while current:
        if current.data[1] == username or current.data[2] == email:
            return None # Collision found!
        current = current.forward[0]

    # Save to SQLite Permanently
    conn = sq.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_name, email, pass) VALUES(?,?,?)", (username, email, password))
    user_id = cursor.lastrowid # Get the newly generated SQL ID
    conn.commit()
    conn.close()
    
    # Inject the entry to the ram skiplist
    # Format: [user_id, username, email, password, [friends_array]]
    user_base.insert([user_id, username, email, password, []])
    return user_id

def login(username, password, user_base):
    print(f"Authenticating Node: {username}")
    
    # Scan the Level 0 where all the data is present
    current = user_base.header.forward[0]
    while current:
        if current.data[1] == username and current.data[3] == password:
            return current.data[0] # Return their integer user_id
        current = current.forward[0]
        
    return None # Invalid credentials

def create_post(content, user_id, posts_base):
    compressed_content = zlib.compress(content.encode('utf-8'))
    
    #Save to SQL Permanently
    conn = sq.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (content, user_id, likes) VALUES (?, ?, 0)", (compressed_content, user_id))
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()

    #Inject into RAM Skip List
    # Format: [post_id, user_id, compressed_content, likes_count, set(liked_by_users)]
    posts_base.insert([post_id, user_id, compressed_content, 0, set()])

def load_feed(user_id, view_type, posts_base, user_base):
    # 1. Get accepted friends from the user_base Skip List
    accepted_friends = get_accepted_friends(user_id, user_base)
    feed_posts = []
    post_feed = PostSkipList(3)
    
    # 2. Traverse the Posts Skip List (Level 0)
    current = posts_base.header.forward[0]
    while current:
        post_data = current.data
        pid, uid, compressed_content, likes, liked_by = post_data[0], post_data[1], post_data[2], post_data[3], post_data[4]
        
        if uid in accepted_friends or uid == user_id:
            post_feed.insert_at_level(post_data, 2) # Insert into level 2 of postskiplist since level 2 is for friends and own posts.
        elif likes >= 2: # Arbitrary threshold for most liked
            post_feed.insert_at_level(post_data, 1) # Insert into level 1 of postskiplist since level 1 is for most liked posts.
        else:
            post_feed.insert_at_level(post_data, 0) # Insert into level 0 where all posts go, but will only be shown in random view.
        
        current = current.forward[0]
    if view_type == 'friends':
        candidates = post_feed.traverse_level(2) #level 2 consists of friends and own posts only.
        # --- THE DSA FILTERING LOGIC ---
                
    elif view_type == 'most_liked':
        candidates = []
        temp_candidates = post_feed.traverse_level(1)
        for current in temp_candidates:
            if current[1] not in accepted_friends and current[1] != user_id: #removing friends and own post from layer 1
                candidates.append(current)
            
    else:
        candidates = post_feed.traverse_level(0) #will generate random posts with every click.

        # hydraing post
    for post in candidates:
        pid, uid, compressed_content, likes, liked_by = post[0], post[1], post[2], post[3], post[4]
        content = zlib.decompress(compressed_content).decode('utf-8')
        author_name = search(uid, user_base, 0, 1)
        
        feed_posts.append({
            'post_id': pid,
            'user_id': uid,
            'username': author_name,
            'content': content,
            'likes': likes,
            'already_liked': user_id in liked_by
        })

    if view_type == 'random':
        random.shuffle(feed_posts)
        return feed_posts[:15] # Return 15 random posts
        
    # Reverse the list so the newest posts (highest IDs) are at the top!
    return feed_posts

def like_post(user_id, post_id, posts_base):
    current = posts_base.header
    for i in range(posts_base.current_level, -1, -1):
        while current.forward[i] and current.forward[i].data[0] < post_id:
            current = current.forward[i]
            
    current = current.forward[0]
    
    # Process the like if found
    if current and current.data[0] == post_id:
        liked_by_set = current.data[4] 
        

        if user_id in liked_by_set:
            return False 
            
        liked_by_set.add(user_id) 
        current.data[3] += 1      
        
        conn = sq.connect("social_media.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO post_likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
            cursor.execute("UPDATE posts SET likes = likes + 1 WHERE post_id = ?", (post_id,))
            conn.commit()
        except sq.IntegrityError:
            pass # Failsafe in case SQL already has the like
        finally:
            conn.close()
            
        return True
        
    return False