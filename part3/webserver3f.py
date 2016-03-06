###########################################################################
# Concurrent server - webserver3f.py                                      #
#                                                                         #
# Tested with Python 2.7.10 & Mac OS X        							  #
#                                                                         #
# - Child process sleeps for 60 seconds after handling a client's request #
# - Parent and child processes close duplicate descriptors                #
#                                                                         #
###########################################################################
import os
import socket
import signal
import errno

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 1024

def grim_reaper(signum, frame):
	print('os.wait')
	pid, status = os.wait()

def handle_request(client_connection):
	request = client_connection.recv(1024)
	print(
		'Child PID: {pid}. Parent PID {ppid}'.format(
			pid = os.getpid(),
			ppid = os.getppid(),
		)
	)
	print(request.decode)
	http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
	print(http_response)
	client_connection.sendall(http_response)



def serve_forever():
	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_socket.bind(SERVER_ADDRESS)
	listen_socket.listen(REQUEST_QUEUE_SIZE)
	print('Serving HTTP on port {port} ...'.format(port=PORT))
	# print('Parent PID (PPID): {pid}\n'.format(pid=os.getpid()))

	signal.signal(signal.SIGCHLD, grim_reaper)

	while True:
		try:
			client_connection, client_address = listen_socket.accept()
		except IOError as e:
			code, msg = e.args
			# restart 'accept' if it was interrupted
			if code == errno.EINTR:
				print('errno.EINTR')
				continue
			else:
				raise

		pid = os.fork()
		print('forked')
		if pid == 0:	# child
			print('enter child')
			listen_socket.close()	# close child copy
			handle_request(client_connection)
			client_connection.close()
			print('exit child')
			os._exit(0)	# child exits here
		else:			# parent
			client_connection.close()	# close parent copy and loop over
			print('parent close')

if __name__ == '__main__':
	serve_forever()