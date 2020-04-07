

function get_kappa_no_intervention(nodes, homes, workplaces, communities,cur_time){
	for (var count = 0; count < nodes.length;count ++){
		nodes[count]['kappa_T'] = kappa_T(nodes[count], cur_time);
		nodes[count]['kappa_H'] = 1;
		nodes[count]['kappa_W'] = 1;
		nodes[count]['kappa_C'] = 1;
		nodes[count]['kappa_PT'] = 1;
		nodes[count]['quarantined'] = false;
		nodes[count]['kappa_H_incoming'] = 1;
		nodes[count]['kappa_W_incoming'] = 1;
		nodes[count]['kappa_C_incoming'] = 1;
		nodes[count]['kappa_PT_incoming'] = 1;
	}

}

function get_kappa_case_isolation(nodes, homes, workplaces, communities,cur_time){
	for (var count = 0; count < nodes.length;count ++){
		var time_since_symptoms = cur_time - (nodes[count]['time_of_infection']+nodes[count]['incubation_period']+nodes[count]['asymptomatic_period']);
		nodes[count]['kappa_T'] = kappa_T(nodes[count], cur_time);
		nodes[count]['kappa_H'] = 1;
		nodes[count]['kappa_W'] = 1;
		nodes[count]['kappa_C'] = 1;
		nodes[count]['kappa_PT'] = 1;
		nodes[count]['quarantined'] = false;
		nodes[count]['kappa_H_incoming'] = 1;
		nodes[count]['kappa_W_incoming'] = 1; 
		nodes[count]['kappa_C_incoming'] = 1;
		nodes[count]['kappa_PT_incoming'] = 1;


		if((nodes[count]['compliant']) && 
		 (time_since_symptoms > NUM_DAYS_TO_RECOG_SYMPTOMS*SIM_STEPS_PER_DAY) && 
		 (time_since_symptoms <= (NUM_DAYS_TO_RECOG_SYMPTOMS+SELF_ISOLATION_DAYS)*SIM_STEPS_PER_DAY)){  
			nodes[count]['quarantined'] = true;
			nodes[count]['kappa_W'] = 0.25;
			nodes[count]['kappa_C'] = 0.25;
			nodes[count]['kappa_PT'] = 0.25;
			nodes[count]['kappa_W_incoming'] = 0.25; 
			nodes[count]['kappa_C_incoming'] = 0.25;
			nodes[count]['kappa_PT_incoming'] = 0.25;
		}
	}
}

function get_kappa_home_quarantine(nodes, homes, workplaces, communities,cur_time){
	
	for(var count = 0; count<homes.length;count++){
		//reset all homes as non-quarantined. The status will be updated depending on the household individuals.
		homes[count]['quarantined'] = false;
	}

	for (var count = 0; count < nodes.length;count++){
		var time_since_symptoms = cur_time - (nodes[count]['time_of_infection']+nodes[count]['incubation_period']+nodes[count]['asymptomatic_period'])
		if((nodes[count]['compliant']) && 
		 (time_since_symptoms > NUM_DAYS_TO_RECOG_SYMPTOMS*SIM_STEPS_PER_DAY) && 
		 (time_since_symptoms <= (NUM_DAYS_TO_RECOG_SYMPTOMS+HOME_QUARANTINE_DAYS)*SIM_STEPS_PER_DAY)){ //The magic number 1 = time to recognise symptoms. 
			homes[nodes[count]['home']]['quarantined'] = true;
		}
	}
	for (var count = 0; count < nodes.length;count++){
		nodes[count]['kappa_T'] = kappa_T(nodes[count], cur_time);
		nodes[count]['kappa_H'] = 1;
		nodes[count]['kappa_W'] = 1;
		nodes[count]['kappa_C'] = 1;
		nodes[count]['kappa_PT'] = 1;
		nodes[count]['quarantined'] = false;
		nodes[count]['kappa_H_incoming'] = 1;
		nodes[count]['kappa_W_incoming'] = 1;
		nodes[count]['kappa_C_incoming'] = 1;
		nodes[count]['kappa_PT_incoming'] = 1;

		if(homes[nodes[count]['home']]['quarantined']){
			nodes[count]['quarantined'] = true;
			nodes[count]['kappa_H'] = 2;
			nodes[count]['kappa_W'] = 0.25;
			nodes[count]['kappa_C'] = 0.25;
			nodes[count]['kappa_PT'] = 0.25;
			nodes[count]['kappa_H_incoming'] = 1;
			nodes[count]['kappa_W_incoming'] = 0.25;
			nodes[count]['kappa_C_incoming'] = 0.25;
			nodes[count]['kappa_PT_incoming'] = 0.25;
		} 		
	}
}

