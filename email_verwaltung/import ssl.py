import imaplib
import ssl

context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, ssl_context=context, timeout=30)
print("Verbunden!")