# SkipFeed 🚀
**A High-Performance Social Media Backend utilizing a Custom Write-Through Skip List Cache.**

SkipFeed is a social media prototype built for a Data Structures and Algorithms (DSA) project. It demonstrates how to handle the massive read-heavy bottlenecks of social network feeds by implementing an **In-Memory Write-Through Cache** using custom **Skip Lists**, all backed by a persistent, normalized SQLite database.

---

## 🧠 Core Architecture (The DSA Flex)

Instead of traditionally querying an SQL database on every page load, SkipFeed uses a hybrid architecture designed for extreme read speeds:

1. **The Primary Datastore (RAM/Skip Lists):** On server startup, the database injects all users, posts, and relationships into memory using custom Skip Lists. This guarantees **$O(\log n)$** search and retrieval times for users and posts.
2. **The Permanent Storage (Disk/SQLite):** A strict, ACID-compliant 4-table relational database acts as the source of truth.
3. **Write-Through Caching:** When a state changes (e.g., a user likes a post), the app instantly updates the Skip List in RAM for an immediate UI response, and simultaneously writes the data *through* to the SQLite database via `INSERT OR IGNORE` to guarantee permanent data safety.

### ⚡ Algorithmic Feed Generation
SkipFeed repurposes the probabilistic levels of a Skip List to act as an algorithmic routing engine:
* **Level 0 (Global Timeline):** Stores all posts.
* **Level 1 (Popular Feed):** Only stores "Highly Charged Nodes" (posts with 2+ likes).
* **Level 2 (Friends Feed):** Only stores posts written by accepted friends or the active user.
* *Result:* Generating a targeted feed does not require scanning the entire database; the algorithm simply traverses the pre-sorted corresponding level in **$O(k)$** time.

---

## 📂 Project Structure

* **`app.py`**: The Flask web server. Handles routing, session cookies, and passes requests to the logic layer.
* **`brain.py`**: The core logic engine. Manages the Write-Through protocol, intercepts Flask requests, updates the RAM Skip Lists, and executes SQLite backups.
* **`skiplist.py`**: The custom Data Structure implementation containing standard `SkipList` and the specialized `PostSkipList` for algorithmic feed generation.
* **`schema.sql`**: The 4-Table relational database blueprint (Users, Posts, and Junction Tables for Friends and Likes).
* **`init_db.py`**: Utility script to build the initial `social_media.db` file.
* **`posts.py`**: Object-oriented models for posts and content compression (using `zlib`).

---

## 🛠️ Setup & Installation

### Prerequisites
* Python 3.x
* Flask (`pip install Flask`)

### Running the App
1. **Initialize the Database:**
   Run the setup script to build the 4-table SQLite schema.
   ```bash
   python init_db.py