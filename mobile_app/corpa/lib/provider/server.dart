import 'dart:convert';

import 'package:corpora/cache/manager.dart';
import 'package:corpora/provider/authentication.dart';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

// TODO the file sizes are 500KB + so must use this to show progress
// import 'package:flutter_uploader/flutter_uploader.dart';

import 'package:shared_preferences/shared_preferences.dart';

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
  static uploadFile(File file, AuthInfo authInfo) async {
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
    request.headers[HttpHeaders.authorizationHeader] =
        "Bearer ${authInfo.apiToken}";
    request.headers[HttpHeaders.cookieHeader] = authInfo.cookies;
    var response = await request.send();
    print(response.statusCode);
    response.stream.transform(utf8.decoder).listen((value) {
      print(value);
    });
  }

  // TODO take name and autogen a username
  // from werkzeug.utils import secure_filename
  // secure_filename("K Phani Rithvij")
  // Good start

  // TODO refreshtoken method
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
      AuthInfo info, String pointer, bool refresh) async {
    print('start cahce data');
    final _response = await CustomCacheManager().getSingleFile(
      ServerDetails.corporaUrl,
      headers: {
        HttpHeaders.authorizationHeader: "Bearer ${info.apiToken}",
        HttpHeaders.cookieHeader: info.cookies,
      },
    );

    int _pointer = 0;
    final _data = _response.readAsStringSync().split('\n');
    print("Not null? $pointer");
    if (pointer != null) {
      _pointer = int.parse(pointer);
      if (refresh) {
        // increment by one so the previous utterence wouldn't be included
        _pointer++;
        pointer = "$_pointer";
      }
      var _found = _data.where((x) => x.startsWith(pointer)).toList();
      if (_found.length == 0) {
        // cache file expired so new file was fecthed
        // or wrong pointer was provided
        // it was not found in the cache file
        // set it to the first one
        _found = _data.sublist(0, 1);
      }
      _pointer = _data.indexOf(_found[0]);
      print("Pointer now is $_pointer");
    }
    // else
    // _pointer = 0 => read from beginning of the cached file

    // should not shuffle because pointer logic will become complex
    return _data.sublist(
      _pointer,
      (_pointer + 30 >= _data.length) ? _data.length : _pointer + 30,
    );
  }

  static Future<void> skipScentences(AuthInfo info, List<String> ids) async {
    // TODO store a skipbuffer in shared prefs
    // And clear it on Success let it stay on failure
    // And when the app is loaded call this method

    SharedPreferences prefs = await SharedPreferences.getInstance();
    final _success = await prefs.setStringList('tempbuffer', ids);
    if (!_success) print("Failed to set tempbuffer in saved preferences");

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
