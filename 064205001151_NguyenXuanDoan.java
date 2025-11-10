// TcpOptExample.java
// Demonstrates: setTcpNoDelay, setSendBufferSize, setReceiveBufferSize
// Compile: javac TcpOptExample.java
// Run: java TcpOptExample

import java.net.Socket;
import java.net.InetSocketAddress;

public class TcpOptExample {
    public static void main(String[] args) throws Exception {
        Socket s = new Socket();
        // set before connect for some platforms
        s.setTcpNoDelay(true);
        s.setSendBufferSize(4 * 1024 * 1024);
        s.setReceiveBufferSize(4 * 1024 * 1024);

        // connect to nowhere just to demonstrate (use a real server in practice)
        try {
            s.connect(new InetSocketAddress("127.0.0.1", 9), 200);
        } catch (Exception ex) {
            // expected if no echo server; options already applied locally
        }

        System.out.println("Socket options set: TCP_NODELAY=" + s.getTcpNoDelay()
            + ", sndbuf=" + s.getSendBufferSize() + ", rcvbuf=" + s.getReceiveBufferSize());
        s.close();
    }
}
