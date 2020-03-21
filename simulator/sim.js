NUM_PEOPLE = 10000; // Number of people
NUM_DAYS = 100 //Number of days
INIT_NUM_INFECTED = 100; // Initial number of people infected
VIRUS_TRANSMISSION_DIST = 100; // Cut off distance (in meters) below which virus transmission might occur
VIRUS_TRANSMISSION_PROB = 0.5; // If within the cut-off distance, transmission probability
DAYS_TO_RECOVER = 10; // After being infected, how many days to recover (assumed infectious during this phase and that no one dies).
PEOPLE_VELOCITY = 10; // Velocity with which people move (in meter/sec). Reduce this to show impact of social distancing.
N_BLOCKS = 50; // Divide city into NxN blocks and look for collision only in adjacent blocks to speed up computation.
NUM_HOMES = 2;
NUM_WORKPLACES = 2;
NUM_COMMUNITIES = 2;

// bounding box around Blore (approx)
MIN_LAT = 12.85
MAX_LAT = 13.15
MIN_LONG = 77.45
MAX_LONG = 77.75

// Beta values
BETA_H = 1
BETA_W = 1
BETA_C = 1
ALPHA = 0.8

function init_nodes() {
	var nodes = [];
	for(var i = 0; i < NUM_PEOPLE; i++) {
	    var node = {
			'index': i,
			'loc': [MIN_LAT + (MAX_LAT - MIN_LAT)*Math.random(), MIN_LONG + (MAX_LONG - MIN_LONG)*Math.random()], // [lat, long]
			'direction': [Math.random(), Math.random()],
			'age': Math.floor(Math.random() * 100),
			'zeta_a': 1,
			'infectiousness': 1, // a.k.a. rho
			'severity': 0, // a.k.a. S_k
			'home': Math.floor(Math.random() * NUM_HOMES), 
			'workplace': Math.floor(Math.random() * NUM_WORKPLACES),
			'community': Math.floor(Math.random() * NUM_COMMUNITIES),
			'time_of_infection': 0,
			'infection_status': 0,
			'lambda_h': 0,
			'lambda_w': 0,
			'lambda_c': 0,
			'lambda': 0,
			'kappa_T': 0,
			'psi_T': 0,
			'funct_d_ck': Math.random(), // function of distance from community...
			'workplace_type': Math.floor(Math.random() * 2) //either school or office
	    };
	    nodes.push(node)
	}
	return nodes;
}

function kappa_T(node, cur_time){

	//Need to compute thresholds based on simulation timesteps
	var threshold1 = 4.5 //TODO: Need to compute appropriate thresholds.
	var threshold2 = 5
	var threshold3 = 10	
	if(node["infection_status"]!=1){
		return 0;
	}
	else {
		var time_since_infection = cur_time - node["time_of_infection"];
		if(time_since_infection < threshold1 || time_since_infection > threshold3) { return 0;}
		else if(time_since_infection < threshold2) {return 1;}
		else if(time_since_infection < threshold3) {return 1.5;}
		else return 0;
	}	
	////return 1; // Add kappa function... 1) less than 4.5, 0 2) 4.5 to 5, 1 3) 5 to 10, 1.5  4) 0 afterwards
}

function psi_T(node, cur_time){
	if(node["infection_status"]!=1){ //check if not infectious
		return 0;
	}
	var PSI_THRESHOLD = 1; //TODO: Need to be computed as a function of simulation time step	
	var time_since_infection = cur_time - node["time_of_infection"];
	var scale_factor = 0.5; 
	if(node['workplace_type']==0) {scale_factor = 0.1} //school
	else if(node['workplace_type']==1) {scale_factor = 0.5} //office
	if(time_since_infection < PSI_THRESHOLD){ return 0;}
	else {return scale_factor;}	
	
	
	return 0.5; // Add psi function... 1) if infected, 0 then constant based on school or workplace... 
}

function get_individuals_at_home(nodes, h){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes[i]['home']==h){
			individuals.push(nodes[i]['index'])
		}
	}
	return individuals;
}

function get_individuals_at_workplace(nodes, w){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes[i]['workplace']==w){
			individuals.push(nodes[i]['index'])
		}
	}
	return individuals;
}

function get_individuals_at_community(nodes, c){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes[i]['community']==c){
			individuals.push(nodes[i]['index'])
		}
	}
	return individuals;
}

