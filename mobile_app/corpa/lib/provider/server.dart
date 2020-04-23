import 'dart:convert';

import 'package:path/path.dart';
import 'package:async/async.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

// TODO
// This server info should be fetched from the network device discovery

/// Server details configured to my machine for now
class ServerDetails {
  static final String server = "http://192.168.43.159:3000";
  static final String fileUploadUrl = server + "/upload";
  static final String fileDownloadUrl = server + "/files";
  static final String authUrl = server + "/auth";
  static final String loginUrl = authUrl + "/login";
  static final String registerUrl = authUrl + "/new";
}

class ServerUtils {
  // https://stackoverflow.com/a/49645074/8608146
  static uploadFile(File file) async {
    print("Started upload");
    var stream = http.ByteStream(DelegatingStream.typed(file.openRead()));
    var length = await file.length();

    print("length $length");

    var uri = Uri.parse(ServerDetails.fileUploadUrl);

    var request = http.MultipartRequest("POST", uri);
    var multipartFile = http.MultipartFile('file', stream, length,
        filename: basename(file.path));
    //contentType:  MediaType('image', 'png'));

    request.files.add(multipartFile);
    var response = await request.send();
    print(response.statusCode);
    response.stream.transform(utf8.decoder).listen((value) {
      print(value);
    });
  }
}
