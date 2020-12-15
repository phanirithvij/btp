import 'package:corpora/components/global.dart';
import 'package:corpora/screens/register.dart';
import 'package:flutter/gestures.dart';
import 'package:provider/provider.dart' as provider;
import 'package:flutter/material.dart';

import 'package:corpora/provider/server.dart';
import 'package:corpora/provider/authentication.dart';
import 'package:corpora/themes/utils.dart';

import 'package:corpora/components/input_username.dart';
import 'package:corpora/components/input_passwd.dart';
import 'package:corpora/components/submit_btn.dart';
import 'package:corpora/components/switch_screen_button.dart';

class LoginPage extends StatefulWidget {
  final String serverURL;
  LoginPage({Key key, @required this.serverURL}) : super(key: key);
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  @override
  Widget build(BuildContext context) {
    return GlobalOrientationHandler(
      child: provider.ChangeNotifierProvider(
        create: (_) => AuthStore()
          ..serverDetails = (ServerDetails()..server = widget.serverURL),
        child: Scaffold(
          body: GestureDetector(
            onTap: () {
              // https://stackoverflow.com/a/51669474/8608146
              // call this method here to hide soft keyboard
              FocusScope.of(context).requestFocus(FocusNode());
            },
            child: Container(
              decoration: kGradientBackgroundLogin,
              child: ListView(
                padding: EdgeInsets.zero,
                children: <Widget>[
                  Column(
                    children: <Widget>[
                      // Some space only when in portrait mode
                      (MediaQuery.of(context).orientation ==
                              Orientation.portrait)
                          ? Padding(padding: EdgeInsets.only(top: 70))
                          : Container(),
                      Center(
                          child: Text(
                        "Login",
                        style: TextStyle(
                            fontSize: 30, fontWeight: FontWeight.bold),
                      )),
                      _FormFields(),
                      // Less space when not in portrait mode
                      (MediaQuery.of(context).orientation ==
                              Orientation.portrait)
                          ? Padding(padding: EdgeInsets.only(top: 50))
                          : Padding(padding: EdgeInsets.only(top: 20)),
                      _Buttons(serverURL: widget.serverURL),
                      buildRichText(context),
                      Padding(padding: EdgeInsets.only(top: 50)),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget buildRichText(BuildContext context) {
    return MediaQuery.of(context).orientation == Orientation.portrait
        ? RichText(
            text: TextSpan(
              children: [
                TextSpan(
                  text: 'Create new account ? ',
                  style: TextStyle(color: Colors.black),
                ),
                TextSpan(
                  text: 'Signup',
                  style: TextStyle(color: Colors.blue),
                  recognizer: TapGestureRecognizer()
                    ..onTap = () {
                      Navigator.of(context).pushReplacement(
                        MaterialPageRoute(
                          builder: (context) =>
                              SignupPage(serverURL: widget.serverURL),
                        ),
                      );
                    },
                ),
              ],
            ),
          )
        : Container();
  }
}

class _Buttons extends StatefulWidget {
  final String serverURL;
  _Buttons({Key key, @required this.serverURL}) : super(key: key);

  @override
  __ButtonsState createState() => __ButtonsState();
}

class __ButtonsState extends State<_Buttons> {
  List<Widget> _children;
  @override
  void initState() {
    super.initState();
    _children = <Widget>[
      SwitchScreenButton(login: true, serverURL: widget.serverURL),
      SubmitButton(AuthType.Login),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 110,
      child: (MediaQuery.of(context).orientation == Orientation.portrait)
          ? Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: _children,
            )
          : Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: _children.reversed.toList(),
            ),
    );
  }
}

class _FormFields extends StatelessWidget {
  const _FormFields({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Column(
        children: <Widget>[
          provider.Consumer<AuthStore>(
              builder: (_, __, ___) => InputUsername()),
          provider.Consumer<AuthStore>(
              builder: (_, __, ___) => PasswordField()),
        ],
      ),
    );
  }
}
