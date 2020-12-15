import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/record.dart';
import 'package:corpora/screens/redirect.dart';
import 'package:corpora/screens/login.dart';
import 'package:flutter/material.dart';
import 'package:corpora/provider/server.dart';

class ServerCard extends StatelessWidget {
  final ServerObj sobj;
  ServerCard({Key key, final this.sobj}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          ListTile(
            leading: Icon(Icons.album),
            title: Text(sobj.name),
            subtitle: Text(sobj.description),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: <Widget>[
              TextButton(
                child: const Text('View'),
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => HomePage(
                        serverURL: sobj.server,
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  final String serverURL;
  HomePage({Key key, this.serverURL}) : super(key: key);

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
    store = AuthStore()
      ..serverDetails = (ServerDetails()..server = widget.serverURL);
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
      info.serverDetails = store.serverDetails;
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
      return LoginPage(serverURL: widget.serverURL);
  }
}
