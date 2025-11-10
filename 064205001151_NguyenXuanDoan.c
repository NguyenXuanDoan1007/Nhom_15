// tcp_opt_example.c
// Demonstrates: TCP_NODELAY, SO_SNDBUF/SO_RCVBUF, and TCP_CONGESTION (Linux)
// Compile: gcc tcp_opt_example.c -o tcp_opt_example
// Note: setting TCP_CONGESTION may require root and Linux support.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main() {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0) { perror("socket"); return 1; }

    // Disable Nagle
    int flag = 1;
    if (setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag)) < 0) perror("TCP_NODELAY");

    // Increase send/recv buffers
    int buf = 4 * 1024 * 1024; // 4MB
    if (setsockopt(s, SOL_SOCKET, SO_SNDBUF, &buf, sizeof(buf)) < 0) perror("SO_SNDBUF");
    if (setsockopt(s, SOL_SOCKET, SO_RCVBUF, &buf, sizeof(buf)) < 0) perror("SO_RCVBUF");

    // Change congestion control (Linux)
#ifdef TCP_CONGESTION
    char cong[16] = "cubic"; // or "bbr" if available
    if (setsockopt(s, IPPROTO_TCP, TCP_CONGESTION, cong, strlen(cong)) < 0) perror("TCP_CONGESTION");
#endif

    printf("Socket options set. Now you can connect and use the socket as usual.\\n");
    close(s);
    return 0;
}
