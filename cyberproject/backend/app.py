from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

# Function to encode message into image
def encode_message(image_data, message):
    img = Image.open(io.BytesIO(image_data)).convert('RGB')
    encoded = img.copy()
    width, height = img.size
    message += chr(0)  # Null-terminate

    data_index = 0
    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for i in range(3):  # R, G, B
                if data_index < len(message):
                    pixel[i] = pixel[i] & ~1 | ((ord(message[data_index]) >> (2 - i)) & 1)
                else:
                    break
            encoded.putpixel((x, y), tuple(pixel))
            if data_index < len(message):
                data_index += 1
            else:
                break
        if data_index >= len(message):
            break

    output = io.BytesIO()
    encoded.save(output, format='PNG')
    return base64.b64encode(output.getvalue()).decode()

@app.route('/encode', methods=['POST'])
def encode():
    file = request.files['image']
    message = request.form['message']
    image_data = file.read()
    encoded_image = encode_message(image_data, message)
    return jsonify({"encoded_image": encoded_image})

@app.route('/')
def index():
    return "Flask Steganography Backend is running"

if __name__ == '__main__':
    app.run(debug=True)
