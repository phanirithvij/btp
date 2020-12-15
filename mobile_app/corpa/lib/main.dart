import 'package:corpora/components/global.dart';
import 'package:corpora/screens/public.dart';
import 'package:corpora/screens/welcome.dart';
import 'package:flutter/material.dart';

import 'package:corpora/themes/utils.dart';

void main() => runApp(CorporaApp());

class CorporaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // TODO add routes here

    // TODO fix input_data

    // TODO fix login/signup layout in big tablets
    // Login / -> buttons should use layout builder instead of orientation

    // TODO request permissions before audio record
    // Needed as the user can still disable permissions after login

    // return DevicePreview(
    // builder: (context) =>
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Corpora Collector",
      theme: kAmoledTheme,
      home: GlobalOrientationHandler(child: WelcomePage()),
      // ),
    );
  }
}
