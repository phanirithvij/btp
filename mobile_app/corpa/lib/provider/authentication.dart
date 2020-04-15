import 'dart:io';

import 'package:corpora/provider/serveinfo.dart';
import 'package:corpora/utils/date.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'dart:convert';
import 'dart:async';

import 'package:shared_preferences/shared_preferences.dart';

/// Enum for the authentication status
enum AuthStatus {
  /// Successful authentication
  Success,
  Forbidden,
  Unauthorized,
  Unknown,
  Failed,

  /// When invalid username or passworld is submitted
  Invalid
}

/// Convert status string to enum
AuthStatus _getStatus(String status) {
  switch (status) {
    case 'ok':
      return AuthStatus.Success;
    case 'forbidden':
      return AuthStatus.Forbidden;
    case 'unauthorized':
      return AuthStatus.Unauthorized;
    default:
      return AuthStatus.Unknown;
  }
}

/// User authentication information
class AuthInfo {
  var status = AuthStatus.Unknown;
  var errors = [];
  String userId;
  String name;

  AuthInfo();

  factory AuthInfo.fromJson(Map<String, dynamic> json) {
    return AuthInfo()
      ..userId = json['userId']
      ..name = json['name']
      ..errors.add(json['error'])
      ..status = _getStatus(json['status'] as String);
  }

  bool get hasErrors {
    // remove empty errors from the server
    errors.removeWhere((err) => err == '');
    return errors.length > 0;
  }

  @override
  String toString() {
    return "Status $status UserId $userId Name $name Errors $errors";
  }

  Future<void> persistLoginonDisk() async {
    print("Save Login Info");
    SharedPreferences prefs = await SharedPreferences.getInstance();
    // String name = (prefs.getString('name') ?? "");
    await prefs.setBool('loggedin', true);
    if (name != "") await prefs.setString('name', name);
    if (userId != "") await prefs.setString('userId', userId);
  }
}

class AuthStore extends ChangeNotifier {
  // Store username, pass, dob, etc..
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  DateTime selectedDate = DateTime.now();

  SharedPreferences _prefs;

  void storeDate(DateTime date) {
    selectedDate = date;
    notifyListeners();
    print("DatePicker $date");
  }

  Future<AuthInfo> tryAuth(String type) async {
    final username = usernameController.text;
    // TODO encrypt password
    final password = passwordController.text;

    print("username is $username");
    print("Passwd is $password");

    AuthInfo info = AuthInfo();
    if (_validate()) {
      var reqUrl = ServerDetails.authUrl;
      print("Sent request to ${ServerDetails.authUrl}");

      http.Response _response;
      if (type == "login") {
        reqUrl = ServerDetails.loginUrl;
        _response = await http.get(
          reqUrl,
          headers: {
            HttpHeaders.authorizationHeader: "Basic your_api_token_here"
          },
        );
      } else {
        // date of birth
        reqUrl = ServerDetails.registerUrl;
        // TODO register
        _response = await http.post(reqUrl, body: {
          "username": username,
          "password": password,
          "age": DateUtils.getAge(selectedDate)
        });
      }

      if (_response.statusCode == 500) {
        // Internal Server error
        info.errors.add("Internal server error 500");
      }
      // print(_response.statusCode);
      else if (_response.statusCode == 200) {
        final _responseJson = json.decode(_response.body);
        info = AuthInfo.fromJson(_responseJson);
        print(info.errors);
      }
      return info;
    } else {
      // Invalid fields
      info = AuthInfo();
      if (!_validUsername(username)) {
        info = info
          ..status = AuthStatus.Invalid
          ..errors.add("Invalid username entered");
      }
      if (!_validPass(password)) {
        info = info
          ..status = AuthStatus.Invalid
          ..errors.add("Invalid Password entered");
      }
      return info;
    }
  }

  bool _validate() {
    var username = usernameController.text;
    var password = passwordController.text;
    return _validUsername(username) && _validPass(password);
  }

  bool _validUsername(String username) {
    // TODO
    if (username == "") {
      return false;
    }
    return true;
  }

  bool _validPass(String pass) {
    // TODO
    if (pass == "") {
      return false;
    }
    return true;
  }

  Future<SharedPreferences> get _getPrefs async {
    if (_prefs == null) {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      _prefs = prefs;
    }
    return _prefs;
  }

  Future<bool> get isLoggedin async {
    SharedPreferences prefs = await _getPrefs;
    bool loggedin = prefs.getBool('loggedin') ?? false;
    return loggedin;
  }

  Future<AuthInfo> getUserInfoFromDisk({bool loggedin = false}) async {
    final info = AuthInfo();
    if (loggedin || await isLoggedin) {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      // String name = (prefs.getString('name') ?? "");
      String name = prefs.getString('name');
      String userId = prefs.getString('userId');
      return info
        ..name = name
        ..userId = userId;
    } else {
      return info..errors.add("User not Logged in");
    }
  }

  void logout() async {
    SharedPreferences prefs = await _getPrefs;
    if (await isLoggedin) {
      // TODO
      // clearing everthing
      // If I save a bool _notFirstTime = true after opening the app once
      // I need to not clear it here
      // Don't show the onboarding screen to the user again

      await prefs.clear();
      print("Logging out");
      // prefs.setBool('loggedin', false);
    } else {
      return;
    }
  }

  @override
  void dispose() {
    usernameController.dispose();
    passwordController.dispose();
    super.dispose();
  }
}
