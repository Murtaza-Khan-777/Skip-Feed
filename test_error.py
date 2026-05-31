#!/usr/bin/env python
import sys
import traceback
from brain import load_server, create_post, load_feed

try:
    print("Loading server...")
    user_base, posts_base = load_server()
    print(f"User base loaded with users")
    print(f"Posts base loaded")
    
    # Try to create a post
    print("\nCreating a post...")
    create_post("Test post content", 1, posts_base)
    print("Post created successfully")
    
    # Try to load feed
    print("\nLoading feed...")
    feed = load_feed(1, 'friends', posts_base, user_base)
    print(f"Feed loaded with {len(feed)} posts")
    
    for post in feed:
        print(f"  - Post {post['post_id']}: {post['username']} - {post['content'][:30]}...")
        
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All tests passed!")
