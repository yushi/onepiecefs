#include "opfs_entries.h"

OPFS::Entries::Entries(string base_dir) {
  this->base_dir = base_dir;

  vector<string> primitive_dirs;

  append_dirs(base_dir, &primitive_dirs);
  append_regular_files(base_dir, &(this->files));

  while(primitive_dirs.size() > 0) {
    string dir = primitive_dirs.back();
    primitive_dirs.pop_back();
    append_dirs(dir, &primitive_dirs);
    append_regular_files(dir, &(this->files));
    this->dirs.push_back(dir);
  }

};

void OPFS::Entries::debug_print() {
  vector<string> tmp;

  vector<string>::iterator i;

  for(i = this->files.begin(); i != this->files.end(); i++) {
    tmp.push_back(*i);
  }

  for(i = dirs.begin(); i != dirs.end(); i++) {
    tmp.push_back(*i);
  }

  std::sort(tmp.begin(), tmp.end());

  for(i = tmp.begin(); i != tmp.end(); i++) {
    cout << i->substr(base_dir.length()) << endl;
  }

};
