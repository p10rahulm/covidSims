
NUM_PEOPLE = 100000; // Number of people. Will change once file is read.
NUM_DAYS = 100; //Number of days. 
SIM_STEPS_PER_DAY = 4; //Number of simulation steps per day. 
NUM_TIMESTEPS = NUM_DAYS*SIM_STEPS_PER_DAY; //

INIT_FRAC_INFECTED = 0.001; // Initial number of people infected


NUM_HOMES = 25000; //Will change once file is read.
NUM_WORKPLACES = 5000; //Will change once file is read.
NUM_COMMUNITIES = 198; //Will change once file is read.
NUM_DISEASE_STATES = 7; //0-S, 1-E, 2-I, 3-Symp,4-R, 5-H, 6-C, 7-D

const SUSCEPTIBLE = 0
const EXPOSED = 1
const INFECTIVE = 2
const SYMPTOMATIC = 3
const RECOVERED = 4
const HOSPITALISED = 5
const CRITICAL = 6
const DEAD = 7

let csvContent = "data:text/csv;charset=utf-8,"; //for file dump

const kappa_threshold1 = 4.5 * SIM_STEPS_PER_DAY; //OPTIMISE: Move this outside function call, compute only once.
const kappa_threshold2 = 5 * SIM_STEPS_PER_DAY;
const kappa_threshold3 = 10* SIM_STEPS_PER_DAY;



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


// Beta values
BETA_H = 0.47 //Thailand data
BETA_W = 0.47 //Thailand data
BETA_S = 0.94 //Thailand data
BETA_C = 0.075 //Thailand data
ALPHA = 0.8

//some required functions

