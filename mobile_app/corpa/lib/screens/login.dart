import 'package:corpora/components/change_screen_button.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';

import 'package:corpora/components/input_email.dart';
import 'package:corpora/components/input_passwd.dart';
import 'package:corpora/components/login_button.dart';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GestureDetector(
        onTap: () {
          // https://stackoverflow.com/a/51669474/8608146
          // call this method here to hide soft keyboard
          FocusScope.of(context).requestFocus(FocusNode());
        },
        child: Container(
          decoration: kGradientBackgroundLogin,
          child: ListView(
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
                    style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                  )),
                  InputEmail(),
                  PasswordField(),
                  // Less space when not in portrait mode
                  (MediaQuery.of(context).orientation == Orientation.portrait)
                      ? Padding(padding: EdgeInsets.only(top: 50))
                      : Padding(padding: EdgeInsets.only(top: 20)),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: <Widget>[
                      ChangeScreenButton(login: true),
                      ButtonLogin(),
                    ],
                  ),
                  Padding(padding: EdgeInsets.only(top: 50)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
