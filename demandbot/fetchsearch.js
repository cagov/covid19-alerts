// fetch popular search terms
const fetch = require('node-fetch')


String.prototype.hashCode = function() {
    var hash = 0, i, chr;
    if (this.length === 0) return hash;
    for (i = 0; i < this.length; i++) {
        chr   = this.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};

const url = 'https://cse.google.com/api/003358532045999200914:uxxka6d3pge/popularqueryjs?view=week';

async function safeParseJSON(response) {
    let body = await response.text();
    // console.log("Got Body",body);
    body = body.replace(/\\\x/g, '%');
    try {
        return JSON.parse(body);
    } catch (err) {
        console.error("Error:", err);
        console.error("Response body:", body);
        // throw err;
        return ReE(response, err.message, 500)
    }
}

/*
porn 3446907
fuck 3154295
fucker -1263686556
fucking -519573749
motherfucker 32245991
nigger -1045620280
dick 3083181
jew 105116
cock 3059156
cocksucker -717313205
blowjob -20842805
shit 3529280
piss 3441177
cunt 3065272
suck 3541578
hentai -1220868373
*/
const rejectList = [
	3154295, -891899646, 3446907, -1263686556,
	-519573749, 32245991, -1045620280, 3083181, 
	105116, 3059156, -717313205, -20842805,
	3529280, 3441177, 3065272, 3541578,
    -1220868373
];

isRejected = function(phrase) {
	return phrase.match(/\S+/g).length > 4 || 
           phrase.split(' ').find(wrd=>(rejectList.includes(wrd.hashCode()))) != undefined;
};


(async () => {
   
    let phrase = process.argv[2];
    if (phrase) {
        for (let i = 2; i < process.argv.length; ++i) {
            console.log( process.argv[i],  process.argv[i].hashCode());
        }
    } else {
        const json = await fetch(url).then(safeParseJSON);
        json.popularQueries.forEach( (qrec) => {
            console.log(`${qrec.num} ${qrec.query} rejected=${isRejected(qrec.query)} (${qrec.query.hashCode()})`);
        });
    }
})()
.catch(e=>{
    console.error(e);
})
.then(() => {
    // console.log("Debug Finished.");
    process.exit(0);
});