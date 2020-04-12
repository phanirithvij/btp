import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:flutter/material.dart';

import 'package:corpora/provider/authentication.dart';
import 'package:corpora/themes/utils.dart';

import 'package:corpora/components/input_email.dart';
import 'package:corpora/components/input_passwd.dart';
import 'package:corpora/components/submit_btn.dart';
import 'package:corpora/components/switch_screen_button.dart';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthStore(),
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
                    (MediaQuery.of(context).orientation == Orientation.portrait)
                        ? Padding(padding: EdgeInsets.only(top: 70))
                        : Container(),
                    Center(
                        child: Text(
                      "Login",
                      style:
                          TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                    )),
                    _FormFields(),
                    // Less space when not in portrait mode
                    (MediaQuery.of(context).orientation == Orientation.portrait)
                        ? Padding(padding: EdgeInsets.only(top: 50))
                        : Padding(padding: EdgeInsets.only(top: 20)),
                    _Buttons(),
                    Padding(padding: EdgeInsets.only(top: 50)),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Buttons extends StatelessWidget {
  _Buttons({Key key}) : super(key: key);

  final _children = <Widget>[
    SwitchScreenButton(login: true),
    SubmitButton("login"),
  ];

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
              children: _children,
            ),
    );
  }
}

class _FormFields extends StatelessWidget {
  const _FormFields({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // TODO should be global
    if (MediaQuery.of(context).orientation == Orientation.portrait) {
      SystemChrome.setEnabledSystemUIOverlays(
          [SystemUiOverlay.bottom, SystemUiOverlay.top]);
    } else {
      SystemChrome.setEnabledSystemUIOverlays([]);
    }

    return Container(
      child: Column(
        children: <Widget>[
          Consumer<AuthStore>(builder: (_, __, ___) => InputEmail()),
          Consumer<AuthStore>(builder: (_, __, ___) => PasswordField()),
        ],
      ),
    );
  }
}
