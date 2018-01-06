#include <cstdio>

int main(int argc, char const *argv[]) {
  fprintf(stderr, "This is a long test output that we expect to be produced by "
                  "the code. We will compare the ouput to this EXACTLY.\n");
  return 0;
}
