// Absolute-time sampling avoids accumulating a frame of delay per character.
export function typingSample(elapsed,{cps=13,columns=43,returnMs=350,feedMs=120}={}){
 const typeMs=columns/cps*1000,period=typeMs+returnMs+feedMs;
 const line=Math.floor(elapsed/period),t=elapsed-line*period;
 const count=Math.min(columns,Math.floor(t*cps/1000));
 const returning=t>=typeMs,feeding=t>=typeMs+returnMs;
 const column=returning?columns*(1-Math.min(1,(t-typeMs)/returnMs)):Math.min(columns,t*cps/1000);
 const glyph=line*columns+count,phase=(t*cps/1000)%1;
 return {column,tilt:returning?0:[-12,-4,4,12][glyph%4],rotate:returning?0:((glyph*73)%280)-140,
  strike:returning?0:Math.sin(phase*Math.PI),characters:line*columns+count,line,count,
  feed:line+(feeding?Math.min(1,(t-typeMs-returnMs)/feedMs):0),phase:returning?(feeding?'linefeed':'return'):'typing'};
}
