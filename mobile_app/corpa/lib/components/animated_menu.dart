import 'dart:async';
import 'dart:math';

import 'package:corpora/provider/authentication.dart';
import 'package:corpora/screens/login.dart';
import 'package:flutter/material.dart';

class AnimatedMenu extends StatefulWidget {
  const AnimatedMenu({
    Key key,
    @required this.store,
  }) : super(key: key);

  final AuthStore store;

  @override
  _AnimatedMenuState createState() => _AnimatedMenuState();
}

class _AnimatedMenuState extends State<AnimatedMenu>
    with SingleTickerProviderStateMixin {
  AnimationController _controller;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      duration: Duration(milliseconds: 400),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MovingMenu(store: widget.store, controller: _controller);
  }
}

class MovingMenu extends StatefulWidget {
  MovingMenu({
    Key key,
    @required this.store,
    @required this.controller,
  })  : startPos = Tween<double>(
          begin: 0.0,
          end: 144.0,
        ).animate(
          CurvedAnimation(
            parent: controller,
            curve: Curves.fastOutSlowIn,
          ),
        ),
        angle = Tween<double>(
          begin: 0.0,
          end: pi,
        ).animate(
          CurvedAnimation(
            parent: controller,
            curve: Curves.fastOutSlowIn,
          ),
        ),
        super(key: key);

  final AuthStore store;
  final AnimationController controller;
  final Animation<double> startPos;
  final Animation<double> angle;

  @override
  _MovingMenuState createState() => _MovingMenuState();
}

class _MovingMenuState extends State<MovingMenu> {
  bool open = true;

  @override
  void initState() {
    super.initState();
    // Hide the menu initially after some time
    Timer(Duration(seconds: 2, milliseconds: 300), () {
      _close();
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(widget.startPos.value, 0),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                bottomLeft: Radius.circular(20),
              ),
              color: Colors.blueGrey.withOpacity(0.6),
            ),
            child: Row(
              children: <Widget>[
                Transform.rotate(
                  angle: widget.angle.value,
                  child: IconButton(
                      icon: Icon(Icons.chevron_right),
                      onPressed: () {
                        open ? _close() : _open();
                      }),
                ),
                IconButton(
                    icon: Icon(Icons.power_settings_new),
                    onPressed: () {
                      widget.store.logout();
                      // redirect to login screen
                      Navigator.of(context).pushReplacement(
                        MaterialPageRoute(builder: (_) => LoginPage()),
                      );
                    }),
                IconButton(
                  icon: Icon(Icons.settings),
                  onPressed: () {},
                ),
                IconButton(icon: Icon(Icons.account_circle), onPressed: () {}),
              ],
            ),
          ),
        );
      },
    );
  }

  void _open() {
    widget.controller.reverse();
    open = true;
    // no need to re build so no setstate
  }

  void _close() {
    widget.controller.forward();
    open = false;
    // no need to re build so no setstate
  }
}
