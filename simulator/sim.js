
NUM_PEOPLE = 100000; // Number of people
NUM_DAYS = 20; //Number of days
SIM_STEPS_PER_DAY = 4; //Number of simulation steps per day
NUM_TIMESTEPS = NUM_DAYS*SIM_STEPS_PER_DAY; //

INIT_NUM_INFECTED = 100; // Initial number of people infected
VIRUS_TRANSMISSION_DIST = 100; // Cut off distance (in meters) below which virus transmission might occur
VIRUS_TRANSMISSION_PROB = 0.5; // If within the cut-off distance, transmission probability
DAYS_TO_RECOVER = 10; // After being infected, how many days to recover (assumed infectious during this phase and that no one dies).
PEOPLE_VELOCITY = 10; // Velocity with which people move (in meter/sec). Reduce this to show impact of social distancing.
N_BLOCKS = 50; // Divide city into NxN blocks and look for collision only in adjacent blocks to speed up computation.
NUM_HOMES = 25000;
NUM_WORKPLACES = 5000;
NUM_COMMUNITIES = 50;
NUM_DISEASE_STATES = 7; //0-S, 1-E, 2-I, 3-Symp,4-R, 5-H, 6-C, 7-D
// bounding box around Blore (approx)
//age related transition probabilities
STATE_TRAN=[
   [0.0010000,   0.0500000,   0.4000000],
   [0.0030000,   0.0500000,   0.4000000],
   [0.0120000,   0.0500000,   0.5000000],
   [0.0320000,   0.0500000,   0.5000000],
   [0.0490000,   0.0630000,   0.4859086],
   [0.1020000,   0.1220000,   0.4821601],
   [0.1660000,   0.2740000,   0.4836866],
   [0.2430000,   0.4320000,   0.4858253],
   [0.2730000,   0.7090000,   0.4804786]
]
MIN_LAT = 12.85
MAX_LAT = 13.15
MIN_LONG = 77.45
MAX_LONG = 77.75

// Beta values
BETA_H = 0.47
BETA_W = 0.47
BETA_C = 0.075
ALPHA = 0.8

function init_nodes() {
	var nodes = [];
	for(var i = 0; i < NUM_PEOPLE; i++) {
	    var node = {
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
			'infection_status': (Math.random() <0.1)?2:0, //random seeding
			'infective': 0,
			'lambda_h': 0,
			'lambda_w': 0,
			'lambda_c': 0,
			'lambda': 0,
			'kappa_T': 1,
			'psi_T': 0,
			'funct_d_ck': Math.random(), // TODO: need to use the kernel function. function of distance from community...
			'workplace_type': Math.floor(Math.random() * 2), //either school or office
	    };
	    node['infective'] = node['infection_status']==2?1:0; //initialise all infected individuals as infective 
	    nodes.push(node)
	}
	return nodes;
}

function kappa_T(node, cur_time){

	
	var threshold1 = 4.5 * SIM_STEPS_PER_DAY; //OPTIMISE: Move this outside function call, compute only once.
	var threshold2 = 5 * SIM_STEPS_PER_DAY;
	var threshold3 = 10* SIM_STEPS_PER_DAY;
	if(node["infective"]!=1){
		return 0;
	}
	else {
		var time_since_infection = cur_time - node["time_of_infection"];

		if(time_since_infection < threshold1 || time_since_infection > threshold3) { return 0;}
		else if(time_since_infection < threshold2) {return 1;}
		else if(time_since_infection < threshold3) {return 1.5;}
		else return 0;
	}	
}

function psi_T(node, cur_time){
	if(node["infective"]!=1){ //check if not infectious
		return 0;
	}
	var PSI_THRESHOLD = SIM_STEPS_PER_DAY;	
	var time_since_infection = cur_time - node["time_of_infection"];
	var scale_factor = 0.5; 
	if(node['workplace_type']==0) {scale_factor = 0.1} //school
	else if(node['workplace_type']==1) {scale_factor = 0.5} //office
	if(time_since_infection < PSI_THRESHOLD){ return 0;}
	else {return scale_factor;}	
	
	
	return 0.5; // Add psi function... 1) if infected, 0 then constant based on school or workplace... 
}

function f_kernel(d){
    var a = 4 //in kms
    var b = 3.8 //both values are for Thailand
	return 1/(1+Math.pow(d/a,b))
}

function zeta(age){
    
    
    if(age < 5) {
    return 0.1;
    } else if(age < 10) {
    return 0.25;
    } else if(age < 15) {
    return 0.5;
    } else if(age < 20) {
    return 0.75;
    } else if(age < 65) {
    return 1;
    } else if(age < 70) {
    return 0.75;
    } else if(age < 75) {
    return 0.5;
    } else if(age < 85) {
    return 0.25;
    } else {
    return 0.1;
    }
}


function get_individuals_at_home(nodes, h){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes[i]['home']==h){
			individuals.push(i)
		}
	}
	return individuals;
}

function get_individuals_at_workplace(nodes, w){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes[i]['workplace']==w){
			individuals.push(i)
		}
	}
	return individuals;
}

function get_individuals_at_community(nodes, c){
	var individuals = []
	for (var i=0; i<NUM_PEOPLE; i++){
		if (nodes[i]['community']==c){
			individuals.push(i)
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
			sum_value += nodes[community['individuals'][i]]['funct_d_ck'];
		}
		community['scale'] = BETA_C*community['Q_c']/sum_value;
		communities.push(community)
	}
	return communities;
}

