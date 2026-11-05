import assert from 'node:assert/strict';
// OCC edit-item-visual.ts accepts canvas-percent x/y (rounded to .01),
// and scalar scale (rounded to .001). HF reframe x/y are canvas pixels.
export function reframeToOcc(reframe={},width=1920,height=1080){
 assert(Number.isFinite(width)&&width>0&&Number.isFinite(height)&&height>0,'Positive canvas required');
 const {x=0,y=0,scale=1}=reframe;
 for(const [k,v] of Object.entries({x,y,scale}))assert(Number.isFinite(v),`Non-finite reframe ${k}`);
 assert(scale>=.05&&scale<=16,'OCC scale range .05..16');
 const rx=x/width*100,ry=y/height*100;
 assert(Math.abs(rx)<=400&&Math.abs(ry)<=400,'OCC translation range ±400 canvas percent');
 return {x:Math.round(rx*100)/100,y:Math.round(ry*100)/100,scale:Math.round(scale*1000)/1000};
}
export function assertOccReframe(actual,expected,label){
 for(const [key,fallback] of Object.entries({x:0,y:0,scale:1}))assert.equal(actual?.[key]??fallback,expected[key],`${label}: native ${key} differs from manifest reframe`);
}
