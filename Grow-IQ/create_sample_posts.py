#!/usr/bin/env python3
"""
Script to create sample posts for Qrow IQ
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import User, Post, Comment
from datetime import datetime, timedelta

def create_sample_posts():
    """Create sample posts in the database"""
    print("📝 Creating Sample Posts...")
    print("=" * 50)
    
    try:
        # Get database session
        print("1️⃣ Getting database session...")
        db = next(get_db())
        print("✅ Database session obtained")
        
        # Get users
        print("2️⃣ Getting users...")
        users = db.query(User).all()
        if not users:
            print("❌ No users found in database")
            return False
        
        print(f"✅ Found {len(users)} users")
        for user in users:
            print(f"   - {user.full_name} ({user.username})")
        
        # Check if posts already exist
        print("3️⃣ Checking if posts already exist...")
        existing_posts = db.query(Post).count()
        if existing_posts > 0:
            print(f"✅ {existing_posts} posts already exist")
            return True
        
        # Create sample posts
        print("4️⃣ Creating sample posts...")
        
        sample_posts = [
            {
                "user": users[0],  # Test User
                "content": "Excited to join Qrow IQ! Looking forward to connecting with fellow professionals and sharing insights about software development. 🚀 #CareerGrowth #Networking",
                "post_type": "general",
                "created_at": datetime.now() - timedelta(hours=2)
            },
            {
                "user": users[1],  # John Developer
                "content": "Just finished a challenging project using React and Node.js. The satisfaction of solving complex problems is what keeps me motivated in this field. 💻 #WebDevelopment #React #NodeJS",
                "post_type": "general",
                "created_at": datetime.now() - timedelta(hours=4)
            },
            {
                "user": users[2],  # Sarah Manager
                "content": "Product management tip: Always start with the user's problem, not the solution. Understanding the 'why' behind user needs leads to better products. 📊 #ProductManagement #UserExperience",
                "post_type": "general",
                "created_at": datetime.now() - timedelta(hours=6)
            },
            {
                "user": users[3],  # Mike Designer
                "content": "Design is not just what it looks like and feels like. Design is how it works. - Steve Jobs. This quote perfectly captures the essence of good UX design. 🎨 #UXDesign #DesignThinking",
                "post_type": "general",
                "created_at": datetime.now() - timedelta(hours=8)
            },
            {
                "user": users[0],  # Test User
                "content": "Looking for opportunities to collaborate on open-source projects. Anyone working on interesting projects that need contributors? 🤝 #OpenSource #Collaboration #SoftwareDevelopment",
                "post_type": "general",
                "created_at": datetime.now() - timedelta(hours=10)
            },
            {
                "user": users[1],  # John Developer
                "content": "The best code is no code at all. Sometimes the simplest solution is the most elegant one. Keep it simple, developers! ✨ #Coding #BestPractices #Simplicity",
                "post_type": "general",
                "created_at": datetime.now() - timedelta(hours=12)
            }
        ]
        
        for post_data in sample_posts:
            post = Post(
                user_id=post_data["user"].id,
                content=post_data["content"],
                post_type=post_data["post_type"],
                created_at=post_data["created_at"]
            )
            db.add(post)
        
        db.commit()
        print("✅ Sample posts created successfully!")
        
        # Create some sample comments
        print("5️⃣ Creating sample comments...")
        
        posts = db.query(Post).all()
        sample_comments = [
            {
                "post": posts[0],
                "user": users[1],
                "content": "Welcome to Qrow IQ! Looking forward to connecting with you! 👋",
                "created_at": datetime.now() - timedelta(hours=1)
            },
            {
                "post": posts[0],
                "user": users[2],
                "content": "Great to have you here! What kind of software development are you focused on?",
                "created_at": datetime.now() - timedelta(minutes=30)
            },
            {
                "post": posts[1],
                "user": users[0],
                "content": "React and Node.js is a powerful combination! What was the most challenging part?",
                "created_at": datetime.now() - timedelta(hours=3)
            },
            {
                "post": posts[2],
                "user": users[3],
                "content": "Absolutely agree! User research is the foundation of good product design.",
                "created_at": datetime.now() - timedelta(hours=5)
            }
        ]
        
        for comment_data in sample_comments:
            comment = Comment(
                post_id=comment_data["post"].id,
                user_id=comment_data["user"].id,
                content=comment_data["content"],
                created_at=comment_data["created_at"]
            )
            db.add(comment)
        
        db.commit()
        print("✅ Sample comments created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample posts: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("Starting Sample Posts Creation...")
    print()
    
    success = create_sample_posts()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Sample posts created successfully!")
        print("\n📱 Now your home page will have:")
        print("   - 6 sample posts from different users")
        print("   - 4 sample comments")
        print("   - Real content to interact with")
        print("\n🌐 Next steps:")
        print("1. Login with: test@qrowiq.com / TestPass123!")
        print("2. Go to: http://localhost:8000/home")
        print("3. See your LinkedIn-style feed with real content!")
    else:
        print("❌ Failed to create sample posts")
        print("Check the error messages above")
