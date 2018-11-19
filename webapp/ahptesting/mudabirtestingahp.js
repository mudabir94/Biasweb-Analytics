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
ahpContext.rankCriteria(
    [{
            preferredCriterion: 'experience',
            comparingCriterion: 'education',
            scale: 4
        }
    ]
);

ahpContext.rankCriteriaItem('experience', [{
    preferredItem: 'dick',
    comparingItem: 'tom',
    scale: 4
}

]);


let output = ahpContext.debug();
console.log(output.log);