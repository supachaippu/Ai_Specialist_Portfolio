import http.server
import socketserver
import json
import os

class MapHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                content = data.get('content')
                folder = data.get('folder') # This comes from the identified builder

                # Logic: If folder is provided, go one level up and then into that folder
                if folder:
                    # Assuming server runs in a V-folder or StoreFactory/template
                    # We look for the folder in the parent directory
                    target_dir = os.path.join(os.path.dirname(os.getcwd()), folder)
                    
                    # If not found there, try the current directory itself (fallback)
                    if not os.path.exists(target_dir):
                        target_dir = os.path.join(os.getcwd(), folder)
                else:
                    target_dir = os.getcwd()

                # Ensure it's a directory
                if folder and not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)

                file_path = os.path.join(target_dir, 'map_config.js')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Saved to: {file_path}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": false, "error": str(e)}).encode('utf-8'))

if __name__ == '__main__':
    PORT = 8085
    socketserver.TCPServer.allow_reuse_address = True
    print("\n" + "="*50)
    print("💎 MASTER MAP SAVER (โหมดระบุร้าน)")
    print(f"📡 รันอยู่ที่พอร์ต: {PORT}")
    print("="*50)
    print("\n[INFO] มึงไม่ต้องปิดหน้านี้ รันมันทิ้งไว้เลยตัวเดียวจบ!")
    print("[INFO] ไม่ว่าจะเปิดร้านไหนมาแก้ มันจะเซฟกลับเข้าโฟลเดอร์ให้เองอัตโนมัติ")
    
    with socketserver.TCPServer(("", PORT), MapHandler) as httpd:
        httpd.serve_forever()
