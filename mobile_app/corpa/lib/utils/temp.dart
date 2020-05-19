// RawDatagramSocket.bind(InternetAddress.anyIPv4, 8020)
//     .then((RawDatagramSocket udpSocket) {
//   // udpSocket.broadcastEnabled = true;
//   udpSocket.listen((e) {
//     Datagram dg = udpSocket.receive();
//     if (dg != null) {
//       // print("received");
//       print(String.fromCharCodes(dg.data));
//     } else {
//       print(dg);
//     }
//   });
// }).catchError((e) {
//   print(e);
// });
