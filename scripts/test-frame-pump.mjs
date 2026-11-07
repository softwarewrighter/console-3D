import assert from 'node:assert/strict';
import {test} from 'node:test';
import {FramePump,ActiveClock} from '../web/frame-pump.mjs';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
test('idle schedules nothing; invalidations coalesce; active drawing is capped',async()=>{
 let draws=0;const pump=new FramePump(()=>draws++);
 await sleep(70);assert.equal(draws,0);assert.equal(pump.stats.pending,false);
 pump.invalidate();pump.invalidate();await sleep(70);assert.equal(draws,1);assert.equal(pump.stats.pending,false);
 pump.continuous=true;pump.invalidate();const start=draws;await sleep(225);assert.ok(draws-start<=5);pump.continuous=false;
 await sleep(70);const stopped=draws;await sleep(70);assert.equal(draws,stopped);
});
test('paused and invisible update queues resume without a polling loop',async()=>{
 let updates=0;const pump=new FramePump(()=>{});pump.activity(true,true);pump.request(()=>updates++);
 await sleep(60);assert.equal(updates,0);assert.equal(pump.stats.pending,false);
 pump.activity(false,false);await sleep(60);assert.equal(updates,0);
 pump.activity(true,false);await sleep(60);assert.equal(updates,1);assert.equal(pump.stats.pending,false);
});
test('overlapping pause reasons freeze the program clock',async()=>{
 const clock=new ActiveClock();clock.pause('manual',true);const frozen=clock.now();await sleep(20);clock.pause('hidden',true);clock.pause('manual',false);await sleep(20);assert.equal(clock.now(),frozen);clock.pause('hidden',false);await sleep(20);assert.ok(clock.now()>frozen+10);
});
