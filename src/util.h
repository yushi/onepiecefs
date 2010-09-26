#ifndef __UTIL_H__
#define __UTIL_H__

#include <stdio.h>
#include <stdarg.h>
void err(const char* format, ...);

#include <dirent.h>
#include <vector>
#include <string>
#include <iostream>
using namespace std;
vector<string> get_dirs(string path);
void append_dirs(string path, vector<string> *target);
vector<string> get_regular_files(string path);
void append_regular_files(string path, vector<string> *target);

#endif
