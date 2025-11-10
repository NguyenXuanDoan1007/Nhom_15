// tcp_opt_example.rs
// Demonstrates: TCP_NODELAY, set buffer sizes using std::net::TcpStream where possible.
// Cargo.toml: use standard library only
// Build: rustc tcp_opt_example.rs && ./tcp_opt_example

use std::net::TcpStream;
use std::time::Duration;

fn main() -> std::io::Result<()> {
    // Create stream (will error if no server; this is just to set options)
    let stream = match TcpStream::connect("127.0.0.1:9") {
        Ok(s) => s,
        Err(_) => {
            // we can still create a stream and set options before connecting on some platforms using socket2 crate,
            // but here we demonstrate options on a created stream if connection succeeded.
            println!("No server at 127.0.0.1:9; example will show API usage instead.");
            return Ok(());
        }
    };
    stream.set_nodelay(true)?;
    stream.set_read_timeout(Some(Duration::from_secs(1)))?;
    stream.set_write_timeout(Some(Duration::from_secs(1)))?;
    // Buffer sizes require platform-specific extensions or socket2 crate
    println!("TCP_NODELAY set: {}", stream.nodelay()?);
    Ok(())
}
