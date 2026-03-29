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

## handshake reference:

'''
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# 1. יצירת מפתח פרטי וציבורי (עקומה SECP256R1 - סטנדרט חזק)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# 2. הפיכת המפתח הציבורי לבייטים כדי לשלוח ברשת
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# 3. אחרי שמקבלים את המפתח של הצד השני (peer_public_bytes):
peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), peer_public_bytes)
shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)

# 4. "אפייה" של הסוד למפתח AES תקני (Key Derivation)
aes_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'c2 handshake',
).derive(shared_secret)
'''