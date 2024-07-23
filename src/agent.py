from agent.socket.FdSocket import FdSocket
from agent.dispatch.Dispatcher import Dispatcher
from agent.socket.SocketListener import SocketListener
from agent.packet.messages import Poke, Packet

s = FdSocket()
d = Dispatcher(s)
l = SocketListener(s, d)
print(Packet.from_message(Poke(3), "gee").to_json())
l.listen()
