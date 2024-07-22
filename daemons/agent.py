from common.communication.socket.SocketListener import SocketListener
from common.communication.socket.FileDescriptorSocket import FileDescriptorSocket

if __name__ == "__main__":
    SocketListener(FileDescriptorSocket()).listen()
