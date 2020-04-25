import 'package:corpora/themes/utils.dart';
import 'package:flutter/material.dart';

class PlaceHolderRedirectScreen extends StatelessWidget {
  const PlaceHolderRedirectScreen({
    Key key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // https://stackoverflow.com/a/49967268/8608146
    // Don't use Scaffold everytime
    return Material(
      type: MaterialType.transparency,
      child: Container(
        decoration: kGradientBackground,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text("Logging in..", style: TextStyle(fontSize: 24)),
            Padding(padding: EdgeInsets.only(top: 50)),
            Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  // TODO replace this with app's logo
                  FlutterLogo(size: 50),
                  CircularProgressIndicator(
                    backgroundColor: Colors.transparent,
                    valueColor: AlwaysStoppedAnimation(Colors.black),
                  )
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