function kappa_T(node, cur_time){

	
	var threshold1 = 4.5 * SIM_STEPS_PER_DAY; //OPTIMISE: Move this outside function call, compute only once.
	var threshold2 = 5 * SIM_STEPS_PER_DAY;
	var threshold3 = 10* SIM_STEPS_PER_DAY;
	if(node["infective"]!=1){
		return 0;
	}
	else {
		var time_since_infection = cur_time - node["time_of_infection"];

		if(time_since_infection < kappa_threshold1 || time_since_infection > kappa_threshold3) { return 0;}
		else if(time_since_infection < kappa_threshold2) {return 1;}
		else if(time_since_infection < kappa_threshold3) {return 1.5;}
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

//Functions to init homes, workplaces and communities

function init_homes(){
	
	var houses_json = JSON.parse(loadJSON_001('bangalore_houses.json'));
	// console.log("In init homes:",houses_json.length,houses_json[0]);
	NUM_HOMES = houses_json.length;

	var homes = [];
	for (var h=0; h < NUM_HOMES; h++) {
		var home = {
			'loc': [houses_json[h]['location'][1],houses_json[h]['location'][0]], // [lat, long],
			'lambda_home': 0,
			'individuals': [], // We will populate this later
			'Q_h': 1,
			'scale': 0
		};
		//home['scale'] = BETA_H*home['Q_h']/(Math.pow(home['individuals'].length, ALPHA));
		homes.push(home)
	}
	return homes;
}

function init_workplaces(){
	var workplaces_json = JSON.parse(loadJSON_001('bangalore_workspaces.json'));
	var schools_json = JSON.parse(loadJSON_001('bangalore_schools.json'));
	// console.log("In init workplaces:",workplaces_json.length,workplaces_json[0]);
	NUM_WORKPLACES = workplaces_json.length;
	NUM_SCHOOLS = schools_json.length;
	// console.log(NUM_WORKPLACES,NUM_SCHOOLS)

	var workplaces = [];
	// schools come first followed by workspaces

	for (var w=0; w < NUM_SCHOOLS; w++) {
		var workplace = {
			'index': w,
			'loc':  [schools_json[w]['location'][1],schools_json[w]['location'][0]], // [lat, long],
			'lambda_workplace': 0, 
			'individuals': [], //get_individuals_at_workplace(nodes, w), // Populate with individuals in same workplace
			'Q_w': 1,
			'scale': 0,
			'workplace_type': 2
		};
		//workplace['scale'] = BETA_W*workplace['Q_w']/workplace['individuals'].length;
		workplaces.push(workplace)
	}

	for (var w=0; w < NUM_WORKPLACES; w++) {
		var workplace = {
			'index': w,
			'loc':  [workplaces_json[w]['location'][1],workplaces_json[w]['location'][0]], // [lat, long],
			'lambda_workplace': 0, 
			'individuals': [], //get_individuals_at_workplace(nodes, w), // Populate with individuals in same workplace
			'Q_w': 1,
			'scale': 0,
			'workplace_type': 1
		};
		//workplace['scale'] = BETA_W*workplace['Q_w']/workplace['individuals'].length;
		workplaces.push(workplace)
	}
	
	return workplaces;
}

function compare_wards(a, b) {
	// Function to sort wards
	const wardA = a["Ward No."];
	const wardB = b["Ward No."];
  
	let comparison = 0;
	if (wardA > wardB) {
	  comparison = 1;
	} else if (wardA < wardB) {
	  comparison = -1;
	}
	return comparison;
}



function init_community(){

	var communities_json = JSON.parse(loadJSON_001('bangalore_cc.json'));
	// console.log("In init community",communities_json.length,communities_json);
	communities_json.sort(compare_wards);
	// console.log("In init community",communities_json.length,communities_json[0]['location']);
	NUM_COMMUNITIES = communities_json.length;

	var communities = [];
	for (var c=0; c < NUM_COMMUNITIES; c++) {
		var community = {
			'index': c,
			'loc':  [communities_json[c]['location'][1],communities_json[c]['location'][0]], // [lat, long]
			'lambda_community': 0, 
			'individuals': [], // We will populate this later
			'Q_c': 1,
			'scale': 0
		};
		var sum_value = 0;
		for (var i=0; i<community['individuals'].length; i++){
			sum_value += nodes[community['individuals'][i]]['funct_d_ck'];
		}
		//community['scale'] = BETA_C*community['Q_c']/sum_value;
		communities.push(community)
	}
	return communities;
}



function init_nodes() {

	const MAX_EXPOSED_DAYS_AT_START = 4.5; //at the start of sim, the oldest exposed limit

	var individuals_json = JSON.parse(loadJSON_001('bangalore_individuals.json'));
	var workplace_json = JSON.parse(loadJSON_001('bangalore_workspaces.json'));
	//console.log(individuals_json.length,individuals_json[0]);
	NUM_PEOPLE =individuals_json.length;
	NUM_WORKPLACES = workplace_json.length;
	//console.log("Num People", NUM_PEOPLE, "Num Workspaces",NUM_WORKPLACES)


	var nodes = [];
	for(var i = 0; i < NUM_PEOPLE; i++) {
	    var node = {
			'loc': [individuals_json[i]['lat'],individuals_json[i]['lon']], // [lat, long]
			'age': individuals_json[i]['age'],
			'zeta_a': 1,
			'infectiousness': 1, // a.k.a. rho
			'severity': (Math.random() <0.5)?1:0, // a.k.a. S_k
			'home': individuals_json[i]['household'], 
			'workplace': individuals_json[i]['workplaceType']==1? individuals_json[i]['workplace']:individuals_json[i]['school'],
			'community': individuals_json[i]['ward'],
			'time_of_infection': 0,
			'infection_status': (Math.random() <INIT_FRAC_INFECTED)?1:0, //random seeding
			'infective': 0,
			'lambda_h': 0,
			'lambda_w': 0,
			'lambda_c': 0,
			'lambda': 0,
			'kappa_T': 1,
			'psi_T': 0,
			'funct_d_ck': f_kernel(individuals_json[i]['CommunityCentreDistance']), // TODO: need to use the kernel function. function of distance from community...
			'workplace_type':  individuals_json[i]['workplaceType'], //either school or office
	    };
		
		if(node['workplace_type']==0) {
			node['workplace'] = null;
		}
	   
	    node['infective'] = node['infection_status']==INFECTIVE?1:0; //initialise all infected individuals as infective 
		node['time_of_infection'] = node['infection_status']==EXPOSED?(-MAX_EXPOSED_DAYS_AT_START*SIM_STEPS_PER_DAY*Math.random()):0;
		node['zeta_a']=zeta(node['age']);
	    nodes.push(node)
	}
	return nodes;
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

// Compute scale factors for each home, workplace and community. Done once at the beginning.
function compute_scale_homes(homes){
	
	for (var w=0; w < homes.length; w++) {
		if(homes[w]['individuals'].length==0){
			homes[w]['scale'] = 0;
			return
		}
	
		homes[w]['scale'] = BETA_H*homes[w]['Q_h']/(Math.pow(homes[w]['individuals'].length, ALPHA));
		}
	
}

function compute_scale_workplaces(workplaces){
	var beta_workplace
	for (var w=0; w < workplaces.length; w++) {
		if(workplaces[w]['individuals'].length==0){
			workplaces[w]['scale'] = 0
			return
		}
		if(workplaces[w]['workplace_type']==1){
			beta_workplace = BETA_H //workplace
		} else if (workplaces[w]['workplace_type']==2){
			beta_workplace = BETA_S //school
		}
		workplaces[w]['scale'] = beta_workplace*workplaces[w]['Q_w']/workplaces[w]['individuals'].length;
	}
	
}


function compute_scale_communities(nodes, communities){
	
	for (var w=0; w < communities.length; w++) {
	
    	var sum_value = 0;
		for (var i=0; i<communities[w]['individuals'].length; i++){
			sum_value += nodes[communities[w]['individuals'][i]]['funct_d_ck'];
		}
		if(sum_value==0){
			communities[w]['scale'] = 0
			return
		}
		communities[w]['scale'] = BETA_C*communities[w]['Q_c']/sum_value;
		}
	
}


function assign_individual_home_community(nodes,homes,workplaces,communities){
	//Assign individuals to homes, workplace, community
	for (var i=0; i < nodes.length; i++) {
	if(nodes[i]['home']!== null) homes[nodes[i]['home']]['individuals'].push(i); //No checking for null as all individuals have a home
	if(nodes[i]['workplace']!== null) workplaces[nodes[i]['workplace']]['individuals'].push(i);
	if(nodes[i]['community']!== null) communities[nodes[i]['community']]['individuals'].push(i);
	}

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
    ///TODO: Parametrise transition times
	if (node['infection_status']==SUSCEPTIBLE && Math.random()<(1-Math.exp(-node['lambda']/SIM_STEPS_PER_DAY))){
    	node['infection_status'] = EXPOSED; //move to exposed state
		node['time_of_infection'] = cur_time;
		node['infective'] = 0;		
	}
	else if(node['infection_status']==EXPOSED && (cur_time - node['time_of_infection'] > 4.5*SIM_STEPS_PER_DAY)){
    	node['infection_status'] = INFECTIVE;//move to infective state
    	node['infective'] = 1;
	}
	else if(node['infection_status']==INFECTIVE && (cur_time - node['time_of_infection'] > 5*SIM_STEPS_PER_DAY)){
    	if(Math.random() < 2/3){
            	node['infection_status'] = SYMPTOMATIC;//move to symptomatic
            	node['infective'] = 1;
    	}
    	else {
        	node['infection_status'] = RECOVERED;//move to recovered
            node['infective'] = 0;
    	}
    	
	}
	else if(node['infection_status']==SYMPTOMATIC && (cur_time - node['time_of_infection'] > 10*SIM_STEPS_PER_DAY)){
    	if(Math.random() < STATE_TRAN[age_index][0]){
            	node['infection_status'] = HOSPITALISED;//move to hospitalisation
            	node['infective'] = 0;
    	}
    	else {
        	node['infection_status'] = RECOVERED;//move to recovered
            node['infective'] = 0;
    	}
	}
	else if(node['infection_status']==HOSPITALISED && (cur_time - node['time_of_infection'] > 18*SIM_STEPS_PER_DAY)){
    	if(Math.random() < STATE_TRAN[age_index][1]){
            	node['infection_status'] = CRITICAL;//move to critical care
            	node['infective'] = 0;
    	}
    	else {
        	node['infection_status'] = RECOVERED;//move to recovered
            node['infective'] = 0;
    	}
	}
	else if(node['infection_status']==CRITICAL && (cur_time - node['time_of_infection'] > 20*SIM_STEPS_PER_DAY)){
    	if(Math.random() < STATE_TRAN[age_index][2]){
            	node['infection_status'] = DEAD;//move to dead
            	node['infective'] = 0;
    	}
    	else {
        	node['infection_status'] = RECOVERED;//move to recovered
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

function get_infected_community(nodes, community){
	var sum_value = 0
	for (var i=0; i<community['individuals'].length; i++){
	//	var temp = nodes.filter( function(node) {
	//		return node['index']==community['individuals'][i];
	//	});
		if (nodes[community['individuals'][i]]['infection_status']==INFECTIVE ||
    		nodes[community['individuals'][i]]['infection_status']==SYMPTOMATIC || 
    		nodes[community['individuals'][i]]['infection_status']==HOSPITALISED ||
    		nodes[community['individuals'][i]]['infection_status']==CRITICAL) {sum_value+=1}
	}
	return sum_value;
	// Populate it afterwards...
}

function update_lambdas(node,homes,workplaces,communities){
	var temp = 0
	if(node['home']!=null) temp+=homes[node['home']]['lambda_home']
	if(node['workplace']!=null) temp+= workplaces[node['workplace']]['lambda_workplace']
	if(node['community']!=null) temp+=node['zeta_a']*node['funct_d_ck']*communities[node['community']]['lambda_community'];
	node['lambda'] = temp
	
}

function run_simulation() {
	
	var homes = init_homes();
	var workplaces = init_workplaces();
	var communities = init_community();
	var nodes = init_nodes();
	
	console.log(NUM_PEOPLE,NUM_HOMES,NUM_WORKPLACES,NUM_COMMUNITIES)


	assign_individual_home_community(nodes,homes,workplaces,communities);
	compute_scale_homes(homes)
	compute_scale_workplaces(workplaces)
	compute_scale_communities(nodes, communities)
	
	var days_num_infected = [];
	var days_num_exposed = [];
	var days_num_hospitalised = [];
	var days_num_critical = [];
	var days_num_fatalities = [];
	var days_num_recovered = [];
	var days_num_affected = [];
	
	var infection_status_community=[]
	
	for(var i = 0; i < NUM_TIMESTEPS; i++) {
		
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
			
			var infected_count=get_infected_community(nodes, communities[c]);
			infection_status_community.push([]);
			let row = [i/SIM_STEPS_PER_DAY,c,infected_count].join(",");
            csvContent += row + "\r\n";
		}
		
		for (var j=0; j<NUM_PEOPLE; j++){
			update_lambdas(nodes[j],homes,workplaces,communities);			
		}
		
		
		var n_infected_wardwise = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==INFECTIVE||node['infection_status']==SYMPTOMATIC||node['infection_status']==HOSPITALISED||node['infection_status']==CRITICAL) ? 1 : 0);}, 0);
		days_num_infected.push([i/SIM_STEPS_PER_DAY, n_infected]);
		
		var n_infected = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==INFECTIVE||node['infection_status']==SYMPTOMATIC||node['infection_status']==HOSPITALISED||node['infection_status']==CRITICAL) ? 1 : 0);}, 0);
		days_num_infected.push([i/SIM_STEPS_PER_DAY, n_infected]);
        
        var n_exposed = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==EXPOSED) ? 1 : 0);}, 0);
		days_num_exposed.push([i/SIM_STEPS_PER_DAY, n_exposed]);
		
		var n_hospitalised = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==HOSPITALISED) ? 1 : 0);}, 0);
		days_num_hospitalised.push([i/SIM_STEPS_PER_DAY, n_hospitalised]);
		
		var n_critical = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==CRITICAL) ? 1 : 0);}, 0);
		days_num_critical.push([i/SIM_STEPS_PER_DAY, n_critical]);
		
		var n_fatalities = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==DEAD) ? 1 : 0);}, 0);
		days_num_fatalities.push([i/SIM_STEPS_PER_DAY, n_fatalities]);
		
		var n_recovered = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']==RECOVERED) ? 1 : 0);}, 0);
		days_num_recovered.push([i/SIM_STEPS_PER_DAY, n_recovered]);
		
		var n_affected = nodes.reduce(function(partial_sum, node) {return partial_sum + ((node['infection_status']) ? 1 : 0);}, 0);
		days_num_affected.push([i/SIM_STEPS_PER_DAY, n_affected]);

	}
	return [days_num_infected,days_num_exposed,days_num_hospitalised,days_num_critical,days_num_fatalities,days_num_recovered,days_num_affected];
}




