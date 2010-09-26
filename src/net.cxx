#include "net.h"

const size_t readsize = 1024;
struct event_base *ev_base = event_init();
struct event server_ev;
int ss;

void setup_network() {
  ss = get_server_socket();
  event_set(&server_ev, ss, EV_READ | EV_PERSIST, accept_handler, &server_ev);
  event_add(&server_ev, NULL);
}

void start_network() {
  event_base_loop(ev_base, 0);
  event_base_free(ev_base);
}

void stop_network(){
  if(event_del(&server_ev) == -1){
    //error log
    printf("error\n");
  }
  
  if(close(ss) == -1){
    //error log
    printf("error\n");
  }
}

static void client_error_handler(struct bufferevent *buffev, short what, void *arg) {
  printf("client disconnected\n");
  bufferevent_disable(buffev, EV_READ);
  bufferevent_free(buffev);
  char* received = (char*)arg;
  printf("%s\n", received);
  free(received);
}

static void client_read_handler(struct bufferevent* buffev, void *arg) {
  printf("data receiving\n");
  char buffer[1024];
  memset(buffer, 0, readsize);

  char* received = (char*)arg;
  int received_size = 0;

  received_size = bufferevent_read(buffev, buffer, readsize);
  strcat(received, buffer);

}

void accept_handler(int fd, short event, void *arg) {
  struct sockaddr_in addr;
  int client;
  socklen_t addrlen = sizeof(addr);
  if(event & EV_READ) {
    client = accept(fd, (struct sockaddr*) & addr, &addrlen);
    printf("client accepted\n");
    char* received = (char*)calloc(1, sizeof(char) * 10000000); // fixme
    struct bufferevent* ev = bufferevent_new(client, client_read_handler, NULL, client_error_handler, received);
    bufferevent_enable(ev, EV_READ);
  }
  stop_network();
}

int get_server_socket() {
  struct addrinfo hints, *res;
  int ss;
  int on = 1;
  memset(&hints, 0, sizeof(hints));
  hints.ai_socktype = SOCK_STREAM;
  hints.ai_flags = AI_PASSIVE;
  //if(getaddrinfo(NULL, "3027", &hints, &res) !=  0){
  if(getaddrinfo(NULL, "LiebDevMgmt_C", &hints, &res) !=  0){
    // error log
    printf("getaddringo: failed");
  }
  ss = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

  if(ss == -1) {
    perror("socket:");
    return -1;
  }

  setsockopt(ss, SOL_SOCKET,
             SO_REUSEADDR, (char *) & on, sizeof(on));

  if(bind(ss, res->ai_addr, res->ai_addrlen) == -1) {
    perror("bind");
    return -1;
  }

  if(listen(ss, SOMAXCONN) == -1) {
    perror("listen");
    return -1;
  };
  
  freeaddrinfo(res);
  
  return ss;
}
