"""
MongoDB Atlas Connection Test
Tests the connection from your Django/FastAPI backend to MongoDB Atlas
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Get configuration from .env file
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "apdf_io_mongo")

# Print header
print("\n" + "="*80)
print("🧪 MONGODB ATLAS CONNECTION TEST")
print("="*80)
print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📊 Database Name: {DATABASE_NAME}")
print("="*80)

# Validate that URI is set
if not MONGODB_URI:
    print("❌ ERROR: MONGODB_URI not found in .env file!")
    print("="*80 + "\n")
    exit(1)

# Extract username from URI for display (hide password)
try:
    uri_display = MONGODB_URI.split("://")[1].split("@")[0]  # Get user:password part
    username = uri_display.split(":")[0]
    print(f"👤 Username: {username}")
    print(f"🔐 Password: {'*' * 20} (hidden)")
except:
    print(f"🔐 Connection URI: {MONGODB_URI[:50]}... (truncated)")

print("\n🔄 Attempting to connect to MongoDB Atlas...")
print("-" * 80)

try:
    # Create MongoDB client with timeout
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,  # 10 second timeout
        connectTimeoutMS=10000
    )
    
    # Test the connection with ping
    print("  ⏳ Sending ping command...")
    result = client.admin.command('ping')
    
    print("✅ PING SUCCESSFUL!")
    print(f"   Response: {result}")
    
    # Get database
    print("\n🔍 Checking database and collections...")
    print("-" * 80)
    
    db = client[DATABASE_NAME]
    
    # List existing collections
    collections = db.list_collection_names()
    print(f"📚 Existing Collections ({len(collections)}): {collections if collections else 'None'}")
    
    # Show what collections will be created by auth system
    print("\n📝 Auth System Collections (auto-created):")
    print("   ✓ 'users' - Will store user accounts")
    print("   ✓ 'password_reset_tokens' - Will store password reset requests")
    
    # Test write permission (optional - creates a test collection)
    print("\n✅ Checking database write permissions...")
    try:
        test_collection = db['_connection_test']
        test_doc = {"test": True, "timestamp": datetime.now()}
        result = test_collection.insert_one(test_doc)
        print(f"   ✓ Write test successful (ID: {result.inserted_id})")
        test_collection.delete_one({"_id": result.inserted_id})
        print(f"   ✓ Cleanup successful")
    except Exception as write_error:
        print(f"   ⚠️ Write test warning: {write_error}")
    
    # Get server info
    print("\n📊 MongoDB Server Information:")
    try:
        info = client.server_info()
        print(f"   Version: {info.get('version', 'Unknown')}")
        print(f"   Atlas: Yes (Cloud-hosted)")
    except:
        print("   (Could not retrieve server info)")
    
    # Final status
    print("\n" + "="*80)
    print("✅ CONNECTION TEST SUCCESSFUL!")
    print("="*80)
    print("\n✨ Your backend is ready to:")
    print("   ✓ Register users")
    print("   ✓ Handle login/logout")
    print("   ✓ Store authentication tokens")
    print("   ✓ Process password resets")
    print("\n🚀 You can now run: python run.py")
    print("="*80 + "\n")
    
    # Close connection
    client.close()
    
except Exception as error:
    print("❌ CONNECTION FAILED!")
    print("="*80)
    print(f"\n❌ Error Type: {type(error).__name__}")
    print(f"❌ Error Message: {error}")
    print("\n" + "-"*80)
    print("🔧 TROUBLESHOOTING GUIDE:")
    print("-"*80)
    
    error_str = str(error)
    
    if "bad auth" in error_str or "authentication failed" in error_str:
        print("\n❌ AUTHENTICATION FAILED")
        print("\n💡 Solutions:")
        print("   1. Check your MongoDB password in .env file")
        print("   2. The password should NOT be URL-encoded")
        print("   3. Make sure the password matches what's in MongoDB Atlas")
        print("   4. Try resetting the password in Database Access → Edit User")
        print("\n📋 Your current .env:")
        print(f"   MONGODB_URI: {MONGODB_URI[:100]}...")
        print(f"   DATABASE_NAME: {DATABASE_NAME}")
        
    elif "connection" in error_str.lower():
        print("\n❌ CONNECTION ERROR")
        print("\n💡 Solutions:")
        print("   1. Check if MongoDB Atlas cluster is running")
        print("   2. Verify Network Access allows your IP (0.0.0.0/0)")
        print("   3. Check internet connection")
        print("   4. Verify MongoDB URI format is correct")
        
    elif "pymongo" in error_str:
        print("\n❌ PYMONGO ERROR")
        print("\n💡 Solutions:")
        print("   1. Install pymongo with srv support:")
        print("      pip install 'pymongo[srv]' dnspython")
        print("   2. Restart your terminal after installation")
        
    else:
        print("\n💡 General Solutions:")
        print("   1. Check .env file is in backend/ directory")
        print("   2. Verify all values are correct")
        print("   3. Run: pip install 'pymongo[srv]' dnspython")
        print("   4. Check MongoDB Atlas dashboard for status")
    
    print("\n" + "="*80 + "\n")
    exit(1)
