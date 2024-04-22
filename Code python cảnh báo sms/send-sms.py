## Tạo thư mục và file send-sms.py
mkdir sendsms && cd sendsms
sudo nano sendsms.py


#### đường dẫn /root/sendsms/sendsms.py
from flask import Flask, request
import subprocess

APP = Flask(__name__)

SMS_API_URL = "http://smsdn.vnptbariavungtau.vn/VNPT_SMS_BrandnameWS.asmx/Send_sms"
USERNAME = "KH_UBNDTPVT"
PASSWORD = "TpVtMNuV1@j8zY@z"
PHONE_NUMBER = "0399122789"

@APP.route('/', methods=['POST'])
def sendsms():
    data = request.json
    message = data.get("message", "")

    # Kiểm tra xem message có tồn tại không
    if not message:
        return "No message provided", 400

    try:
        # Gọi subprocess để thực hiện lệnh cURL
        cmd = [
            "curl",
            "-X", "POST",
            "-d", f"sodienthoai={PHONE_NUMBER}&noidung={message}&congtyId=52&username={USERNAME}&password={PASSWORD}",
            SMS_API_URL
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Kiểm tra kết quả từ lệnh cURL
        if result.returncode == 0:
            return "Messages sent successfully!"
        else:
            return f"Failed to send SMS. Error: {result.stderr}", 500

    except Exception as e:
        return f"Failed to send SMS. Error: {str(e)}", 500

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=5000)
