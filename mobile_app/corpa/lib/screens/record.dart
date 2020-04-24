import 'package:corpora/components/global.dart';
import 'package:corpora/components/player.dart';
import 'package:corpora/provider/recorder.dart';
import 'package:corpora/screens/login.dart';
import 'package:corpora/themes/utils.dart';
import 'package:flutter/material.dart';

import 'package:corpora/provider/authentication.dart';
import 'package:provider/provider.dart';

class RecordPageProviderWrapper extends StatelessWidget {
  const RecordPageProviderWrapper({Key key, @required this.info})
      : super(key: key);

  final AuthInfo info;

  @override
  Widget build(BuildContext context) {
    return GlobalOrientationHandler(
      child: ChangeNotifierProvider(
        create: (_) => RecorderStore(),
        child:
            Consumer<RecorderStore>(builder: (_, __, ___) => RecordPage(info)),
      ),
    );
  }
}

class RecordPage extends StatefulWidget {
  RecordPage(this.authInfo, {Key key}) : super(key: key);

  final AuthInfo authInfo;

  @override
  _RecordPageState createState() => _RecordPageState();
}

class _RecordPageState extends State<RecordPage> {
  void rebuild() {
    setState(() {});
  }

  @override
  void initState() {
    super.initState();

    print(widget.authInfo);
  }

  @override
  void didChangeDependencies() {
    Provider.of<RecorderStore>(context, listen: false).userInfo =
        widget.authInfo;
    // This order is important
    Provider.of<RecorderStore>(context, listen: false)
        .fetchGlobalPointer()
        .whenComplete(() {
      Provider.of<RecorderStore>(context, listen: false).populateSentences();
    });

    super.didChangeDependencies();
  }

  void _handleRecording() {
    switch (Provider.of<RecorderStore>(context, listen: false).state) {
      case RecordingState.Started:
        Provider.of<RecorderStore>(context, listen: false).stopRecording();
        rebuild();
        break;
      case RecordingState.Ended:
        Provider.of<RecorderStore>(context, listen: false).startRecording();
        rebuild();
        break;
      default:
        Provider.of<RecorderStore>(context, listen: false).startRecording();
        rebuild();
    }
  }

  Widget get _controls {
    switch (Provider.of<RecorderStore>(context, listen: false).state) {
      case RecordingState.Unknown:
        return SkipCurrent();
        break;
      case RecordingState.Ended:
        return PlayerControls();
        break;
      case RecordingState.Started:
        return RecordDetails();
        break;
      default:
        return SkipCurrent();
    }
  }

  @override
  Widget build(BuildContext context) {
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
              onPressed:
                  Provider.of<RecorderStore>(context, listen: false).openRec,
            ),
          ],
        ),
      ),
      floatingActionButton: Consumer<RecorderStore>(
        builder: (_, __, ___) => FloatingActionButton(
          onPressed: _handleRecording,
          child: Icon(
            Provider.of<RecorderStore>(context, listen: false).state ==
                    RecordingState.Started
                ? Icons.stop
                : Icons.fiber_manual_record,
            size: 27,
          ),
          tooltip: Provider.of<RecorderStore>(context, listen: false).state ==
                  RecordingState.Started
              ? 'Stop Recording'
              : 'Start Recording',
          backgroundColor: Colors.black87,
          foregroundColor: Colors.blueGrey,
        ),
      ),
      body: Stack(
        children: <Widget>[
          Container(
            width: double.infinity,
            height: double.infinity,
            decoration: kGradientBackgroundRecord,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                WelcomeWidget(info: widget.authInfo),
                // https://stackoverflow.com/questions/50554110/how-do-i-center-text-vertically-and-horizontally-in-flutter
                Utterance(),
                _controls
              ],
            ),
          ),
          CustomAppBar(),
        ],
      ),
    );
  }
}

class Utterance extends StatelessWidget {
  const Utterance({
    Key key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: (Provider.of<RecorderStore>(context).currentSentence != null)
            ? Text(
                Provider.of<RecorderStore>(context).currentSentence,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              )
            : CircularProgressIndicator(),
      ),
    );
  }
}

class WelcomeWidget extends StatelessWidget {
  const WelcomeWidget({
    Key key,
    @required this.info,
  }) : super(key: key);

  final AuthInfo info;

  @override
  Widget build(BuildContext context) {
    return info.isNewUser
        ? Text(
            "Welcome ${info.name}, read this:",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          )
        // Must return this empty container for the ui to look the same
        // As in the column [spaceEvenly] looks for children count
        // when spacing them evenly
        : Container();
  }
}

class RecordDetails extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(child: Text("Duration : 0:00"));
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
