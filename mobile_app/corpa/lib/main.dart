import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/record.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';
import 'package:corpora/screens/login.dart';
import 'package:flutter/services.dart';

void main() {
  // RawDatagramSocket.bind(InternetAddress.anyIPv4, 8020)
  //     .then((RawDatagramSocket udpSocket) {
  //   // udpSocket.broadcastEnabled = true;
  //   udpSocket.listen((e) {
  //     Datagram dg = udpSocket.receive();
  //     if (dg != null) {
  //       // print("received");
  //       print(String.fromCharCodes(dg.data));
  //     } else {
  //       print(dg);
  //     }
  //   });
  // }).catchError((e) {
  //   print(e);
  // });

  runApp(CorporaApp());
}

class CorporaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Corpora Collector",
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
  bool isLoggedin = false;
  AuthInfo info;
  AuthStore store;
  bool _fecthed = false;

  @override
  void initState() {
    store = AuthStore();
    _fetchAuthInfo();
    super.initState();
  }

  void _fetchAuthInfo() async {
    info = await store.getUserInfoFromDisk();
    var loggedin = await store.isLoggedin;
    setState(() {
      print("Loggedin $loggedin");
      isLoggedin = loggedin;
      _fecthed = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Hide bars when on landscape orientation
    if (MediaQuery.of(context).orientation == Orientation.portrait) {
      SystemChrome.setEnabledSystemUIOverlays(
          [SystemUiOverlay.bottom, SystemUiOverlay.top]);
    } else {
      SystemChrome.setEnabledSystemUIOverlays([]);
    }

    // If we have not fetched the auth info yet show a trying to login screen
    if (!_fecthed) return PlaceHolderRedirectScreen();

    if (isLoggedin) {
      // redirect to record page
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => RecordPage(info),
          ),
        );
      });
      // Show a placeholder redirect screen
      return PlaceHolderRedirectScreen();
    } else
      return WelcomePage();
  }
}

/// Welcome page i.e. Onboarding page
class WelcomePage extends StatelessWidget {
  const WelcomePage({
    Key key,
  }) : super(key: key);

  // TODO add some more functionality
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
          // TODO handle _notFirstTime logic
          // push replacement so pop will not go to welcome screen again
          // If not loggedin when pressing back should come back here
          Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => LoginPage()));
        },
        tooltip: 'Start',
        backgroundColor: Colors.black87,
        foregroundColor: Colors.greenAccent,
        child: Icon(Icons.play_arrow, size: 27),
      ),
    );
  }
}

class PlaceHolderRedirectScreen extends StatelessWidget {
  const PlaceHolderRedirectScreen({
    Key key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // https://stackoverflow.com/a/49967268/8608146
    // Don't use Scaffold everytime
    return Material(
      type: MaterialType.transparency,
      child: Container(
        decoration: kGradientBackground,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text("Logging in..", style: TextStyle(fontSize: 24)),
            Padding(padding: EdgeInsets.only(top: 50)),
            Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  // TODO replace this with app's logo
                  FlutterLogo(size: 50),
                  CircularProgressIndicator(
                    backgroundColor: Colors.transparent,
                    valueColor: AlwaysStoppedAnimation(Colors.black),
                  )
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
