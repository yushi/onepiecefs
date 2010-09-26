#include <stdlib.h>
#include "util.h"
#include "opfs_entries.h"
#include <event.h>
#include <signal.h>
#include "net.h"

void sigint_handler(int signum) {
  stop_network();
}

void setup_signal() {
  struct sigaction sa_sigint;

  memset(&sa_sigint, 0, sizeof(sa_sigint));
  sa_sigint.sa_handler = sigint_handler;
  sa_sigint.sa_flags = SA_RESTART;

  if(sigaction(SIGINT, &sa_sigint, NULL) < 0) {
    perror("sigaction");
    exit(1);
  }
}

int main(int argc, char** argv) {
  setup_signal();
  setup_network();

  if(argc != 2) {
    err("argument required\n");
    exit(-1);
  }

  char* rp = realpath(argv[1], NULL);

  if(rp == NULL) {
    err("get realpath failed\n");
    exit(-1);
  }

  err("arg: %s\n", rp);

  OPFS::Entries local_entries = OPFS::Entries(string(rp));
  local_entries.debug_print();
  free(rp);

  start_network();
  return 0;
}
