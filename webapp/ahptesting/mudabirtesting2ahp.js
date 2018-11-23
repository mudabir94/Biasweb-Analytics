

const AHP = require('ahp');
var Combinatorics = require('js-combinatorics');

module.exports = AHP;

var ahpContext = new AHP();
var alternatives_list=['Samsung galaxy S7','Samsung Galaxy A3 2017']
var criteria_list=['price', 'Resolution', 'Size'];
ahpContext.addItems(alternatives_list);
ahpContext.addCriteria(criteria_list);
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
ahpContext.rankCriteriaItem(criteria_list[0], 
    [{
        preferredItem:'Samsung galaxy S7' ,
        comparingItem:'Samsung Galaxy A3 2017' ,
        scale: 9
    }
]);
var output = ahpContext.debug();
console.log("output1",output.log);
