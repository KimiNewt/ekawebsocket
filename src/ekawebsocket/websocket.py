import json

from tornado.websocket import WebSocketHandler


class EkaWebsocket(WebSocketHandler):
    """
    A websocket handler with extended capbilities.

    Can be used to send a broadcast message to all clients, or to place clients in "rooms" and broadcast messages there.
    It also allows to divide messages by type, which the client can handle diferent.
    """
    all_clients = set()
    _all_rooms = set()

    ROOM_REGISTER = '_room_register'
    ROOM_UNREGISTER = '_room_unregister'

    def initialize(self, allow_client_room_creation=True):
        """
        Initializes the websocket.
        If allow_client_room_creation is True, when clients register for a room they can also create one (rather than
        simply joining preexisting ones).
        """
        self.allow_client_room_creation = allow_client_room_creation
        self.rooms = set()

    def open(self):
        self.all_clients.add(self)

    def on_close(self):
        self.all_clients.remove(self)

    def add_room(self, room):
        """
        Adds the given room to the room list. If allow_client_room_creation is set to True, this is partially
        meaningless since the clients can create the rooms on their own.

        :param room The new room name
        """
        self._all_rooms.add(room)

    def on_message(self, message):
        """
        Receives a message from the client and handles it according to its type.
        Should not be overridden.
        """
        message = json.loads(message)

        if message['type'].startswith('_room'):
            self.handle_room_registration_msg(message['type'], message['data']['room'])
        else:
            self.handle_message(message['type'], message['data'])

    def broadcast_to_client_rooms(self, message):
        """
        Broadcasts a given message (a json-serializable object) to all rooms the client is in.

        :param message: the message to broadcast.
        """
        for room in self.rooms:
            self.broadcast_to_room(room, message)

    @classmethod
    def broadcast_to_room(cls, room, message_data, message_type=''):
        """
        Broadcast a message to a given room.

        :param room: The room to broadcast the message to.
        :type room: str
        :param message_data: The data of the message to broadcast (json-serializable object)
        :param message_type: Type of the message (optional)
        :type message_type: str
        """
        for client in cls.get_clients_in_room(room):
            client.send_message(message_data, message_type=message_type, room=room)

    def send_message(self, message_data, message_type='', room=None):
        """
        Send a message to this client.

        :param message_data: JSON-serializable message.
        :param message_type: Message type, which the client can filter by (optional).
        """
        self.write_message(json.dumps({'type': message_type, 'data': message_data, 'room': room}))

    def handle_message(self, message_type, message):
        """
        This method should be overridden by a child class.
        It handles all incoming messages apart from control ones (room registration, etc.)

        :param message_type: type of the message, which the user sent
        :type message_type: str
        :param message: The message received from the client.
        """
        raise NotImplementedError()

    @classmethod
    def get_clients_in_room(cls, room):
        """
        Returns all clients in a given room.
        """
        return [client for client in cls.all_clients if room in client.rooms]

    def handle_room_registration_msg(self, msg_type, room):
        if room not in self._all_rooms:
            # Got registration/unregistration request for a room that does not exist
            if self.allow_client_room_creation:
                self.add_room(room)
            else:
                return

        if msg_type == self.ROOM_REGISTER:
            self.rooms.add(room)
        elif msg_type == self.ROOM_UNREGISTER:
            self.rooms.remove(room)

