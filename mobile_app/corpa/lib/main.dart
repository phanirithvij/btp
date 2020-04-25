import 'package:corpora/components/global.dart';
import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/record.dart';
import 'package:corpora/screens/redirect.dart';
import 'package:corpora/screens/welcome.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';

void main() => runApp(CorporaApp());

class CorporaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // TODO add routes here

    // TODO fix input_data

    // TODO fix login/signup layout in big tablets
    // Login / -> buttons should use layout builder instead of orientation

    // TODO request permissions before audio record
    // Needed as the user can still disable permissions after login

    // return DevicePreview(
    // builder: (context) =>
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Corpora Collector",
      theme: kAmoledTheme,
      home: GlobalOrientationHandler(child: HomePage()),
      // ),
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
