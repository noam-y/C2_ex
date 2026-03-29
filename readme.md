## encryption phased based on the build i got from gemini:

### התקנה: pip install cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

### 1. יצירת מפתח (במציאות, זה יקרה פעם אחת או ב-Handshake)
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)

### 2. הכנת ההודעה
nonce = os.urandom(12)  # Nonce ייחודי לכל הודעה
data = b"Hello from C2 Client"

### 3. הצפנה (מחזירה Ciphertext + Tag)
ciphertext = aesgcm.encrypt(nonce, data, None)

### --- שליחה ברשת: צריך לשלוח גם את ה-nonce וגם את ה-ciphertext ---

### 4. פענוח (בצד השני)
decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
print(decrypted_data.decode())