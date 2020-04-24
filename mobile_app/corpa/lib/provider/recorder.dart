import 'dart:io';

import 'package:corpora/provider/authentication.dart';
import 'package:corpora/provider/server.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum RecordingState { Started, Ended, Unknown }

class RecorderStore with ChangeNotifier {
  static const platform = const MethodChannel('com.example.corpora/open');
  File saveFile;
  int current = 0;
  String pointer;
  RecordingState _state = RecordingState.Unknown;
  List<String> _skipped = [];
  set state(RecordingState _states) {
    _state = _states;
    notifyListeners();
  }

  get state => _state;

  AuthInfo userInfo;
  List<String> sentences = [];

  void openRec() async => await platform.invokeMethod("startRec");

  void startRecording() async {
    state = RecordingState.Started;

    final _temp = await getTemporaryDirectory();
    saveFile = File("${_temp.path}/${userInfo.userId}_$pointer.wav");

    await platform.invokeMethod('startRec', {'name': saveFile.path});

    // TODO
    // audio format mp3/wav is preferred
    // with sampling rate 44.1/48 khz
  }

  void stopRecording() async {
    state = RecordingState.Ended;

    await platform.invokeMethod('stopRec');
  }

  /// Uploads the recording to the server
  void uploadRecording() async {
    ServerUtils.uploadFile(saveFile, userInfo.apiToken);
  }

  /// The global pointer is fecthed from shared_preferences
  Future<void> fetchGlobalPointer() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    pointer = prefs.getString('pointer') ?? 0;
  }

  /// The next sentence is displayed
  void next() {
    current++;
    pointer = sentences[current].split("||")[0];
    uploadRecording();
    state = RecordingState.Unknown;
    notifyListeners();
  }

  String get currentSentence {
    return (sentences.length != 0) ? sentences[current].split('||')[1] : null;
  }

  void populateSentences() async {
    // pointer would be fecthed by now from the shared preferences
    sentences = await ServerUtils.getSentences(userInfo, pointer);
    // init the pointer
    assert(pointer == sentences[current].split("||")[0]);
    notifyListeners();
  }

  void sendSkippedData() {
    ServerUtils.skipScentences(userInfo, _skipped).whenComplete(() {
      _skipped.clear();
    });
  }

  /// add to the skipped List the current sentence
  void skipScentence() {
    _skipped.add(pointer);
    current++;
    // update the pointer
    pointer = sentences[current].split("||")[0];
    notifyListeners();
  }
}
