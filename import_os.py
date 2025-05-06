import os
secrets_dir = ".streamlit"
secrets_file = os.path.join(secrets_dir, "secrets.toml")
if not os.path.exists(secrets_dir):
    os.makedirs(secrets_dir)  # Создаем папку .streamlit, если она не существует

gemini_api_key = "AIzaSyCOB-OSNN-v7GNdw4Katn4-aYUj5sxU1NI" # Замените на ваш настоящий ключ
API_KEY = "d51dce684e6fd529bfbef5c8e83078b4"
# Записываем секреты в файл secrets.toml
with open(secrets_file, "w") as f:
    f.write("[general]\n")
    f.write(f"GEMINI_API_KEY = \"{gemini_api_key}\"\n")
    f.write(f"API_KEY = \"{API_KEY}\"\n")
    print(f"Файл {secrets_file} успешно создан и записан!")
