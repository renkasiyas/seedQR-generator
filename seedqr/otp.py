# import qrcode
import pyotp

# data = {
#     "type": "totp",
#     "label": "Example Label",
#     "issuer": "Example Isuer",
#     "secret": "UNZG4J2QDMGVN6G2WSJXO74HKQC6TBAR",
# }

# url = f"otpauth://{data['type']}/label={data['label'].replace(' ','+')}?issuer={data['issuer'].replace(' ', '+')}&secret={data['secret']}"
# print(url)

# qr = qrcode.QRCode()
# qr.add_data(url)
# qr.print_tty()


if __name__ == "__main__":
    secret = input("Secret: ")
    print(pyotp.TOTP(secret).now())
