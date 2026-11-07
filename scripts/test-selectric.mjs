import test from 'node:test';
import assert from 'node:assert/strict';
import {SelectricMachine} from '../web/selectric-machine.mjs';
const config={max_column:130,max_tilt_deg:20};
function setup(){let time=0,next=0;const frames=new Map(),poses=[];const m=new SelectricMachine(config,p=>poses.push(p),{now:()=>time,requestFrame:cb=>{frames.set(++next,cb);return next;},cancelFrame:id=>frames.delete(id)});return {m,poses,tick(t){time=t;const callbacks=[...frames.values()];frames.clear();callbacks.forEach(cb=>cb());}};}
test('queued selection, advance, correction, and return preserve glyph pose',async()=>{
 const {m}=setup();
 await m.run([{op:'select',tilt:12,rotate:75,duration:0},{op:'advance',columns:7,duration:0},{op:'backspace',columns:2,duration:0}]);
 assert.equal(m.state.column,5);assert.equal(m.state.tilt,12);assert.equal(m.state.rotate,75);
 await m.carriageReturn({duration:0});assert.equal(m.state.column,0);assert.equal(m.state.tilt,12);
 await m.backspace(1,{duration:0});assert.equal(m.state.column,0);
});
test('reject invalid programs before moving; enforce right margin',async()=>{
 const {m}=setup();
 await assert.rejects(m.run([{op:'advance',duration:0},{op:'select',tilt:99}]),/Tilt/);assert.equal(m.state.column,0);
 await m.advance(130,{duration:0});await assert.rejects(m.advance(1,{duration:0}),/margin/);assert.equal(m.state.column,130);
 await assert.rejects(m.run([{op:'advance',columns:-1}]),/columns/);
});
test('interpolate motion; stop cancels the remainder and reset clears pose',async()=>{
 const {m,tick}=setup();
 const moving=m.run([{op:'advance',columns:10,duration:100},{op:'select',tilt:12,duration:0}]);
 const rejected=assert.rejects(moving,{name:'AbortError'});
 await new Promise(setImmediate);tick(50);assert.equal(m.state.column,5);
 m.stop();tick(100);await rejected;assert.equal(m.state.column,5);assert.equal(m.state.tilt,0);
 m.reset();assert.deepEqual(m.state,{column:0,tilt:0,rotate:0,busy:false});
 await m.advance(1,{duration:0});assert.equal(m.state.column,1);
});
test('selection takes the short angular path; dispose rejects new work',async()=>{
 const {m,tick}=setup();await m.select({rotate:170,duration:0});
 const rotating=m.select({rotate:-170,duration:100});await new Promise(setImmediate);tick(50);assert.equal(m.state.rotate,180);tick(100);await rotating;assert.equal(m.state.rotate,-170);
 m.dispose();await assert.rejects(m.advance(),/disposed/);
});
test('continuous typing advances at 13 characters/s, returns, feeds, and repeats',async()=>{
 const {m,tick}=setup();
 const pending=m.typeContinuously({columns:43});const stopped=assert.rejects(pending,{name:'AbortError'});
 await new Promise(setImmediate);tick(1000);assert.equal(m.typing.characters,13);assert.equal(m.state.column,13);
 tick(2000);assert.equal(m.typing.characters,26);
 tick(43/13*1000);assert.equal(m.typing.count,43);assert.equal(m.typing.phase,'return');
 tick(43/13*1000+410);assert.equal(m.state.column,0);assert.equal(m.typing.phase,'linefeed');assert.ok(m.typing.feed>0);
 tick(43/13*1000+470+1000);assert.equal(m.typing.line,1);assert.equal(m.typing.characters,56);
 assert.ok(m.state.busy);m.stop();await stopped;
});
