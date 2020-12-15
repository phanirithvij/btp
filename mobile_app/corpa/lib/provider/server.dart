import 'dart:convert';

import 'package:corpora/cache/manager.dart';
import 'package:corpora/provider/authentication.dart';
import 'package:path/path.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

// TODO the file sizes are 500KB + so must use this to show progress
// import 'package:flutter_uploader/flutter_uploader.dart';

import 'package:shared_preferences/shared_preferences.dart';

// TODO
// Not for this project but useful for me when building the plex like app
// This server info should be fetched from the network device discovery

// {
//   id: 1
//   address: Hyderabad
//   alias: sample
//   description: Sample Description
//   emails: [
//     {
//       private: false
//       email: public@sample.org
//       id: 2
//       main: false
//     }
//   ]
//   location: null
//   name: Sample Organization
//   private: false
//   privateLoc: null
//   server: http://localhost:8080
//   serverAlias: SampleDBX1
//   serverID: 1
// }

class ServerObj {
  int id;
  String address;
  String alias;
  String name;
  String description;
  List<Email> emails;
  String serverAlias;
  int serverID;
  String server;
  bool private;
  bool privateLoc;
  List<double> location;
  ServerObj();

  factory ServerObj.fromJson(Map<String, dynamic> json) {
    return ServerObj()
      ..id = json['id']
      ..name = json['name']
      ..description = json['description']
      ..alias = json['alias']
      ..server = json['server']
      ..emails = (json['emails'] as List).map((e) => Email.fromJson(e)).toList()
      ..serverAlias = json['serverAlias']
      ..private = json['private']
      ..privateLoc = json['privateLoc']
      ..location = json['location']
      ..address = json['address']
      ..serverID = json['serverID'];
  }
}

class Email {
  String email;
  bool private;
  int id;
  bool main;

  Email();

  factory Email.fromJson(Map<String, dynamic> json) {
    return Email()
      ..email = json['email']
      ..id = json['id']
      ..main = json['main']
      ..private = json['private'];
  }
}

/// Server details configured to my machine for now
class ServerDetails {
  String _server;
  set server(String s) {
    this._server = s;
  }

  String get server {
    return _server;
  }

  String get centralServer {
    return "http://192.168.0.102:9090";
  }

  String get centralServerPublicList {
    return centralServer + '/api/v1/home/public';
  }

  String get fileUploadUrl {
    return server + "/upload";
  }

  String get fileDownloadUrl {
    return server + "/files";
  }

  String get corporaUrl {
    return server + "/data";
  }

  String get authUrl {
    return server + "/auth";
  }

  String get refreshTokenUrl {
    return server + "/refresh";
  }

  String get loginUrl {
    return authUrl + "/login";
  }

  String get registerUrl {
    return authUrl + "/new";
  }

  String get skipUrl {
    return server + "/skipped";
  }
}

class ServerUtils {
  // https://stackoverflow.com/a/49645074/8608146
  static uploadFile(File file, AuthInfo authInfo) async {
    print("Started upload");
    var stream = http.ByteStream(file.openRead().cast());
    var length = await file.length();

    print("length $length");

    var uri = Uri.parse(authInfo.serverDetails.fileUploadUrl);

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
      info.serverDetails.refreshTokenUrl,
      headers: {
        HttpHeaders.authorizationHeader: "Bearer ${info.refreshToken}",
        HttpHeaders.cookieHeader: info.cookies,
      },
    );

    final _newtoken = json.decode(_response.body);
    print(_newtoken);

    return "_newtoken";
  }

  static Future<List<ServerObj>> getPublicServers() async {
    final _response = await http.get(
      // no need to worry about .server here central server is different
      ServerDetails().centralServerPublicList,
    );

    final jsonx = json.decode(_response.body);
    final sObjs = (jsonx as List).map((x) => ServerObj.fromJson(x)).toList();
    print(sObjs);

    return sObjs;
  }

  static Future<List<String>> getSentences(
      AuthInfo info, String pointer, bool refresh) async {
    print('start cahce data');
    final _response = await CustomCacheManager().getSingleFile(
      info.serverDetails.corporaUrl,
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
      info.serverDetails.skipUrl,
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

    if (_response.statusCode == 200) {
      await prefs.remove('tempbuffer');
    }

    print(_response.body);
  }
}
