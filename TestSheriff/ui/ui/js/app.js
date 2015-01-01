var host = window.location.href.replace(/\/$/, '');
host = host.substr(0, host.search('/ui') + 1);
root = 'api/v1/';


(function() {

  var app = angular.module('statuses', []);

  app.controller('last_statuses', [ '$http', function($http){

    var self = this;
    this.statuses = [];

    this.get_last = function() {
      $http.get(host + root + 'statuses')
      .success(function(data){
        self.statuses = data.statuses
      });
    };

  }])

})();
