import 'package:corpora/components/server_card.dart';
import 'package:corpora/provider/server.dart';
import 'package:corpora/themes/utils.dart';
import 'package:flutter/material.dart';

class PublicServersHome extends StatefulWidget {
  const PublicServersHome({
    Key key,
  }) : super(key: key);

  @override
  _PublicServersHomeState createState() => _PublicServersHomeState();
}

class _PublicServersHomeState extends State<PublicServersHome> {
  List<ServerObj> _servers = [];

  @override
  void initState() {
    // TODO: implement initState
    asyncInitState();
    super.initState();
  }

  void asyncInitState() async {
    _servers = await ServerUtils.getPublicServers();
    setState(() {});
  }

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
          children: _servers.length > 0
              ? _servers.map((s) => ServerCard(sobj: s)).toList()
              : [CircularProgressIndicator()],
        ),
      ),
    );
  }
}