function init_workplaces(nodes){
	var workplaces = [];
	for (var w=0; w < NUM_WORKPLACES; w++) {
		var workplace = {
			'index': w,
			'loc': [MIN_LAT + (MAX_LAT - MIN_LAT)*Math.random(), MIN_LONG + (MAX_LONG - MIN_LONG)*Math.random()],
			'lambda_workplace': 0, 
			'individuals': get_individuals_at_workplace(nodes, w), // Populate with individuals in same workplace
			'Q_w': 1,
			'scale': 0
		};
		workplace['scale'] = BETA_W*workplace['Q_w']/workplace['individuals'].length;
		workplaces.push(workplace)
	}
	return workplaces;
}

function init_homes(nodes){
	var homes = [];
	for (var h=0; h < NUM_HOMES; h++) {
		var home = {
			'index': h,
			'loc': [MIN_LAT + (MAX_LAT - MIN_LAT)*Math.random(), MIN_LONG + (MAX_LONG - MIN_LONG)*Math.random()],
			'lambda_home': 0,
			'individuals': get_individuals_at_home(nodes, h), // Populate with individuals in same home
			'Q_h': 1,
			'scale': 0
		};
		home['scale'] = BETA_H*home['Q_h']/(Math.pow(home['individuals'].length, ALPHA));
		homes.push(home)
	}
	return homes;
}

function init_community(nodes){
	var communities = [];
	for (var c=0; c < NUM_COMMUNITIES; c++) {
		var community = {
			'index': c,
			'loc': [MIN_LAT + (MAX_LAT - MIN_LAT)*Math.random(), MIN_LONG + (MAX_LONG - MIN_LONG)*Math.random()],
			'lambda_community': 0, 
			'individuals': get_individuals_at_community(nodes, c), // Populate with individuals in same community
			'Q_c': 1,
			'scale': 0
		};
		var sum_value = 0;
		for (var i=0; i<community['individuals'].length; i++){
			var temp = nodes.filter( function(node) {
				return node['index']==community['individuals'][i];
			});
			sum_value += temp[0]['funct_d_ck'];
		}
		community['scale'] = BETA_C*community['Q_c']/sum_value;
		communities.push(community)
	}
	return communities;
}

function update_individual_lambda_h(node){
	return node['infection_status'] * node['kappa_T'] * node['infectiousness'] * (1 + node['severity']);
}

function update_individual_lambda_w(node){
	return node['infection_status'] * node['kappa_T'] * node['infectiousness'] * (1 + node['severity']*(2*node['psi_T']-1));
}

function update_individual_lambda_c(node){
	return node['infection_status'] * node['kappa_T'] * node['infectiousness'] * node['funct_d_ck'] * (1 + node['severity']);
	// optimised version: return node['lambda_h] * node['funct_d_ck']; 
}

function update_infection(node){
	if (node['infection_status']==0 && Math.random()>0.5){
		node['infection_status'] = 1;
	}
	node['lambda_h'] = update_individual_lambda_h(node);
	node['lambda_w'] = update_individual_lambda_w(node);
	node['lambda_c'] = update_individual_lambda_c(node);
}

function update_kappa(node, cur_time){
	node['kappa_T'] = kappa_T(node, cur_time);
}

function update_psi(node, cur_time){
	node['psi_T'] = psi_T(node, cur_time);
}

function update_lambda_h(nodes, home){
	var sum_value = 0
	
	for (var i=0; i<home['individuals'].length; i++){
	//	var temp = nodes.filter( function(node) {
	//		return node['index']==home['individuals'][i];
	//	});
		sum_value += nodes[home['individuals'][i]]['lambda_h'];
	}
	return home['scale']*sum_value;
	// Populate it afterwards...
}

function update_lambda_w(nodes, workplace){
	var sum_value = 0
	for (var i=0; i<workplace['individuals'].length; i++){
	//	var temp = nodes.filter( function(node) {
	///		return node['index']==workplace['individuals'][i];
	//	});
		sum_value += nodes[workplace['individuals'][i]]['lambda_w'];
	}
	return workplace['scale']*sum_value;
	// Populate it afterwards...
}

