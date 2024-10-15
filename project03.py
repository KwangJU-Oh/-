import os
import socket
from datetime import datetime
class SocketServer:
    def __init__(self):
        self.buffsize = 524288 #버퍼 크기 설정(bird의 크기가 12kb 이기 때문에 크게 설정하였음)
        with open('./response.bin','rb') as file:
            self.RESPONSE = file.read() #응답 파일 읽기

        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_image_file(self, data, filename):
        with open(filename, 'wb') as img_file:
            img_file.write(data)
    def run(self, ip, port):
        """서버 실행"""
        #소켓 생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                #클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)#타임아웃 설정(5초)
                print("Request Message...\r\n")

                response = b""

                data = clnt_sock.recv(self.buffsize)

                # 현재 시간을 기반으로 파일명 생성
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                filename = f"request/{timestamp}.bin"

                # 이진 파일로 저장
                with open(filename, 'wb') as file:
                    file.write(data)

                print(f"데이터를 {filename}에 저장했습니다.")

                if b'Content-Disposition: form-data; name="image"' in data:
                    # 이미지 데이터 추출
                    boundary = b'------------------------'  # 요청 바운더리
                    parts = data.split(boundary)

                    for part in parts:
                        if b'Content-Disposition: form-data; name="image"; filename="' in part:
                            # 이미지 파일명 추출
                            filename_start = part.index(b'filename="') + len(b'filename="')
                            filename_end = part.index(b'"', filename_start)
                            image_filename = part[filename_start:filename_end].decode()

                            # 이미지 데이터 추출
                            img_data_start = part.index(b'\r\n\r\n') + 4
                            img_data = part[img_data_start:]

                            # 이미지 파일로 저장
                            self.save_image_file(img_data, image_filename)
                            print(f"Image saved: {image_filename}")

                #응답 전송
                clnt_sock.sendall(self.RESPONSE)

                #클라이언트 소켓 닫기
                clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStop the server...")

        #서버 소켓 닫기
        self.sock.close()

if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)