#!/usr/bin/env python3
"""
Server phục vụ ứng dụng AI Data Analytics Agent B2B - Trường Giang
Hỗ trợ serve file tĩnh + API POST /api/upload đọc mọi file CSV / XLSX / XLS bằng pandas & openpyxl
Chạy trên cổng 8000 (hoặc cổng truyền qua biến môi trường PORT)
"""
import base64
import http.server
import json
import os
import re
import socketserver
from email.parser import BytesParser
from email.policy import default as email_policy

from data_loader import load_from_file

PORT = int(os.environ.get("PORT", 8000))


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def _parse_multipart(content_type: str, body: bytes):
    """Tách file tải lên từ multipart/form-data mà không phụ thuộc module cgi."""
    header_block = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
    msg = BytesParser(policy=email_policy).parsebytes(header_block + body)
    if msg.is_multipart():
        for part in msg.iter_parts():
            filename = part.get_filename()
            if filename:
                payload = part.get_payload(decode=True)
                return filename, payload
    return None, None


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def _send_json(self, status_code: int, payload: dict):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if self.path.rstrip("/") == "/api/upload":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                if content_len <= 0:
                    return self._send_json(400, {"ok": False, "error": "Không nhận được dữ liệu file."})

                body = self.rfile.read(content_len)
                ctype = self.headers.get("Content-Type", "")
                filename = None
                raw_bytes = None

                if "application/json" in ctype:
                    obj = json.loads(body.decode("utf-8"))
                    filename = obj.get("filename", "upload.xlsx")
                    b64 = obj.get("data_base64", "")
                    if "," in b64:
                        b64 = b64.split(",", 1)[1]
                    raw_bytes = base64.b64decode(b64)
                elif "multipart/form-data" in ctype:
                    filename, raw_bytes = _parse_multipart(ctype, body)
                else:
                    filename = self.headers.get("X-Filename", "upload.csv")
                    raw_bytes = body

                if not raw_bytes or not filename:
                    return self._send_json(400, {"ok": False, "error": "Không trích xuất được nội dung file tải lên."})

                req_list = load_from_file(raw_bytes, filename)
                if not req_list:
                    return self._send_json(400, {"ok": False, "error": f"File '{filename}' không có dòng dữ liệu hợp lệ."})

                rows = []
                for idx, r in enumerate(req_list):
                    items_str = ", ".join(
                        f"{it.get('product_id', '')}: {it.get('quantity', 0)}"
                        for it in r.get("items", [])
                    )
                    rows.append({
                        "id": r.get("request_id") or f"REQ-{idx+1:03d}",
                        "customer": r.get("customer_name") or f"Khách hàng #{idx+1}",
                        "contact": r.get("contact") or "",
                        "itemsStr": items_str,
                        "budget": r.get("budget"),
                        "days": r.get("requested_lead_days"),
                        "disc": r.get("requested_discount_pct") or 0,
                        "note": ""
                    })

                return self._send_json(200, {"ok": True, "filename": filename, "rows": rows})
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": str(exc)})

        return self._send_json(404, {"ok": False, "error": "Endpoint không tồn tại."})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        print("==================================================================")
        print("  AI Data Analytics Agent B2B - Trường Giang")
        print(f"  Đang chạy tại: http://localhost:{PORT}")
        print("==================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nĐang dừng server...")
            httpd.shutdown()
