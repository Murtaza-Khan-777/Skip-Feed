import sqlite3

def initialize_database():
    try:
        connection = sqlite3.connect('social_media.db')
        
        with open('schema.sql', 'r') as f:
            schema_script = f.read()
        connection.executescript(schema_script)
        connection.commit()
        connection.close()
        print("✅ Database 'social_media.db' created successfully with your schema!")
        
    except FileNotFoundError:
        print("❌ Error: 'schema.sql' not found. Make sure the file name is correct.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    initialize_database()