import 'package:corpora/provider/authentication.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class InputUsername extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 50, left: 50, right: 50),
      child: Container(
        height: 60,
        // Same width in both orientations
        width: MediaQuery.of(context).orientation == Orientation.portrait
            ? MediaQuery.of(context).size.width
            : MediaQuery.of(context).size.height,
        child: TextField(
          controller: Provider.of<AuthStore>(context).usernameController,
          style: TextStyle(
            color: Colors.white,
          ),
          decoration: InputDecoration(
            // helperText: "Input",
            fillColor: Colors.lightBlueAccent,
            labelText: 'username',
            labelStyle: TextStyle(
              color: Colors.white70,
            ),
          ),
        ),
      ),
    );
  }
}
