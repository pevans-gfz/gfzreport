var app = angular.module('MyApp', []);
app.controller('MyController', function ($scope, $http, $window, $timeout) {
	$scope._init = true; //basically telling setView to update the commits only the first time
	$scope._VIEWS = ['html', 'pdf'];
	$scope.view = null;  // the current view null for the moment
	$scope.lastBuildExitcode = -1; //-1: already updated (no build): 0: Ok, 1: doc created with errors, 2:doc NOT created with errors
	
	// note: needsRefresh means: false: display what's in the iframe; true: request the server 
	// (if the page has really to be refreshed - e.g.e built, is up to the server).
	// Pdfs could be quite heavy so we don't want to download them all the time
	$scope.needsRefresh = {};
	$scope.frames = {'edit': document.getElementById("edit_iframe")};

	// setting up frames and needsRefresh. The two obects above have $scope._VIEWS as keys.
	// Note that we avoid closure with forEach
	// http://stackoverflow.com/questions/750486/javascript-closure-inside-loops-simple-practical-example
	$scope._VIEWS.forEach(function(_view) {
		$scope.needsRefresh[_view] = true;
		var frame = document.getElementById(_view + "_iframe");  // e.g. 'html_iframe'
		// add listener on load complete:
		frame.onload = function() {
			$scope.$apply(function() {
				$scope.needsRefresh[_view] = false;
				$scope.loading = false;
				$scope._init = false; //if first time, notify that everything is loaded succesfully
				$scope.fetchLastBuildExitcode();
			});
		};
		$scope.frames[_view] = frame;
	});

	$scope.fetchLastBuildExitcode = function(){
		$http.post(
    		'last_build_exitcode',
    		JSON.stringify({}),  // not used
	    	{headers: { 'Content-Type': 'application/json' }}
    	).then(
			function(response){ // success callback
	    		$scope.lastBuildExitcode = parseInt(response.data);
			},
	    	function(response){ // failure callback
				$scope.lastBuildExitcode = -1;  //for safety
			}
    	);
	};
	
	$scope.loading = false;
	$scope.loadingMsgs = [];
	$scope.modified = false;
	$scope.editing = false;
	
	$scope.aceEditor = null;  //this will be set to an object after we init editing the first time
	// therefore do not bound angular properties to editor properties. For instance, if the editor wrap is on
	// the check box below:
	// <input type="checkbox" ng-checked="aceEditoraceEditor.getSession().getUseWrapMode()" ... >
	// will NOT be selected when the editor shows up.
	// What to do: bound  angular properties to $cope variables (the usual way) and update the variables
	// "manually" when the editor relative property changes. We use a dict to store these options:
	$scope.editorOptions = {wrap:false};
	$scope.toggleEdit = function(){
		$scope.editing = !$scope.editing;
		if ($scope.editing && !$scope.aceEditor){
			//$scope.loading = true;
			var iframe =  $scope.frames['edit'];
			iframe.onload= function() {
		        //$scope.loading = false;
		        $scope.aceEditor = iframe.contentWindow.editor;
		        
		        // set options:
		        // In case you want more options,type Cmd , or Ctrl ,
		        // and inspect the given element
		        // var elm = document.querySelector('#setUseWrapMode');
		        // But there are
		        // actually listeners and we use them:
		        
		        $scope.aceEditor.getSession().on("changeWrapMode", function(){
		        	// arguments[1] seems to be the aceEditor.getSession()
		        	var val = arguments[1].getUseWrapMode();
		        	console.log(val);
		        });

		        // add command to save via keybinding
		        $scope.aceEditor.commands.addCommand({
		            name: "saveContent",
		            bindKey: {win: "Ctrl-s", mac: "Command-s"},
		            exec: function(editor) {
		            	if ($scope.editing && $scope.modified){
		            		$scope.save();
		            	}
		            }
		        });
		        
	    		//add listener WHEN LOADED:
	    		$scope.aceEditor.on("input", function() {
	    			$scope.$apply(function() {
	    				// If popup commits is showing, do not mark the editor as modified
	    				// I.e., do not update save buttons and alike
	    				if ($scope.popups.commits.visible){
	    					return;
	    				}
	    				$scope.modified = true;
	    			});
	    		});
		    };
		    iframe.src = "content/edit";
		}
	};
	
	$scope.editorToggleKeyboardShortcuts = function(string){
		if ($scope.editorShowKeyboardShortcuts){
			$scope.aceEditor.execCommand("hideKeyboardShortcuts");
		}else{
			$scope.aceEditor.execCommand("showKeyboardShortcuts");
		}
		$scope.editorShowKeyboardShortcuts = !$scope.editorShowKeyboardShortcuts;
	};
	
	$scope.editorToggleSettingsMenu = function(string){
		if ($scope.editorShowSettingsMenu){
			$scope.aceEditor.execCommand("hideSettingsMenu");
		}else{
			$scope.aceEditor.execCommand("showSettingsMenu");
		}
		$scope.editorShowSettingsMenu = !$scope.editorShowSettingsMenu;
	};
	
    $scope.save = function(){
    	/**
    	 * Saves the content of the editor on the server, which returns the new commits
    	 * list. The commits list is then passed to $scope._setCommits to update what will
    	 * be shown in the 'commits popup' window
    	 */
    	if (!$scope.aceEditor){
    		return;
    	}
    	$http.post(
    		'save',
    		JSON.stringify({source_text: $scope.aceEditor.getValue() }),
	    	{headers: { 'Content-Type': 'application/json' }}
    	).then(
			function(response){ // success callback
	    		$scope.modified = false;
			  	$scope.aceEditor.session.getUndoManager().markClean();
			  	if (response.data){
			  		for (var i=0; i < $scope._VIEWS.length; i++){
			  			$scope.needsRefresh[$scope._VIEWS[i]] = true;
			  		}
			  	}
			  	//$scope._setCommits(response.data || [], true); //true: do a check to see if we need to refresh the views (pdf, html)
	    	},
	    	function(response){ // failure callback
	    		console.log("failed saving");  //FIXME: handle failure
			}
    	);
    };

    
	$scope.setView = function(view){  // value can be 'html' or 'pdf
		if($scope.loading){
			// this is very DANGEROUS: jumping clicks on the tabs while loading
			// might trigger several build for the same view (e.g., 'html') in the
			// server. So return:
			return;
		}
		if(view === $scope.view && !$scope.needsRefresh[view]){
			return;
		}
		$scope.view = view;
		if(!$scope.needsRefresh[view]){
			return;
		}
		$scope.loading = true;
		// this should update the progressbar, but it's currently not implemented:
		// $scope.startBuildingListener();
		// mark view as not dirty anymore. This is set also on iframe.onload but I stated
		// (withoyt specifying WHY) that "due to current html page view design we need to add it now"
		// (probably some angular update which otherwise needs $digest in iframe onload?)
		$scope.needsRefresh[view] = false; 
		var frame = $scope.frames[view]
		// seems that sometimes browsers have cache, so, for safety:
		var append = "?preventcache=" + Date.now()
		frame.src = "content/" + view + append;
	
		// As a remainder. If the url is already set, one could use also:
		// iframe.contentWindow.location.reload(true);
		// (http://stackoverflow.com/questions/13477451/can-i-force-a-hard-refresh-on-an-iframe-with-javascript)
	};
	
	/********************************************************************************************
	 * POPUPS STUFF 
	 ********************************************************************************************/
	
	/** first define our popup data container:
	 * we want an object type reflecting a popup, storing popup properties and that:
	 * can get if it's visible (by default it isn't) easily
	 * can toggle its visibility easily
	 * can store properties like a normal object for eg. ng-model bindings
	 * we implement the props class which will be mapped to any popup defined here:
	 */
	function props(defaults){
		// initialize by setting all our desfaults properties to this object
		var defs = defaults || {};
		for (var d in defs){
			this[d] = defs[d];
		}
		// attach common properties (for the moment, visible and errMsg)
		if (this.visible === undefined){
			this.visible = false;
		}
		if (this.errMsg === undefined){
			this.errMsg = '';
		}
		// methods:
		this.show = function(){
			// make errMsg empty, so that previous errors, if any, do not appear when window shows up (misleading)
			this.errMsg = '';
			this.visible = true;
		};
		this.hide = function(){
			this.visible = false;
		};
		this.toggle = function(){
			// call the respective functions so if there is something to setup in there, we do it
			if (this.visible){
				this.hide();
			}else{
				this.show();
			}
		};
	};
	
	$scope.popups = {
		'commits': new props({'title': 'History (git commits)', 'loading': false}),
		'logIn': new props({'title': 'Log in'}),
		'addFig': new props({'label': '', 'keepOpen': false, 'title': 'Add figure'}),
		'logs': new props({'title': 'Build log-files', 'loading': false, 'showFullLog': false})
	};	
	
	$scope.exc = function(message, response){
		/**
		 * handle http exception by returning message + response (response converted as text)
		 */
		// if there is no connection status seems to be -1 and statusText empty, so try to help:
		var status = response.status;
		var statusText = response.statusText;
		if(status == -1 && !statusText){
			statusText = "No internet connection?";
		}
		return message + " (" + status + ": " + statusText + ")";
	};
	
	/**
	 * COMMITS POPUP callback(s) and data. Commits are loaded in a $scope variable to
	 * bind them to the view, and a selIndex to bind it to color the panel of the current commit
	 * But for safety, they are loaded as new data every time we click on the commits/history button
	 */
	
	$scope.commits = {data:[], selIndex: -1};
	$scope.showCommits = function(){
		$scope.popups.commits.loading = true;
		$scope.popups.commits.show();
		$scope.commits = {data:[], selIndex: -1};
		$http.post(
			'get_commits',
			JSON.stringify({}),
			{headers: { 'Content-Type': 'application/json' }}
		).then(
    		function(response){ // success callback
    			$scope.popups.commits.loading = false;
    			$scope.commits.data = response.data || [];
    			$scope.commits.selIndex = $scope.commits.data.length ? 0 : -1; //as returned from server `git` command (0=last)
    		},
    		function(response){ // failure callback
    			$scope.popups.commits.errMsg = $scope.exc("Error", response);
    		}
	    );
	}
	
	$scope.currentCommit = function(hash){
		/**
		 * This function is executed from the view (html) in the "commits popup" div.
		 * Without argument, returns the current commit. With arguments, sets the
		 * current commit, modifying the editor test accordingly. IT IS ASSUMED THAT 
		 * showCommits HAS BEEN CALLED BEFORE THIS FUNCTION
		 */
		var cmts = $scope.commits;
		if (hash === undefined){ // called with no argument, return current commit or null
			if (!cmts.data || cmts.selIndex<0){
				return null;
			}
			return cmts.data[cmts.selIndex];
		}
		
		$http.post(
			'get_source_rst', 
	    	JSON.stringify({'commit_hash': hash}),
	    	{headers: { 'Content-Type': 'application/json' }}
    	).then(
    		function(response){ // success callback
			   $scope.aceEditor.setValue(response.data, 1);  // 1: moves cursor to the start
			   cmts.selIndex = -1;
			   for( var i=0 ;i < cmts.data.length; i++){
					if (cmts.data[i].hash == hash){
						cmts.selIndex = i;
						break;
					}
				}
    		},
    		function(response){ // failure callback
    			$scope.popups.commits.errMsg = $scope.exc(msg, response);
    		}
    	);
	}

	/**
	 * LOGIN/OUT POPUP(s) callback(s) and data
	 */

	$scope.isLoggedIn = false;
	$scope.logIn = function(){
		// create a FormData object. The FormData gets a Form html elements and will add to it
		// all inputs with a name attribute set
		var elm = document.getElementById('login');
		var formData = new FormData(elm);
		$http.post(
			'login', 
			formData,
			{headers: {'Content-Type': undefined }, transformRequest: angular.identity}  // let angular guess the type (it works!)
		).then(
    		function(response){ // success callback
    			$scope.isLoggedIn=true;
    			$scope.popups.logIn.hide();
    			//load commits now:
    			//$scope.fetchCommits();
    		},
    		function(response){ // failure callback
    			$scope.isLoggedIn=false; // for safety
    			var msg = response.statusText;
    			if (response.status == 401){
    				msg = "Email not registered."
    			}else if (response.status == 403){
    				msg = "Email registered but not authorized to access this URL.";
    			}
    			$scope.popups.logIn.errMsg = $scope.exc(msg, response);
    		}
    	);
	};

	$scope.logOut = function(){
		function doLogout(response){
			$scope.isLoggedIn = false; //should hide editor if visible
    		$scope.setView('html'); //if we are on the pdf, restore the html view. This forces a rebuild if needed
    		for(var k in $scope.popups){ //hide all popups
    			$scope.popups[k].hide();
    		}
		};
		$http.post('logout', 
			JSON.stringify({}),
	    	{headers: { 'Content-Type': 'application/json' }}
	    ).then(
    		doLogout, // success callback
    		doLogout // failure callback (there might be a way to write doLogout only once like a 'finally' clause, too lazy to search for it)
    	);
	};
	
	/**
	 * ADD FIGURE POPUP callback(s) and data
	 */
	
	$scope.addFigure = function(){
		// create a FormData object. The FormData gets a Form html elements and will add to it
		// all inputs with a name attribute set
		var elm = document.getElementById('upload-file');
		var formData = new FormData(elm);
		// BUT: from http://stackoverflow.com/questions/13963022/angularjs-how-to-implement-a-simple-file-upload-with-multipart-form
		// Angularjs (1.0.6, but apparently also 1.5.6) does not support ng-model on "input-file"
		// tags so you have to do it in
		// a "native-way" that pass the all (eventually) selected files from the user.
		var files = elm.querySelector('#flupld_').files;
		formData.append('file', files[0]);
		// post and see if it worked
		$http.post(
			'upload_file',
			formData,
			{headers: {'Content-Type': undefined }, transformRequest: angular.identity} // let angular guess the type (it works!)
	    ).then(
	    	function(response){ // success callback
	    		// $scope.aceEditor.setValue(response.data, 1);  // 1: moves cursor to the start
	    		var text = response.data;
	    		var editor = $scope.aceEditor;
	    		var edSession = editor.session;
	    		// detect position of end:
	    		var row = edSession.getLength() - 1
	    		var column = edSession.getLine(row).length // or simply Infinity
	    		edSession.insert({
	    		   row: edSession.getLength(),
	    		   column: 0
	    		}, "\n\n" + text + "\n\n");
	    		// select added text:
	    		var edSelection = editor.selection;
	    		edSelection.setSelectionAnchor(row+1, 0);
	    		var row = edSession.getLength() - 1
	    		var column = edSession.getLine(row).length // or simply Infinity
	    		edSelection.selectTo(row, column);
	    		
	    		// editor.selection.moveCursorTo(row+1, 0, false);
	    		// editor.selection.selectFileEnd();
	    		editor.renderer.scrollSelectionIntoView();
	    		
	    		if (!$scope.popups.addFig.keepOpen){
	    			$scope.popups.addFig.hide();
	    		}
	    	},
	    	function(response){ // failure callback
	    		$scope.popups.addFig.errMsg = $scope.exc("Error", response);
	    	}
	    );
	}
	
	/**
	 * LOGS POPUP callback(s) and data (note logs are the build logs (sphinx + pdflatex) not the login/out functionality!
	 * Build logs are loaded in a $scope variable to
	 * bind them to the view
	 * But for safety, they are loaded as new data every time we click on the commits/history button
	 */

	$scope.logs = {};
	$scope.showLogs = function(){
		$scope.popups.logs.loading = true;
		$scope.logs = {};
		$scope.popups.logs.show();
		$http.post(
			'get_logs', 
			JSON.stringify({'buildtype': $scope.view}),
	    	{headers: { 'Content-Type': 'application/json' }}
    	).then(
    		function(response){ // success callback
    		   // response.data is a dict
    			$scope.popups.logs.loading = false;
    			if (response.data){
    				for(var i in response.data){
    					$scope.logs[response.data[i][0]] = response.data[i][1];
    				}
    			}
    		},
    		function(response){ // failure callback
    			$scope.popups.logs.errMsg = $scope.exc("Error", response);
    		}
    	);
	}

	/**
	 * FINALLY, SETUP THE INITIAL VIEW:
	 */
	
	$scope.setView('html');

});


