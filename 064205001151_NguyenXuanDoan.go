// tcp_opt_example.go
// Demonstrates: TCP_NODELAY, SetReadBuffer/SetWriteBuffer, non-blocking not needed for Go's net
// Run: go run tcp_opt_example.go

package main

import (
    "fmt"
    "net"
    "syscall"
)

func main() {
    // Dial a TCP connection (will error if no server); we create a socket via syscall then wrap into net.Conn
    fd, err := syscall.Socket(syscall.AF_INET, syscall.SOCK_STREAM, syscall.IPPROTO_TCP)
    if err != nil {
        panic(err)
    }
    // disable Nagle
    if err := syscall.SetsockoptInt(fd, syscall.IPPROTO_TCP, syscall.TCP_NODELAY, 1); err != nil {
        fmt.Println("set TCP_NODELAY failed:", err)
    }
    // set buffers
    if err := syscall.SetsockoptInt(fd, syscall.SOL_SOCKET, syscall.SO_SNDBUF, 4*1024*1024); err != nil {
        fmt.Println("set SO_SNDBUF failed:", err)
    }
    if err := syscall.SetsockoptInt(fd, syscall.SOL_SOCKET, syscall.SO_RCVBUF, 4*1024*1024); err != nil {
        fmt.Println("set SO_RCVBUF failed:", err)
    }

    // Note: converting fd into net.Conn is more work; libraries can do this (os.NewFile + net.FileConn)
    fmt.Println("Socket-level options applied (fd). To use in Go net.Conn wrap fd using os.NewFile + net.FileConn.")
    syscall.Close(fd)
}
