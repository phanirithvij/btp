import 'package:corpora/screens/login.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:corpora/provider/authentication.dart';

class RecordPage extends StatefulWidget {
  RecordPage(this.authInfo, {Key key}) : super(key: key);

  final AuthInfo authInfo;

  @override
  _RecordPageState createState() => _RecordPageState();
}

class _RecordPageState extends State<RecordPage> {
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
      body: Stack(
        children: <Widget>[
          Container(
            decoration: BoxDecoration(
              gradient: RadialGradient(
                radius: 2.5,
                center: Alignment.centerRight,
                colors: [Colors.blueGrey, Colors.black],
              ),
            ),
            child: Center(
                child: Text("Welcome ${widget.authInfo.name}",
                    style:
                        TextStyle(fontSize: 22, fontWeight: FontWeight.bold))),
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
