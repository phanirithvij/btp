import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';
import 'package:corpora/screens/login.dart';

void main() => runApp(corporaApp());

class corporaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "corpora Collector",
      theme: kAmoledTheme,
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  HomePage({Key key}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: kGradientBackground,
        child: Center(
          child: Text("Welcome to corpora collector!",
              style: TextStyle(fontSize: 24)),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.of(context)
              .push(MaterialPageRoute(builder: (context) => LoginPage()));
        },
        tooltip: 'Start',
        backgroundColor: Colors.black87,
        foregroundColor: Colors.greenAccent,
        child: Icon(Icons.play_arrow, size: 27),
      ),
    );
  }
}
