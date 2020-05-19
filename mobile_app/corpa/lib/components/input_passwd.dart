import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:corpora/provider/authentication.dart';

class PasswordField extends StatefulWidget {
  const PasswordField({Key key}) : super(key: key);

  @override
  _PasswordFieldState createState() => _PasswordFieldState();
}

class _PasswordFieldState extends State<PasswordField> {
  bool _obscure = true;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
      child: Container(
        height: 60,
        width: (MediaQuery.of(context).orientation == Orientation.portrait
            ? MediaQuery.of(context).size.width
            : MediaQuery.of(context).size.height),
        child: TextField(
          controller: Provider.of<AuthStore>(context).passwordController,
          style: TextStyle(
            color: Colors.black,
          ),
          obscureText: _obscure,
          decoration: InputDecoration(
            // border: InputBorder.none,
            labelText: 'password',
            labelStyle: TextStyle(
              color: Colors.white70,
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _obscure ? Icons.remove_red_eye : Icons.panorama_fish_eye,
              ),
              onPressed: () {
                setState(() {
                  _obscure = !_obscure;
                  Timer(Duration(milliseconds: 1200), () {
                    _obscure = true;
                    setState(() {});
                  });
                });
              },
            ),
          ),
        ),
      ),
    );
  }
}
