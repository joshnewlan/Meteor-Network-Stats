NetInfo = new Mongo.Collection("networking");
var pythonPath = "/path/to/bin/python";
var scriptPath = "/path/to/nettop.py";

var bytesToSize = function (bytes) {
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
   bytes = parseInt(bytes);
   if (bytes == 0) return '0 Bytes';
   var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
   return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
};

if (Meteor.isClient) {
  Template.netinfo.helpers({
    netInfo: function () {
      
      var netInfo = [];
      // Meteor's mongodb api doesn't seem to support deduping, so I'll list some interfaces manually. 
      // Otherwise I would do something like:
      // NetInfo.find({}).distinct(ifname) and get an array of ifnames
      var ifaces = ['all','en0','en1','en2','lo0','bridge0','p2p0','awd10'];
      for (var i in ifaces) {
        var ifaceName = ifaces[i];
        ifInfo = NetInfo.find({ifname: ifaceName}, {sort: {timestamp: -1}, limit: 2}).fetch();
        
        if (ifInfo.length > 1){
          var info = {};
          info.ifname = ifaceName;
          info.sent = bytesToSize(ifInfo[0].bytes_sent);
          info.receieved = bytesToSize(ifInfo[0].bytes_received);
          info.sentRate = bytesToSize((ifInfo[0].bytes_sent - ifInfo[1].bytes_sent));
          info.recvRate = bytesToSize((ifInfo[0].bytes_received - ifInfo[1].bytes_received));
          netInfo.push(info);
        }
      }
      return netInfo;
    }
  });
}

if (Meteor.isServer) {
  Meteor.startup(function () {
    // Run a network info python psutil script as a subprocess
    var spawn = Npm.require('child_process').spawn;
    var child = spawn(pythonPath, ['-u',scriptPath]);
    child.stdout.pipe(process.stdout);
    child.stderr.pipe(process.stderr);
    
    console.log("Python client started, pid: " + child.pid);
  });
}