function get_kappa_lockdown(nodes, homes, workplaces, communities,cur_time){
	for (var count = 0; count < nodes.length;count ++){
		nodes[count]['kappa_T'] = kappa_T(nodes[count], cur_time);
		if(nodes[count]['compliant']){
			nodes[count]['kappa_H'] = 2;
			nodes[count]['kappa_C'] = 0.25;
			nodes[count]['quarantined'] = true;
			nodes[count]['kappa_H_incoming'] = 1;
			nodes[count]['kappa_W_incoming'] = 0.25;
			nodes[count]['kappa_C_incoming'] = 0.25;
			if(nodes[count]['workplace_type']==WTYPE_OFFICE){
				nodes[count]['kappa_W'] = 0.25;
				nodes[count]['kappa_PT'] = 0.25;
			}
			else{
				nodes[count]['kappa_W'] = 0;
				nodes[count]['kappa_PT'] = 0;
			}		
		}
		else{ //non-compliant
			nodes[count]['kappa_H'] = 1.25;
			nodes[count]['kappa_C'] = 1;
			nodes[count]['quarantined'] = true;
			nodes[count]['kappa_H_incoming'] = 1;
			nodes[count]['kappa_C_incoming'] = 1;
			if(nodes[count]['workplace_type']==WTYPE_OFFICE){
				nodes[count]['kappa_W'] = 0.25;
				nodes[count]['kappa_W_incoming'] = 0.25;
				nodes[count]['kappa_PT'] = 0.25;
				nodes[count]['kappa_PT_incoming'] = 0.25;
			}
			else{
				nodes[count]['kappa_W'] = 0;
				nodes[count]['kappa_W_incoming'] = 0;
				nodes[count]['kappa_PT'] = 0;
				nodes[count]['kappa_PT_incoming'] = 0;
			}
		}		
	}
}

function get_kappa_CI_HQ(nodes, homes, workplaces, communities,cur_time){
	for(var count = 0; count<homes.length;count++){
		//reset all homes as non-quarantined. The status will be updated depending on the household individuals.
		//Same as 
		homes[count]['quarantined'] = false;
	}

	for (var count = 0; count < nodes.length;count++){
		var time_since_symptoms = cur_time - (nodes[count]['time_of_infection']+nodes[count]['incubation_period']+nodes[count]['asymptomatic_period'])
		if((nodes[count]['compliant']) && 
		 (time_since_symptoms > NUM_DAYS_TO_RECOG_SYMPTOMS*SIM_STEPS_PER_DAY) && 
		 (time_since_symptoms <= (NUM_DAYS_TO_RECOG_SYMPTOMS+HOME_QUARANTINE_DAYS)*SIM_STEPS_PER_DAY)){ //The magic number 1 = time to recognise symptoms. 
			homes[nodes[count]['home']]['quarantined'] = true;
		}
	}
	for (var count = 0; count < nodes.length;count++){
		nodes[count]['kappa_T'] = kappa_T(nodes[count], cur_time);
		nodes[count]['kappa_H'] = 1;
		nodes[count]['kappa_W'] = 1;
		nodes[count]['kappa_C'] = 1;
		nodes[count]['kappa_PT'] = 1;
		nodes[count]['quarantined'] = false;
		nodes[count]['kappa_H_incoming'] = 1;
		nodes[count]['kappa_W_incoming'] = 1;
		nodes[count]['kappa_C_incoming'] = 1;
		nodes[count]['kappa_PT_incoming'] = 1;

		if(homes[nodes[count]['home']]['quarantined']){
			nodes[count]['quarantined'] = true;
			nodes[count]['kappa_H'] = 1; //case isolation reduces 
			nodes[count]['kappa_W'] = 0.25;
			nodes[count]['kappa_C'] = 0.25;
			nodes[count]['kappa_PT'] = 0.25;
			nodes[count]['kappa_H_incoming'] = 1;
			nodes[count]['kappa_W_incoming'] = 0.25;
			nodes[count]['kappa_C_incoming'] = 0.25;
			nodes[count]['kappa_PT_incoming'] = 0.25;
		} 		
	}
}

