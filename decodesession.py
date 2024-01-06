from itsdangerous import URLSafeTimedSerializer
import base64
import json

# Ваш секретный ключ, используемый в приложении Flask
secret_key = 'your_secret_key'

# Данные сессии для декодирования
session_cookie = 'eyJ1c2VyX2lkIjoxfQ.ZZVHZQ.H-cZgJrEODUupK0Grp5aNch-tHA'

# Создаем экземпляр сериализатора
serializer = URLSafeTimedSerializer(secret_key)

# Декодирование
# Разделяем данные сессии на части
payload = session_cookie.split(".")[0]

# Декодируем из base64
decoded_payload = base64.urlsafe_b64decode(payload + "==")

# Конвертируем из JSON в словарь
session_data = json.loads(decoded_payload)

print(session_data)
