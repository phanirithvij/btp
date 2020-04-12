import 'package:corpora/provider/authentication.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';

import 'package:corpora/components/input_email.dart';
import 'package:corpora/components/input_age.dart';
import 'package:corpora/components/switch_screen_button.dart';
import 'package:corpora/components/submit_btn.dart';
import 'package:corpora/components/input_passwd.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

class SignupPage extends StatefulWidget {
  @override
  _SignupPageState createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  static final _signup = Center(
      child: Text(
    "Sign Up",
    style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
  ));
  static final _formFields = _FormFields();
  static final _buttons = _Buttons();

  final _columnChildren = <Widget>[
    // Some space only when in portrait mode
    Padding(padding: EdgeInsets.only(top: 70)),
    _signup,
    _formFields,
    // Less space when not in portrait mode
    Padding(padding: EdgeInsets.only(top: 50)),
    _buttons,
  ];
  final _rowChildren = <Widget>[
    Expanded(flex: 1, child: _signup),
    Expanded(
      child: _formFields,
      flex: 4,
    ),
    Expanded(
      child: _buttons,
      flex: 1,
    ),
  ];

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
              // It adds padding to keep it in safearea
              // https://github.com/flutter/flutter/issues/14842#issuecomment-371344881
              padding: EdgeInsets.zero,
              children: <Widget>[
                // TODO OrientationBuilder
                // OrientationBuilder(
                //   builder: (BuildContext context, Orientation orientation) {
                //     return Container(
                //       child: child,
                //     );
                //   },
                // ),
                LayoutBuilder(builder: (context, constraints) {
                  if (constraints.maxWidth < 600)
                    return Column(children: _columnChildren);
                  else
                    return Container(
                      height: MediaQuery.of(context).size.height,
                      child: Center(
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: _rowChildren,
                        ),
                      ),
                    );
                }),
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
    SwitchScreenButton(login: false),
    SubmitButton("signup"),
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
    return Container(
      child: Column(
        children: <Widget>[
          Consumer<AuthStore>(builder: (_, __, ___) => InputEmail()),
          Consumer<AuthStore>(builder: (_, __, ___) => DatePicker()),
          Consumer<AuthStore>(builder: (_, __, ___) => PasswordField()),
        ],
      ),
    );
  }
}
