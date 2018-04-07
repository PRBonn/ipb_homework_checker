#include <cstdio>
#include <string>

int main(int argc, char const *argv[]) {
  fprintf(stdout, "%d\n", std::stoi(argv[1]) + std::stoi(argv[2]));
}