/* EXPERIMENTAL (not workong): show keyboard shortcuts:

$scope.toggleKeyboardShortcuts = function(){
	var editor = $scope.aceEditor;
	if(editor && $scope.editing){
		ace.config.loadModule("ace/ext/keybinding_menu", function(module) {
            module.init(editor);
            editor.showKeyboardShortcuts()
        });
	}
}


$scope.startBuildingListener = function(){
	var terminate = false;
	$scope.loadingMsgs = ['Building report (it might take few minutes)'];

    var countUp = function() {
    	$http.post(
    		'building_info',
    		JSON.stringify({}), // not used
	    	{headers: { 'Content-Type': 'application/json' }}
    	).then(
			function(response){ // success callback
				$scope.loadingMsgs = response.data;
				if ($scope.loading && !terminate){
					$timeout(countUp, 1000);
				}
				$scope.loadingMsgs = [];
	    	},
	    	function(response){ // failure callback. This is actually a safety case
	    		terminate = true;
				$scope.loadingMsgs = [];
			}
    	);
    }
	countUp();
}



// experimental: components. PLEASE REMOVE:
app.component("popup",{
	selector: '[popup]',
    template: "<button ng-click='$ctrl.showPopup=true'>{{$ctrl.name}}</button>" +
    		  "<div class='popup' ng-show='$ctrl.showPopup'><button ng-click='$ctrl.showPopup=false' class='close' data-dismiss='alert' aria-label='close'>&times;</button>" +
    		  "<div ng-transclude></div>" +
    		  "</div>",
    bindings: { name: '@', showPopup: '<' },
    transclude: true,
});
*/