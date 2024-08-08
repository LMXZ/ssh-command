from std import *

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

def connect_ssh(host_name: str):
    host_config: dict = config['hosts'][host_name]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs = host_config.copy()
    if not kwargs.setdefault('proxy_jump', None) is None:
        sock = connect_ssh(kwargs['proxy_jump']).get_transport().open_channel(
            'direct-tcpip', (kwargs['hostname'], kwargs['port']), ('', 0)
        )
        kwargs['sock'] = sock
    kwargs = {k: v for k, v in filter(lambda x: x[0]!='proxy_jump', kwargs.items())}
    ssh.connect(**kwargs)
    return ssh

# 端口映射请求处理
def tcp_mapping_request(local_conn: socket.socket, target_host: str, command: str):
    try:
        print('trying to connect...')
        ssh = connect_ssh(target_host)

        # 使用这个连接执行命令
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        print('success!')
    except Exception as e:
        print('failed!')
        print(e.args)
        local_conn.close()
        return
    threading.Thread(target=tcp_mapping_worker, args=(local_conn, ssh_stdin)).start()
    threading.Thread(target=tcp_reverse_mapping_worker, args=(local_conn, ssh_stdout)).start()
    return

if __name__ == "__main__":
    local_ip = config['local_ip']          # 本机地址
    local_port = config['local_port']            # 本机端口
    
    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind((local_ip, local_port))
    local_server.listen(5)
    while True:
        try:
            (local_conn, local_addr) = local_server.accept()
        except Exception:
            local_server.close()
            break
        
        threading.Thread(target=tcp_mapping_request, args=(local_conn, config['target_host'], config['command'])).start()
