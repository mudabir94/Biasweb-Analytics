'use strict';
const AHP = require('ahp');

module.exports = AHP;


var ahpContext = new AHP();
ahpContext.addItems(['tom', 'dick']);
ahpContext.addCriteria(['experience', 'education', 'charisma']);

ahpContext.rankCriteriaItem('experience', [{
        preferredItem: 'dick',
        comparingItem: 'tom',
        scale: 4
    },
   
]);
ahpContext.rankCriteriaItem('education', [{
        preferredItem: 'tom',
        comparingItem: 'dick',
        scale: 3
    },
    
]);
ahpContext.rankCriteriaItem('charisma', [{
        preferredItem: 'tom',
        comparingItem: 'dick',
        scale: 5
    }
]);
ahpContext.rankCriteria(
    [{
            preferredCriterion: 'experience',
            comparingCriterion: 'education',
            scale: 4
        },
        {
            preferredCriterion: 'experience',
            comparingCriterion: 'charisma',
            scale: 3
        },
        {
            preferredCriterion: 'charisma',
            comparingCriterion: 'education',
            scale: 3
        },
       
    ]
);
let output = ahpContext.debug();
console.log(output.log);