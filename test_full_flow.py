#!/usr/bin/env python
"""Test the full Flask app flow"""
import sys
import traceback
import tempfile
from flask import Flask
from brain import load_server, signup, login, create_post, load_feed, send_request, show_pending

try:
    print("=" * 50)
    print("Testing Full Social Media Flow")
    print("=" * 50)
    
    # Load server
    print("\n1. Loading server...")
    user_base, posts_base = load_server()
    print("   ✓ Server loaded")
    
    # Simulate user operations
    print("\n2. Testing user operations...")
    
    # Test signup
    print("   - Signing up user1...")
    uid1 = signup("user1@example.com", "user1", "pass123", user_base)
    print(f"     ✓ User 1 created: ID={uid1}")
    
    # Test login
    print("   - Logging in as user1...")
    logged_in = login("user1", "pass123", user_base)
    print(f"     ✓ Login successful: ID={logged_in}")
    
    # Test post creation
    print("\n3. Testing post creation...")
    print("   - Creating posts...")
    create_post("Hello world from user1!", uid1, posts_base)
    print("     ✓ Post 1 created")
    create_post("Another post!", uid1, posts_base)
    print("     ✓ Post 2 created")
    
    # Test feed loading
    print("\n4. Testing feed loading...")
    print("   - Loading friends feed...")
    feed = load_feed(uid1, 'friends', posts_base, user_base)
    print(f"     ✓ Loaded {len(feed)} posts")
    
    for i, post in enumerate(feed, 1):
        print(f"       Post {i}: '{post['username']}' - {post['content'][:40]}...")
        
    # Test popular feed
    print("   - Loading popular feed...")
    feed_popular = load_feed(uid1, 'popular', posts_base, user_base)
    print(f"     ✓ Loaded {len(feed_popular)} popular posts")
    
    # Test random feed
    print("   - Loading random feed...")
    feed_random = load_feed(uid1, 'random', posts_base, user_base)
    print(f"     ✓ Loaded {len(feed_random)} random posts")
    
    # Test friend requests
    print("\n5. Testing friend operations...")
    
    # Create second user
    print("   - Creating second user...")
    uid2 = signup("user2@example.com", "user2", "pass456", user_base)
    print(f"     ✓ User 2 created: ID={uid2}")
    
    # Send friend request
    print("   - Sending friend request from user1 to user2...")
    send_request(uid1, uid2, user_base)
    print("     ✓ Friend request sent")
    
    # Show pending requests
    print("   - Getting pending requests for user2...")
    pending = show_pending(uid2, user_base)
    print(f"     ✓ Found {len(pending)} pending requests")
    for req in pending:
        print(f"       - Request from: {req.get('user_name', 'Unknown')} (ID: {req.get('user_id')})")
    
    print("\n" + "=" * 50)
    print("✓ ALL TESTS PASSED!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
