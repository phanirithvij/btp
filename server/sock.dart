import 'dart:io';

// https://stackoverflow.com/a/54330146/8608146
main() {
  // https://stackoverflow.com/questions/4464207/android-find-a-server-in-the-network
  // final destination = InternetAddress("255.255.255.255");

  RawDatagramSocket.bind(InternetAddress.anyIPv4, 9000)
      .then((RawDatagramSocket udpSocket) {
    udpSocket.broadcastEnabled = true;
    udpSocket.listen((e) {
      Datagram dg = udpSocket.receive();
      if (dg != null) {
        // print("received");
        stdout.write(String.fromCharCodes(dg.data));
      }
    });

    // import 'dart:convert';
    // List<int> data = utf8.encode('TEST');
    // udpSocket.send(data, destination, 8020);
  });
}
