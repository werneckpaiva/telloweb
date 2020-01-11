import socket
import threading

class Tello:

    TELLO_CMD_ADDRESS = ('192.168.10.1', 8889)
    LOCAL_STATUS_ADDRESS = ('', 8890)

    sock_command = None
    sock_status = None

    status_thread = None

    is_monitoring = False
    is_flying = False

    current_status = {}

    def __init__(self):
        print("Connecting to Tello")
        self.sock_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_status = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock_status.bind(Tello.LOCAL_STATUS_ADDRESS)

    def init(self):
        self.send_command("command")
        if not self.is_monitoring:
            self.is_monitoring = True
            self.status_thread = threading.Thread(target=self.status_monitoring)
            self.status_thread.daemon = True
            self.status_thread.start()

    def stop(self):
        self.is_monitoring = False
        self.sock_command.close()
        self.sock_status.close()

    def send_command(self, cmd):
        print("Command: ", cmd)
        msg = cmd.encode(encoding="utf-8")
        self.sock_command.sendto(msg, Tello.TELLO_CMD_ADDRESS)

    def send_rc_command(self, a, b, c, d):
        if not self.is_flying:
            return
        cmd = "rc %.0f %.0f %.0f %.0f" % (a, b, c, d)
        msg = cmd.encode(encoding="utf-8")
        self.sock_command.sendto(msg, Tello.TELLO_CMD_ADDRESS)

    def takeoff(self):
        self.send_command("takeoff")
        self.is_flying = True

    def land(self):
        self.send_rc_command(0, 0, 0, 0)
        self.send_command("land")
        self.is_flying = False

    def status_monitoring(self):
        print("Monitoring Tello")
        while self.is_monitoring:
            try:
                data, server = self.sock_status.recvfrom(1518, 100)
                self.current_status = self.parse_status(data.decode(encoding="utf-8"))
            except Exception:
                pass

    def parse_status(self, raw_status):
        status = raw_status.replace('\n', '').replace('\r', '')
        all_status={}
        for item in status.split(";"):
            if not item: continue
            (k, v) = item.split(":")
            all_status[k] = v
        return all_status