function update_lambda_c(nodes, community){
	var sum_value = 0
	for (var i=0; i<community['individuals'].length; i++){
	//	var temp = nodes.filter( function(node) {
	//		return node['index']==community['individuals'][i];
	//	});
		sum_value += nodes[community['individuals'][i]]['lambda_c'];
	}
	return community['scale']*sum_value;
	// Populate it afterwards...
}

function update_lambdas(node){
	node['lambda'] = node['lambda_h'] + node['lambda_w'] + node['zeta_a']*node['funct_d_ck']*node['lambda_c'];
}


function update_pos(node) {
	// update position of node for one timestep
	var lat = node['loc'][0];
	var long = node['loc'][1];
	
	// Reverse direction if node goes outside bounding box
	if(lat > MAX_LAT || lat < MIN_LAT) {
		node['direction'][0] *= -1;
	}
	if(long > MAX_LONG || long < MIN_LONG) {
		node['direction'][1] *= -1; 
	}
		
	var direction_lat = node['direction'][0];
	var direction_long = node['direction'][1];
	
	var v = PEOPLE_VELOCITY * 0.001; // convert velocity in mt/sec to mt/timestep
	var new_lat = lat + v * direction_lat;
	var new_long = long + v * direction_long;
	
	node['loc'] = [new_lat, new_long]
}

function dist(n1, n2) {
	// Approx distance using https://blog.mapbox.com/fast-geodesic-approximations-with-cheap-ruler-106f229ad016
	// This function is good only for Bangalore (lat = 13)! Do NOT use without correction for other cities.
	
    var lat1 = n1['loc'][0];
   	var long1 = n1['loc'][1];

    var lat2 = n2['loc'][0];
    var long2 = n2['loc'][1];
	
	var dy = (lat1 - lat2) * 111134.144;
	var dx = (long1 - long2) * 111317.43;

    var d = (dx**2 + dy**2)**0.5;

    return d;
}

function clamp_block_id(id) {
	if(id < 0) id = 0;
	if(id >= N_BLOCKS) id = N_BLOCKS - 1;
	return id;
}

function node_to_block_id(node) {
	var idy = Math.floor((node['loc'][0] - MIN_LAT) * N_BLOCKS / (MAX_LAT - MIN_LAT));
	var idx = Math.floor((node['loc'][1] - MIN_LONG) * N_BLOCKS / (MAX_LONG - MIN_LONG));
	
	return [clamp_block_id(idx), clamp_block_id(idy)]; // clamp because node can go just outside city limits
}

function run_simulation() {
	var nodes = init_nodes();
	var homes = init_homes(nodes);
	var workplaces = init_workplaces(nodes);
	var communities = init_community(nodes);
	var days_num_infected = [];
	for(var i = 0; i < NUM_DAYS; i++) {
		var n_infected = nodes.reduce(function(partial_sum, node) {return partial_sum + (node['infection_status'] ? 1 : 0);}, 0);
		days_num_infected.push([i, n_infected]);

		for (var j=0; j<NUM_PEOPLE; j++){
			update_kappa(nodes[j], i);
			update_infection(nodes[j]);
		}
		for (var h=0; h<NUM_HOMES; h++){
			update_lambda_h(nodes, homes[h]);
		}
		for (var w=0; w<NUM_WORKPLACES; w++){
			update_lambda_w(nodes, workplaces[w]);
		}
		for (var c=0; c<NUM_COMMUNITIES; c++){
			update_lambda_c(nodes, communities[c]);
		}
		for (var j=0; j<NUM_PEOPLE; j++){
			update_lambdas(nodes[j]);
		}

	}
	return days_num_infected;
}

function plot_simulation(days_num_infected) {
	google.charts.load('current', {packages: ['corechart', 'line']});
	google.charts.setOnLoadCallback(drawBasic);

	function drawBasic() {
	    var data = new google.visualization.DataTable();
	    data.addColumn('number', 'X');
	    data.addColumn('number', 'Number infected');

	    data.addRows(days_num_infected);

	    var options = {
	        hAxis: {
	            title: 'Timesteps'
	        },
	        vAxis: {
	            title: 'Number infected'
	        },
			title: 'Infection curve for people_velocity = ' + PEOPLE_VELOCITY,
	    };

	    var chart = new google.visualization.LineChart(document.getElementById('num_infected_plot'));

	    chart.draw(data, options);
	}
}

function run_and_plot() {
	days_num_infected = run_simulation();
	plot_simulation(days_num_infected);
}

run_and_plot();
