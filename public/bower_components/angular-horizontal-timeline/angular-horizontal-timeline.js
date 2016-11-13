/**
 * Angular JS horizontal timeline
 *
 * (c) eowo
 * http://github.com/eowo/angularjs-horizontal-timeline
 *
 * Version: v0.0.1
 *
 * Licensed under the MIT license
 */

var template =
'<ul class="timeline" id="timeline">'+
'<li class="li{{event.css}}" ng-repeat="event in events">'+
'<div class="timestamp">'+
'<span class="date">{{event.date}}<span>'+
'</div>'+
'<div class="status">'+
'<h4> {{event.content|unsafe}} </h4>'
'</div>'+
'</li></ul>';

angular.module('angular-horizontal-timeline', [])

.filter('unsafe', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
})

.directive('horizontalTimeline', function(){
	function controller($scope){
            console.log("test");
            /*
		for(var i=0;i<$scope.events.length;i++) {
			if (moment($scope.events[i].date) < moment()) {
				$scope.events[i].css = " complete";
			} else {
				$scope.events[i].css = "";
			}
			console.log($scope.events[i].css);
		}*/
	}

	return {
		restrict: 'AEC',
		/*controller: controller,*/
		scope: {
			events: '='
		},
		template:template
	};
});