function update_individual_lambda_h(node){
	return node['infective'] * node['kappa_T'] * node['infectiousness'] * (1 + node['severity']);
}

function update_individual_lambda_w(node){
	return node['infective'] * node['kappa_T'] * node['infectiousness'] * (1 + node['severity']*(2*node['psi_T']-1));
}

function update_individual_lambda_c(node){
	return node['infective'] * node['kappa_T'] * node['infectiousness'] * node['funct_d_ck'] * (1 + node['severity']);
	// optimised version: return node['lambda_h] * node['funct_d_ck']; 
}

function update_infection(node,cur_time){
    
    
    var age_index = 0;
    // Determine age category of individual. TODO: Could be part of individual datastructure as this is static
    if(node['age'] < 10) {
    age_index = 0;
    } else if(node['age'] < 20) {
    age_index = 1;
    } else if(node['age'] < 30) {
    age_index = 2;
    } else if(node['age'] < 40) {
    age_index = 3;
    } else if(node['age'] < 50) {
    age_index = 4;
    } else if(node['age'] < 60) {
    age_index = 5;
    } else if(node['age'] < 70) {
    age_index = 6;
    } else if(node['age'] < 80) {
    age_index = 7;
    } else {
    age_index = 8;
    }
    
    //console.log(1-Math.exp(-node['lambda']/SIM_STEPS_PER_DAY))
	if (node['infection_status']==0 && Math.random()<(1-Math.exp(-node['lambda']/SIM_STEPS_PER_DAY))){
    	node['infection_status'] = 1; //move to exposed state
		node['time_of_infection'] = cur_time;
		node['infective'] = 0;		
	}
	else if(node['infection_status']==1 && (cur_time - node['time_of_infection'] > 4.5*SIM_STEPS_PER_DAY)){
    	node['infection_status'] = 2;//move to infective state
    	node['infective'] = 1;
	}
	else if(node['infection_status']==2 && (cur_time - node['time_of_infection'] > 5*SIM_STEPS_PER_DAY)){
    	if(Math.random() < 2/3){
            	node['infection_status'] = 3;//move to symptomatic
            	node['infective'] = 1;
    	}
    	else {
        	node['infection_status'] = 4;//move to recovered
            node['infective'] = 0;
    	}
    	
	}
	else if(node['infection_status']==3 && (cur_time - node['time_of_infection'] > 10*SIM_STEPS_PER_DAY)){
    	if(Math.random() < STATE_TRAN[age_index][0]){
            	node['infection_status'] = 5;//move to hospitalisation
            	node['infective'] = 0;
    	}
    	else {
        	node['infection_status'] = 4;//move to recovered
            node['infective'] = 0;
    	}
	}
	else if(node['infection_status']==5 && (cur_time - node['time_of_infection'] > 18*SIM_STEPS_PER_DAY)){
    	if(Math.random() < STATE_TRAN[age_index][1]){
            	node['infection_status'] = 6;//move to critical care
            	node['infective'] = 0;
    	}
    	else {
        	node['infection_status'] = 4;//move to recovered
            node['infective'] = 0;
    	}
	}
	else if(node['infection_status']==5 && (cur_time - node['time_of_infection'] > 20*SIM_STEPS_PER_DAY)){
    	if(Math.random() < STATE_TRAN[age_index][2]){
            	node['infection_status'] = 7;//move to dead
            	node['infective'] = 0;
    	}
    	else {
        	node['infection_status'] = 4;//move to recovered
            node['infective'] = 0;
    	}
	}
	
	
	
	node['lambda_h'] = update_individual_lambda_h(node);
	node['lambda_w'] = update_individual_lambda_w(node);
	node['lambda_c'] = update_individual_lambda_c(node);
}

function update_kappa(node, cur_time){
	node['kappa_T'] = kappa_T(node, cur_time);
	//console.log(node['kappa_T'])
}

function update_psi(node, cur_time){
	node['psi_T'] = psi_T(node, cur_time);
	//console.log(node['psi_T'])
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

function update_lambdas(node,homes,workplaces,communities){
	node['lambda'] = homes[node['home']]['lambda_home'] + workplaces[node['workplace']]['lambda_workplace'] + node['zeta_a']*node['funct_d_ck']*communities[node['community']]['lambda_community'];

	
}


function run_simulation() {
	var nodes = init_nodes();
	var homes = init_homes(nodes);
	var workplaces = init_workplaces(nodes);
	var communities = init_community(nodes);
	var days_num_infected = [];
	for(var i = 0; i < NUM_TIMESTEPS; i++) {
		var n_infected = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==2||node['infection_status']==3||node['infection_status']==5||node['infection_status']==6) ? 1 : 0);}, 0);
		days_num_infected.push([i, n_infected]);

		for (var j=0; j<NUM_PEOPLE; j++){
			update_infection(nodes[j],i);
			update_kappa(nodes[j], i);
			update_psi(nodes[j], i);
		}
		for (var h=0; h<NUM_HOMES; h++){
			homes[h]['lambda_home'] = update_lambda_h(nodes, homes[h]);
		}
		for (var w=0; w<NUM_WORKPLACES; w++){
			workplaces[w]['lambda_workplace'] = update_lambda_w(nodes, workplaces[w]);
		}
		for (var c=0; c<NUM_COMMUNITIES; c++){
			communities[c]['lambda_community'] = update_lambda_c(nodes, communities[c]);
		}
		for (var j=0; j<NUM_PEOPLE; j++){
			update_lambdas(nodes[j],homes,workplaces,communities);
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

//Main function
run_and_plot();
