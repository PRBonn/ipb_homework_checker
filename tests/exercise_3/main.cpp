#include <cstdio>
#include <string>

int main(int argc, char const *argv[]) {
  fprintf(stderr, "%d\n", std::stoi(argv[1]) + std::stoi(argv[2]));
}
