"""
Flask Web Application for Image Size Reducer
A modern web interface for reducing image file sizes.
"""

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    flash,
    redirect,
    url_for,
)
import os
import io
import zipfile
from werkzeug.utils import secure_filename
from image_reducer import ImageSizeReducer
import tempfile
import shutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size

# Create necessary directories
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Clean up old files to prevent disk space issues."""
    current_time = datetime.now()
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                # Delete files older than 1 hour
                if (current_time - file_time).seconds > 3600:
                    try:
                        os.remove(filepath)
                    except:
                        pass


@app.route("/")
def index():
    cleanup_old_files()
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        if "files" not in request.files:
            return jsonify({"error": "No files selected"}), 400

        files = request.files.getlist("files")
        max_size_mb = float(request.form.get("max_size", 1.0))

        if not files or all(file.filename == "" for file in files):
            return jsonify({"error": "No files selected"}), 400

        # Validate max size
        if max_size_mb <= 0 or max_size_mb > 10:
            return jsonify({"error": "Max size must be between 0.1 and 10 MB"}), 400

        results = []
        reducer = ImageSizeReducer(max_file_size_mb=max_size_mb)

        for file in files:
            if file and allowed_file(file.filename):
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{filename}"
                input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(input_path)

                try:
                    # Process the image
                    output_filename = f"reduced_{unique_filename.rsplit('.', 1)[0]}.jpg"
                    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

                    result = reducer.reduce_image_size(input_path, output_path)

                    # Add file info to result
                    result["original_filename"] = filename
                    result["output_filename"] = output_filename
                    result["download_url"] = url_for(
                        "download_file", filename=output_filename
                    )

                    results.append(result)

                except Exception as e:
                    results.append({"original_filename": filename, "error": str(e)})

                # Clean up input file
                try:
                    os.remove(input_path)
                except:
                    pass

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/download/<filename>")
def download_file(filename):
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500


@app.route("/download_all", methods=["POST"])
def download_all():
    try:
        filenames = request.json.get("filenames", [])

        if not filenames:
            return jsonify({"error": "No files to download"}), 400

        # Create a temporary zip file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")

        with zipfile.ZipFile(temp_zip.name, "w") as zip_file:
            for filename in filenames:
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                if os.path.exists(filepath):
                    zip_file.write(filepath, filename)

        temp_zip.close()

        # Send the zip file
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name="reduced_images.zip",
            mimetype="application/zip",
        )

    except Exception as e:
        return jsonify({"error": f"Error creating zip: {str(e)}"}), 500


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    print("🖼️  Image Size Reducer Web App")
    print("📡 Starting server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")

    app.run(debug=True, host="0.0.0.0", port=5000)
