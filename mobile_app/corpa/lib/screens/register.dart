import 'package:corpora/provider/authentication.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';

import 'package:corpora/components/input_email.dart';
import 'package:corpora/components/input_age.dart';
import 'package:corpora/components/switch_screen_button.dart';
import 'package:corpora/components/submit_btn.dart';
import 'package:corpora/components/input_passwd.dart';
import 'package:provider/provider.dart';

class SignupPage extends StatefulWidget {
  @override
  _SignupPageState createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
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
              children: <Widget>[
                Column(
                  children: <Widget>[
                    // Some space only when in portrait mode
                    (MediaQuery.of(context).orientation == Orientation.portrait)
                        ? Padding(padding: EdgeInsets.only(top: 70))
                        : Container(),
                    Center(
                        child: Text(
                      "Sign Up",
                      style:
                          TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                    )),
                    Consumer<AuthStore>(builder: (_, __, ___) => InputEmail()),
                    Consumer<AuthStore>(builder: (_, __, ___) => DatePicker()),
                    Consumer<AuthStore>(
                        builder: (_, __, ___) => PasswordField()),
                    // Less space when not in portrait mode
                    (MediaQuery.of(context).orientation == Orientation.portrait)
                        ? Padding(padding: EdgeInsets.only(top: 50))
                        : Padding(padding: EdgeInsets.only(top: 20)),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: <Widget>[
                        SwitchScreenButton(login: false),
                        SubmitButton("signup"),
                      ],
                    ),
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
