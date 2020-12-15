import 'package:corpora/components/global.dart';
import 'package:corpora/components/input_gender.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';

import 'package:corpora/components/input_username.dart';
import 'package:corpora/components/input_age.dart';
import 'package:corpora/components/switch_screen_button.dart';
import 'package:corpora/components/submit_btn.dart';
import 'package:corpora/components/input_passwd.dart';

import 'package:provider/provider.dart' as provider;
import 'package:corpora/provider/authentication.dart';
import 'package:corpora/provider/server.dart';

class SignupPage extends StatefulWidget {
  final String serverURL;
  SignupPage({Key key, this.serverURL}) : super(key: key);
  @override
  _SignupPageState createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final _signup = Center(
      child: Text(
    "Sign Up",
    style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
  ));
  final _formFields = _FormFields();
  _Buttons _buttons;

  List<Widget> _columnChildren;
  List<Widget> _rowChildren;

  @override
  void initState() {
    super.initState();
    _buttons = _Buttons(serverURL: widget.serverURL);
    _columnChildren = <Widget>[
      // Some space only when in portrait mode
      Padding(padding: EdgeInsets.only(top: 70)),
      _signup,
      _formFields,
      // Less space when not in portrait mode
      Padding(padding: EdgeInsets.only(top: 50)),
      _buttons,
    ];
    _rowChildren = <Widget>[
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
  }

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
                // It adds padding to keep it in safearea
                // https://github.com/flutter/flutter/issues/14842#issuecomment-371344881
                padding: EdgeInsets.zero,
                children: <Widget>[
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
      ),
    );
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
      SwitchScreenButton(login: false, serverURL: widget.serverURL),
      SubmitButton(AuthType.Register),
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
              children: _children,
            ),
    );
  }
}

class _FormFields extends StatelessWidget {
  const _FormFields({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        provider.Consumer<AuthStore>(builder: (_, __, ___) => InputUsername()),
        provider.Consumer<AuthStore>(builder: (_, __, ___) => PasswordField()),
        provider.Consumer<AuthStore>(builder: (_, __, ___) => DatePicker()),
        provider.Consumer<AuthStore>(builder: (_, __, ___) => InputGender()),
      ],
    );
  }
}
