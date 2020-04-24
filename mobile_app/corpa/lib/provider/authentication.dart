import 'dart:io';

import 'package:corpora/cache/manager.dart';
import 'package:corpora/provider/server.dart';
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

  /// Successful authentication but new user,
  /// Useful when a tutorial needs to be shown
  NewUser,

  /// When invalid username or passworld is submitted
  Invalid
}

enum AuthType { Login, Register }

/// Convert status string to enum
AuthStatus _getStatus(String status) {
  switch (status) {
    case 'ok':
      return AuthStatus.Success;
    case 'new':
      return AuthStatus.NewUser;
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
  String gender;
  String apiToken;
  String refreshToken;
  String cookies;

  AuthInfo();

  factory AuthInfo.fromJson(Map<String, dynamic> json) {
    return AuthInfo()
      ..userId = json['userId']
      ..name = json['name']
      ..gender = json['gender']
      ..apiToken = json['access_token']
      ..refreshToken = json['refresh_token']
      ..errors.add(json['error'])
      ..status = _getStatus(json['status'] as String);
  }

  bool get hasErrors {
    // remove empty errors from the server
    errors.removeWhere((err) => err == '');
    return errors.length > 0;
  }

  bool get isNewUser => status == AuthStatus.NewUser;

  @override
  String toString() {
    return """
    Status $status
    UserId $userId
    Name $name
    Gender $gender
    Errors $errors
    Cookies $cookies
    APIToken $apiToken
    """
        .split('\n')
        .map((f) => f.trim())
        .join('\n');
  }

  Future<void> persistLoginonDisk() async {
    print("Save Login Info");
    SharedPreferences prefs = await SharedPreferences.getInstance();
    // String name = (prefs.getString('name') ?? "");
    await prefs.setBool('loggedin', true);
    if (name != null) await prefs.setString('name', name);
    if (userId != null) await prefs.setString('userId', userId);
    if (apiToken != null) await prefs.setString('apiToken', apiToken);
    if (refreshToken != null)
      await prefs.setString('refreshToken', refreshToken);
    if (cookies != null) await prefs.setString('cookies', cookies);
  }
}

class AuthStore extends ChangeNotifier {
  // Store username, pass, dob, etc..
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  DateTime selectedDate = DateTime.now();
  String _gender = "m";
  String get selectedGender => _gender;
  set selectedGender(String gender) {
    _gender = gender;
    notifyListeners();
  }

  SharedPreferences _prefs;

  /// fecth from shared_preferences
  String get apiToken {
    return _prefs.getString('apiToken');
  }

  void storeDate(DateTime date) {
    selectedDate = date;
    notifyListeners();
    print("DatePicker $date");
  }

  Future<AuthInfo> tryAuth({AuthType type = AuthType.Login}) async {
    final username = usernameController.text;
    final password = passwordController.text;

    print("username is $username");
    print("Passwd is $password");
    print("Gender is $_gender");
    print("D.O.B is $selectedDate");

    AuthInfo info = AuthInfo();
    if (_validate(type)) {
      var reqUrl = ServerDetails.authUrl;
      print("Sent request to ${ServerDetails.authUrl}");

      http.Response _response;
      if (type == AuthType.Login) {
        // https://stackoverflow.com/a/55000232/8608146
        reqUrl = ServerDetails.loginUrl;
        _response = await http.post(
          reqUrl,
          headers: {HttpHeaders.contentTypeHeader: "application/json"},
          body: json.encode({
            "username": username,
            "password": password,
          }),
        );
      } else {
        // date of birth
        reqUrl = ServerDetails.registerUrl;
        _response = await http.post(reqUrl, body: {
          "username": username,
          "password": password,
          "age": DateUtils.getAge(selectedDate).toString(),
          "gender": _gender,
        });
      }

      if (_response.statusCode == 500) {
        // Internal Server error
        info.errors.add("Internal server error 500");
      }
      // print(_response.statusCode);
      else {
        // print(_response.body);
        final _responseJson = json.decode(_response.body);
        info = AuthInfo.fromJson(_responseJson);
        info.cookies = _response.headers[HttpHeaders.setCookieHeader];
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
      if (!_validAge(selectedDate)) {
        info = info
          ..status = AuthStatus.Invalid
          ..errors.add("Age is < 6 please re-check");
      }
      return info;
    }
  }

  bool _validate(AuthType loginType) {
    final _username = usernameController.text;
    final _password = passwordController.text;
    var _valid = false;
    if (loginType == AuthType.Register) {
      _valid = _validUsername(_username) &&
          _validPass(_password) &&
          _validAge(selectedDate);
    } else {
      _valid = _validUsername(_username) && _validPass(_password);
    }
    return _valid;
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

  bool _validAge(DateTime date) {
    if (DateUtils.getAge(date) < 6) {
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
      String apiToken = prefs.getString('apiToken');
      String refreshToken = prefs.getString('refreshToken');
      String cookies = prefs.getString('cookies');
      return info
        ..name = name
        ..userId = userId
        ..cookies = cookies
        ..apiToken = apiToken
        ..refreshToken = refreshToken;
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
      // clearing cache so a different file will be downloaded most likely.
      // because if we don't the user will see the same utterence that they skipped
      await CustomCacheManager().emptyCache();
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
