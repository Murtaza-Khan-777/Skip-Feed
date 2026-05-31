#!/usr/bin/env python
"""Test Flask app endpoints directly"""
import sys
import traceback

try:
    from app import app
    print("=" * 50)
    print("Testing Flask App Endpoints")
    print("=" * 50)
    
    # Create test client
    client = app.test_client()
    
    print("\n1. Testing signup endpoint...")
    response = client.post('/signup', data={
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'testpass123'
    })
    print(f"   Status: {response.status_code}")
    if response.status_code != 302:
        print(f"   Error: Expected 302, got {response.status_code}")
        print(f"   Response: {response.data[:200]}")
    else:
        print("   ✓ Signup successful")
    
    print("\n2. Testing login endpoint...")
    with client:
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Login successful")
        else:
            print(f"   ✗ Login failed: {response.status_code}")
        
        # Test home page
        print("\n3. Testing home page...")
        response = client.get('/home')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Home page loaded")
        else:
            print(f"   ✗ Home page error: {response.status_code}")
            
        # Test add_post
        print("\n4. Testing add post...")
        response = client.post('/add_post', data={
            'content': 'Test post from Flask client'
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Post added")
        else:
            print(f"   ✗ Post creation failed: {response.status_code}")
            print(f"   Response: {response.data[:500]}")
            
        # Test home page again with posts
        print("\n5. Testing home page with posts...")
        response = client.get('/home')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Home page loaded with posts")
        else:
            print(f"   ✗ Home page error: {response.status_code}")
            print(f"   Response: {response.data[:500]}")
    
    print("\n" + "=" * 50)
    print("✓ Flask app tests completed!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
