import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/record.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class SubmitButton extends StatefulWidget {
  const SubmitButton(this.type, {Key key}) : super(key: key);

  final String type;

  @override
  _SubmitButtonState createState() => _SubmitButtonState();
}

enum ButtonState { Loading, Error, Success, Start }

class _SubmitButtonState extends State<SubmitButton> {
  ButtonState _loading = ButtonState.Start;
  bool _started = false;
  bool _errorsDissmissed = false;

  @override
  void initState() {
    super.initState();

    _loading = ButtonState.Start;
  }

  // TODO
  /// Tries logging in
  /// This function should be in top level
  /// Provider or bloc it
  ///
  void _startAuth() {
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
        .tryAuth(widget.type);

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

  // padding: EdgeInsets.only(
  //     top: 40, right: 50, left: MediaQuery.of(context).size.width / 2),
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
                  future: _tryAuth(context),
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      final info = snapshot.data;

                      if (info.hasErrors) {
                        _loading = ButtonState.Error;
                        WidgetsBinding.instance.addPostFrameCallback((_) {
                          _showErrors(info);
                        });
                      } else {
                        // Login or signup success save the info to disk
                        snapshot.data.persistLoginonDisk().whenComplete(() {
                          // https://stackoverflow.com/a/59478165/8608146
                          WidgetsBinding.instance.addPostFrameCallback((_) {
                            Navigator.of(context).pushReplacement(
                              MaterialPageRoute(
                                builder: (context) => RecordPage(snapshot.data),
                              ),
                            );
                          });
                        });
                      }
                    } else if (snapshot.hasError) {
                      _loading = ButtonState.Error;
                      print(snapshot.error);
                    }
                    return button;
                  },
                ),
        ),
      ),
    );
  }
}