function plot_simulation(days_num_infected,plot_element,title_1,title_2) {
	google.charts.load('current', {packages: ['corechart', 'line']});
	google.charts.setOnLoadCallback(drawBasic);

	function drawBasic() {
	    var data = new google.visualization.DataTable();
	    data.addColumn('number', 'X');
	    data.addColumn('number', title_1);

	    data.addRows(days_num_infected);

	    var options = {
	        hAxis: {
	            title: 'Days'
	        },
	        vAxis: {
	            title: title_1
	        },
			title: title_2,
			legend: {position:'none'}
	    };

	    var chart = new google.visualization.LineChart(document.getElementById(plot_element));

	    chart.draw(data, options);
	}
}

function run_and_plot() {
    var returned_values 
	returned_values = run_simulation();
	plot_simulation(returned_values[6],'num_affected_plot','Number Affected','Evolution of Affected Population');
	plot_simulation(returned_values[0],'num_infected_plot','Number Infected','Evolution of Infected Population');
	plot_simulation(returned_values[1],'num_exposed_plot','Number Exposed','Evolution of Exposed Population');
	plot_simulation(returned_values[2],'num_hospitalised_plot','Number Hospitalised','Evolution of Hospitalised Population');
	plot_simulation(returned_values[3],'num_critical_plot','Number Crtitical','Evolution of Crtitical Population');
	plot_simulation(returned_values[4],'num_fatalities_plot','Number Fatalities','Evolution of Fatalities Population');
	plot_simulation(returned_values[5],'num_recovered_plot','Number Recovered','Evolution of Recovered Population');
	
	var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "my_data.csv");
    document.body.appendChild(link); // Required for FF

	//link.click();	//TODO: Instead of click link, add link for download on page.
}


//Main function
//var mydata_ind = JSON.parse(data);
//console.log(mydata_ind)
//var mydata_school = JSON.parse(schools);
//console.log(mydata_school)
run_and_plot();
