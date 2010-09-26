#ifndef __OPFS_ENTRIES_H__
#define __OPFS_ENTRIES_H__

#include <string>
#include <vector>
#include <iostream>
#include "util.h"

using namespace std;

namespace OPFS {
  class Entries {
  public:
    Entries(string base_dir);
    void debug_print();
    string base_dir;
    vector<string> dirs;
    vector<string> files;
  };
}

#endif
