#ifndef __NET_H__
#define __NET_H__
#include <event.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <unistd.h>

int get_server_socket();
void accept_handler(int fd, short event, void *arg);
void setup_network();
void start_network();
void stop_network();
#endif
