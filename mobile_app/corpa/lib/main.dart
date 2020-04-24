import 'package:corpora/components/global.dart';
import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/record.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';
import 'package:corpora/screens/login.dart';
import 'package:permission_handler/permission_handler.dart';

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
    // TODO add routes here
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Corpora Collector",
      theme: kAmoledTheme,
      home: GlobalOrientationHandler(child: HomePage()),
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
    print(info);
    var loggedin = await store.isLoggedin;
    setState(() {
      print("Loggedin $loggedin");
      isLoggedin = loggedin;
      _fecthed = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    // If we have not fetched the auth info yet show a trying to login screen
    if (!_fecthed) return PlaceHolderRedirectScreen();

    if (isLoggedin) {
      // redirect to record page
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => RecordPageProviderWrapper(info: info),
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
class WelcomePage extends StatefulWidget {
  const WelcomePage({
    Key key,
  }) : super(key: key);

  @override
  _WelcomePageState createState() => _WelcomePageState();
}

class _WelcomePageState extends State<WelcomePage> {
  bool _permissionsGranted = false;

  @override
  void initState() {
    super.initState();

    _asyncInitState();
  }

  void _asyncInitState() async {
    var status = await Permission.speech.status;
    if (status.isGranted) {
      print("isGranted");
      setState(() {
        _permissionsGranted = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SizedBox.expand(
        child: Container(
          decoration: kGradientBackground,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text(
                "Welcome to corpora collector!",
                style: TextStyle(fontSize: 24),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 40.0),
                child: Text(
                  _permissionsGranted
                      ? "The required permissions were"
                      : "The app requires some permissions",
                  style: TextStyle(fontSize: 20),
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 30.0),
                child: RaisedButton(
                  color: _permissionsGranted ? Colors.green : Colors.blueGrey,
                  onPressed: _requestPermissions,
                  child: Text(
                    _permissionsGranted ? "Granted" : "Grant",
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: _permissionsGranted
          ? FloatingActionButton(
              onPressed: () {
                // TODO handle _notFirstTime logic
                // push replacement so pop will not go to welcome screen again
                // If not loggedin when pressing back should come back here
                Navigator.of(context).pushReplacement(MaterialPageRoute(
                  builder: (context) => LoginPage(),
                ));
              },
              tooltip: 'Start',
              backgroundColor: Colors.black87,
              foregroundColor: Colors.greenAccent,
              child: Icon(Icons.play_arrow, size: 27),
            )
          : Container(),
    );
  }

  void _requestPermissions() async {
    var status = await Permission.speech.status;
    if (status.isUndetermined) {
      // We didn't ask for permission yet.
      if (await Permission.speech.isRestricted) {
        return;
      }

      final _req = await Permission.speech.request();
      if (_req.isGranted) {
        // Either the permission was already granted before or the user just granted it.
        setState(() {
          _permissionsGranted = true;
        });
      }
    }
    if (status.isDenied) {
      final _req = await Permission.speech.request();
      if (_req.isGranted) {
        // Either the permission was already granted before or the user just granted it.
        setState(() {
          _permissionsGranted = true;
        });
      }
    }
    if (await Permission.speech.isPermanentlyDenied) {
      openAppSettings();
    }
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
