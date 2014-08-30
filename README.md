ekawebsocket
============

A simple tornado websocket wrapper, extending its capabilities

I created this because I wanted a simple package that adds more capabilities to websockets, and the others out there (socketio, SockJS) do not provide a lot of extended capbilities and instead focus on fallbacks.
They also do not have a good python back-end which supports those features.

See https://github.com/KimiNewt/ekawebsocket-js for a simple client side.

Capabilities
------------

  * Automatically serializes server-client messages to json and assigns a type to them.
  * Allows the broadcasting of a message to all clients.
  * Allows the creation of "rooms" to which clients can join and a message can be sent to all clients in a room.
  * Allows the client to "subscribe" only to certain types of messages.
  
How to use
----------

To use, you must subclass EkaWebsocket and implement the *handle_message* method. 
The method gets a message type and the message data.

Relevant methods:
  * *send_message* - to send a message to the current client.
  * *broadcast_to_client_rooms* - send a message to all the rooms the current client is in.
  * *broadcast_to_room* - (classmethod, can be called outside without any reference to a client) send a message to all clients in a given room.
