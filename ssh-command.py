import paramiko
import socket, threading
from paramiko.channel import ChannelStdinFile, ChannelFile
import json

config = json.load(open('config.json', 'rb'))

# 单向流数据传递
def tcp_mapping_worker(conn_receiver: socket.socket, stdin: ChannelStdinFile):
    while True:
        try:
            # 接收数据缓存大小
            data = conn_receiver.recv(2048)
        except Exception:
            break
        if not data:
            break
        try:
            stdin.write(data)
        except Exception:
            break
    conn_receiver.close()
    stdin.close()
    return

def tcp_reverse_mapping_worker(conn_receiver: socket.socket, stdout: ChannelFile):
    while True:
        try:
            # 接收数据缓存大小
            data = stdout._read(2048)
        except Exception:
            break
        if not data:
            break
        try:
            conn_receiver.send(data)
        except Exception:
            break
    conn_receiver.close()
    stdout.close()
    return

# 端口映射请求处理
def tcp_mapping_request(local_conn: socket.socket, remote_ip, remote_port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 建立连接
        ssh.connect(remote_ip, username=username, port=remote_port, password=password)

        # 使用这个连接执行命令
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    except Exception:
        local_conn.close()
        return
    threading.Thread(target=tcp_mapping_worker, args=(local_conn, ssh_stdin)).start()
    threading.Thread(target=tcp_reverse_mapping_worker, args=(local_conn, ssh_stdout)).start()
    return

if __name__ == "__main__":
    local_ip = config['local-ip']          # 本机地址
    local_port = config['local-port']            # 本机端口
    
    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind((local_ip, local_port))
    local_server.listen(5)
    while True:
        try:
            (local_conn, local_addr) = local_server.accept()
        except Exception:
            local_server.close()
            break
        
        threading.Thread(target=tcp_mapping_request, args=(local_conn, config['remote-ip'], config['remote-port'],
                                                           config['username'], config['password'], config['command'])).start()
