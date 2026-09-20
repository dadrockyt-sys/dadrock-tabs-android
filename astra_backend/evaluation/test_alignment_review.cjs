// Standard-library checks of the actual browser export function; no DOM shim.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync(__dirname+'/alignment_review.html','utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1].replace('__DATA__','{}');
new vm.Script(script);
const functionText=script.slice(script.indexOf('function makeDraft'),script.indexOf('const player='));
const makeDraft=vm.runInNewContext(functionText+';makeDraft');
const data={duration:30,audioSha256:'a'.repeat(64),evidenceSha256:'b'.repeat(64)};
const anchors=[{beat:4,time:3.2},{beat:0,time:1.25}];
const draft=JSON.parse(JSON.stringify(makeDraft(anchors,data,'Independent listening required')));
assert.equal(draft.reviewStatus,'draft');
assert.equal(draft.independentOfPredictions,true);
assert.deepEqual(draft.segments,[{beatStart:0,beatEnd:4,timeStart:1.25,timeEnd:3.2}]);
assert.equal(anchors[0].beat,4);
assert.ok(draft.unresolvedItems.length>0);
for(const invalid of [[],[{beat:0,time:0}],[{beat:0,time:0},{beat:0,time:1}],[{beat:0,time:1},{beat:4,time:.5}],[{beat:0,time:0},{beat:4,time:31}],[{beat:0,time:NaN},{beat:4,time:2}]])assert.throws(()=>makeDraft(invalid,data,''));
console.log('PASS: browser script syntax; draft export, segment mapping, input immutability and six invalid anchor cases. DOM/playback not exercised.');
