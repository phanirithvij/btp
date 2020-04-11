import 'package:corpora/screens/login.dart';
import 'package:corpora/screens/register.dart';
import 'package:flutter/material.dart';

class ChangeScreenButton extends StatelessWidget {
  const ChangeScreenButton({Key key, this.login = true}) : super(key: key);

  final login;

  @override
  Widget build(BuildContext context) {
    return Container(
      alignment: Alignment.bottomRight,
      height: 50,
      width: 120,
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(30),
      ),
      child: FlatButton(
        onPressed: () {
          // Switch Screen
          // Navigator.of(context).pop();
          // Navigator.of(context).pushReplacement(newRoute)
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(
              builder: (context) => login ? SignupPage() : LoginPage(),
            ),
          );
        },
        child: Center(
          child: Text(
            // [Login|Signup]
            login ? 'SIGN UP' : 'LOGIN',
            style: TextStyle(
              color: Colors.greenAccent,
              fontSize: 14,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}
