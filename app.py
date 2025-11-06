from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# 🧱 Database Connection Helper
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print("❌ Database connection failed:", str(e))
        raise

# ✅ Home route (for testing)
@app.route("/")
def home():
    return jsonify({"message": "Backend is running successfully ✅"}), 200

# ✅ Get all books
@app.route("/books", methods=["GET"])
def get_books():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, author, image_url FROM books ORDER BY created_at DESC")
        rows = cur.fetchall()
        books = [
            {"id": r[0], "title": r[1], "author": r[2], "image_url": r[3]}
            for r in rows
        ]
        cur.close()
        conn.close()
        return jsonify(books), 200
    except Exception as e:
        print("❌ Error fetching books:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Upload a book with image
@app.route("/upload", methods=["POST"])
def upload_book():
    try:
        title = request.form.get("title")
        author = request.form.get("author")
        image = request.files.get("image")

        if not title or not author or not image:
            return jsonify({"error": "Missing title, author, or image"}), 400

        # Upload image to S3
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )

        bucket = os.getenv("S3_BUCKET_NAME")
        filename = secure_filename(image.filename)
        s3.upload_fileobj(image, bucket, filename)

        image_url = f"https://{bucket}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{filename}"

        # Insert into RDS (with dummy user_id + created_at)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO books (title, author, image_url, user_id, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, author, image_url, "test-user", datetime.utcnow()),
        )
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Book '{title}' uploaded successfully!")
        return jsonify({"message": "Book uploaded successfully"}), 200

    except Exception as e:
        print("❌ Upload failed:", str(e))
        return jsonify({"error": str(e)}), 500


# ✅ Delete a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"🗑️ Book ID {book_id} deleted.")
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        print("❌ Delete failed:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
@app.route("/upload", methods=["POST"])
def upload_book():
    try:
        print("🟢 Step 1: Starting upload")
        title = request.form.get("title")
        author = request.form.get("author")
        image = request.files.get("image")
        if not title or not author or not image:
            return jsonify({"error": "Missing title, author, or image"}), 400

        print("🟢 Step 2: Connecting to S3...")
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        bucket = os.getenv("S3_BUCKET_NAME")
        filename = secure_filename(image.filename)

        print("🟢 Step 3: Uploading file to S3...")
        s3.upload_fileobj(image, bucket, filename)
        print("✅ Step 4: S3 upload complete")

        image_url = f"https://{bucket}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{filename}"

        print("🟢 Step 5: Connecting to RDS...")
        conn = get_db_connection()
        cur = conn.cursor()

        print("🟢 Step 6: Inserting record into DB...")
        cur.execute(
            """
            INSERT INTO books (title, author, image_url, user_id, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, author, image_url, "test-user", datetime.utcnow()),
        )
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Step 7: DB insert complete")

        return jsonify({"message": "Book uploaded successfully"}), 200

    except Exception as e:
        print("❌ Upload failed:", str(e))
        return jsonify({"error": str(e)}), 500
