import 'dart:async';

import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/record.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class SubmitButton extends StatefulWidget {
  const SubmitButton(this.type, {Key key}) : super(key: key);

  final AuthType type;

  @override
  _SubmitButtonState createState() => _SubmitButtonState();
}

enum ButtonState { Loading, Error, Success, Start }

class _SubmitButtonState extends State<SubmitButton> {
  ButtonState _loading = ButtonState.Start;
  bool _started = false;
  bool _errorsDissmissed = false;
  Future<AuthInfo> _future;

  @override
  void initState() {
    super.initState();

    _loading = ButtonState.Start;
  }

  /// Tries logging in
  void _startAuth() {
    if (_future == null) {
      _future = _tryAuth(context);
    }
    setState(() {
      // new button press implies retry => new errors
      _errorsDissmissed = false;
      // Set state to loading
      _loading = ButtonState.Loading;
      // when started it starts the futureBuilder
      _started = true;
    });
  }

  void _showErrors(AuthInfo info) {
    // TODO bugfix these are shown multiple times for evey build

    // If error was dissmissed don't show it again
    if (_errorsDissmissed) return;

    final snackBar = SnackBar(
      duration: Duration(seconds: 2, milliseconds: 500),
      backgroundColor: Colors.black,
      content: Text(
        info.errors.join(', '),
        style: TextStyle(color: Colors.white),
      ),
      action: SnackBarAction(
          textColor: Colors.red,
          label: "Dismiss",
          onPressed: () {
            _errorsDissmissed = true;
            Scaffold.of(context).removeCurrentSnackBar();
          }),
    );
    Scaffold.of(context).showSnackBar(snackBar);
  }

  Future<AuthInfo> _tryAuth(BuildContext context) async {
    print("Start login");
    AuthInfo info = await Provider.of<AuthStore>(context, listen: false)
        .tryAuth(type: widget.type);

    return info;
  }

  Widget get button {
    switch (_loading) {
      case ButtonState.Start:
        return Icon(Icons.arrow_forward, color: Colors.greenAccent);
        break;
      case ButtonState.Loading:
        return Container(
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(Colors.greenAccent),
              backgroundColor: Colors.black,
            ),
            constraints: BoxConstraints.tight(Size(20, 20)));
        break;
      case ButtonState.Error:
        return Icon(Icons.warning, color: Colors.orange);
        break;
      default:
        return Container();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      alignment: Alignment.bottomRight,
      height: 50,
      // constraints: BoxConstraints(maxWidth: 120),
      width: 120,
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(30),
      ),
      child: Center(
        child: FlatButton(
          onPressed: _startAuth,
          child: !_started
              ? button
              : FutureBuilder<AuthInfo>(
                  // https://stackoverflow.com/a/55626839/8608146
                  future: _future,
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      final info = snapshot.data;

                      if (info.hasErrors) {
                        WidgetsBinding.instance.scheduleFrameCallback((_) {
                          _showErrors(info);
                          setState(() {
                            _loading = ButtonState.Error;
                            // reset stuff on error
                            _started = false;
                            _future = null;
                            // hide error icon after some time
                            Timer(Duration(milliseconds: 400), () {
                              setState(() {
                                _loading = ButtonState.Start;
                              });
                            });
                          });
                        });
                      } else {
                        // Login or signup success save the info to disk
                        snapshot.data.persistLoginonDisk().whenComplete(() {
                          // https://stackoverflow.com/a/59478165/8608146
                          WidgetsBinding.instance.scheduleFrameCallback((_) {
                            Navigator.of(context).pushReplacement(
                              MaterialPageRoute(
                                builder: (context) => RecordPageProviderWrapper(
                                    info: snapshot.data),
                              ),
                            );
                          });
                        });
                      }
                    } else if (snapshot.hasError) {
                      _loading = ButtonState.Error;
                      // reset stuff
                      _started = false;
                      _future = null;
                      print(snapshot.error);
                      Timer(Duration(milliseconds: 400), () {
                        setState(() {
                          _loading = ButtonState.Start;
                        });
                      });
                    }
                    return button;
                  },
                ),
        ),
      ),
    );
  }
}
