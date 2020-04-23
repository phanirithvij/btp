import 'dart:io';

import 'package:corpora/provider/server.dart';
import 'package:corpora/screens/login.dart';
import 'package:corpora/themes/utils.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:corpora/provider/authentication.dart';

class RecordPage extends StatefulWidget {
  RecordPage(this.authInfo, {Key key}) : super(key: key);

  final AuthInfo authInfo;

  @override
  _RecordPageState createState() => _RecordPageState();
}

enum RecordingState { Started, Ended, Unknown }

class _RecordPageState extends State<RecordPage> {
  static const platform = const MethodChannel('com.example.corpora/open');

  // FlutterSoundRecorder flutterSoundRecorder = FlutterSoundRecorder();
  File _saveFile;
  // StreamSubscription _recorderSubscription;
  RecordingState _state = RecordingState.Unknown;

  void openRec() async => await platform.invokeMethod("startRec");

  void rebuild() {
    setState(() {});
  }

  void _handleRecording() {
    switch (_state) {
      case RecordingState.Started:
        _stopRecording();
        rebuild();
        break;
      case RecordingState.Ended:
        _startRecording();
        rebuild();
        break;
      default:
        _startRecording();
        rebuild();
    }
  }

  void _startRecording() async {
    _state = RecordingState.Started;

    Directory tempDir = Directory.systemTemp;
    _saveFile = File('${tempDir.path}/flutter_sound-tmp.wav');

    await platform.invokeMethod('startRec', {'name': _saveFile.path});

    // TODO
    // audio format mp3/wav is preferred
    // with sampling rate 44.1/48 khz
  }

  void _stopRecording() async {
    _state = RecordingState.Ended;

    await platform.invokeMethod('stopRec');
  }

  void _uploadRecording() {
    ServerUtils.uploadFile(_saveFile);
  }

  @override
  Widget build(BuildContext context) {
    // TODO figure out a way to make this global
    if (MediaQuery.of(context).orientation == Orientation.portrait) {
      SystemChrome.setEnabledSystemUIOverlays(
          [SystemUiOverlay.bottom, SystemUiOverlay.top]);
    } else {
      SystemChrome.setEnabledSystemUIOverlays([]);
    }
    return Scaffold(
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: Container(
        color: Colors.blueGrey,
        padding: EdgeInsets.all(8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: <Widget>[
            IconButton(
              icon: Icon(Icons.folder_open),
              onPressed: openRec,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _handleRecording,
        child: Icon(
          _state == RecordingState.Started
              ? Icons.stop
              : Icons.fiber_manual_record,
          size: 27,
        ),
        tooltip: 'Start',
        backgroundColor: Colors.black87,
        foregroundColor: Colors.blueGrey,
      ),
      body: Stack(
        children: <Widget>[
          Container(
            decoration: kGradientBackgroundRecord,
            child: Center(
                child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Text("Welcome ${widget.authInfo.name}, read this:",
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                Text("I'm an awesome human",
                    style:
                        TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              ],
            )),
          ),
          CustomAppBar(),
        ],
      ),
    );
  }
}

class CustomAppBar extends StatelessWidget {
  CustomAppBar({
    Key key,
  }) : super(key: key);

  final store = AuthStore();

  @override
  Widget build(BuildContext context) {
    return Positioned(
      right: 0,
      // camera covers it in portrait mode without this
      top: MediaQuery.of(context).orientation == Orientation.portrait ? 31 : 0,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(20), bottomLeft: Radius.circular(20)),
          color: Colors.blueGrey.withOpacity(0.6),
        ),
        child: Row(
          children: <Widget>[
            IconButton(icon: Icon(Icons.chevron_right), onPressed: () {}),
            IconButton(
                icon: Icon(Icons.power_settings_new),
                onPressed: () {
                  store.logout();
                  // redirect to login screen
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => LoginPage()),
                  );
                }),
            IconButton(icon: Icon(Icons.settings), onPressed: () {}),
            IconButton(icon: Icon(Icons.account_circle), onPressed: () {}),
          ],
        ),
      ),
    );
  }
}
