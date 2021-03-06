import 'package:corpora/components/player.dart';
import 'package:corpora/provider/recorder.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class PlayerControls extends StatelessWidget {
  const PlayerControls({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
        width: MediaQuery.of(context).size.width / 1.5,
        child: Column(
          children: <Widget>[
            AudioPlayerWidget(
              urlPath: Provider.of<RecorderStore>(context).saveFile.path,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                FloatingActionButton(
                  elevation: 3,
                  heroTag: 'uniqu1e',
                  tooltip: "Retry Recording",
                  backgroundColor: Colors.blueGrey,
                  child: Icon(Icons.replay),
                  onPressed: () {
                    Provider.of<RecorderStore>(context, listen: false).state =
                        RecordingState.Unknown;
                  },
                ),
                // FloatingActionButton(
                //   elevation: 3,
                //   heroTag: 'uniqu2e',
                //   tooltip: "Play Recording",
                //   backgroundColor: Colors.blueGrey,
                //   child: Icon(Icons.play_arrow),
                //   onPressed: () {},
                // ),
                Padding(
                  padding: const EdgeInsets.only(left: 8.0),
                  child: RaisedButton(
                    color: Colors.blueGrey,
                    child: Text(
                      "Next",
                      semanticsLabel: "Next Recording",
                    ),
                    onPressed: Provider.of<RecorderStore>(context).next,
                  ),
                ),
              ],
            ),
          ],
        ));
  }
}

class SkipCurrent extends StatelessWidget {
  const SkipCurrent({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      child: RaisedButton(
        color: Colors.blueGrey,
        child: Text(
          'Skip',
          semanticsLabel: "Skip this Recording",
        ),
        onPressed:
            Provider.of<RecorderStore>(context, listen: false).skipScentence,
      ),
    );
  }
}
