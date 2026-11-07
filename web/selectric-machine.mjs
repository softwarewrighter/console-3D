import {typingSample} from './typing-cycle.mjs';
/** Renderer-independent, queued Selectric mechanism control. Units: degrees/ms/columns. */
const abortError = () => Object.assign(new Error('Motion stopped'), {name:'AbortError'});
const finite = (x,name) => {if(typeof x!=='number'||!Number.isFinite(x))throw new TypeError(`${name} must be finite`);return x;};
export class SelectricMachine {
  constructor(config, applyPose, options={}) {
    if(!Number.isInteger(config.max_column)||config.max_column<1)throw new TypeError('Invalid max_column');
    this.config=config;this.applyPose=applyPose;this.onChange=options.onChange||(()=>{});
    this.now=options.now||(()=>performance.now());
    this.frame=options.requestFrame||(callback=>requestAnimationFrame(callback));
    this.cancelFrame=options.cancelFrame||(id=>cancelAnimationFrame(id));
    this.pose={column:0,tilt:0,rotate:0};this._epoch=0;this._active=null;this._tail=Promise.resolve();this._disposed=false;
    this._publish();
  }
  get state(){return {...this.pose,busy:!!this._active};}
  _publish(){this.applyPose({...this.pose});this.onChange(this.state);}
  _validate(command){
    if(!command||typeof command!=='object'||Array.isArray(command))throw new TypeError('Expected a command object');
    if(!['select','advance','backspace','return','wait'].includes(command.op))throw new TypeError('Unknown operation: '+command.op);
    const c={...command};
    if(c.duration!==undefined){finite(c.duration,'duration');if(c.duration<0||c.duration>60000)throw new RangeError('duration must be 0–60000 ms');}
    if(c.op==='select'){
      if(c.tilt===undefined&&c.rotate===undefined)throw new TypeError('select needs tilt or rotate');
      if(c.tilt!==undefined&&Math.abs(finite(c.tilt,'tilt'))>this.config.max_tilt_deg)throw new RangeError('Tilt exceeds the configured limit');
      if(c.rotate!==undefined&&Math.abs(finite(c.rotate,'rotate'))>3600)throw new RangeError('Rotation exceeds 3600 degrees');
    }
    if(c.op==='advance'||c.op==='backspace'){
      c.columns=c.columns??1;
      if(!Number.isInteger(c.columns)||c.columns<1||c.columns>this.config.max_column)throw new RangeError('columns must be a positive integer within travel');
    }
    return c;
  }
  _schedule(task){
    if(this._disposed)return Promise.reject(new Error('Mechanism disposed'));
    const epoch=this._epoch;
    const result=this._tail.catch(()=>{}).then(async()=>{
      if(epoch!==this._epoch||this._disposed)throw abortError();
      const controller=new AbortController();this._active=controller;this.onChange(this.state);
      try{return await task(controller.signal);}finally{if(this._active===controller){this._active=null;this.onChange(this.state);}}
    });
    this._tail=result;return result;
  }
  _transition(target,duration,signal){
    if(signal.aborted)return Promise.reject(abortError());
    const start={...this.pose},end={...start,...target};
    let rotationDelta=end.rotate-start.rotate;
    rotationDelta=((rotationDelta+180)%360+360)%360-180;
    if(!duration){this.pose=end;this._publish();return Promise.resolve(this.state);}
    return new Promise((resolve,reject)=>{
      const began=this.now();let id;
      const abort=()=>{this.cancelFrame(id);signal.removeEventListener('abort',abort);reject(abortError());};
      signal.addEventListener('abort',abort,{once:true});
      const tick=()=>{
        if(signal.aborted)return;
        const t=Math.min(1,Math.max(0,(this.now()-began)/duration)),u=t*t*(3-2*t);
        this.pose={column:start.column+(end.column-start.column)*u,tilt:start.tilt+(end.tilt-start.tilt)*u,rotate:start.rotate+rotationDelta*u};
        if(t===1)this.pose=end;
        this._publish();
        if(t<1)id=this.frame(tick);else{signal.removeEventListener('abort',abort);resolve(this.state);}
      };
      id=this.frame(tick);
    });
  }
  _execute(c,signal){
    const target={};let duration=c.duration;
    if(c.op==='select'){if(c.tilt!==undefined)target.tilt=c.tilt;if(c.rotate!==undefined)target.rotate=c.rotate;duration??=140;}
    if(c.op==='advance'){
      target.column=this.pose.column+c.columns;
      if(target.column>this.config.max_column)throw new RangeError('Right margin reached; issue a return');
      duration??=150;
    }
    if(c.op==='backspace'){target.column=Math.max(0,this.pose.column-c.columns);duration??=150;}
    if(c.op==='return'){target.column=0;duration??=Math.max(180,Math.min(800,this.pose.column*7));}
    if(c.op==='wait')duration??=200;
    return this._transition(target,duration,signal);
  }
  run(program){
    if(!Array.isArray(program))return Promise.reject(new TypeError('Program must be an array'));
    let commands;try{commands=program.map(c=>this._validate(c));}catch(e){return Promise.reject(e);}
    return this._schedule(async signal=>{for(const c of commands)await this._execute(c,signal);return this.state;});
  }
  typeContinuously(options={}){
    const settings={cps:13,columns:Math.floor(this.config.max_column/3),...options};
    if(!Number.isFinite(settings.cps)||settings.cps<1||settings.cps>100||!Number.isInteger(settings.columns)||settings.columns<1||settings.columns>this.config.max_column)return Promise.reject(new RangeError('Invalid typing speed or line width'));
    return this._schedule(signal=>new Promise((resolve,reject)=>{
      const began=this.now();let id;
      const abort=()=>{this.cancelFrame(id);signal.removeEventListener('abort',abort);reject(abortError());};
      signal.addEventListener('abort',abort,{once:true});
      const tick=()=>{if(signal.aborted)return;this.typing=typingSample(this.now()-began,settings);this.pose={column:this.typing.column,tilt:this.typing.tilt,rotate:this.typing.rotate};this._publish();options.onPrint?.(this.typing);id=this.frame(tick);};
      tick();
    }));
  }
  select(pose={}){return this.run([{...pose,op:'select'}]);}
  advance(columns=1,options={}){return this.run([{...options,op:'advance',columns}]);}
  backspace(columns=1,options={}){return this.run([{...options,op:'backspace',columns}]);}
  carriageReturn(options={}){return this.run([{...options,op:'return'}]);}
  stop(){this._epoch++;this._active?.abort();this._active=null;this._tail=Promise.resolve();this.pose.column=Math.round(this.pose.column);this._publish();}
  reset(){this.stop();this.typing=null;this.pose={column:0,tilt:0,rotate:0};this._publish();}
  dispose(){this.stop();this._disposed=true;}
}
