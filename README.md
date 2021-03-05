# Dropbox clone 


This is mainly a python sockets project. It keeps one directory in sync while the other is changed. The code has 3 parts; one for testing and running: test_homework.py, one for the client: Client.py, and one for the Server: Server.py 

## Code 

### test_homework 

This file contains common code used by both the client and the server, and the code for running the client and server. IT also contains tests for the code. 

  
All the tests and most of the common code was provided. I have changed the path_content_to_string to path_content_to_hash, and extracted the main for loop to a different function called path_to_hashed_tuples. This is so that i can compare individual files and not only the whole state. This allows me to only send the updated files. 

  
I also changed the Client and Server functions to use my new classes, which uses sockets to communicate to not rely on the fact that both the client and server has access to both directories. 
  

### Client 

Both the client and server contain two classes, one for handling the sending and receiving of data, and a class using the other class. 


#### client class methods 

* constructor: starts a socket object. 

* start: connects to the server, with the given hostname and path. 

* send: sends messages, first a header telling how big the msg is, then the actual data. The data is pickled before it is sent, to convert it to bytes, and for easy decoding on the receiving side. 


#### DropboxClient class methods: 

* constructor: starts a client object and gets the initial state of the client directory. 

* start: 

  1. Send all data from directory 

  2. Infinite loop: If state changed send the updates, else sleep a second. 

* get_new_state: Getting the hashed state list. This is used for comparing the states, and used by the get_updates method, to find the updates. 

* get_updates: Uses the new and old state to find which files and directories are updated with a set diff. Then for all the updates it reads the file if it's a file, and if dir. gives the tuple from the new state. Then all the file which are removed are added, with size -1 and an empty string as content. 

  
### Server 


#### Server class methods 

* Constructor: Sets up the socket and adds needed settings. Binds the socket to the hostname and port, then adds a listening que. 

* Start: Infinite loop. Accepts a client and accepts messages from the client with the receive_msg method and yields the message. 

* _receive_msg: receives the header and the message, then decodes the pickled data and returns. This function blocks until a message is received. 


#### DropboxServer 

* Constructor: Starts a Server object. 

* Start: Starts the server, and uses the yields from the Server in a for loop, and because of this, it is a infinite for loop. The loop is pausing until a yield from the server and then it uses the update path method to update the Server directory. If no data is received it tries to start over the server. For then to print the path of all directories and files updated. 

* Update path realizes the updates from the messages. Overwrites changed files and removes what is to be removed. 

  
## Improvements 
 
### Error handling 

The code now is quite strict and does not handle many possible errors. This is important for a client facing product since they can't be expected to figure out what went wrong. 

### Logging 

Logging is useful for seeing that the program is running as expected. In this project logging could be added to log which files and dirs. was changed on the client and server side. This could be used to find desync errors and allows for a resync function to fix the error on trigger. 

Logging is also important for monitoring performance. It can often be hard to spot bottlenecks and other problems whiteout logging with timestamps. 


Tools to help with logging: 
  * pythons logger lib. 
  * DataDog 

### Change only the differences in files not the whole file. 

To save on compute and bandwidth it would be better to send only the updates in the files instead of sending the whole files.  

### Async 

There are many possibilities with async compute in this project. For example, the receiving updates and updating does not need to be in sync. We can simply have the receiver method put all updates into a stack which the updates grab from. This will allow for many smaller bursts of updates to come in at the same time. Although this can be said to be handled by the sockets listening que. 

The infinite loops could be handles by their own treads to shut down the servers more gracefully.  

## Dependencies 

Can be installed with: 
 
```shell 
$ pip -r install requirements.txt 
``` 

The code was developed with python 3.8.5 

  

 

 