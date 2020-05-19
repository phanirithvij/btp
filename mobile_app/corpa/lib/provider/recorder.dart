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
  int _count = 0;
  set state(RecordingState _states) {
    _state = _states;
    notifyListeners();
  }

  get state => _state;

  AuthInfo userInfo;
  List<String> sentences = [];

  void playAudio() async {
    await platform.invokeMethod('startPlay');
  }

  void stopAudio() async {
    await platform.invokeMethod('stopPlay');
  }

  void handleRecording() {
    switch (state) {
      case RecordingState.Started:
        stopRecording();
        break;
      case RecordingState.Ended:
        startRecording();
        break;
      default:
        startRecording();
    }
  }

  void startRecording() async {
    state = RecordingState.Started;
    notifyListeners();

    final _temp = await getTemporaryDirectory();
    assert(userInfo.userId != null);
    saveFile = File("${_temp.path}/${userInfo.userId}_$pointer.wav");

    await platform.invokeMethod('startRec', {'name': saveFile.path});

    // TODO
    // audio format mp3/wav is preferred
    // with sampling rate 44.1/48 khz
  }

  void stopRecording() async {
    state = RecordingState.Ended;
    await platform.invokeMethod('stopRec');
    notifyListeners();
  }

  /// Uploads the recording to the server
  void uploadRecording() async {
    _count++;
    notifyListeners();
    ServerUtils.uploadFile(saveFile, userInfo);
  }

  void saveState(String pointer) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    prefs.setString('pointer', pointer);
  }

  /// The global pointer is fecthed from shared_preferences
  Future<void> fetchGlobalPointer() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    // this will be null initially
    pointer = prefs.getString('pointer');
  }

  /// The next sentence is displayed
  void next() async {
    current++;
    // reached the end repopulate the sentences
    if (current == sentences.length) await populateSentences(refresh: true);
    pointer = sentences[current].split("||")[0];
    saveState(pointer);
    uploadRecording();
    state = RecordingState.Unknown;
    notifyListeners();
  }

  Widget promptsSentence(BuildContext context) {
    String _text = "";
    if (_count != 0) _text = "Prompts read: $_count";
    return Padding(
      padding: const EdgeInsets.only(bottom: 30.0, right: 10, left: 10),
      child: Align(
        alignment: MediaQuery.of(context).orientation == Orientation.portrait
            ? Alignment.bottomCenter
            : Alignment.bottomRight,
        // bottom: 0,
        child: Container(
          child: Text(_text),
          decoration: _text != "" ? BoxDecoration(border: Border.all()) : null,
        ),
      ),
    );
  }

  String get currentSentence {
    return (sentences.length != 0) ? sentences[current].split('||')[1] : null;
  }

  Future populateSentences({bool refresh = false}) async {
    // pointer would be fecthed by now from the shared preferences
    sentences = await ServerUtils.getSentences(userInfo, pointer, refresh);
    current = 0;
    // init the pointer
    pointer = sentences[current].split("||")[0];
    notifyListeners();
  }

  // K = decide later
  // for every k skips it is sent to sever
  final K = 5;

  void sendSkippedData() {
    ServerUtils.skipScentences(userInfo, _skipped).whenComplete(() {
      _skipped.clear();
    });
  }

  /// add to the skipped List the current sentence
  void skipScentence() async {
    _skipped.add(pointer);
    // call this method for evey K skips
    if (_skipped.length >= K) sendSkippedData();

    current++;
    // reached the end repopulate the sentences
    if (current == sentences.length) await populateSentences(refresh: true);

    // update the pointer
    pointer = sentences[current].split("||")[0];
    saveState(pointer);
    print("Sentences length ${sentences.length}");
    print("Current $current");

    notifyListeners();
  }
}
