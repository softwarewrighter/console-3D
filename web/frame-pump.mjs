// One shared, capped scheduler for motion and rendering. No callbacks while idle.
export class FramePump {
 constructor(draw,{fps=20}={}){this.draw=draw;this.fps=fps;this.updates=new Map();this.next=0;this.frames=0;this.timer=null;this.visible=true;this.paused=false;this.continuous=false;this.dirty=false;this.running=false;this.lastEnd=0;this.cost=0;}
 schedule(){if(this.running||this.timer!==null||!this.visible||!(this.dirty||this.continuous||(!this.paused&&this.updates.size)))return;this.timer=setTimeout(()=>{this.timer=null;this.tick();},Math.max(0,this.lastEnd+Math.max(1000/this.fps-this.cost,16,this.cost*.5)-performance.now()));}
 tick(){if(!this.visible)return;this.running=true;const start=performance.now();try{if(!this.paused){const callbacks=[...this.updates.values()];this.updates.clear();for(const cb of callbacks)cb(start);}if(this.dirty||this.continuous){this.draw(start);this.frames++;}this.dirty=false;}finally{this.cost=performance.now()-start;this.lastEnd=performance.now();this.running=false;this.schedule();}}
 invalidate(){this.dirty=true;this.schedule();}
 request(cb){const id=++this.next;this.updates.set(id,cb);this.schedule();return id;}
 cancel(id){this.updates.delete(id);}
 activity(visible,paused){this.visible=visible;this.paused=paused;if(this.timer!==null){clearTimeout(this.timer);this.timer=null;}this.schedule();}
 get stats(){return {frames:this.frames,pending:this.timer!==null,visible:this.visible,paused:this.paused,continuous:this.continuous,fpsLimit:this.fps,lastRenderMs:this.cost,queuedUpdates:this.updates.size};}
}
export class ActiveClock {
 constructor(){this.reasons=new Set();this.offset=0;this.pausedAt=null;}
 now(){return (this.pausedAt??performance.now())-this.offset;}
 pause(reason,value){const was=this.reasons.size>0;if(value)this.reasons.add(reason);else this.reasons.delete(reason);if(!was&&this.reasons.size)this.pausedAt=performance.now();if(was&&!this.reasons.size){this.offset+=performance.now()-this.pausedAt;this.pausedAt=null;}}
}
