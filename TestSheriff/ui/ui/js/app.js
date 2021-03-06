var url = window.location.href.replace(/\/$/, '');

host = url.substr(0, url.search('/ui') + 1);
root = 'api/v1/';

nb_item = 15;

(function() {

  var app = angular.module('statuses', ['infinite-scroll', 'ui.bootstrap']);

  app.controller('last_statuses', [ '$http', '$modal', '$anchorScroll', '$interval', function($http, $modal, $anchorScroll, $interval){

    var self = this;
    this.statuses = [];
    this.filter = false;
    this.continuous = false;
    this.continuous_interval = false
    this.next_page = "";
    this.loaded_pages = [];

    this.get_last = function() {
      this.filter = false;
      this.get_last_filtered()
    };

    this.continuous_refresh = function() {
      if (this.continuous) {
        this.continuous_interval = $interval(this.get_last_filtered, 2000);
      } else {
        $interval.cancel(this.continuous_interval);
      }
    };

    this.get_last_filtered = function() {
      var filter_query = '';
      var i_field = 1;
      for (var key in self.filter) {
        if (self.filter[key]['enabled']) {
          if (self.filter[key]['is_details']) {
            filter_query += '&field' + i_field + '=' + key + '&value' + i_field + '=' + self.filter[key]['value'];
            i_field++;
          } else {
            filter_query += '&' + key + '=' + self.filter[key]['value'];
          }
        }
      }
      self.loaded_pages = [];
      $anchorScroll();
      $http.get(host + root + 'statuses?nb_status=' + nb_item + filter_query)
      .success(function(data){
        self.statuses = data.statuses;
        if (data['pagination'] && data['pagination']['next']) {
          self.next_page = data['pagination']['next']['href'];
        } else {
          self.next_page = "";
        }
        self.get_next_page();
      });
    };

    this.get_next_page = function() {
      var next_page = self.next_page;
      if ((next_page != "") && (self.loaded_pages.indexOf(next_page) == -1)) {
        this.loaded_pages.push(next_page);
        $http.get(self.next_page)
        .success(function(data){
          Array.prototype.push.apply(self.statuses, data.statuses);
          if (data['pagination'] && data['pagination']['next']) {
            self.next_page = data['pagination']['next']['href'];
          } else {
            self.next_page = "";
          }
        });
      }
    };

    this.add_filter = function(key, value, is_details) {
      if (!this.filter)
        this.filter = {};
      this.filter[key] = {value: value, is_details: is_details, enabled: true};
      this.get_last_filtered();
    };

    this.toggle_filter = function(key) {
      if (this.filter[key]['value'].substring(0, 1) == '!') {
        this.filter[key]['enabled'] = false;
        this.filter[key]['value'] = this.filter[key]['value'].substring(1);
      } else if (this.filter[key]['enabled']) {
        this.filter[key]['value'] = '!' + this.filter[key]['value'];
      } else {
        this.filter[key]['enabled'] = true;
      }
      this.get_last_filtered()
    };

    this.add_filter_open = function() {
      var modalInstance = $modal.open({
        templateUrl: 'AddFilter.html',
        controller: 'AddFilter'
      });
      modalInstance.result.then(function (filter) {
        var is_details = false;
        if (['status', 'test_id', 'type'].indexOf(filter['field']) == -1) { is_details = true; }
        if (filter['field'] != "") {
          self.add_filter(filter['field'], filter['value'], is_details);
        }
      });
    };

    this.remove_status = function(status) {
      $http.delete(status['_links']['self']['href']);
      self.get_last_filtered();
    };

  }]);


  app.controller('AddFilter', ['$scope', '$modalInstance', function ($scope, $modalInstance) {

    $scope.field = "";
    $scope.value = "";

    $scope.ok = function () {
      $modalInstance.close({field: $scope.field, value: $scope.value});
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  }]);

})();
