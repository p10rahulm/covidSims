NUM_PEOPLE = 10000; // Number of people
INIT_NUM_INFECTED = 100; // Initial number of people infected
VIRUS_TRANSMISSION_DIST = 100; // Cut off distance (in meters) below which virus transmission might occur
VIRUS_TRANSMISSION_PROB = 0.5; // If within the cut-off distance, transmission probability
DAYS_TO_RECOVER = 10; // After being infected, how many days to recover (assumed infectious during this phase and that no one dies).
PEOPLE_VELOCITY = 10; // Velocity with which people move (in meter/sec). Reduce this to show impact of social distancing.
N_BLOCKS = 50; // Divide city into NxN blocks and look for collision only in adjacent blocks to speed up computation.
NUM_HOMES = 100;
NUM_WORKPLACES = 100;
NUM_COMMUNITIES = 200;

// bounding box around Blore (approx)
MIN_LAT = 12.85
MAX_LAT = 13.15
MIN_LONG = 77.45
MAX_LONG = 77.75

function init_nodes() {
	var nodes = [];
	for(var i = 0; i < NUM_PEOPLE; i++) {
	    var node = {
			'index': i,
			'loc': [MIN_LAT + (MAX_LAT - MIN_LAT)*Math.random(), MIN_LONG + (MAX_LONG - MIN_LONG)*Math.random()], // [lat, long]
			'direction': [Math.random(), Math.random()],
			'age': Math.floor(Math.random() * 100),
			'zeta_a': 1,
			'infectiousness': 1,
			'severity': 0,
			'home': Math.floor(Math.random() * NUM_HOMES), 
			'workplace': Math.floor(Math.random() * NUM_WORKPLACES),
			'community': Math.floor(Math.random() * NUM_COMMUNITIES),
			'time_of_infection': 0,
			'infection_status': 0,
			'lambda_h': 0,
			'lambda_w': 0,
			'lambda_c': 0,
			'lambda': 0
	    };
	    nodes.push(node)
	}
	return nodes;
}

function get_individuals_at_home(nodes, h){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes['home']==h){
			individuals.push(nodes['index'])
		}
	}
	return individuals;
}

function get_individuals_at_workplace(nodes, w){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes['workplace']==w){
			individuals.push(nodes['index'])
		}
	}
	return individuals;
}

function get_individuals_at_community(nodes, c){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes['community']==c){
			individuals.push(nodes['index'])
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

		};
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
			'd_ck': Math.random(),
			'lambda_home': 0,
			'individuals': get_individuals_at_home(nodes, h), // Populate with individuals in same home
		};
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
		};
		communities.push(community)
	}
	return communities;
}

function update_individual_lambda_h(node){
	return node['lambda_h'];
}

function update_individual_lambda_w(node){
	return node['lambda_w'];
}

function update_individual_lambda_c(node){
	return node['lambda_c'];
}

function update_infection(node){
	if (node['infection_status']==0 && Math.random()>0.5){
		node['infection_status'] = 1;
	}
	node['lambda_h'] = update_individual_lambda_h(node);
	node['lambda_w'] = update_individual_lambda_w(node);
	node['lambda_c'] = update_individual_lambda_c(node);
}

function update_lambda_h(home){
	// Populate it afterwards...
}

function update_lambda_w(workplace){
	// Populate it afterwards...
}

function update_lambda_c(community){
	// Populate it afterwards...
}

function update_lambdas(node){
	// Populate it afterwards...
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
	for(var i = 0; i < 200; i++) {
		var n_infected = nodes.reduce(function(partial_sum, node) {return partial_sum + (node['infection_status'] ? 1 : 0);}, 0);
		days_num_infected.push([i, n_infected]);

		for (var j=0; j<NUM_PEOPLE; j++){
			update_infection(nodes[j]);
		}
		for (var h=0; h<NUM_HOMES; h++){
			update_lambda_h(homes[h]);
		}
		for (var w=0; w<NUM_WORKPLACES; w++){
			update_lambda_w(workplaces[w]);
		}
		for (var c=0; c<NUM_COMMUNITIES; c++){
			update_lambda_c(communities[c]);
		}
		for (var j=0; j<NUM_PEOPLE; j++){
			update_lambdas(nodes[j])
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
