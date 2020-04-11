import 'package:flutter/material.dart';

class ButtonLogin extends StatefulWidget {
  @override
  _ButtonLoginState createState() => _ButtonLoginState();
}

enum ButtonState { Loading, Error, Success, Start }

class _ButtonLoginState extends State<ButtonLogin> {
  ButtonState _loading = ButtonState.Start;

  @override
  void initState() {
    super.initState();

    _loading = ButtonState.Start;
  }

  // TODO
  /// Tries logging in
  /// This function should be in top level
  /// Provider or bloc it
  void tryAuth(BuildContext context) {
    // Validate input fields

    // http req server for login
    setState(() {
      _loading = ButtonState.Loading;
    });
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
          onPressed: () => tryAuth(context),
          child: button,
        ),
      ),
    );
  }
}
