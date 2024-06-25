# Network Chat Application

This is a simple chat application consisting of server and client components written in Python. The application allows users to connect to a server and exchange messages or files with other connected users.

## Features

- **Messaging**: Send text messages to one or multiple recipients.
- **File Sharing**: Send files to one or multiple recipients.
- **User Management**: Track connected users and handle username availability.
- **Error Handling**: Manage server full conditions and unavailable usernames.

## Components

### Server (`server.py`)

The server manages incoming client connections, message forwarding, file transfers, and user management.

### Client (`client.py`)

The client connects to the server, sends messages/files, receives messages/files, and handles user interactions via command-line input.

### Utility Functions (`util.py`)

Contains utility functions and constants used by both server and client scripts.

## Requirements

- Python 3.x
- `socket` module (standard library)
- `threading` module (standard library)

## Usage

### Setting Up and Running the Server

1. Navigate to the directory containing `server.py`.
2. Run the server script: python server.py -p 15000. (Replace `15000` with your desired port number.)

### Setting Up and Running the Client

1. Navigate to the directory containing `client.py`.
2. Run the client script: python client.py -u your_username -p 15000. (Replace `your_username` with your desired username and `15000` with the same port number used for the server.)

### Commands

- `list`: Lists all connected users.
- `msg <count> <user1> <user2> ... <userN> <message>`: Send a message to specified users.
- `file <count> <user1> <user2> ... <userN> <filename>`: Send a file to specified users.
- `help`: Display available commands.
- `quit`: Disconnect from the server and exit the client.
