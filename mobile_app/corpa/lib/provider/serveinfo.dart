// TODO
// This server info should be fetched from the network device discovery

/// Server details configured to my machine for now
class ServerDetails {
  static final String server = "http://192.168.43.159:3000";
  static final String fileUploadUrl = server + "/upload";
  static final String fileDownloadUrl = server + "/files";
  static final String authUrl = server + "/auth";
  static final String loginUrl = authUrl + "/login";
  static final String registerUrl = authUrl + "/new";
}
