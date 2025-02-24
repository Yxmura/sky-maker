from flask import Flask, render_template, request, send_file
from PIL import Image
import webbrowser
import io
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_images():
    try:
        files = request.files.getlist('files')

        final_image = Image.new('RGB', (3072, 2048))

        positions = {
            'Bottom': (0, 0),  # (x1, y1)
            'Top': (1024, 0),  # (x2, y1)
            'Back': (2048, 0),  # (x3, y1)
            'Left': (0, 1024),  # (x1, y2)
            'Front': (1024, 1024),  # (x2, y2)
            'Right': (2048, 1024)  # (x3, y2)
        }

        for file in files:
            if file.filename:
                position = None
                for pos in positions.keys():
                    if f"_{pos}.bmp" in file.filename:
                        position = pos
                        break

                if position:
                    img = Image.open(file)
                    img = img.resize((1024, 1024))

                    final_image.paste(img, positions[position])

        # Save to bytes
        img_byte_arr = io.BytesIO()
        final_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return send_file(
            img_byte_arr,
            mimetype='image/png',
            as_attachment=True,
            download_name='minecraft_sky.png'
        )

    except Exception as e:
        return str(e), 400


templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minecraft Skies Mapper</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
            position: relative;
        }
        
        .background-grid {
            position: fixed;
            inset: 0;
            z-index: -10;
            height: 150%;
            width: 100%;
            background-color: white;
            background-image: 
                linear-gradient(to right, rgba(240, 240, 240, 0.6) 1px, transparent 1px), 
                linear-gradient(to bottom, rgba(240, 240, 240, 0.6) 1px, transparent 1px);
            background-size: 6rem 4rem;
        }
        
        .background-radial {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            top: 0;
            background-image: radial-gradient(circle 700px at 80% 150px, rgba(213, 197, 255, 0.4), transparent);
        }
        
        .container {
            background-color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
        }
        
        .container:hover {
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        }
        
        h1 {
            color: #333;
            text-align: center;
            font-weight: 600;
        }
        
        .upload-area {
            border: 2px dashed #bbb;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
            border-radius: 8px;
            transition: all 0.3s ease-in-out;
            background-color: #fafafa;
            cursor: pointer;
        }
        
        .upload-area:hover {
            background-color: #eef2ff;
            border-color: #3b82f6;
        }
        
        .upload-area.dragover {
            background-color: #e1f5fe;
            border-color: #2196f3;
        }
        
        .file-item {
            background-color: #f9f9f9;
            padding: 12px;
            margin: 5px 0;
            border-radius: 6px;
            font-weight: 500;
        }
        
        #btn {
            justify-content: center;
            align-items: center;
            display: flex;
        }
        
        button {
            background-color: #3b82f6;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.2s ease-in-out;
            font-weight: 500;
            text-align: center
        }
        
        button:hover {
            background-color: #2563eb;
        }
        
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        
        .error {
            color: red;
            font-weight: 500;
            margin: 10px 0;
        }
        
        .preview {
            max-width: 100%;
            display: block;
            margin: 20px auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .grid-info {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        
        .grid-info h3 {
            margin: 0 0 10px;
            font-weight: 600;
        }
        
        .grid-info table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 14px;
        }
        
        .grid-info th, .grid-info td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        
        .grid-info th {
            background-color: #e0e0e0;
        }
        
        #footer {
            text-align: center;
            padding-top: 10px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
<div class="background-grid">
  <div class="background-radial"></div>
</div>
    <div class="container">
        <h1>Minecraft Sky Maker</h1>

        <div class="grid-info">
            <h3>Grid Layout</h3>
            <table>
                <tr>
                    <th>Row 1</th>
                    <td>Bottom (0,0)</td>
                    <td>Top (1024,0)</td>
                    <td>Back (2048,0)</td>
                </tr>
                <tr>
                    <th>Row 2</th>
                    <td>Left (0,1024)</td>
                    <td>Front (1024,1024)</td>
                    <td>Right (2048,1024)</td>
                </tr>
            </table>
        </div>

        <div class="upload-area" id="dropZone">
            <p>Drag and drop your BMP files here or click to select files</p>
            <input type="file" id="fileInput" multiple accept=".bmp" style="display: none">
        </div>

        <div id="fileList"></div>
        <div id="error" class="error"></div>
        
        <div id="btn">
            <button id="processButton" disabled>Process Images</button>
        </div>
        
        <img id="preview" class="preview" style="display: none">
        
        <p id="footer"></p>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const processButton = document.getElementById('processButton');
        const errorDiv = document.getElementById('error');
        const preview = document.getElementById('preview');
        const footer = document.getElementById('footer');

        let files = [];

        // footer auto get current year
        footer.innerHTML = '&copy; '+new Date().getFullYear() + ' by Yamura'

        // Drag n drop 
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
    
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
    
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
    
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        function handleFiles(newFiles) {
            files = Array.from(newFiles).filter(file => file.name.endsWith('.bmp'));
            updateFileList();
            validateFiles();
        }

        function updateFileList() {
            fileList.innerHTML = '';
            files.forEach(file => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.textContent = file.name;
                fileList.appendChild(div);
            });
        }

        function validateFiles() {
            const required = ['Back', 'Front', 'Left', 'Right', 'Top', 'Bottom'];
            const missing = required.filter(pos => 
                !files.some(file => file.name.includes(`_${pos}.bmp`))
            );

            if (missing.length > 0) {
                errorDiv.textContent = `Missing files for positions: ${missing.join(', ')}`;
                processButton.disabled = true;
            } else if (files.length > 6) {
                errorDiv.textContent = 'Too many files selected';
                processButton.disabled = true;
            } else {
                errorDiv.textContent = '';
                processButton.disabled = false;
            }
        }

        processButton.addEventListener('click', async () => {
            const formData = new FormData();
            files.forEach(file => formData.append('files', file));
    
            try {
                processButton.disabled = true;
                processButton.textContent = 'Processing...';
    
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
    
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    preview.src = url;
                    preview.style.display = 'block';
    
                    // download
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'sky.png';
                    a.click();
                } else {
                    throw new Error('Processing failed');
                }
            } catch (error) {
                errorDiv.textContent = 'Error processing images: ' + error.message;
            } finally {
                processButton.disabled = false;
                processButton.textContent = 'Process Images';
            }
        });
    </script>
</body>
</html>
'''

# Write the template file
with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
    f.write(index_html)

webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    app.run(debug=True)