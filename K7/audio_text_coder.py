import wave
import os
import tempfile
import unittest

def encode_lsb(input_audio, output_audio, secret_message):
    """
    Кодирует секретное сообщение в аудиофайл используя LSB-метод
    """
    with wave.open(input_audio, 'rb') as audio:
        params = audio.getparams()
        frames = audio.readframes(audio.getnframes())
    
    message_bytes = secret_message.encode('utf-8') + b'\x00\x00\x00\x00'
    bits = []
    for byte in message_bytes:
        bits += [(byte >> i) & 1 for i in range(7, -1, -1)]
    
    available_bits = len(frames) 
    required_bits = len(bits)
    
    if required_bits > available_bits:
        raise ValueError(f"Сообщение слишком длинное. Требуется: {required_bits} бит, доступно: {available_bits} бит")
    
    audio_bytes = bytearray(frames)
    for i in range(required_bits):
        audio_bytes[i] = (audio_bytes[i] & 0xFE) | bits[i]
    
    with wave.open(output_audio, 'wb') as output:
        output.setparams(params)
        output.writeframes(audio_bytes)

def decode_lsb(input_audio):
    """
    Декодирует сообщение из аудиофайла, используя LSB-метод
    """
    with wave.open(input_audio, 'rb') as audio:
        frames = audio.readframes(audio.getnframes())
    
    bits = [byte & 1 for byte in frames]
    
    message_bytes = bytearray()
    message_bits = []
    stop_marker = [0] * 32  
    
    for i, bit in enumerate(bits):
        message_bits.append(bit)
        if len(message_bits) >= 32 and message_bits[-32:] == stop_marker:
            message_bits = message_bits[:-32]  
            break
    
    for i in range(0, len(message_bits), 8):
        byte_bits = message_bits[i:i+8]
        if len(byte_bits) < 8:
            break
        byte_val = 0
        for b in byte_bits:
            byte_val = (byte_val << 1) | b
        message_bytes.append(byte_val)
    
    try:
        return message_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return "Ошибка декодирования"

def get_max_message_length(input_audio):
    """
    Возвращает максимальную длину сообщения (в байтах) для аудиофайла
    """
    with wave.open(input_audio, 'rb') as audio:
        nframes = audio.getnframes()
        nchannels = audio.getnchannels()
        sampwidth = audio.getsampwidth()
        total_audio_bytes = nframes * nchannels * sampwidth
    

    return (total_audio_bytes - 32) // 8

class TestAudioLSB(unittest.TestCase):
    def setUp(self):
        self.test_audio = 'data_audio/input_audio.wav'
        self.tmp_files = []
    
    def tearDown(self):
        for f in self.tmp_files:
            if os.path.exists(f):
                os.unlink(f)
    
    def create_temp_file(self, content):
        tmp = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False, encoding='utf-8')
        tmp.write(content)
        tmp.close()
        self.tmp_files.append(tmp.name)
        return tmp.name
    
    def test_short_message(self):
        message = "Тестовое сообщение"
        txt_path = self.create_temp_file(message)
        encoded_audio = 'test_encoded_short.wav'
        self.tmp_files.append(encoded_audio)
        
        encode_lsb(self.test_audio, encoded_audio, message)
        decoded = decode_lsb(encoded_audio)
        self.assertEqual(decoded, message)
    
    def test_max_length_message(self):
        max_len = get_max_message_length(self.test_audio)
        message = "A" * max_len
        txt_path = self.create_temp_file(message)
        encoded_audio = 'test_encoded_max.wav'
        self.tmp_files.append(encoded_audio)
        
        encode_lsb(self.test_audio, encoded_audio, message)
        decoded = decode_lsb(encoded_audio)
        self.assertEqual(decoded, message)
    
    def test_message_too_long(self):
        max_len = get_max_message_length(self.test_audio)
        message = "A" * (max_len + 1)
        encoded_audio = 'test_encoded_too_long.wav'
        self.tmp_files.append(encoded_audio)
        
        with self.assertRaises(ValueError):
            encode_lsb(self.test_audio, encoded_audio, message)

if __name__ == "__main__":
    unittest.main()