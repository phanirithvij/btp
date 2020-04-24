import 'dart:convert';

import 'package:corpora/cache/manager.dart';
import 'package:corpora/provider/authentication.dart';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

// TODO
// Not for this project but useful for me when building the plex like app
// This server info should be fetched from the network device discovery

/// Server details configured to my machine for now
class ServerDetails {
  static final String server = "http://192.168.43.159:3000";
  static final String fileUploadUrl = server + "/upload";
  static final String fileDownloadUrl = server + "/files";
  static final String corporaUrl = server + "/data";
  static final String authUrl = server + "/auth";
  static final String refreshTokenUrl = server + "/refresh";
  static final String loginUrl = authUrl + "/login";
  static final String registerUrl = authUrl + "/new";
  static final String skipUrl = server + "/skipped";
}

class ServerUtils {
  // https://stackoverflow.com/a/49645074/8608146
  static uploadFile(File file, String apiToken) async {
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
    request.headers[HttpHeaders.authorizationHeader] = "Bearer $apiToken";
    var response = await request.send();
    print(response.statusCode);
    response.stream.transform(utf8.decoder).listen((value) {
      print(value);
    });
  }

  static Future<String> refreshToken(AuthInfo info) async {
    final _response = await http.get(
      ServerDetails.refreshTokenUrl,
      headers: {
        HttpHeaders.authorizationHeader: "Bearer ${info.refreshToken}",
        HttpHeaders.cookieHeader: info.cookies,
      },
    );

    final _newtoken = json.decode(_response.body);
    print(_newtoken);

    return "_newtoken";
  }

  static Future<List<String>> getSentences(
      AuthInfo info, String pointer) async {
    print('start cahce data');
    final _response = await CustomCacheManager().getSingleFile(
      ServerDetails.corporaUrl,
      headers: {
        HttpHeaders.authorizationHeader: "Bearer ${info.apiToken}",
        HttpHeaders.cookieHeader: info.cookies,
      },
    );

    int _pointer = int.parse(pointer);
    final _data = _response.readAsStringSync().split('\n');

    // should not shuffle because pointer logic will become complex
    return _data.sublist(
      _pointer,
      (_pointer + 100 >= _data.length) ? _data.length : _pointer + 100,
    );
  }

  static Future<void> skipScentences(AuthInfo info, List<String> ids) async {
    final _response = await http.post(
      ServerDetails.skipUrl,
      headers: {
        HttpHeaders.authorizationHeader: "Bearer ${info.apiToken}",
        HttpHeaders.cookieHeader: info.cookies,
        HttpHeaders.contentTypeHeader: "application/json"
      },
      body: json.encode({"ids": ids}),
    );

    if (_response.statusCode == 401) {
      refreshToken(info);
    }

    print(_response.body);
  }
}
