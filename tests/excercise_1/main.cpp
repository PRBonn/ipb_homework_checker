#include <cstdio>

int main(int argc, char const *argv[]) {
  if (argc == 1) {
    fprintf(stderr,
            "This is a long test output that we expect to be produced by "
            "the code. We will compare the ouput to this EXACTLY.\n");
  } else {
    fprintf(stderr, "%s %s output\n", argv[1], argv[2]);
  }
}
