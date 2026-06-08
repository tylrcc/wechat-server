from flask import Flask, request, make_response
import hashlib
import time
import xml.etree.ElementTree as ET

app = Flask(__name__)
TOKEN = "test_token"


def verify_signature(signature, timestamp, nonce):
    items = sorted([TOKEN, timestamp, nonce])
    digest = hashlib.sha1("".join(items).encode("utf-8")).hexdigest()
    return digest == signature


@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")

    if request.method == "GET":
        if verify_signature(signature, timestamp, nonce):
            return make_response(echostr)
        return make_response("verification failed", 403)

    xml_data = request.data
    root = ET.fromstring(xml_data)
    msg_type = root.find("MsgType").text if root.find("MsgType") is not None else ""
    from_user = root.find("FromUserName").text if root.find("FromUserName") is not None else ""
    to_user = root.find("ToUserName").text if root.find("ToUserName") is not None else ""

    if msg_type == "text":
        content = root.find("Content").text if root.find("Content") is not None else "echo"
        reply_xml = (
            "<xml>"
            "<ToUserName><![CDATA[" + from_user + "]]></ToUserName>"
            "<FromUserName><![CDATA[" + to_user + "]]></FromUserName>"
            "<CreateTime>" + str(int(time.time())) + "</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[[echo] " + content + "]]></Content>"
            "</xml>"
        )
        return make_response(reply_xml, 200, {"Content-Type": "application/xml"})

    return make_response("success", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
