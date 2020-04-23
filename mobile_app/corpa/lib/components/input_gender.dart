import 'package:corpora/provider/authentication.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class InputGender extends StatefulWidget {
  @override
  _InputGenderState createState() => _InputGenderState();
}

class _InputGenderState extends State<InputGender> {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
      child: Container(
        height: 60,
        // Same width in both orientations
        width: MediaQuery.of(context).orientation == Orientation.portrait
            ? MediaQuery.of(context).size.width
            : MediaQuery.of(context).size.height,
        child: DropdownButton(
            underline: Container(
              height: 2,
              color: Colors.white30,
            ),
            value: Provider.of<AuthStore>(context).selectedGender,
            items: [
              DropdownMenuItem(child: Text("Male"), value: "m"),
              DropdownMenuItem(child: Text("Female"), value: "f"),
            ],
            onChanged: (value) {
              Provider.of<AuthStore>(context, listen: false).selectedGender =
                  value;
            }),
      ),
    );
  }
}
