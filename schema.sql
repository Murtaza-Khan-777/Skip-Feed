-- 1. USERS TABLE
CREATE TABLE users(
  user_id INTEGER PRIMARY KEY,
  user_name TEXT UNIQUE, 
  email TEXT,
  pass TEXT
);

-- 2. FRIENDS TABLE (Junction Table)
CREATE TABLE friends(
  user_id_1 INTEGER,
  friend_id INTEGER,
  friend_status TEXT,
  PRIMARY KEY (user_id_1, friend_id),
  FOREIGN KEY (user_id_1) REFERENCES users(user_id),
  FOREIGN KEY (friend_id) REFERENCES users(user_id)
);

-- 3. POSTS TABLE
CREATE TABLE posts(
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    content BLOB, 
    likes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 4. POST LIKES TABLE (Junction Table)
CREATE TABLE post_likes (
    user_id INTEGER,
    post_id INTEGER,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);