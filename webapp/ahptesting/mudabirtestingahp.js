// this is a test case for a 2 by 2 phone comparison. 
// 
'use strict';
const AHP = require('ahp');
var Combinatorics = require('js-combinatorics');


/*
 * Reference: https://en.wikipedia.org/wiki/Analytic_hierarchy_process_%E2%80%93_leader_example
 */

module.exports = AHP;

var ahpContext = new AHP();

var ahpContext = new AHP();
var alternatives_list=['MobileA','MobileB']
var criteria_list=['price', 'Resolution', 'Size'];
ahpContext.addItems(alternatives_list);
ahpContext.addCriteria(criteria_list);
// 
var cmb_alt_lst = Combinatorics.combination(alternatives_list, 2);
var combination_alt_list=[]

for (var a=0;a<cmb_alt_lst.length;a++) {
    combination_alt_list.push(cmb_alt_lst.next())
}
var cmb_crit_lst = Combinatorics.combination(criteria_list, 2);
var combination_crit_list=[]

for (var a=0;a<cmb_crit_lst.length;a++) {
    combination_crit_list.push(cmb_crit_lst.next())
}
console.log(combination_crit_list);

// on user event 
// get the two phones in camparison
// the criteria on which they are compared 
// the scale given by the user. 

ahpContext.rankCriteria(
    [  {
            preferredCriterion: criteria_list[0],
            comparingCriterion: criteria_list[1],
            scale: 9
        },
        {
            preferredCriterion: criteria_list[0],
            comparingCriterion: criteria_list[2],
            scale: 3
        },
        {
            preferredCriterion: criteria_list[1],
            comparingCriterion: criteria_list[2],
            scale: 9
        }
       
    ]
);


// BASED ON 
// items/alternatives and criterias we would get the max number of combinations. 
// we will generate rankCriteria by giving it a dictionary. 
var criteria=criteria_list[0];
var usr_scl_input=1
var mob1='MobileA';
var mob2='MobileB';

ahpContext.rankCriteriaItem(criteria_list[0], 
    [{
        preferredItem:mob1 ,
        comparingItem:mob1 ,
        scale: 9
    }
]);
ahpContext.rankCriteriaItem(criteria_list[1], 
    [{
        preferredItem:'MobileA' ,
        comparingItem:'MobileB' ,
        scale: 3
    }
]);
ahpContext.rankCriteriaItem(criteria_list[2], 
    [{
        preferredItem:'MobileA' ,
        comparingItem:'MobileB' ,
        scale: 2
    }
]);

var output = ahpContext.debug();
console.log("output1",output.log);


ahpContext.rankCriteriaItem(criteria_list[0], 
    [{
        preferredItem:'MobileA' ,
        comparingItem:'MobileB' ,
        scale: 1/2
    }
]);


var output = ahpContext.debug();
console.log("output2",output);
