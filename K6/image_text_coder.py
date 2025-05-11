from PIL import Image
import numpy as np
import struct
import os
import tempfile

def encode_image(input_image_path, output_image_path, secret_message):
    img = Image.open(input_image_path).convert('RGB')
    width, height = img.size
    pixels = np.array(img)

    secret_bytes = secret_message.encode('utf-8')
    secret_length = struct.pack('>I', len(secret_bytes))
    bit_stream = []
    
    for byte in secret_length:
        bit_stream.extend([(byte >> i) & 1 for i in range(7,-1,-1)])
    
    for byte in secret_bytes:
        bit_stream.extend([(byte >> i) & 1 for i in range(7,-1,-1)])
    
    required_bits = len(bit_stream)
    available_bits = width * height * 3
    if required_bits > available_bits:
        raise ValueError("Сообщение слишком длинное для этого изображения")
    
    bit_index = 0
    for row in range(height):
        for col in range(width):
            if bit_index >= required_bits:
                break
            for color in range(3):
                if bit_index >= required_bits:
                    break
                pixels[row][col][color] = (pixels[row][col][color] & 0xFE) | bit_stream[bit_index]
                bit_index += 1
    
    encoded_image = Image.fromarray(pixels)
    encoded_image.save(output_image_path)
    print(f"Сообщение успешно закодировано в {output_image_path}")

def decode_image(input_image_path):
    img = Image.open(input_image_path).convert('RGB')
    pixels = np.array(img)
    width, height = img.size
    
    bit_stream = []
    for row in range(height):
        for col in range(width):
            for color in range(3):
                bit_stream.append(pixels[row][col][color] & 1)
    
    length_bytes = []
    for i in range(4):  
        byte = 0
        for j in range(8):
            if (i*8 + j) >= len(bit_stream):
                raise ValueError("Недостаточно данных для чтения длины сообщения")
            byte = (byte << 1) | bit_stream[i*8 + j]
        length_bytes.append(byte)
    
    message_length = struct.unpack('>I', bytes(length_bytes))[0]
    
    total_required_bits = 32 + (message_length * 8)
    if len(bit_stream) < total_required_bits:
        raise ValueError("Сообщение повреждено или неполное")
    
    message_bytes = []
    for i in range(4, 4 + message_length):
        byte = 0
        for j in range(8):
            pos = i*8 + j
            if pos >= len(bit_stream):
                break
            byte = (byte << 1) | bit_stream[pos]
        message_bytes.append(byte)
    
    try:
        decoded_message = bytes(message_bytes).decode('utf-8')
    except UnicodeDecodeError:
        decoded_message = bytes(message_bytes)
    
    return decoded_message

def get_max_message_length(image_path):
    img = Image.open(image_path)
    width, height = img.size
    max_bits = width * height * 3
    max_length = (max_bits - 32) // 8  
    return max_length

def test_short_message():
    message = "Короткое сообщение для теста!"
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', encoding='utf-8', delete=False) as tmp_file:
        tmp_file.write(message)
        tmp_path = tmp_file.name
    
    encoded_image_path = 'test_encoded_short.png'
    try:
        encode_image('data_img\\test.png', encoded_image_path, message)
        decoded = decode_image(encoded_image_path)
        assert decoded == message, f"Ошибка: ожидалось '{message}', получено '{decoded}'"
        print("Тест с коротким сообщением пройден.")
    finally:
        os.unlink(tmp_path)
        if os.path.exists(encoded_image_path):
            os.unlink(encoded_image_path)

def test_medium_message():
    message = "Это сообщение средней длины, содержащее несколько предложений. "\
              "Оно включает различные символы: !@#$%^&*(), цифры 1234567890, и пробелы."
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', encoding='utf-8', delete=False) as tmp_file:
        tmp_file.write(message)
        tmp_path = tmp_file.name
    
    encoded_image_path = 'test_encoded_medium.png'
    try:
        encode_image('data_img\\test.png', encoded_image_path, message)
        decoded = decode_image(encoded_image_path)
        assert decoded == message, f"Ошибка: ожидалось '{message}', получено '{decoded}'"
        print("Тест с сообщением средней длины пройден.")
    finally:
        os.unlink(tmp_path)
        if os.path.exists(encoded_image_path):
            os.unlink(encoded_image_path)

def test_max_length_message():
    image_path = 'data_img\\test.png'
    max_len = get_max_message_length(image_path)
    message = 'A' * max_len  
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', encoding='utf-8', delete=False) as tmp_file:
        tmp_file.write(message)
        tmp_path = tmp_file.name
    
    encoded_image_path = 'test_encoded_max.png'
    try:
        encode_image(image_path, encoded_image_path, message)
        decoded = decode_image(encoded_image_path)
        assert decoded == message, "Ошибка: сообщение максимальной длины не совпадает"
        print("Тест с максимальной длиной сообщения пройден.")
    finally:
        os.unlink(tmp_path)
        if os.path.exists(encoded_image_path):
            os.unlink(encoded_image_path)

def test_message_too_long():
    image_path = 'data_img\\test.png'
    max_len = get_max_message_length(image_path)
    message = 'A' * (max_len + 1)  
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', encoding='utf-8', delete=False) as tmp_file:
        tmp_file.write(message)
        tmp_path = tmp_file.name
    
    encoded_image_path = 'test_encoded_too_long.png'
    try:
        try:
            encode_image(image_path, encoded_image_path, message)
            assert False, "Ожидалось исключение ValueError"
        except ValueError as e:
            assert "слишком длинное" in str(e), f"Неверное сообщение об ошибке: {e}"
        print("Тест на слишком длинное сообщение пройден.")
    finally:
        os.unlink(tmp_path)
        if os.path.exists(encoded_image_path):
            os.unlink(encoded_image_path)

if __name__ == "__main__":
    test_short_message()
    test_medium_message()
    test_max_length_message()
    test_message_too_long()
    print("\nВсе тесты успешно пройдены!")