function get_kappa_CI_HQ_70P(nodes, homes, workplaces, communities,cur_time){
	for(var count = 0; count<homes.length;count++){
		//reset all homes as non-quarantined. The status will be updated depending on the household individuals.
		//Same as 
		homes[count]['quarantined'] = false;
	}

	for (var count = 0; count < nodes.length;count++){
		var time_since_symptoms = cur_time - (nodes[count]['time_of_infection']+nodes[count]['incubation_period']+nodes[count]['asymptomatic_period'])
		if((nodes[count]['compliant']) && 
		 (time_since_symptoms > NUM_DAYS_TO_RECOG_SYMPTOMS*SIM_STEPS_PER_DAY) && 
		 (time_since_symptoms <= (NUM_DAYS_TO_RECOG_SYMPTOMS+HOME_QUARANTINE_DAYS)*SIM_STEPS_PER_DAY)){ //The magic number 1 = time to recognise symptoms. 
			homes[nodes[count]['home']]['quarantined'] = true;
		}
	}
	for (var count = 0; count < nodes.length;count++){
		nodes[count]['kappa_T'] = kappa_T(nodes[count], cur_time);
		nodes[count]['kappa_H'] = 1;
		nodes[count]['kappa_W'] = 1;
		nodes[count]['kappa_C'] = 1;
		nodes[count]['kappa_PT'] = 1;
		nodes[count]['quarantined'] = false;
		nodes[count]['kappa_H_incoming'] = 1;
		nodes[count]['kappa_W_incoming'] = 1;
		nodes[count]['kappa_C_incoming'] = 1;
		nodes[count]['kappa_PT_incoming'] = 1;

		if(homes[nodes[count]['home']]['quarantined']){
			nodes[count]['quarantined'] = true;
			nodes[count]['kappa_H'] = 1;
			nodes[count]['kappa_W'] = 0.25;
			nodes[count]['kappa_C'] = 0.25;
			nodes[count]['kappa_PT'] = 0.25;
			nodes[count]['kappa_H_incoming'] = 1;
			nodes[count]['kappa_W_incoming'] = 0.25;
			nodes[count]['kappa_C_incoming'] = 0.25;
			nodes[count]['kappa_PT_incoming'] = 0.25;
		}
		if(nodes[count]['age']>= 70 && nodes[count]['compliant']){
			nodes[count]['kappa_W_incoming'] = 0.25;
			nodes[count]['kappa_C_incoming'] = 0.25;
			nodes[count]['kappa_PT_incoming'] = 0.25;

		} 		
	}
}

function get_kappa_LOCKDOWN_21_CI_HQ_SD_70_PLUS_21_CI(nodes, homes, workplaces, communities,cur_time){
	const FIRST_PERIOD = 21;
	const SECOND_PERIOD = 21;
	if(cur_time < FIRST_PERIOD*SIM_STEPS_PER_DAY){
		get_kappa_lockdown(nodes, homes, workplaces, communities,cur_time);
	}else if(cur_time < (FIRST_PERIOD+SECOND_PERIOD)*SIM_STEPS_PER_DAY){
		get_kappa_CI_HQ_70P(nodes, homes, workplaces, communities,cur_time);
	}else{
		get_kappa_case_isolation(nodes, homes, workplaces, communities,cur_time);
	}
}

function get_kappa_LOCKDOWN_21(nodes, homes, workplaces, communities,cur_time){
	const FIRST_PERIOD = 21;
	if(cur_time < FIRST_PERIOD*SIM_STEPS_PER_DAY){
		get_kappa_lockdown(nodes, homes, workplaces, communities,cur_time);
	}else{
		get_kappa_no_intervention(nodes, homes, workplaces, communities,cur_time);
	}
}