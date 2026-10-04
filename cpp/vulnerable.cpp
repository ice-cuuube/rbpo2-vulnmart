#include <iostream>
#include <cstring>
#include <cstdio>
#include <cstdlib>

using namespace std;

// CWE-120: Buffer Overflow
void vulnerable_copy(const char* input) {
    char buffer[10];

    // УЯЗВИМОСТЬ: размер входных данных не проверяется
    strcpy(buffer, input);

    cout << "Copied: " << buffer << endl;
}


// CWE-134: Format String
void vulnerable_printf(const char* input) {

    // УЯЗВИМОСТЬ: строка пользователя используется как формат
    printf(input);

    printf("\n");
}


// CWE-78: OS Command Injection
void vulnerable_system(const char* input) {

    char command[100];

    // УЯЗВИМОСТЬ: пользовательский ввод помещается
    // непосредственно в системную команду
    sprintf(command, "echo %s", input);

    system(command);
}


int main(int argc, char* argv[]) {

    if (argc < 2) {
        cout << "Usage: ./vulnerable <text>" << endl;
        return 1;
    }

    vulnerable_copy(argv[1]);
    vulnerable_printf(argv[1]);
    vulnerable_system(argv[1]);

    return 0;
}
