# API Testing Guide

## Step 1: Install Dependencies

```bash
# Activate your virtual environment (if using one)
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

## Step 2: Start the Server

```bash
# From the project root directory
uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Step 3: Test the API

### Option 1: Using the Test Script (Easiest)

```bash
# Test with an image from your raw folder
python test_api.py images/raw/ChatGPT\ Image\ Dec\ 25,\ 2025,\ 11_32_03\ PM.png
```

### Option 2: Using curl (Command Line)

```bash
curl -X POST "http://localhost:8000/api/extract-cloth" \
  -F "file=@images/raw/test.jpg" \
  --output output.png
```

### Option 3: Using Python requests

```python
import requests

url = "http://localhost:8000/api/extract-cloth"
with open("images/raw/test.jpg", "rb") as f:
    files = {"file": ("test.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)

if response.status_code == 200:
    with open("output.png", "wb") as out:
        out.write(response.content)
    print("✅ Success!")
```

### Option 4: Using Postman

1. Open Postman
2. Create a new POST request
3. URL: `http://localhost:8000/api/extract-cloth`
4. Go to "Body" tab
5. Select "form-data"
6. Add key: `file` (type: File)
7. Select an image file
8. Click "Send"
9. Save the response as PNG

### Option 5: Using Browser (Swagger UI)

1. Open: http://localhost:8000/docs
2. Find the `/api/extract-cloth` endpoint
3. Click "Try it out"
4. Upload an image file
5. Click "Execute"
6. Download the response

### Option 6: Using Flutter/Dart

```dart
import 'package:http/http.dart' as http;
import 'dart:io';

Future<void> testAPI() async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://localhost:8000/api/extract-cloth'),
  );
  
  request.files.add(
    await http.MultipartFile.fromPath('file', imagePath),
  );
  
  var response = await request.send();
  
  if (response.statusCode == 200) {
    var bytes = await response.stream.toBytes();
    File('output.png').writeAsBytes(bytes);
    print('✅ Success!');
  }
}
```

## Step 4: Verify the Output

- Check that the output PNG has a transparent background
- Open the file in an image viewer
- The background should be transparent (checkerboard pattern in most viewers)

## Health Check

Test the health endpoint:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status": "ok", "message": "AI Stylist Backend is running"}
```

## Troubleshooting

### Server won't start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use

### Import errors
- Make sure you're running from the project root directory
- Verify virtual environment is activated

### API returns 500 error
- Check server logs for detailed error messages
- Verify the image file is valid
- Make sure rembg models are downloaded (first run may download models)

### Connection refused
- Make sure the server is running
- Check the URL is correct: `http://localhost:8000`

