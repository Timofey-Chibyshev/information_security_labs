import re
import matplotlib.pyplot as plt
from collections import Counter

# Референсные частоты букв с учётом "ё"
russian_letter_frequencies = {
    'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70,
    'т': 6.26, 'с': 5.47, 'р': 4.73, 'в': 4.54, 'л': 4.40,
    'к': 3.49, 'м': 3.21, 'д': 2.98, 'п': 2.81, 'у': 2.62,
    'я': 2.01, 'ы': 1.90, 'ь': 1.74, 'г': 1.70, 'з': 1.65,
    'б': 1.59, 'ч': 1.44, 'й': 1.21, 'х': 0.97, 'ж': 0.94,
    'ш': 0.73, 'ю': 0.64, 'ц': 0.48, 'щ': 0.36, 'э': 0.32,
    'ф': 0.26, 'ъ': 0.04, 'ё': 0.04
}


def data_reader(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Ошибка: {e}")
        return ""


def process_raw_text(raw_text):
    alphabet = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    processed = []
    clean_chars = []
    for char in raw_text.lower():
        if char in alphabet:
            processed.append(char)
            clean_chars.append(char)
        else:
            processed.append(char)
    return ''.join(processed), ''.join(clean_chars)


def calculate_freqs(text):
    counter = Counter(text)
    total = len(text)
    return {char: count / total for char, count in counter.items()}


def true_freqs():
    total = sum(russian_letter_frequencies.values())
    return {k: v / total for k, v in russian_letter_frequencies.items()}


def plot_frequencies(ref_freq, text_freq, title1, title2):
    # Сортируем символы по порядку из эталонных частот
    sorted_chars = list(ref_freq.keys())

    # Создаем списки значений частот в одинаковом порядке
    ref_values = [ref_freq[char] for char in sorted_chars]
    text_values = [text_freq.get(char, 0) for char in sorted_chars]

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.bar(sorted_chars, ref_values, color='skyblue')
    plt.title(title1)
    plt.xticks(rotation=45)
    plt.ylim(0, max(ref_values) * 1.1)  # Автомасштаб по Y

    plt.subplot(1, 2, 2)
    plt.bar(sorted_chars, text_values, color='lightgreen')
    plt.title(title2)
    plt.xticks(rotation=45)
    plt.ylim(0, max(text_values) * 1.1 if text_values else 0)  # Автомасштаб по Y

    plt.tight_layout()
    plt.show()


def calculate_sum_of_squares(text, N):
    substrings = [text[i::N] for i in range(N)]
    total_sum = 0.0
    valid_substrings = 0

    for substr in substrings:
        if len(substr) < 1:
            continue
        freqs = Counter(substr)
        total_chars = len(substr)
        sum_sq = sum((cnt / total_chars) ** 2 for cnt in freqs.values())
        total_sum += sum_sq
        valid_substrings += 1

    return total_sum / valid_substrings if valid_substrings > 0 else 0


def find_keylength(text, max_length=30):
    best_length = 1
    best_avg = 0

    for n in range(1, max_length + 1):
        avg = calculate_sum_of_squares(text, n)
        if avg > best_avg:
            best_avg = avg
            best_length = n

    return best_length


def find_key(text, key_length):
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    ref_freq = true_freqs()
    key = []

    for i in range(key_length):
        substr = text[i::key_length]
        best_score = -1
        best_shift = 0

        for shift in range(len(alphabet)):
            shifted = ''.join([alphabet[(alphabet.index(c) - shift) % len(alphabet)]
                               for c in substr])
            freq = calculate_freqs(shifted)
            score = sum(freq.get(char, 0) * ref_freq[char] for char in ref_freq)

            if score > best_score:
                best_score = score
                best_shift = shift

        key.append(alphabet[best_shift])

    return ''.join(key)


def decrypt_vigenere(text, key):
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    key_repeated = []
    key_idx = 0
    result = []

    # Генерируем ключ только для буквенных символов
    for char in text:
        if char in alphabet:
            key_repeated.append(key[key_idx % len(key)])
            key_idx += 1
        else:
            key_repeated.append(None)  # Маркер для не-букв

    key_idx = 0
    for t_char, k_char in zip(text, key_repeated):
        if k_char is not None:
            shift = alphabet.index(k_char)
            idx = (alphabet.index(t_char) - shift) % len(alphabet)
            result.append(alphabet[idx])
            key_idx += 1
        else:
            result.append(t_char)

    return ''.join(result)


if __name__ == '__main__':
    file_path = input("Введите путь к файлу: ")
    raw_text = data_reader(file_path)
    processed_text, clean_text = process_raw_text(raw_text)
    print(f"Обработано символов (с учетом пробелов): {len(processed_text)}")
    print(f"Букв для анализа: {len(clean_text)}")

    ref_freq = true_freqs()
    text_freq = calculate_freqs(clean_text)
    plot_frequencies(ref_freq, text_freq, 'Эталонные частоты', 'Частоты в кодированном тексте')

    key_len = find_keylength(clean_text)
    print(f"Предполагаемая длина ключа: {key_len}")

    key = find_key(clean_text, key_len)
    print(f"Найденный ключ: {key}")

    decrypted = decrypt_vigenere(processed_text, key)
    print("\nПервые 500 символов расшифрованного текста:")
    print(decrypted[:500])

    decrypted_text_freqs = calculate_freqs(process_raw_text(raw_text)[1])
    plot_frequencies(ref_freq, decrypted_text_freqs, 'Эталонные частоты', 'Частоты в декодированном тексте')
