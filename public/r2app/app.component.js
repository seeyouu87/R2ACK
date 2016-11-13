boApp.controller('SettingCtrl',
['$scope', '$timeout', '$mdSidenav', '$log', 
function ($scope)
{
    $scope.params = {
        menu: {
            sections: [{
                name: "Client",
                url: "#!/client"
            }, {
                name: "Portfolio Risk",
                url: "#!/portfolio"
            }, {
                name: "Recommendation",
                url: "#!/risk"
            }]
        },
        toolbarTitle: "R2ACK Dashboard",
        titleTag: "R2ACK"
    };
}]);//end of NavCtrl

boApp.controller('ClientView',
['$scope', '$location', 'clients',"NgTableParams",
 function ($scope, $location, clients,NgTableParams)
{

    var self = this;

    /* default data loader while launching */
    self.tableParams = new NgTableParams();
    self.tableParams.settings({
              dataset:clients
            });
    $scope.browse=function(id){
        $location.path("/clidet/"+id);
    }
}]);//end of ClientView

boApp.controller('ClientDetail',
['$scope', '$http', '$location', 'clients',"NgTableParams",
 '$filter', '$timeout', '$mdSidenav', '$log','$routeParams', '$cookies','$mdDialog',
 function ($scope, $http, $location, clients,NgTableParams,$filter,
 $timeout, $mdSidenav, $log,$routeParams,$cookies,$mdDialog)
{

    var self = this;
    $scope.portfolio=[];
    $scope.data = [];
    
    $scope.clientId = $routeParams.cliId
    angular.forEach(clients,function(val, key){
        if(val.clientId==$scope.clientId){
            $scope.data = val;
            console.log($scope.data);
        }
    });

    $scope.retrievePortfolio=function(custid){
           alert = $mdDialog.alert({
            template: '<md-dialog aria-label="List dialog">' +
            '<md-toolbar>'+
              '<div class="md-toolbar-tools">'+
                '<h2>Loading Real Time Portfolio Data</h2>'+
              '</div>'+
            '</md-toolbar>'+
           '  <md-dialog-content>'+
           '<img style="margin-left:60px" id="loader" src="public/img/watson.gif" />' +
           '  </md-dialog-content>' +
           '</md-dialog>',
            ok: 'Close'
          });
      $mdDialog
        .show( alert )
        .finally(function() {
          alert = undefined;
        });
        $http.get("/portfolio/"+custid).success(
            function(data,status){
                $scope.portfolio = data;
                $scope.portfolioTotal = parseFloat(data.cash) + parseFloat(data.bond) + parseFloat(data.stock);
                $mdDialog.hide();
            }
        ).error(function (data, status) {
            console.log(status+" error!");
        });
        ;
    };
    $scope.showAlert = function(ev, bio) {
        // Appending dialog to document.body to cover sidenav in docs app
        // Modal dialogs should fully cover application
        // to prevent interaction outside of dialog
        $mdDialog.show({
          controller: DialogController,
          templateUrl: 'public/r2app/partial/dialog1.tmpl.html',
          locals: {
           bio: bio
          },
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
        })
        .then(function(answer) {
          $scope.status = 'You said the information was "' + answer + '".';
        }, function() {
          $scope.status = 'You cancelled the dialog.';
        });
      };

      function DialogController($scope, $mdDialog, $http,bio) {
          $http.post('/personal', bio).success(
              function (data, status) {
                  $("#loader").hide();
                   $("#personalityRes").show();
                  $scope.big5 = data.tree.children[0].children[0].children;
                })
                .error(function (data, status) {
                    console.log(status+" error!");
                });
        $scope.hide = function() {
          $mdDialog.hide();
        };

        $scope.cancel = function() {
          $mdDialog.cancel();
        };

        $scope.answer = function(answer) {
          $mdDialog.hide(answer);
        };
      }
}]);//end of ClientDetail

//portfolio tab
boApp.controller('Portfolio',
['$scope', '$location', 'clients',"NgTableParams",
 function ($scope, $location, clients,NgTableParams)
{

    var self = this;

    /* default data loader while launching */
    self.tableParams = new NgTableParams();
    self.tableParams.settings({
              dataset:clients
            });

}]);//end of Portfolio controller
//risk page
boApp.controller('Risk',
['$scope', '$http','$location', 'clients',"NgTableParams",
 function ($scope,$http, $location, clients,NgTableParams)
{

    var self = this;
    $scope.recommend =[];
    /* default data loader while launching */
    self.tableParams = new NgTableParams();
    self.tableParams.settings({
              dataset:clients
            });
$scope.getRecommendation=function(){
            $http.post('/',{}).success(function(data,status){
                angular.forEach(data,function(val, key){
                    $scope.recommend.push(val);
                });
            }).error(function (data, status) {
                console.log(status+" error!");
            });
    };
}]);//end of Risk View