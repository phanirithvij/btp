import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class GlobalOrientationHandler extends StatelessWidget {
  const GlobalOrientationHandler({
    Key key,
    @required this.child,
  }) : super(key: key);

  final Widget child;

  @override
  Widget build(BuildContext context) {
    // Hide bars when on landscape orientation
    if (MediaQuery.of(context).orientation == Orientation.portrait) {
      SystemChrome.setEnabledSystemUIOverlays(
          [SystemUiOverlay.bottom, SystemUiOverlay.top]);
    } else {
      SystemChrome.setEnabledSystemUIOverlays([]);
    }
    return child;
  }
}
