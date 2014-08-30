'use strict';

var app = angular.module('ChatApp', []);
app.controller('ChatController', ['$scope', function($scope, $http) {
    $scope.chatLines = ['hello'];
    $scope.websocket = null;
    $scope.currentRoom = null;

    $scope.recvMessage = function(msgData, msgRoom) {
        $scope.$apply(function() {
            $scope.chatLines.push('#' + msgRoom + ': ' + msgData);
        })
    }

    $scope.connectToWebsocket = function() {
        $scope.websocket = new EkaWebSocket('ws://localhost:8888/chat')
        
        // Register for 'blank' message type messages, and call the recvMessage callback when the message is received.
        $scope.websocket.on('', $scope.recvMessage);
    }

    $scope.connectToRoom = function(roomName) {
        $scope.websocket.connectToRoom(roomName)
        $scope.chatLines = ['Joining #' + roomName];
    };

    $scope.connectToWebsocket();
}]);

// Example client (ekawebsocket-js)

var roomRegister = '_room_register';
var roomUnregister = '_room_unregister';

function EkaWebSocket(url, protocols) {
    this.rooms = [];
    this.subscriptions = [];
    this.topicCallbacks = {};

    if (!protocols) {
        this.websocket = new WebSocket(url);
    } else {
        this.websocket = new WebSocket(url, protocols);
    }
    this.websocket.onmessage = this.onmessage;
    this.websocket.eka = this;
}

EkaWebSocket.prototype.sendMessage = function(messageData, messageType) {
    if (!messageType) {
        messageType = '';
    }
    this.websocket.send(JSON.stringify({type: messageType, data: messageData}));
}

EkaWebSocket.prototype.connectToRoom = function(roomName) {
    this.rooms.push(roomName);
    this.sendMessage({room: roomName}, roomRegister);
}

EkaWebSocket.prototype.disconnectFromRoom = function(roomName) {
    this.rooms.remove(roomName);
    this.sendMessage({room: roomName}, roomUnregister);
}

EkaWebSocket.prototype.on = function(topicName, callback) {
    this.topicCallbacks[topicName] = callback;
}

EkaWebSocket.prototype.onmessage = function(data) {
    var message = JSON.parse(data.data);
    if (this.eka.topicCallbacks[message.type]) {
        this.eka.topicCallbacks[message.type](message.data, message.room, data);
    }
}