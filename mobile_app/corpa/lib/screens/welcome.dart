import 'package:corpora/screens/login.dart';
import 'package:corpora/screens/public.dart';
import 'package:corpora/screens/register.dart';
import 'package:corpora/themes/utils.dart';
import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';

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
              Padding(padding: EdgeInsets.only(top: 50)),
              _permissionsGranted
                  ? RaisedButton(
                      child: Text("Next"),
                      onPressed: () {
                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(
                            builder: (context) => PublicServersHome(),
                          ),
                        );
                      },
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.all(Radius.circular(200)),
                      ),
                      color: Colors.green.shade700,
                    )
                  : Container(),
              // buildButtonBar(context),
            ],
          ),
        ),
      ),

      // floatingActionButton: _permissionsGranted
      //     ? FloatingActionButton(
      //         onPressed: () {
      //           // TODO handle _notFirstTime logic
      //           // push replacement so pop will not go to welcome screen again
      //           // If not loggedin when pressing back should come back here
      //           Navigator.of(context).pushReplacement(MaterialPageRoute(
      //             builder: (context) => LoginPage(),
      //           ));
      //         },
      //         tooltip: 'Start',
      //         backgroundColor: Colors.black87,
      //         foregroundColor: Colors.greenAccent,
      //         child: Icon(Icons.play_arrow, size: 27),
      //       )
      //     : Container(),
    );
  }

  Widget buildButtonBar(BuildContext context) {
    return _permissionsGranted
        ? ButtonBar(
            buttonPadding: const EdgeInsets.only(),
            alignment: MainAxisAlignment.center,
            children: <Widget>[
              ButtonTheme(
                minWidth: 100.0,
                height: 50.0,
                child: RaisedButton(
                  onPressed: () {
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(
                        builder: (context) => LoginPage(),
                      ),
                    );
                  },
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(200),
                        bottomLeft: Radius.circular(200)),
                  ),
                  color: Colors.blueGrey.shade600,
                  child: Text(
                    "Login",
                    style: TextStyle(fontSize: 20),
                  ),
                ),
              ),
              ButtonTheme(
                minWidth: 100.0,
                height: 50.0,
                child: RaisedButton(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.only(
                        topRight: Radius.circular(200),
                        bottomRight: Radius.circular(200)),
                  ),
                  color: Colors.green.shade700,
                  onPressed: () {
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(
                        builder: (context) => SignupPage(),
                      ),
                    );
                  },
                  child: Text(
                    "Signup",
                    style: TextStyle(fontSize: 20),
                  ),
                ),
              ),
            ],
          )
        : Container();
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
