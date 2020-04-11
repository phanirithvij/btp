import 'package:flutter/material.dart';

class PasswordField extends StatelessWidget {
  const PasswordField({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
      child: Container(
        height: 60,
        width: MediaQuery.of(context).size.width,
        child: TextField(
          style: TextStyle(
            color: Colors.black,
          ),
          obscureText: true,
          decoration: InputDecoration(
            // border: InputBorder.none,
            labelText: 'password',
            labelStyle: TextStyle(
              color: Colors.white70,
            ),
          ),
        ),
      ),
    );
  }
}
