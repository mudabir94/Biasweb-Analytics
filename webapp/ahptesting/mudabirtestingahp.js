'use strict';
const AHP = require('ahp');

/*
 * Reference: https://en.wikipedia.org/wiki/Analytic_hierarchy_process_%E2%80%93_leader_example
 */

module.exports = AHP;

var ahpContext = new AHP();

var ahpContext = new AHP();
alternatives_list=['MobileA','MobileB','MobileC']
criteria_list=['price', 'Resolution', 'Size'];
ahpContext.addItems(alternatives_list);
ahpContext.addCriteria(criteria_list);
dict={
    preferredItem: alternatives_list[0],
    comparingItem: alternatives_list[1],
    scale: 4
}
dict_in_list=[dict];

ahpContext.rankCriteriaItem(criteria_list[0],dict_in_list );

let output = ahpContext.debug();
console.log(output.log);