#include "util.h"

void err(const char* format, ...) {
  va_list list;
  va_start(list, format);
  vfprintf(stderr, format, list);
  va_end(list);
}

vector<string> get_files(string path, __uint8_t type) {
  vector<string> ret;
  DIR *d = opendir(path.c_str());

  if(d == NULL) {
    err("invalid path\n");
    return ret;
  }

  struct dirent entry, *result;

  while(1) {
    if(readdir_r(d, &entry, &result) == -1){
      // error log
      break;
    }

    if(strcmp(entry.d_name, ".") == 0) {
      continue;
    }

    if(strcmp(entry.d_name, "..") == 0) {
      continue;
    }

    if(result == NULL) {
      break;
    }

    if(entry.d_type == type) {
      ret.push_back(path + string("/") + string(entry.d_name));
    }
  }
  if(closedir(d) == -1){
    // error log
  }
  return ret;
}

vector<string> get_dirs(string path) {
  return get_files(path, DT_DIR);
}

void append_dirs(string path, vector<string> *target){
  vector<string> dirs = get_dirs(path);

  vector<string>::iterator i;
  for(i = dirs.begin(); i != dirs.end(); i++){
    target->push_back(*i);
  }
}

vector<string> get_regular_files(string path) {
  return get_files(path, DT_REG);
}

void append_regular_files(string path, vector<string> *target){
  vector<string> files = get_regular_files(path);

  vector<string>::iterator i;
  for(i = files.begin(); i != files.end(); i++){
    target->push_back(*i);
  }
}

